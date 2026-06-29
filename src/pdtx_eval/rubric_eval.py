"""LLM-as-judge rubric scorer for PD-TxBench deliverables.

`evaluate_deliverable` scores one deliverable against its gold/rubric file. With an
LLMClient it uses Claude as the judge (per-criterion 0-5 scoring + red-flag and
decision assessment). Without a client (offline mode) it falls back to schema
validation plus concept/red-flag string matching, so the pipeline is testable with
no API key.

The weighted rubric score follows the plan's global formula: each criterion's
0-5 score is normalised to 0-1 and weighted by its rubric weight (weights sum to 1).
A small red-flag penalty is applied to produce the final score.
"""

import json
from typing import Any, Optional

from src.pdtx_eval import schemas
from src.pdtx_eval.judge_prompt import (
    JUDGE_SYSTEM_PROMPT,
    build_judge_user_prompt,
    submit_scores_tool,
    submit_scores_tool_choice,
)

RED_FLAG_PENALTY = 0.10  # fractional score reduction per triggered red flag (capped)


def _decision_strings(deliverable: Any) -> str:
    """Extract the decision field(s) from a deliverable for string comparison."""
    if isinstance(deliverable, dict):
        for key in ("go_no_go", "classification", "claim_classification", "decision"):
            if key in deliverable and deliverable[key]:
                return str(deliverable[key])
    return schemas.deliverable_text(deliverable)


def _weighted_score(criterion_scores: list[dict], criteria: list[dict]) -> float:
    """Combine 0-5 per-criterion scores into a 0-1 weighted score."""
    by_name = {c["name"]: c for c in criteria}
    total = 0.0
    for cs in criterion_scores:
        crit = by_name.get(cs["name"])
        if not crit:
            continue
        total += crit["weight"] * (cs["score"] / 5.0)
    return round(total, 4)


def _apply_red_flag_penalty(score: float, n_triggered: int) -> float:
    penalty = min(1.0, RED_FLAG_PENALTY * n_triggered)
    return round(max(0.0, score * (1.0 - penalty)), 4)


def evaluate_deliverable(
    task_prompt: str,
    deliverable: Any,
    gold: dict,
    client: Optional[Any] = None,
    judge_model: Optional[str] = None,
) -> dict:
    """Score one deliverable. Returns a result dict (see keys below).

    Args:
        task_prompt: the prompt the agent was given (for the judge's context).
        deliverable: the agent's result (dict parsed from result.json, or raw text).
        gold: parsed gold/rubric file (see schemas.load_gold).
        client: an LLMClient. If None, runs the offline string-match scorer.
        judge_model: optional model override (not used directly; client carries the model).
    """
    category = gold["category"]
    criteria = gold["rubric"]["criteria"]

    valid, schema_errors = schemas.validate_for_gold(deliverable, gold)

    if client is None:
        return _evaluate_offline(deliverable, gold, valid, schema_errors)

    return _evaluate_with_judge(task_prompt, deliverable, gold, client, valid, schema_errors)


def _evaluate_with_judge(task_prompt, deliverable, gold, client, valid, schema_errors) -> dict:
    criteria = gold["rubric"]["criteria"]
    user_prompt = build_judge_user_prompt(task_prompt, deliverable, gold)

    provider = getattr(client, "provider", "anthropic")
    if hasattr(client, "_system_prompt"):
        client._system_prompt = None  # ensure isolated anthropic call doesn't inherit a stale system prompt
    response = client.create(
        messages=[
            {"type": "message", "role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"type": "message", "role": "user", "content": user_prompt},
        ],
        tools=[submit_scores_tool(provider)],
        tool_choice=submit_scores_tool_choice(provider),
        reasoning_effort="medium",
        isolated=True,
    )

    judged = None
    for item in response.output:
        # Anthropic/unified items are dicts; raw OpenAI Responses items are objects.
        if isinstance(item, dict):
            name, args = (item.get("name"), item.get("arguments")) if item.get("type") == "function_call" else (None, None)
        elif getattr(item, "type", None) == "function_call":
            name, args = getattr(item, "name", None), getattr(item, "arguments", None)
        else:
            name, args = None, None
        if name == "submit_scores":
            judged = json.loads(args or "{}")
            break
    if judged is None:
        return {
            "method": "judge",
            "error": "judge did not return submit_scores",
            "schema_valid": valid,
            "schema_errors": schema_errors,
            "final_score": 0.0,
        }

    criterion_scores = judged.get("criterion_scores", [])
    rubric_score = _weighted_score(criterion_scores, criteria)
    red_flags_triggered = judged.get("red_flags_triggered", [])
    final_score = _apply_red_flag_penalty(rubric_score, len(red_flags_triggered))
    decision_match = judged.get("decision_match", "missing")

    return {
        "method": "judge",
        "category": gold["category"],
        "task_family": gold.get("task_family"),
        "rubric_id": gold.get("rubric_id"),
        "schema_valid": valid,
        "schema_errors": schema_errors,
        "criterion_scores": criterion_scores,
        "rubric_score": rubric_score,
        "red_flags_triggered": red_flags_triggered,
        "missing_concepts": judged.get("missing_concepts", []),
        "decision_match": decision_match,
        "decision_correct": decision_match in ("match", "acceptable"),
        "decision_found": judged.get("decision_found", _decision_strings(deliverable)),
        "final_score": final_score,
        "comment": judged.get("overall_comment", ""),
    }


def _evaluate_offline(deliverable, gold, valid, schema_errors) -> dict:
    """No-API scorer: schema validity + concept coverage + crude red-flag/decision check.

    Approximates each rubric criterion's 0-5 score from concept-coverage fraction, so the
    weighted score is meaningful without a judge. Clearly labelled method='offline'.
    """
    criteria = gold["rubric"]["criteria"]
    concepts = gold.get("required_concepts", [])
    variants = gold.get("acceptable_variants", [])
    red_flags = gold.get("red_flags", [])

    hits = schemas.concept_hits(deliverable, concepts, variants)
    coverage = (sum(hits.values()) / len(hits)) if hits else 0.0
    rf_hits = schemas.red_flag_hits(deliverable, red_flags)
    triggered = [rf for rf, hit in rf_hits.items() if hit]

    # Approximate every criterion by concept coverage, modulated by schema validity.
    base = coverage * (1.0 if valid else 0.7)
    approx_5 = round(base * 5)
    criterion_scores = [
        {"name": c["name"], "score": approx_5, "justification": "offline approximation from concept coverage"}
        for c in criteria
    ]
    rubric_score = _weighted_score(criterion_scores, criteria)
    final_score = _apply_red_flag_penalty(rubric_score, len(triggered))

    decision = _decision_strings(deliverable)
    preferred = gold.get("preferred_decision", "")
    acceptable = gold.get("acceptable_decisions", [])
    # Some Phase 2.5 families (e.g. target-mechanism, lead-optimization) make no
    # Go/No-Go call; their gold preferred_decision is "N/A" and the decision is
    # not scored.
    if preferred.strip().upper() in ("N/A", "NA", "NONE", ""):
        decision_match, decision_correct = "n/a", True
    else:
        decision_correct = (
            preferred.lower() in decision.lower()
            or any(a.lower() in decision.lower() for a in acceptable)
        )
        decision_match = "match" if decision_correct else "mismatch"

    return {
        "method": "offline",
        "category": gold["category"],
        "task_family": gold.get("task_family"),
        "rubric_id": gold.get("rubric_id"),
        "schema_valid": valid,
        "schema_errors": schema_errors,
        "concept_coverage": round(coverage, 4),
        "concept_hits": hits,
        "criterion_scores": criterion_scores,
        "rubric_score": rubric_score,
        "red_flags_triggered": triggered,
        "decision_match": decision_match,
        "decision_correct": decision_correct,
        "decision_found": decision,
        "final_score": final_score,
        "comment": "Offline string-match scoring (no LLM judge). Indicative only.",
    }
