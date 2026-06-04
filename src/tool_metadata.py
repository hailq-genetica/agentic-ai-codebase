"""
Tool metadata registry for declarative tool properties.

This replaces all hardcoded tool name checks with a metadata-based approach.
When adding a new tool, register its metadata here instead of updating
multiple hardcoded lists throughout the codebase.

Tool properties:
- is_plotting: Tool generates matplotlib figures (set show=False, auto-save plots)
- output_path_params: Parameter names that contain output file paths (redirect to output_dir)
- module: Module path where the tool function is defined
"""

from typing import Optional


# =============================================================================
# Tool Metadata Definitions
# =============================================================================

# Tools that generate matplotlib plots - need show=False and auto-save
PLOTTING_TOOLS = {
    # These are registered dynamically from tool registry modules
    # See _register_plotting_tools_from_registry()
}

# Tool-specific output path parameter names
# Maps tool_name -> set of parameter names that are output paths
TOOL_OUTPUT_PATH_PARAMS = {
    # Default applies to all tools
    "_default_": {"output_dir", "filename", "save_output_base", "output_path", "save_path", "dest"},
    # Tool-specific overrides (add here if a tool uses non-standard param names)
    "run_python_repl": {"output_dir"},
}

# Module mappings for tool execution
# Maps tool_name -> module_path for import
TOOL_MODULE_MAPPINGS = {
    # Support tools
    "run_python_repl": "src.tools_external.support_tools",
    "read_function_source_code": "src.tools_external.support_tools",
    "download_synapse_data": "src.tools_external.support_tools",
    "run_terminal": "src.tools_external.support_tools",
    # scselected tools - scRNA (limited curated set)
    "scRNA_calculate_qc_metrics": "src.tool_scselected.scrna",
    "scRNA_perform_qc_filtering": "src.tool_scselected.scrna",
    "scRNA_remove_high_mt_cells": "src.tool_scselected.scrna",
    "scRNA_get_doublet_scores": "src.tool_scselected.scrna",
    "scRNA_normalize_data": "src.tool_scselected.scrna",
    "scRNA_feature_selection": "src.tool_scselected.scrna",
    "scRNA_dimensionality_reduction": "src.tool_scselected.scrna",
    "scRNA_batch_correction": "src.tool_scselected.scrna",
    "scRNA_clustering": "src.tool_scselected.scrna",
    "scRNA_cnmf_factorization": "src.tool_scselected.scrna",
    "scRNA_infercnv": "src.tool_scselected.scrna",
    # scselected tools - scATAC (using snapatac2)
    "scATAC_calculate_qc_metrics": "src.tool_scselected.scatac",
    "scATAC_qc_filter_cells": "src.tool_scselected.scatac",
    "scATAC_calculate_tiles": "src.tool_scselected.scatac",
    "scATAC_feature_selection": "src.tool_scselected.scatac",
    "scATAC_doublet_detection": "src.tool_scselected.scatac",
    "scATAC_filter_doublets": "src.tool_scselected.scatac",
    "scATAC_dimensionality_reduction": "src.tool_scselected.scatac",
    "scATAC_batch_correction": "src.tool_scselected.scatac",
    "scATAC_clustering": "src.tool_scselected.scatac",
    "scATAC_identify_marker_peaks": "src.tool_scselected.scatac",
    # scselected tools - multimodal (joint RNA + ATAC)
    "scRNA_scATAC_perform_joint_embedding": "src.tool_scselected.multiome",
}


# =============================================================================
# Public API
# =============================================================================

def is_plotting_tool(tool_name: str) -> bool:
    """Check if a tool generates matplotlib plots."""
    # First check explicit registry
    if tool_name in PLOTTING_TOOLS:
        return True
    # Lazy-load from tool registry if not already done
    _ensure_plotting_tools_registered()
    return tool_name in PLOTTING_TOOLS


def get_output_path_params(tool_name: str) -> set:
    """Get the set of parameter names that are output paths for a tool."""
    # Tool-specific params take precedence
    if tool_name in TOOL_OUTPUT_PATH_PARAMS:
        return TOOL_OUTPUT_PATH_PARAMS[tool_name]
    # Fall back to defaults
    return TOOL_OUTPUT_PATH_PARAMS.get("_default_", set())


def get_tool_module(tool_name: str) -> Optional[str]:
    """Get the module path for a tool, or None if not explicitly mapped."""
    return TOOL_MODULE_MAPPINGS.get(tool_name)


def register_plotting_tool(tool_name: str):
    """Register a tool as a plotting tool."""
    PLOTTING_TOOLS.add(tool_name)


def register_tool_module(tool_name: str, module_path: str):
    """Register the module path for a tool."""
    TOOL_MODULE_MAPPINGS[tool_name] = module_path


def register_output_path_params(tool_name: str, param_names: set):
    """Register output path parameter names for a tool."""
    TOOL_OUTPUT_PATH_PARAMS[tool_name] = param_names


# =============================================================================
# Auto-registration from Tool Registry
# =============================================================================

_plotting_tools_registered = False


def _ensure_plotting_tools_registered():
    """Lazy-load plotting tools from the tool registry modules."""
    global _plotting_tools_registered
    if _plotting_tools_registered:
        return
    
    _plotting_tools_registered = True
    _register_plotting_tools_from_registry()


def _register_plotting_tools_from_registry():
    """
    Scan tool registry modules and register plotting tools based on their metadata.
    
    Tools are marked as plotting tools if they have 'is_plotting': True in their
    definition, OR if they are in a plotting-specific registry module.
    """
    from pathlib import Path
    import importlib
    
    registry_dir = Path(__file__).parent / "tool_registry"
    if not registry_dir.exists():
        return
    
    for py_file in registry_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        
        module_name = py_file.stem
        try:
            module = importlib.import_module(f"src.tool_registry.{module_name}")
            if not hasattr(module, "description"):
                continue
            
            # Check if this is a plotting-focused registry (by module name or content)
            is_plotting_module = "plotting" in module_name.lower()
            
            for tool in module.description:
                tool_name = tool.get("name", "")
                
                # Register if explicitly marked as plotting
                if tool.get("is_plotting", False):
                    PLOTTING_TOOLS.add(tool_name)
                    continue
                
                # Register if in a plotting module
                if is_plotting_module:
                    PLOTTING_TOOLS.add(tool_name)
                    continue
                
                # Register if tool has 'show' parameter (strong indicator of plotting)
                all_params = tool.get("required_parameters", []) + tool.get("optional_parameters", [])
                param_names = {p.get("name", "") for p in all_params}
                if "show" in param_names:
                    PLOTTING_TOOLS.add(tool_name)
                    
        except Exception:
            pass  # Skip modules that can't be loaded


def get_all_plotting_tools() -> set:
    """Get all registered plotting tools."""
    _ensure_plotting_tools_registered()
    return PLOTTING_TOOLS.copy()
