"""
Unified tool registry loader for LLM function calling.

Usage:
    from src.tool_registry import get_tools, execute_tool, list_categories
    
    # Get all tools (default: OpenAI format)
    tools = get_tools()
    
    # Get tools by exact category name
    tools = get_tools("scselected_scrna")
    tools = get_tools("external_genomics")
    
    # Get tools formatted for a specific provider
    tools = get_tools("scselected_scrna", provider="openai")
    tools = get_tools("scselected_scrna", provider="anthropic")
    
    # Execute a tool
    result = execute_tool("scRNA_pp_filter_cells", adata, min_genes=200)
"""

import importlib
import inspect
import re
from pathlib import Path
from typing import Any

from src.tool_metadata import get_tool_module


# Cache for loaded registries
_registry_cache: dict[str, Any] = {}
_tool_to_module: dict[str, str] = {}


def _load_all_registries():
    """Load all registry modules and build lookup tables."""
    if _registry_cache:
        return
    
    registry_dir = Path(__file__).parent
    
    for py_file in registry_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        
        module_name = py_file.stem
        try:
            module = importlib.import_module(f"src.tool_registry.{module_name}")
            if hasattr(module, "description"):
                _registry_cache[module_name] = module
                for tool in module.description:
                    _tool_to_module[tool["name"]] = module_name
        except Exception as e:
            print(f"Warning: Could not load {module_name}: {e}")


# =============================================================================
# Tool Formatting (raw tool definition → provider-specific format)
# =============================================================================

def _build_json_schema(tool: dict) -> dict:
    """Build JSON Schema properties and required list from a raw tool definition.
    
    This is the shared logic used by both OpenAI and Anthropic formatters.
    Converts our internal parameter format (required_parameters / optional_parameters
    with Python type names) into JSON Schema.
    """
    type_map = {
        "str": "string", "int": "integer", "float": "number", "bool": "boolean",
        "list": "array", "dict": "object", "tuple": "array",
    }
    
    def get_type(t: str) -> str:
        t = str(t)
        if "|" in t or " or " in t:
            return "string"
        return type_map.get(t.split()[0], "string")

    def build_prop(param: dict) -> dict:
        t = get_type(param["type"])
        prop = {"type": t, "description": param["description"]}
        if t == "array":
            prop["items"] = {"type": "string"}  # Default
            if "int" in param["type"]:
                prop["items"] = {"type": "integer"}
            elif "float" in param["type"]:
                prop["items"] = {"type": "number"}
        return prop

    properties = {}
    required = []
    
    for p in tool.get("required_parameters", []):
        properties[p["name"]] = build_prop(p)
        required.append(p["name"])
    
    for p in tool.get("optional_parameters", []):
        properties[p["name"]] = build_prop(p)
    
    return {"type": "object", "properties": properties, "required": required}


def _format_tool_for_openai(tool: dict) -> dict:
    """Format a raw tool definition for OpenAI Responses API (flat format).
    
    Returns:
        {"type": "function", "name": ..., "description": ..., "parameters": {...}}
    """
    schema = _build_json_schema(tool)
    return {
        "type": "function",
        "name": tool["name"],
        "description": tool["description"],
        "parameters": schema,
    }


def _format_tool_for_anthropic(tool: dict) -> dict:
    """Format a raw tool definition for Anthropic Messages API.
    
    Returns:
        {"name": ..., "description": ..., "input_schema": {...}}
    """
    schema = _build_json_schema(tool)
    return {
        "name": tool["name"],
        "description": tool["description"],
        "input_schema": schema,
    }


def format_tool_for_llm(tool: dict, provider: str = "openai") -> dict:
    """Format a raw tool definition for a specific LLM provider.
    
    Args:
        tool: Raw tool definition dict (with required_parameters, optional_parameters).
        provider: "openai" (or "azure_openai") or "anthropic".
    
    Returns:
        Tool definition in the provider's expected format.
    """
    provider = provider.lower()
    if provider in ("openai", "azure_openai"):
        return _format_tool_for_openai(tool)
    elif provider == "anthropic":
        return _format_tool_for_anthropic(tool)
    else:
        raise ValueError(f"Unsupported provider for tool formatting: {provider}")


# =============================================================================
# Public API
# =============================================================================

# Cache of top-level def names per convention module, for phantom-tool filtering.
_module_defs_cache: dict[str, "set | None"] = {}


def _tool_is_executable(module_name: str, tool_name: str) -> bool:
    """True if the tool's backing function can actually be resolved at call time.

    The registry generator can mistakenly register nested helper functions (e.g.
    `ADMET_pred` defined inside `predict_admet_properties`) as top-level tools.
    These are advertised to the LLM but fail with "Tool not found" when called.
    A tool is executable iff it has an explicit curated module mapping, or — for
    the convention-based `external_*` registries — a matching top-level `def` in
    `src/tools_external/<category>.py`. Anything we can't statically verify
    (non-external registries, missing source) is kept, to avoid false drops.
    """
    if get_tool_module(tool_name):  # explicit curated mapping → trust it
        return True
    if not module_name.startswith("external_"):
        return True  # only convention-verify external_* here
    if module_name not in _module_defs_cache:
        cat = module_name.replace("external_", "")
        src = Path(__file__).resolve().parents[1] / "tools_external" / f"{cat}.py"
        _module_defs_cache[module_name] = (
            set(re.findall(r"^def ([A-Za-z_]\w*)", src.read_text(), re.M)) if src.exists() else None
        )
    defs = _module_defs_cache[module_name]
    return True if defs is None else tool_name in defs


def get_tools(category: str = None, provider: str = "openai") -> list[dict]:
    """
    Get tools formatted for LLM function calling.
    
    Parameters
    ----------
    category : str, optional
        Exact category name to filter (e.g., 'scselected_scrna', 'external_genomics').
        Must match the registry module name exactly.
        If None, returns all tools.
    provider : str, default "openai"
        LLM provider format: "openai" / "azure_openai" or "anthropic".
    
    Returns
    -------
    list[dict]
        Tool definitions in the requested provider format.
    """
    _load_all_registries()
    
    tools = []
    for module_name, module in _registry_cache.items():
        if category is None or module_name == category:
            for tool in module.description:
                if _tool_is_executable(module_name, tool["name"]):
                    tools.append(format_tool_for_llm(tool, provider))
    return tools


def list_categories() -> list[str]:
    """List all available tool category names (module names)."""
    _load_all_registries()
    return sorted(_registry_cache.keys())


def execute_tool(tool_name: str, *args, **kwargs) -> Any:
    """
    Execute a tool by name.
    
    Automatically filters invalid kwargs to handle LLM hallucinations.
    Uses tool_metadata registry for module lookups - NO implicit fallbacks.
    
    Tools are found via:
    1. Explicit module mapping in tool_metadata.TOOL_MODULE_MAPPINGS
    2. Registry-based lookup from tool definition files
    """
    _load_all_registries()
    
    # Find the function
    func = None
    
    # 1. Check tool_metadata registry for explicit module mapping
    explicit_module = get_tool_module(tool_name)
    if explicit_module:
        try:
            module = importlib.import_module(explicit_module)
            func = getattr(module, tool_name, None)
        except ImportError as e:
            raise ValueError(f"Could not import module {explicit_module} for {tool_name}: {e}")
    
    # 3. Use registry mapping to find the module
    # Registry module naming convention determines import path:
    #   - "singlecell_*" -> src.tools_singlecell
    #   - "external_*"   -> src.tools_external.{category}
    #   - Other          -> requires explicit TOOL_MODULE_MAPPINGS entry
    if func is None:
        module_name = _tool_to_module.get(tool_name)
        if module_name:
            try:
                if module_name.startswith("singlecell"):
                    # Single-cell tools are in src.tools_singlecell package
                    from src import tools_singlecell
                    func = getattr(tools_singlecell, tool_name, None)
                elif module_name.startswith("external_"):
                    # External tools: external_genomics -> src.tools_external.genomics
                    category = module_name.replace("external_", "")
                    submodule = importlib.import_module(f"src.tools_external.{category}")
                    func = getattr(submodule, tool_name, None)
                else:
                    # Unknown registry type - tool needs explicit module mapping
                    pass
            except ImportError as e:
                raise ValueError(f"Could not import module for {tool_name} (registry: {module_name}): {e}")
    
    if func is None:
        # Suggest close/likely tool names so a hallucinated name (e.g. "ADMET_pred"
        # for "predict_admet_properties") self-corrects on the next step instead of
        # the agent guessing blindly.
        import difflib
        all_names = sorted(_tool_to_module.keys())
        lower_map = {n.lower(): n for n in all_names}
        close = [lower_map[c] for c in difflib.get_close_matches(tool_name.lower(), list(lower_map), n=5, cutoff=0.4)]
        toks = [t for t in re.split(r"[^a-z0-9]+", tool_name.lower()) if len(t) >= 4]
        substr = [n for n in all_names if any(t in n.lower() for t in toks)]
        hints = list(dict.fromkeys(close + substr))[:6]
        msg = f"Tool not found: {tool_name}"
        if hints:
            msg += f"\nDid you mean one of: {', '.join(hints)}?"
        msg += (
            "\nUse the exact registered tool name. Tools are defined in "
            "src/tool_registry/*.py (run with --list-tools to see categories)."
        )
        raise ValueError(msg)
    
    # Filter invalid kwargs
    if kwargs:
        sig = inspect.signature(func)
        valid_params = set(sig.parameters.keys())
        has_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if not has_var_kwargs:
            kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
    
    return func(*args, **kwargs)


__all__ = [
    "get_tools",
    "format_tool_for_llm",
    "list_categories",
    "execute_tool",
]
