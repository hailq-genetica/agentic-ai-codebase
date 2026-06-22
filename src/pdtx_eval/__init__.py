"""PD-TxBench Phase 2 evaluation package.

LLM-as-judge rubric scoring for Parkinson's disease therapeutic-discovery
deliverables produced by the M3A agent. Dependency-light (no single-cell stack)
so it runs in a bare environment.
"""

from src.pdtx_eval.rubric_eval import evaluate_deliverable
from src.pdtx_eval.schemas import load_gold, validate_output, load_output_schema
from src.pdtx_eval.aggregate import aggregate, update_leaderboard, render_markdown

__all__ = [
    "evaluate_deliverable",
    "load_gold",
    "validate_output",
    "load_output_schema",
    "aggregate",
    "update_leaderboard",
    "render_markdown",
]
