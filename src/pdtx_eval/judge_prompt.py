"""Judge prompt construction for the PD-TxBench LLM-as-judge rubric scorer."""

import json

JUDGE_SYSTEM_PROMPT = (
    "You are an expert reviewer for a Parkinson's disease (PD) therapeutic-discovery benchmark. "
    "You grade an AI assistant's deliverable against a gold reference and a scoring rubric. "
    "You are rigorous and calibrated: you reward correct mechanism, well-grounded evidence, honest "
    "uncertainty, and safe Go/No-Go judgment, and you penalize overclaiming (e.g. treating preclinical "
    "or mechanistic evidence as proven clinical efficacy) and ignored safety liabilities. "
    "Score each rubric criterion on a 0-5 integer scale:\n"
    "0 = completely wrong or unsafe; 1 = mostly wrong, many unsupported claims; "
    "2 = partially correct but incomplete; 3 = mostly correct, acceptable reasoning; "
    "4 = strong answer with good evidence; 5 = expert-level, actionable, well-calibrated.\n"
    "Return ONLY the structured scores via the provided tool."
)

SUBMIT_SCORES_NAME = "submit_scores"
SUBMIT_SCORES_DESCRIPTION = (
    "Submit the rubric scores, decision assessment, and red-flag findings for the deliverable."
)

# JSON Schema for the structured judge output (provider-agnostic).
SUBMIT_SCORES_SCHEMA = {
    "type": "object",
    "properties": {
        "criterion_scores": {
            "type": "array",
            "description": "One entry per rubric criterion, in the order given.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "score": {"type": "integer", "minimum": 0, "maximum": 5},
                    "justification": {"type": "string"}
                },
                "required": ["name", "score", "justification"]
            }
        },
        "decision_match": {
            "type": "string",
            "description": "How the deliverable's Go/No-Go (or claim classification) compares to the gold preferred decision.",
            "enum": ["match", "acceptable", "mismatch", "missing"]
        },
        "decision_found": {"type": "string", "description": "The decision the deliverable actually reached."},
        "red_flags_triggered": {
            "type": "array",
            "description": "Which of the listed red flags the deliverable actually commits.",
            "items": {"type": "string"}
        },
        "missing_concepts": {
            "type": "array",
            "description": "Required concepts the deliverable failed to engage with.",
            "items": {"type": "string"}
        },
        "overall_comment": {"type": "string"}
    },
    "required": ["criterion_scores", "decision_match", "red_flags_triggered", "overall_comment"]
}


def submit_scores_tool(provider: str) -> dict:
    """Provider-specific tool definition that forces structured per-criterion scores.

    Anthropic uses ``input_schema``; the OpenAI Responses API uses a flat
    ``function`` tool with ``parameters``.
    """
    if (provider or "").lower() == "anthropic":
        return {
            "name": SUBMIT_SCORES_NAME,
            "description": SUBMIT_SCORES_DESCRIPTION,
            "input_schema": SUBMIT_SCORES_SCHEMA,
        }
    # openai / azure_openai (Responses API function tool)
    return {
        "type": "function",
        "name": SUBMIT_SCORES_NAME,
        "description": SUBMIT_SCORES_DESCRIPTION,
        "parameters": SUBMIT_SCORES_SCHEMA,
    }


def submit_scores_tool_choice(provider: str) -> dict:
    """Force-call the submit_scores tool, in the provider's tool_choice format."""
    if (provider or "").lower() == "anthropic":
        return {"type": "tool", "name": SUBMIT_SCORES_NAME}
    return {"type": "function", "name": SUBMIT_SCORES_NAME}


# Backwards-compatible default (Anthropic format).
SUBMIT_SCORES_TOOL = submit_scores_tool("anthropic")


def build_judge_user_prompt(task_prompt: str, deliverable, gold: dict) -> str:
    """Assemble the user message handed to the judge."""
    criteria_lines = []
    for c in gold["rubric"]["criteria"]:
        criteria_lines.append(
            f"  - {c['name']} (weight {c['weight']}): {c.get('description', '')}"
        )
    criteria_block = "\n".join(criteria_lines)

    deliverable_str = deliverable if isinstance(deliverable, str) else json.dumps(deliverable, indent=2, default=str)

    return (
        f"[TASK PROMPT GIVEN TO THE AI]\n{task_prompt.strip()}\n\n"
        f"[GOLD REFERENCE]\n"
        f"Preferred decision: {gold.get('preferred_decision', 'N/A')}\n"
        f"Acceptable decisions: {gold.get('acceptable_decisions', [])}\n"
        f"Gold rationale: {gold.get('gold_rationale', 'N/A')}\n"
        f"Required concepts: {gold.get('required_concepts', [])}\n"
        f"Red flags to watch for: {gold.get('red_flags', [])}\n\n"
        f"[RUBRIC CRITERIA — score each 0-5]\n{criteria_block}\n\n"
        f"[AI DELIVERABLE TO GRADE]\n{deliverable_str}\n\n"
        f"Grade the deliverable now. Score every rubric criterion in order, assess the decision, "
        f"and list which red flags (if any) the deliverable commits. Call submit_scores."
    )
