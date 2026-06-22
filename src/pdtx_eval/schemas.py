"""Schema loading and validation for PD-TxBench deliverables and gold files.

Kept dependency-light: uses ``jsonschema`` if available, otherwise falls back to
lightweight required-key checks. Imports nothing from the single-cell stack, so
the evaluator can run in a bare environment.
"""

import json
from pathlib import Path
from typing import Any

# Repo root = three levels up from this file (src/pdtx_eval/schemas.py)
_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "tasks" / "pdtx" / "schemas"

VALID_CATEGORIES = ("small_molecule", "gene_therapy", "cell_therapy", "evidence_reasoning")


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_gold(path: str | Path) -> dict:
    """Load a gold/rubric file (tasks/pdtx/gold/<task_id>.json)."""
    gold = _load_json(Path(path))
    missing = [k for k in ("task_id", "category", "rubric", "preferred_decision") if k not in gold]
    if missing:
        raise ValueError(f"Gold file {path} missing required keys: {missing}")
    if gold["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Gold file {path} has unknown category: {gold['category']}")
    weights = [c.get("weight", 0) for c in gold["rubric"].get("criteria", [])]
    total = sum(weights)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Gold file {path} rubric weights sum to {total:.3f}, expected 1.0")
    return gold


def load_output_schema() -> dict:
    return _load_json(_SCHEMA_DIR / "output_schema_v2.json")


def validate_output(deliverable: dict, category: str) -> tuple[bool, list[str]]:
    """Validate a result.json deliverable against its per-category output schema.

    Returns (is_valid, errors). Uses jsonschema when installed; otherwise checks
    that the category definition's ``required`` keys are present.
    """
    if category not in VALID_CATEGORIES:
        return False, [f"unknown category: {category}"]

    schema_doc = load_output_schema()
    subschema = schema_doc["definitions"][category]

    try:
        import jsonschema  # type: ignore

        # Resolve internal $ref against the full document.
        validator_cls = jsonschema.validators.validator_for(schema_doc)
        resolver = jsonschema.RefResolver.from_schema(schema_doc)
        validator = validator_cls(subschema, resolver=resolver)
        errors = [f"{'/'.join(str(p) for p in e.path)}: {e.message}" for e in validator.iter_errors(deliverable)]
        return (len(errors) == 0), errors
    except ImportError:
        # Lightweight fallback: required-key presence only.
        required = subschema.get("required", [])
        errors = [f"missing required field: {k}" for k in required if k not in deliverable]
        return (len(errors) == 0), errors


import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _normalize(s: str) -> str:
    """Lowercase and collapse non-alphanumerics to single spaces (e.g. blood-brain -> blood brain)."""
    return _NON_ALNUM.sub(" ", s.lower()).strip()


def _tokens(s: str) -> set[str]:
    return {t for t in _normalize(s).split() if len(t) >= 4}


def deliverable_text(deliverable: Any) -> str:
    """Flatten a deliverable (dict or str) to searchable lowercase text."""
    if isinstance(deliverable, str):
        return deliverable.lower()
    return json.dumps(deliverable, default=str).lower()


def concept_hits(deliverable: Any, concepts: list[str], variants: list[str] | None = None) -> dict[str, bool]:
    """Match each required concept against the deliverable (offline heuristic).

    A concept counts as covered if its normalized string appears in the normalized
    deliverable text, OR if an acceptable variant that shares a substantive token
    (length >= 4) with the concept appears. Variants are coupled to concepts by token
    overlap so a single generic variant cannot mark every concept as covered.
    Case- and punctuation-insensitive.
    """
    norm_text = _normalize(deliverable_text(deliverable))
    variants = variants or []
    hits: dict[str, bool] = {}
    for c in concepts:
        if _normalize(c) in norm_text:
            hits[c] = True
            continue
        c_tokens = _tokens(c)
        coupled = [
            v for v in variants
            if (_tokens(v) & c_tokens) or _normalize(v) in _normalize(c) or _normalize(c) in _normalize(v)
        ]
        hits[c] = any(_normalize(v) in norm_text for v in coupled if v)
    return hits


def red_flag_hits(deliverable: Any, red_flags: list[str]) -> dict[str, bool]:
    """Heuristic detection of red-flag phrases in the deliverable (offline mode only).

    This is intentionally crude (substring match on the red-flag description); the LLM
    judge does the real red-flag reasoning. Kept so the offline path produces a signal.
    """
    text = deliverable_text(deliverable)
    return {rf: (rf.lower() in text) for rf in red_flags}
