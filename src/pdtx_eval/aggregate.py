"""Aggregate PD-TxBench evaluation results into a leaderboard + markdown report."""

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


def _safe_mean(xs):
    xs = [x for x in xs if x is not None]
    return round(mean(xs), 4) if xs else None


def aggregate(evaluations: list[dict]) -> dict:
    """Roll up a list of per-task evaluation dicts.

    Each evaluation is expected to carry: task_id, category, mode, model, final_score,
    decision_correct, red_flags_triggered, schema_valid.
    """
    by_category = defaultdict(list)
    by_mode = defaultdict(list)
    for e in evaluations:
        by_category[e.get("category", "unknown")].append(e)
        by_mode[e.get("mode", "unknown")].append(e)

    def _summ(group):
        return {
            "n": len(group),
            "mean_final_score": _safe_mean([g.get("final_score") for g in group]),
            "decision_accuracy": _safe_mean([1.0 if g.get("decision_correct") else 0.0 for g in group]),
            "schema_valid_rate": _safe_mean([1.0 if g.get("schema_valid") else 0.0 for g in group]),
            "red_flag_rate": _safe_mean([1.0 if g.get("red_flags_triggered") else 0.0 for g in group]),
        }

    return {
        "overall": _summ(evaluations),
        "by_category": {k: _summ(v) for k, v in sorted(by_category.items())},
        "by_mode": {k: _summ(v) for k, v in sorted(by_mode.items())},
        "tasks": [
            {
                "task_id": e.get("task_id"),
                "category": e.get("category"),
                "mode": e.get("mode"),
                "model": e.get("model"),
                "final_score": e.get("final_score"),
                "decision_match": e.get("decision_match"),
                "red_flags_triggered": e.get("red_flags_triggered", []),
                "method": e.get("method"),
            }
            for e in evaluations
        ],
    }


def update_leaderboard(leaderboard_path: str | Path, evaluation: dict) -> dict:
    """Append/replace one task's evaluation in the leaderboard JSON and rewrite aggregates.

    Keyed by (task_id, mode, model) so re-runs overwrite rather than duplicate.
    """
    path = Path(leaderboard_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    if path.exists():
        try:
            runs = json.loads(path.read_text()).get("runs", [])
        except (json.JSONDecodeError, OSError):
            runs = []

    key = (evaluation.get("task_id"), evaluation.get("mode"), evaluation.get("model"))
    runs = [r for r in runs if (r.get("task_id"), r.get("mode"), r.get("model")) != key]
    runs.append(evaluation)

    doc = {"runs": runs, "summary": aggregate(runs)}
    path.write_text(json.dumps(doc, indent=2, default=str))
    return doc


def render_markdown(summary: dict) -> str:
    """Render an aggregate summary dict as a markdown report."""
    lines = ["# PD-TxBench evaluation report", ""]
    ov = summary.get("overall", {})
    lines += [
        f"**Tasks scored:** {ov.get('n', 0)}  ",
        f"**Mean final score:** {ov.get('mean_final_score')}  ",
        f"**Decision accuracy:** {ov.get('decision_accuracy')}  ",
        f"**Schema-valid rate:** {ov.get('schema_valid_rate')}  ",
        f"**Red-flag rate:** {ov.get('red_flag_rate')}",
        "",
        "## By therapy category",
        "",
        "| Category | N | Mean score | Decision acc | Schema valid | Red-flag rate |",
        "|---|--:|--:|--:|--:|--:|",
    ]
    for cat, s in summary.get("by_category", {}).items():
        lines.append(
            f"| {cat} | {s['n']} | {s['mean_final_score']} | {s['decision_accuracy']} "
            f"| {s['schema_valid_rate']} | {s['red_flag_rate']} |"
        )
    lines += ["", "## By mode", "", "| Mode | N | Mean score | Decision acc |", "|---|--:|--:|--:|"]
    for mode, s in summary.get("by_mode", {}).items():
        lines.append(f"| {mode} | {s['n']} | {s['mean_final_score']} | {s['decision_accuracy']} |")
    return "\n".join(lines) + "\n"
