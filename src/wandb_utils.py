"""Wandb logging utilities for the agent."""

import wandb
from src.logging_utils import logger, log


def log_tokens(token_info: dict, tracker: "TokenTracker"):
    """Log token usage metrics to wandb.
    
    Args:
        token_info: Dict from TokenTracker.process_usage() with per-step metrics
        tracker: TokenTracker instance with cumulative state
    """
    if not logger.wandb_run:
        return
    
    metrics = {
        # Per-step token metrics
        "tokens/input": token_info["input_tokens"],
        "tokens/output": token_info["output_tokens"],
        "tokens/reasoning": token_info["reasoning_tokens"],
        "tokens/completion": token_info["completion_tokens"],
        # Cumulative totals
        "tokens/cumulative_input": tracker.cumulative_input,
        "tokens/cumulative_output": tracker.cumulative_output,
        "tokens/cumulative_total": tracker.cumulative_input + tracker.cumulative_output,
        # Context saturation
        "context/saturation_pct": token_info["saturation_pct"],
        "context/peak_saturation_pct": tracker.peak_saturation_pct,
        "context/limit": tracker.context_limit,
    }
    
    # Add image metrics if images were sent
    if token_info.get("images_sent", 0) > 0 or tracker.total_images_sent > 0:
        metrics.update({
            "tokens/image_estimate": token_info.get("image_tokens_estimate", 0),
            "tokens/images_sent": token_info.get("images_sent", 0),
            "tokens/cached": token_info.get("cached_tokens", 0),
            "tokens/cumulative_image_estimate": tracker.cumulative_image_tokens,
            "tokens/cumulative_images_sent": tracker.total_images_sent,
        })
    
    wandb.log(metrics)


_execution_rows = []  # Simple list of rows

# All columns - including flattened reasoning fields
_COLUMNS = [
    "step", "exec_id", "tool", "args", "success", "error",
    "input_tokens", "output_tokens", "reasoning_tokens", "completion_tokens", "saturation_pct",
    # Flattened reasoning fields
    "intent", "alternatives_considered", "reason_for_choice", "assumptions", "expected_outcome",
    # Flattened retry reasoning fields  
    "error_diagnosis", "parameters_changed",
]

def log_execution(entry: dict):
    """Log execution to wandb table at each step."""
    if not logger.wandb_run:
        return
    
    # Get reasoning dict (may be empty)
    reasoning = entry.get("reasoning", {}) or {}
    
    # Append row with ALL columns including flattened reasoning
    _execution_rows.append([
        entry.get("step", 0),
        entry.get("exec_id", 0),
        entry.get("name", "unknown"),
        str(entry.get("args_preview", ""))[:200],
        entry.get("success", True),
        str(entry.get("error", ""))[:100] if entry.get("error") else "",
        entry.get("input_tokens", 0),
        entry.get("output_tokens", 0),
        entry.get("reasoning_tokens", 0),
        entry.get("completion_tokens", 0),
        entry.get("saturation_pct", 0),
        # Flattened reasoning fields
        str(reasoning.get("intent", ""))[:300],
        str(reasoning.get("alternatives_considered", ""))[:300],
        str(reasoning.get("reason_for_choice", ""))[:300],
        str(reasoning.get("assumptions", ""))[:300],
        str(reasoning.get("expected_outcome", ""))[:300],
        # Flattened retry reasoning fields
        str(reasoning.get("error_diagnosis", ""))[:300],
        str(reasoning.get("parameters_changed", ""))[:300],
    ])
    
    # Create fresh table with all rows and log
    table = wandb.Table(columns=_COLUMNS, data=_execution_rows)
    wandb.log({"execution": table})


def log_plot(plot_path: str, step: int):
    """Log a plot image to wandb."""
    if not logger.wandb_run:
        return
    from pathlib import Path
    plot_file = Path(plot_path)
    if plot_file.exists():
        wandb.log({f"plots/{plot_file.stem}": wandb.Image(str(plot_file))})


def finalize(output_dir, step_count: int, plot_count: int,
             execution_history: list, interaction_history: list, tracker: "TokenTracker",
             config_path: str = None, task_path: str = None):
    """Finalize wandb run - log summary metrics, tables, and artifacts.
    
    Args:
        output_dir: Output directory containing logs, plots, notebooks
        config_path: Path to config YAML file (for reproducibility)
        task_path: Path to task.txt file (for reproducibility)
        
    Note: .h5ad files are NOT uploaded (too large) - saved locally in output_dir.
    """
    if not logger.wandb_run:
        return
    
    # Calculate stats from execution history
    total_calls = len(execution_history)
    failures = sum(1 for h in execution_history if not h.get("success", True))
    
    # Summary metrics
    wandb.summary.update({
        "total_steps": step_count,
        "total_tool_calls": total_calls,
        "total_failures": failures,
        "success_rate": (total_calls - failures) / total_calls if total_calls > 0 else 1.0,
        "total_plots": plot_count,
        # Token totals
        "tokens/total_input": tracker.cumulative_input,
        "tokens/total_output": tracker.cumulative_output,
        "tokens/total_reasoning": tracker.cumulative_reasoning,
        "tokens/total_consumed": tracker.cumulative_input + tracker.cumulative_output,
        # Context
        "context/peak_saturation_pct": tracker.peak_saturation_pct,
        "context/limit": tracker.context_limit,
        "context/high_saturation_warning": tracker.peak_saturation_pct > 80,
    })
    
    # Image token summary (if any images were sent)
    if tracker.total_images_sent > 0:
        wandb.summary.update({
            "tokens/total_image_estimate": tracker.cumulative_image_tokens,
            "tokens/total_images_sent": tracker.total_images_sent,
        })
    
    # Note: execution table is already maintained incrementally by log_execution().
    # No need to rebuild it here — avoids storage duplication.
    
    # Log interaction history table (only produced at end-of-run)
    _log_interaction_table(interaction_history)
    
    # Log artifacts (including config for reproducibility, excluding .h5ad)
    _log_artifacts(output_dir, config_path, task_path)
    
    # Finish wandb run
    wandb.finish()
    logger.set_wandb_run(None)
    print(f"📊 Wandb run finished")


def _log_interaction_table(interaction_history: list):
    """Log user interactions as a wandb Table."""
    if not interaction_history:
        return
    
    columns = ["step", "type", "content", "response", "affects_context"]
    table = wandb.Table(columns=columns)
    for h in interaction_history:
        table.add_data(
            h.get("step", 0),
            h.get("type", "unknown"),
            h.get("content", "")[:500],
            h.get("response", h.get("reason", ""))[:500],
            h.get("affects_context", False),
        )
    wandb.log({"user_interactions": table})
    
    # Interaction summary
    wandb.summary["interactions/total"] = len(interaction_history)
    wandb.summary["interactions/questions"] = sum(1 for h in interaction_history if h.get("type") == "question")
    wandb.summary["interactions/feedbacks"] = sum(1 for h in interaction_history if h.get("type") == "feedback")


def _log_artifacts(output_dir, config_path: str = None, task_path: str = None):
    """Log output files as wandb Artifacts.
    
    Includes config, task, logs, plots, and notebooks.
    Note: .h5ad files are excluded (too large) - saved locally in output_dir.
    """
    from pathlib import Path
    
    artifact = wandb.Artifact(f"agent_output_{logger.wandb_run.id}", type="output")
    
    # Config files (for reproducibility)
    if config_path and Path(config_path).exists():
        artifact.add_file(str(config_path), name="config.yaml")
    if task_path and Path(task_path).exists():
        artifact.add_file(str(task_path), name="task.txt")
    
    # Agent log
    log_file = output_dir / "agent.log"
    if log_file.exists():
        artifact.add_file(str(log_file))
    
    # Plots
    for plot_file in output_dir.glob("plot_*.png"):
        artifact.add_file(str(plot_file))
    
    # Notebooks
    for nb_file in output_dir.glob("*.ipynb"):
        artifact.add_file(str(nb_file))
    
    wandb.log_artifact(artifact)


def print_summary(step_count: int, execution_history: list, tracker: "TokenTracker"):
    """Print execution summary to console/log."""
    total_calls = len(execution_history)
    failures = [h for h in execution_history if not h.get("success", True)]
    
    log(f"\n## Summary")
    log(f"📊 Steps: {step_count} | Tool calls: {total_calls} | Failures: {len(failures)}")
    
    # Context usage
    log(f"\n### Context Usage")
    total_consumed = tracker.cumulative_input + tracker.cumulative_output
    log(f"   📏 Total tokens consumed: {total_consumed:,}")
    log(f"      Input:  {tracker.cumulative_input:,}")
    log(f"      Output: {tracker.cumulative_output:,}")
    
    if tracker.cumulative_reasoning > 0:
        reasoning_pct = (tracker.cumulative_reasoning / tracker.cumulative_output * 100) if tracker.cumulative_output > 0 else 0
        log(f"        🧠 Reasoning:  {tracker.cumulative_reasoning:,} ({reasoning_pct:.1f}% of output)")
        log(f"        💬 Completion: {tracker.cumulative_completion:,}")
    
    if tracker.total_images_sent > 0:
        image_pct = (tracker.cumulative_image_tokens / tracker.cumulative_input * 100) if tracker.cumulative_input > 0 else 0
        log(f"   🖼️ Images sent to model: {tracker.total_images_sent}")
        log(f"      Estimated image tokens: ~{tracker.cumulative_image_tokens:,} ({image_pct:.1f}% of input)")
    
    log(f"   📈 Peak context saturation: {tracker.peak_saturation_pct:.1f}% of {tracker.context_limit:,} token limit")
    if tracker.peak_saturation_pct > 80:
        log(f"   ⚠️  Context saturation exceeded 80% - consider summarization or context pruning")
    
    # Saturation progression
    if len(execution_history) > 1:
        saturations = [f"{h.get('saturation_pct', 0):.0f}%" for h in execution_history if h.get('saturation_pct', 0) > 0]
        if saturations:
            log(f"   📉 Saturation progression: " + " → ".join(saturations))
    
    # Errors
    if failures:
        log(f"\n### Errors Encountered")
        for f in failures:
            log(f"   Step {f['step']}: {f['name']} - {f.get('error', 'unknown')[:80]}")
    
    return total_calls, len(failures)
