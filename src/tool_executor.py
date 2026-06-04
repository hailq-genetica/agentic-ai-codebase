"""Tool execution logic for the agent."""

import base64
import json
import traceback
from pathlib import Path
import matplotlib.pyplot as plt

from src.tool_registry import execute_tool
from src.hooks import pre_tool_call_hook, REASONING_FIELDS, RETRY_REASONING_FIELDS
from src.logging_utils import log
from src.wandb_utils import log_execution, log_plot
from src.tool_metadata import is_plotting_tool, get_output_path_params

# Tools that accept literature_blacklist (injected from config to exclude source study)
LITERATURE_TOOLS = frozenset({
    "query_pubmed",
    "query_arxiv",
    "query_scholar",
    "search_google",
    "extract_url_content",
    "extract_pdf_content",
    "fetch_supplementary_info_from_doi",
    "advanced_web_search_claude",
})


class ToolCallWrapper:
    """Wrapper for tool call data from unified response format."""
    __slots__ = ('name', 'call_id', 'arguments', 'type')

    def __init__(self, data: dict):
        self.name = data.get("name")
        self.call_id = data.get("call_id")
        self.arguments = data.get("arguments", "{}")
        self.type = "function_call"


def _encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string for Responses API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _save_new_figures(state, output_dir, figures_before: set, tool_name: str = None) -> list[dict]:
    """
    Save any matplotlib figures that were created during tool execution.
    
    Args:
        state: AgentState instance (for plot ID tracking)
        output_dir: Path for output files
        figures_before: Set of figure numbers that existed before tool execution
        tool_name: Name of the tool that generated the plots (for organized naming)
    
    Returns:
        list[dict]: List of dicts with 'path' and 'base64' keys for each saved plot
    """
    saved_plots = []
    figures_after = set(plt.get_fignums())
    new_figures = figures_after - figures_before
    
    for fig_idx, fig_num in enumerate(sorted(new_figures), 1):
        fig = plt.figure(fig_num)
        plot_id = state.get_next_plot_id()  # Monotonic ID ensures unique filenames
        
        # Build descriptive filename: try figure title first, then tool name
        fig_title = None
        if fig._suptitle:
            # Use figure suptitle if set (sanitized)
            fig_title = fig._suptitle.get_text().strip()
        elif fig.axes and fig.axes[0].get_title():
            # Fall back to first axes title
            fig_title = fig.axes[0].get_title().strip()
        
        if fig_title:
            # Sanitize title for filename
            safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in fig_title)[:50]
            plot_file = output_dir / f"{safe_title}.png"
        elif tool_name:
            # Use tool name with index if multiple plots
            plot_file = output_dir / f"{tool_name}_{fig_idx}.png"
        else:
            # Fallback to generic naming (use plot_id for uniqueness)
            plot_file = output_dir / f"plot_{plot_id:02d}.png"
        
        fig.savefig(plot_file, dpi=150, bbox_inches="tight")
        plt.close(fig)
        
        # Encode to base64 for vision capability
        base64_data = _encode_image_to_base64(str(plot_file))
        saved_plots.append({
            "path": str(plot_file),
            "base64": base64_data,
        })
        # Log plot immediately to wandb (survives crashes)
        log_plot(str(plot_file), state.step_count)
    
    return saved_plots


def execute_tool_call(tc, state, output_dir, token_info=None):
    """
    Execute a single tool call and return the output dict(s).

    Args:
        tc: Tool call object from API response (has .name, .call_id, .arguments)
        state: AgentState instance (includes client, task, execution_history)
        output_dir: Path for output files
        token_info: Token usage from the API call that issued this tool (for unified history)

    Returns:
        list: List containing the function_call_output dict, plus any image messages
              for the model to see generated plots (Responses API format)
    """
    name = tc.name
    args = json.loads(tc.arguments) if tc.arguments else {}
    
    # Get unique execution ID for this tool call
    exec_id = state.get_next_exec_id()
    
    # Detect retry
    recent_failures = state.get_recent_failures(name)
    is_retry = len(recent_failures) > 0
    retry_count = len(recent_failures)
    
    # Log tool call
    args_preview_str = ', '.join(f'{k}={v}' for k, v in list(args.items())[:2])
    retry_indicator = f" 🔄 RETRY #{retry_count + 1}" if is_retry else ""
    log(f"🔧 {name}({args_preview_str}){retry_indicator}")
    
    # Log changed params for retries
    if is_retry and recent_failures:
        _log_retry_changes(args, recent_failures[-1]["args"])
    
    # Get reasoning via observability hook (skipped if capture_telemetry=False)
    reasoning = None
    if getattr(state, "capture_telemetry", True):
        last_failure = recent_failures[-1] if recent_failures else None
        reasoning = pre_tool_call_hook(
            client=state.client,
            tool_name=name,
            tool_args=args,
            previous_response_id=state.previous_response_id,
            pending_tool_calls=[tc],
            is_retry=is_retry,
            previous_error=last_failure.get("error") if last_failure else None,
            previous_args=last_failure.get("args") if last_failure else None,
            # Additional context for Anthropic (ignored by Azure)
            task=state.task,
            execution_history=state.execution_history,
        )
    
    # Extract reasoning data
    reasoning_data, intent = _extract_reasoning(reasoning)
    
    # Prepare args for execution
    exec_args = _prepare_args(args, output_dir, tool_name=name,
                               adata_rna=state.adata_rna,
                               adata_atac=state.adata_atac,
                               adata_atac_backed=state.adata_atac_backed,
                               adata_combined=state.adata_combined,
                               data_dir=state.data_dir,
                               literature_blacklist=getattr(state, "literature_blacklist", None),
                               cnmf_usage_df=getattr(state, "cnmf_usage_df", None),
                               cnmf_spectra_scores_df=getattr(state, "cnmf_spectra_scores_df", None),
                               cnmf_top_genes_df=getattr(state, "cnmf_top_genes_df", None))
    args_preview = {k: (f"<AnnData {v.n_obs}x{v.n_vars}>" if hasattr(v, 'n_obs') else v) for k, v in exec_args.items()}
    log(f"    📥 Args: {args_preview}")
    
    # Track existing figures before execution (to detect new plots)
    figures_before = set(plt.get_fignums())
    
    # Execute
    # PyO3 converts most Rust panics to PanicException (BaseException) which we catch here.
    # True SIGABRT (double-panic, panic=abort) is uncatchable; the ReadOnlyAnnDataProxy on
    # adata_atac_backed prevents the most common trigger (writing to read-only backed data).
    saved_plots = []
    try:
        result = execute_tool(name, **exec_args)

        # Handle AnnData return — route to correct state slot by tool name prefix
        if hasattr(result, "n_obs"):
            if name.startswith("scRNA_scATAC_"):
                state.adata_combined = result
                label = "genes/peaks"
            elif name.startswith("scATAC_"):
                state.adata_atac = result
                label = "peaks"
            elif name.startswith("scRNA_"):
                state.adata_rna = result
                label = "genes"
            else:
                state.adata_combined = result  # External / unknown → combined
                label = "features"
            result = f"{result.n_obs} cells, {result.n_vars} {label}"
        
        # Handle plots - automatically detect and save any new matplotlib figures
        saved_plots = _save_new_figures(state, output_dir, figures_before, tool_name=name)
        if saved_plots:
            plot_info = ", ".join(f"📊 {p['path']}" for p in saved_plots)
            result = f"{result}\n{plot_info}" if result else plot_info
        
        log(f"   ✅ {str(result)}")
        output = json.dumps({"status": "success", "result": str(result)[:500]})
        
        # Record success (unified: tool + tokens together)
        args_for_log = json.dumps(args_preview, default=str)[:500]
        state.add_execution(name, args, args_for_log, intent, reasoning_data, True, str(result), 
                           token_info=token_info, exec_id=exec_id)
        # Log immediately to wandb (survives crashes)
        log_execution(state.execution_history[-1])
        
    except (KeyboardInterrupt, SystemExit):
        raise  # Do not swallow; let run_agent or caller handle
    except BaseException as e:
        # Catch Exception and PyO3 PanicException (BaseException) so tool fails gracefully
        # instead of crashing the agent. Rust panics that abort the process still cannot be caught.
        err_msg = str(e) or f"{type(e).__name__}: (no message)"
        log(f"   ❌ FAILED [{type(e).__name__}] {err_msg}")
        log(f"      Traceback: {traceback.format_exc().splitlines()[-2]}")
        output = json.dumps({"status": "error", "error": err_msg})

        # Still try to save any plots that were created before the error
        saved_plots = _save_new_figures(state, output_dir, figures_before, tool_name=name)

        # Record failure (unified: tool + tokens together)
        args_for_log = json.dumps(args_preview, default=str)[:500]
        state.add_execution(name, args, args_for_log, intent, reasoning_data, False, err_msg,
                           token_info=token_info, exec_id=exec_id, error=err_msg)
        # Log immediately to wandb (survives crashes)
        log_execution(state.execution_history[-1])
    
    # Collect plots tracked by REPL monkey-patches (plt.show, savefig, plotly)
    # These are plots that the REPL already saved to disk but tool_executor hasn't seen.
    if name == "run_python_repl":
        from src.tools_external.support_tools import get_repl_saved_plots
        for path in get_repl_saved_plots():
            if Path(path).is_file():
                try:
                    b64 = _encode_image_to_base64(path)
                    saved_plots.append({"path": path, "base64": b64})
                    log_plot(path, state.step_count)
                except Exception:
                    pass

    # Build return list: function output + any generated images for vision
    outputs = [{"type": "function_call_output", "call_id": tc.call_id, "output": output}]
    
    # Add image messages for the model to see plots (Responses API format)
    if saved_plots:
        image_content = []
        for plot in saved_plots:
            image_content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{plot['base64']}"
            })
        # Add descriptive text so model knows these are the plots from the tool
        image_content.insert(0, {
            "type": "input_text",
            "text": f"[GENERATED PLOTS]: The tool generated {len(saved_plots)} plot(s). Please analyze them:"
        })
        # Add a user message containing the images so the model can see them
        outputs.append({
            "type": "message",
            "role": "user",
            "content": image_content
        })
        log(f"   👁️ {len(saved_plots)} plot(s) sent to model for visual inspection")
    
    return outputs


def _log_retry_changes(new_args: dict, old_args: dict):
    """Log what changed between retry attempts."""
    changed = []
    for k, v in new_args.items():
        if k in old_args and str(old_args[k]) != str(v):
            changed.append(f"{k}: {old_args[k]} → {v}")
        elif k not in old_args:
            changed.append(f"{k}: (new) {v}")
    if changed:
        log(f"    📝 Changed params: {', '.join(changed)}")


def _extract_reasoning(reasoning: dict) -> tuple[dict, str]:
    """Extract reasoning data and intent from hook response."""
    reasoning_data = {}
    intent = None
    
    if reasoning:
        if reasoning.get("_is_retry"):
            for field in RETRY_REASONING_FIELDS:
                reasoning_data[field] = reasoning.get(field, 'N/A')
            intent = f"Retry: {reasoning.get('error_diagnosis', 'N/A')}"
        else:
            for field in REASONING_FIELDS:
                reasoning_data[field] = reasoning.get(field, 'N/A')
            intent = reasoning.get('intent', 'N/A')
    
    return reasoning_data, intent


def _prepare_args(args: dict, output_dir: Path, tool_name: str = None,
                   adata_rna=None, adata_atac=None, adata_atac_backed=None,
                   adata_combined=None, data_dir=None, literature_blacklist=None,
                   cnmf_usage_df=None, cnmf_spectra_scores_df=None, cnmf_top_genes_df=None) -> dict:
    """Prepare args for tool execution (inject adata, redirect paths).
    
    Data objects are injected unconditionally; execute_tool() filters
    kwargs by function signature so each tool only receives what it declares:
    - scRNA tools  (``adata``)             → adata_rna
    - scATAC tools (``adata_atac``)        → adata_atac
    - scATAC tools (``adata_atac_backed``) → adata_atac_backed (snapatac2 backed, read-only)
    - Multimodal   (``adata_rna`` + ``adata_atac``) → both
    - REPL         (``adata_rna``, ``adata_atac``, ``adata_atac_backed``, ``adata_combined``, ``data_dir``)
    - Literature   (``literature_blacklist``) → from config, to exclude source study
    Uses tool_metadata registry to determine:
    - Which tools need output_dir passed
    - Which tools are plotting tools (need show=False)
    - Which parameter names are output paths (need redirection)
    """
    exec_args = args.copy()
    exec_args.pop("dataset", None)  # Legacy arg from LLM; no longer used
    
    # Inject literature blacklist for search/fetch tools (so agent cannot shortcut via source paper)
    if tool_name in LITERATURE_TOOLS and literature_blacklist is not None:
        exec_args["literature_blacklist"] = literature_blacklist
    
    # Inject all available data — execute_tool filters kwargs by function signature,
    # so each tool only receives the parameters it actually declares.
    # scRNA tools accept "adata", scATAC tools accept "adata_atac",
    # multimodal tools accept "adata_rna" + "adata_atac".
    if adata_rna is not None:
        exec_args["adata"] = adata_rna       # scRNA tools use "adata"
        exec_args["adata_rna"] = adata_rna   # multimodal + REPL use "adata_rna"
    if adata_atac is not None:
        exec_args["adata_atac"] = adata_atac
    if adata_atac_backed is not None:
        exec_args["adata_atac_backed"] = adata_atac_backed
    if adata_combined is not None:
        exec_args["adata_combined"] = adata_combined
    if data_dir is not None:
        exec_args["data_dir"] = str(data_dir)
    if cnmf_usage_df is not None:
        exec_args["usage_df"] = cnmf_usage_df
    if cnmf_spectra_scores_df is not None:
        exec_args["spectra_scores_df"] = cnmf_spectra_scores_df
    if cnmf_top_genes_df is not None:
        exec_args["top_genes_df"] = cnmf_top_genes_df

    # Get output path parameters for this tool from metadata registry
    output_path_params = get_output_path_params(tool_name) if tool_name else set()
    
    # If tool has output_dir in its output path params, pass it
    if "output_dir" in output_path_params and "output_dir" not in args:
        exec_args["output_dir"] = str(output_dir)
    
    # If tool is registered as a plotting tool OR has 'show' parameter, set show=False
    # so figures stay in memory for auto-saving
    if "show" in args or (tool_name and is_plotting_tool(tool_name)):
        exec_args["show"] = False
    
    # Redirect output paths using metadata-defined parameter names
    for path_key in output_path_params:
        if path_key in exec_args and exec_args[path_key]:
            original = str(exec_args[path_key])
            if not original.startswith(str(output_dir)):
                basename = Path(original).name or original.replace("./", "").replace("/", "_")
                exec_args[path_key] = str(output_dir / basename)
    
    return exec_args


def parse_response(response, state) -> tuple[list, str]:
    """
    Parse API response into tool calls, final text, and reasoning.
    Handles both unified dict format and raw object format.
    
    Returns:
        tuple: (tool_calls list, final_text or None)
    """
    tool_calls = []
    final_text = None
    
    for item in response.output:
        # Handle dict format (unified response — Anthropic and converted formats)
        if isinstance(item, dict):
            item_type = item.get("type")
            
            if item_type == "message":
                content = item.get("content", [])
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        final_text = c.get("text")
            
            elif item_type == "reasoning":
                summary = item.get("summary")
                if summary:
                    state.add_reasoning(summary)
                    log(f"💭 {summary}\n")
            
            elif item_type == "function_call":
                tool_calls.append(ToolCallWrapper(item))
        
        # Handle object format (raw Azure OpenAI response)
        elif hasattr(item, "type"):
            if item.type == "message":
                for c in item.content:
                    if hasattr(c, "text"):
                        final_text = c.text
            
            elif item.type == "reasoning":
                summary = getattr(item, "summary", None)
                if summary:
                    state.add_reasoning(summary)
                    log(f"💭 {summary}\n")
            
            elif item.type == "function_call":
                tool_calls.append(item)
    
    return tool_calls, final_text
