"""
Generate Jupyter notebooks from agent execution for verification and audit trail.

This module creates reproducible notebooks that capture:
- All tool calls with their arguments
- Results and outputs
- Plots (embedded as images)
- Errors and their resolution
"""

import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell, new_output

# System event prefixes - these are internal agent events, not actual tools
# Defined here rather than relying on string matching in multiple places
SYSTEM_EVENT_PREFIXES = {"REWIND", "USER_"}


def generate_verification_notebook(
    output_dir: Path,
    task: str,
    execution_history: List[Dict],
    interaction_history: List[Dict],
    adata_info: Optional[Dict] = None,
) -> Path:
    """
    Generate a Jupyter notebook capturing the entire agent execution.
    
    Args:
        output_dir: Directory to save the notebook
        task: Original task description
        execution_history: Unified execution history (tool + token info per entry)
        interaction_history: List of user interactions (feedback, questions)
        adata_info: Info about final adata state
        
    Returns:
        Path to the generated notebook
    """
    nb = new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    }
    
    cells = []
    
    # Title and metadata
    cells.append(new_markdown_cell(_generate_header(task, output_dir)))
    
    # Setup cell
    cells.append(new_code_cell(_generate_setup_code()))
    
    # Process execution history grouped by step
    step_tools = {}
    
    for record in execution_history:
        step = record.get("step", 0)
        if step not in step_tools:
            step_tools[step] = []
        step_tools[step].append(record)
    
    # Generate cells for each step
    for step in sorted(step_tools.keys()):
        tools = step_tools[step]
        
        cells.append(new_markdown_cell(f"## Step {step}"))
        
        for tool_record in tools:
            # Add tool execution cell
            code_cell, output = _generate_tool_cell(tool_record, output_dir)
            cell = new_code_cell(code_cell)
            if output:
                cell.outputs = [output]
            cells.append(cell)
    
    # Check for feedback in interaction history
    feedback_entries = [h for h in interaction_history if h.get("type") == "feedback"]
    if feedback_entries:
        cells.append(new_markdown_cell("## User Feedback"))
        for fb in feedback_entries:
            cells.append(new_markdown_cell(f"**Step {fb.get('step', '?')}**: {fb.get('content', '')}"))
    
    # Summary section
    cells.append(new_markdown_cell(_generate_summary(execution_history, interaction_history, adata_info)))
    
    nb.cells = cells
    
    # Save notebook
    notebook_path = output_dir / "verification_notebook.ipynb"
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    
    return notebook_path


def _generate_header(task: str, output_dir: Path) -> str:
    """Generate the notebook header markdown."""
    return f"""# Agent Execution Verification Notebook

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Output Directory**: `{output_dir}`

## Task
{task}

---

This notebook captures the complete execution trace of the agent, including:
- All tool calls with arguments
- Results and outputs  
- Plots (embedded)
- Errors encountered
- Rewinds and alternative paths

You can re-run individual cells to verify results or explore alternative parameters.
"""


def _generate_setup_code() -> str:
    """Generate the setup code cell."""
    return """# Setup - Run this cell first
import warnings
warnings.filterwarnings('ignore')

import scanpy as sc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load the data (if available)
import os
from pathlib import Path

# Set plotting defaults
sc.settings.verbosity = 1
sc.settings.set_figure_params(dpi=100, frameon=False)

print("Setup complete!")
"""


def _generate_tool_cell(record: Dict, output_dir: Path) -> tuple[str, Any]:
    """Generate a code cell for a tool execution.
    
    Returns:
        tuple: (code_string, output_object or None)
    """
    name = record.get("name", "unknown")
    args = record.get("args", {})
    success = record.get("success", False)
    intent = record.get("intent", "")
    reasoning = record.get("reasoning", {})
    
    # Build the code representation
    lines = []
    
    # Add intent as comment
    if intent and intent != "N/A":
        lines.append(f"# Intent: {intent}")
    
    # Add reasoning summary if available
    if reasoning and isinstance(reasoning, dict):
        analysis_step = reasoning.get("analysis_step", "")
        if analysis_step and analysis_step != "N/A":
            lines.append(f"# Analysis step: {analysis_step}")
    
    # Check if this is a system event (not an actual tool)
    is_system_event = any(name.startswith(prefix) for prefix in SYSTEM_EVENT_PREFIXES)
    
    # Special handling for Python REPL - show actual code
    if name == "run_python_repl":
        command = args.get("command", "")
        lines.append(f"# Python code executed via run_python_repl")
        # Add the actual Python code (cleaned up)
        code_lines = command.strip("```").strip()
        if code_lines.startswith("python"):
            code_lines = code_lines[6:].strip()
        lines.append(code_lines)
    elif is_system_event:
        # System events (REWIND, USER_FEEDBACK, etc.) - just show as comment
        lines.append(f"# {name}")
        if args:
            lines.append(f"# Args: {args}")
    else:
        # All other tools - show as execute_tool call
        args_str = _format_args_for_code(args)
        lines.append(f"# Tool: {name}")
        lines.append(f"result = execute_tool('{name}', {args_str})")
    
    code = "\n".join(lines)
    
    # Generate output
    output = None
    if success:
        result_str = record.get("result", "")
        
        # Check if the result mentions any plot files (📊 indicates a saved plot)
        if "📊" in result_str and "plot_" in result_str:
            # Extract plot file paths from result
            import re
            plot_paths = re.findall(r'plot_\d+\.png', result_str)
            for plot_name in plot_paths:
                pf = output_dir / plot_name
                if pf.exists():
                    try:
                        with open(pf, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode("utf-8")
                        output = new_output(
                            output_type="display_data",
                            data={"image/png": img_data},
                            metadata={}
                        )
                        break
                    except Exception:
                        pass
        
        if output is None:
            # Text output
            output = new_output(
                output_type="stream",
                name="stdout",
                text=f"✅ Success\n"
            )
    else:
        error_msg = record.get("error", "Unknown error")
        output = new_output(
            output_type="stream",
            name="stderr",
            text=f"❌ Error: {error_msg}\n"
        )
    
    return code, output


def _format_args_for_code(args: Dict) -> str:
    """Format arguments dictionary as Python code string."""
    if not args:
        return "adata=adata"
    
    parts = ["adata=adata"]
    for k, v in args.items():
        if k == "adata":
            continue
        if isinstance(v, str):
            parts.append(f"{k}='{v}'")
        elif isinstance(v, (list, dict)):
            parts.append(f"{k}={json.dumps(v)}")
        else:
            parts.append(f"{k}={v}")
    
    return ", ".join(parts)


def _generate_summary(
    execution_history: List[Dict],
    interaction_history: List[Dict],
    adata_info: Optional[Dict],
) -> str:
    """Generate the summary section markdown."""
    total_tools = len(execution_history)
    successful = sum(1 for t in execution_history if t.get("success", True))
    failed = total_tools - successful
    
    feedback_count = sum(1 for h in interaction_history if h.get("type") == "feedback")
    
    lines = [
        "## Execution Summary",
        "",
        f"- **Total tool calls**: {total_tools}",
        f"- **Successful**: {successful}",
        f"- **Failed**: {failed}",
        f"- **User feedback entries**: {feedback_count}",
    ]
    
    if adata_info:
        lines.extend(["", "### Final Data State"])
        # adata_info can be nested: {"rna": {n_obs, n_vars}, "atac": {...}, "atac_backed": {...}, "combined": {...}}
        if "n_obs" in adata_info and "n_vars" in adata_info:
            lines.extend([
                f"- Cells: {adata_info.get('n_obs', 'N/A')}",
                f"- Genes: {adata_info.get('n_vars', 'N/A')}",
            ])
        else:
            for key, info in adata_info.items():
                if isinstance(info, dict) and "n_obs" in info and "n_vars" in info:
                    lines.append(f"- **{key}**: {info['n_obs']} cells × {info['n_vars']} features")
    
    # Token usage from unified history
    if execution_history:
        total_input = sum(t.get("input_tokens", 0) for t in execution_history)
        total_output = sum(t.get("output_tokens", 0) for t in execution_history)
        if total_input > 0 or total_output > 0:
            lines.extend([
                "",
                "### Token Usage",
                f"- Total input tokens: {total_input:,}",
                f"- Total output tokens: {total_output:,}",
            ])
    
    return "\n".join(lines)




def add_plot_to_notebook(notebook_path: Path, plot_path: Path, cell_index: int = -1):
    """Add a plot image to an existing notebook cell.
    
    Args:
        notebook_path: Path to the notebook
        plot_path: Path to the plot image
        cell_index: Index of cell to add plot to (-1 for last cell)
    """
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    
    with open(plot_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")
    
    output = new_output(
        output_type="display_data",
        data={"image/png": img_data},
        metadata={}
    )
    
    if cell_index < 0:
        cell_index = len(nb.cells) + cell_index
    
    if 0 <= cell_index < len(nb.cells):
        if not hasattr(nb.cells[cell_index], 'outputs'):
            nb.cells[cell_index].outputs = []
        nb.cells[cell_index].outputs.append(output)
    
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
