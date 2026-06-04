#!/usr/bin/env python3
"""
Generator script to create tool definitions from functions.
"""

import ast
import re
from pathlib import Path
import sys

def parse_docstring(docstring: str) -> dict:
    """Parse a numpy-style docstring to extract description and parameters."""
    if not docstring:
        return {"description": "", "parameters": {}}
    
    lines = docstring.strip().split('\n')
    
    # First non-empty line is the description
    description = ""
    param_section = False
    current_param = None
    parameters = {}
    
    i = 0
    # Get description (everything before Parameters section)
    desc_lines = []
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Parameters"):
            param_section = True
            i += 2  # Skip "Parameters" and "----------"
            break
        if line:
            desc_lines.append(line)
        i += 1
    
    description = " ".join(desc_lines)
    
    # Parse parameters
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check for Returns section - stop parsing
        if stripped.startswith("Returns"):
            break
        
        # Check for new parameter (line with parameter name and type)
        param_match = re.match(r'^(\w+)\s*:\s*(.+)$', stripped)
        if param_match and not line.startswith(' ' * 8):  # Not a continuation
            current_param = param_match.group(1)
            param_type = param_match.group(2).strip()
            parameters[current_param] = {
                "type": param_type,
                "description": ""
            }
        elif current_param and stripped:
            # This is a description line for the current parameter
            # Extract default value if present
            default_match = re.search(r'\(default[:\s]*([^)]+)\)', stripped, re.IGNORECASE)
            if default_match:
                parameters[current_param]["default"] = default_match.group(1).strip()
            
            # Append to description
            if parameters[current_param]["description"]:
                parameters[current_param]["description"] += " " + stripped
            else:
                parameters[current_param]["description"] = stripped
        
        i += 1
    
    return {"description": description, "parameters": parameters}


def get_function_signature(node: ast.FunctionDef) -> dict:
    """Extract function signature including parameters and defaults."""
    params = {"required": [], "optional": []}
    
    # Get all arguments
    args = node.args
    
    # Calculate where defaults start
    num_defaults = len(args.defaults)
    num_args = len(args.args)
    first_default_idx = num_args - num_defaults
    
    for i, arg in enumerate(args.args):
        if arg.arg == 'self' or arg.arg == 'adata':
            continue  # Skip self and adata (always first arg)
        
        param_info = {"name": arg.arg}
        
        # Check if this arg has a default
        if i >= first_default_idx:
            default_idx = i - first_default_idx
            default_node = args.defaults[default_idx]
            param_info["default"] = ast_node_to_value(default_node)
            params["optional"].append(param_info)
        else:
            params["required"].append(param_info)
    
    return params


def ast_node_to_value(node):
    """Convert an AST node to its Python value."""
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id == 'None':
            return None
        if node.id == 'True':
            return True
        if node.id == 'False':
            return False
        return node.id
    if isinstance(node, ast.List):
        return [ast_node_to_value(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(ast_node_to_value(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return {ast_node_to_value(k): ast_node_to_value(v) 
                for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -ast_node_to_value(node.operand)
    if isinstance(node, ast.Call):
        # For things like float("inf")
        if isinstance(node.func, ast.Name) and node.func.id == 'float':
            if node.args and isinstance(node.args[0], ast.Constant):
                return node.args[0].value
        return None
    if isinstance(node, ast.Attribute):
        return f"{node.value.id}.{node.attr}" if isinstance(node.value, ast.Name) else None
    return None


def infer_type_from_default(default_value):
    """Infer parameter type from its default value."""
    if default_value is None:
        return "str"  # Default assumption
    if isinstance(default_value, bool):
        return "bool"
    if isinstance(default_value, int):
        return "int"
    if isinstance(default_value, float):
        return "float"
    if isinstance(default_value, str):
        return "str"
    if isinstance(default_value, list):
        if default_value and isinstance(default_value[0], str):
            return "List[str]"
        return "list"
    if isinstance(default_value, tuple):
        return "tuple"
    if isinstance(default_value, dict):
        return "dict"
    return "str"


def parse_tool_file(filepath: str) -> list:
    """Parse a Python file and extract all public function definitions.
    
    Includes all functions except:
    - Functions starting with '_' (internal/private functions)
    - Functions starting with '__' (dunder methods)
    """
    with open(filepath, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    tools = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip internal/private functions (starting with _)
            if node.name.startswith('_'):
                continue
            
            # Get docstring
            docstring = ast.get_docstring(node) or ""
            doc_info = parse_docstring(docstring)
            
            # Get signature
            sig_info = get_function_signature(node)
            
            # Build tool definition
            tool = {
                "name": node.name,
                "description": doc_info["description"] or f"Function {node.name}",
                "required_parameters": [],
                "optional_parameters": []
            }
            
            # Process required parameters
            for param in sig_info["required"]:
                param_doc = doc_info["parameters"].get(param["name"], {})
                tool["required_parameters"].append({
                    "name": param["name"],
                    "type": param_doc.get("type", "str").split(",")[0].strip(),
                    "description": param_doc.get("description", f"Parameter {param['name']}"),
                    "default": None
                })
            
            # Process optional parameters
            for param in sig_info["optional"]:
                param_doc = doc_info["parameters"].get(param["name"], {})
                default_val = param.get("default")
                
                # Infer type from docstring or default value
                param_type = param_doc.get("type", infer_type_from_default(default_val))
                # Clean up type string
                param_type = param_type.split(",")[0].strip()
                if param_type.startswith("optional"):
                    param_type = param_type.replace("optional", "").strip().strip("()")
                
                tool["optional_parameters"].append({
                    "name": param["name"],
                    "type": param_type,
                    "description": param_doc.get("description", f"Parameter {param['name']}"),
                    "default": default_val
                })
            
            tools.append(tool)
    
    return tools


def python_repr(value):
    """Convert a Python value to its repr, handling special cases."""
    if value is None:
        return "None"
    if value == float('inf'):
        return 'float("inf")'
    if value == float('-inf'):
        return 'float("-inf")'
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return repr(value)
    if isinstance(value, dict):
        return repr(value)
    return repr(value)


def generate_tool_registry(tools: list, output_path: str):
    """Generate the scanpy_tools.py file."""
    
    # Group tools by category based on name prefix
    categories = {
        "scRNA_pp_": "PREPROCESSING FUNCTIONS (sc.pp.*)",
        "scRNA_tl_": "TOOLS FUNCTIONS (sc.tl.*)",
        "scRNA_pl_": "PLOTTING FUNCTIONS (sc.pl.*)",
        "scRNA_read": "READING FUNCTIONS (sc.read_*)",
        "scRNA_write": "WRITING FUNCTIONS (sc.write)",
        "scRNA_get_": "GET FUNCTIONS (sc.get.*)",
        "scRNA_queries_": "QUERIES FUNCTIONS (sc.queries.*)",
        "scRNA_metrics_": "METRICS FUNCTIONS (sc.metrics.*)",
        "scRNA_datasets_": "DATASETS FUNCTIONS (sc.datasets.*)",
        "scRNA_set_": "SETTINGS FUNCTIONS",
        "scRNA_ext_pp_": "EXTERNAL API - PREPROCESSING (sc.external.pp.*)",
        "scRNA_ext_tl_": "EXTERNAL API - TOOLS (sc.external.tl.*)",
        "scRNA_ext_pl_": "EXTERNAL API - PLOTTING (sc.external.pl.*)",
        "scRNA_ext_exporting_": "EXTERNAL API - EXPORTING (sc.external.exporting.*)",
    }
    
    # Sort tools into categories
    categorized = {cat: [] for cat in categories.values()}
    categorized["OTHER"] = []
    
    for tool in tools:
        placed = False
        for prefix, category in categories.items():
            if tool["name"].startswith(prefix):
                categorized[category].append(tool)
                placed = True
                break
        if not placed:
            categorized["OTHER"].append(tool)
    
    # Generate the file content
    lines = [
        '"""',
        'Tool definitions for scanpy single-cell analysis functions.',
        'Format follows Biomni tool description convention.',
        '',
        'AUTO-GENERATED by generate_tool_registry.py - DO NOT EDIT MANUALLY',
        '"""',
        '',
        'description = [',
    ]
    
    for category, cat_tools in categorized.items():
        if not cat_tools:
            continue
        
        lines.append(f'    # {"=" * 77}')
        lines.append(f'    # {category}')
        lines.append(f'    # {"=" * 77}')
        
        for tool in cat_tools:
            lines.append('    {')
            lines.append(f'        "name": {repr(tool["name"])},')
            lines.append(f'        "description": {repr(tool["description"])},')
            
            # Required parameters
            lines.append('        "required_parameters": [')
            for param in tool["required_parameters"]:
                lines.append('            {')
                lines.append(f'                "name": {repr(param["name"])},')
                lines.append(f'                "type": {repr(param["type"])},')
                lines.append(f'                "description": {repr(param["description"])},')
                lines.append(f'                "default": {python_repr(param["default"])}')
                lines.append('            },')
            lines.append('        ],')
            
            # Optional parameters
            lines.append('        "optional_parameters": [')
            for param in tool["optional_parameters"]:
                lines.append('            {')
                lines.append(f'                "name": {repr(param["name"])},')
                lines.append(f'                "type": {repr(param["type"])},')
                lines.append(f'                "description": {repr(param["description"])},')
                lines.append(f'                "default": {python_repr(param["default"])}')
                lines.append('            },')
            lines.append('        ],')
            lines.append('    },')
    
    lines.append(']')
    lines.append('')
    
    # Add simple helper functions (formatting is done in unified __init__.py)
    lines.extend([
        '# Create a lookup dictionary for quick access',
        'TOOL_LOOKUP = {tool["name"]: tool for tool in description}',
        '',
        '',
        'def get_tool_names():',
        '    """Return list of all tool names."""',
        '    return [tool["name"] for tool in description]',
        '',
        '',
        'def get_tool_by_name(name):',
        '    """Get tool definition by name."""',
        '    return TOOL_LOOKUP.get(name)',
        '',
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated {output_path} with {len(tools)} tools")


def main():
    tool_file_path = Path(sys.argv[1])
    source_name = tool_file_path.stem
    
    # Extract module name from parent directory (e.g., tools_singlecell -> singlecell)
    parent_dir = tool_file_path.parent.name
    if parent_dir.startswith("tools_"):
        module_name = parent_dir.replace("tools_", "")
    else:
        module_name = parent_dir
    
    # Output: tool_registry_<module>_<filename>.py
    # e.g., src/tools_singlecell/preprocessing.py -> singlecell_preprocessing.py
    output_path = Path("src/tool_registry") / f"{module_name}_{source_name}.py"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Parsing {tool_file_path}...")
    tools = parse_tool_file(str(tool_file_path))
    print(f"Found {len(tools)} functions")
    
    print(f"Generating {output_path}...")
    generate_tool_registry(tools, str(output_path))
    
    print("Done!")


if __name__ == "__main__":
    main()
