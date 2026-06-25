#!/usr/bin/env python3
"""Generate a standardized expert-review report for a PD-TxBench run.

Pulls a run's artifacts (result.json, reasoning.txt, evaluation.json, agent.log)
plus the task's gold file and prompt, and emits a self-contained markdown report
that a domain expert can use to evaluate the agent's deliverable — including a
citation-verification table and a fillable scoring worksheet.

Usage:
    python scripts/pdtx_expert_report.py --task <category>/<task_id>      # newest run
    python scripts/pdtx_expert_report.py --run <path/to/run_dir>
    python scripts/pdtx_expert_report.py --all                            # newest run of every task
Reports are written to reports/pdtx/<task_id>_expert_review.md.
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_BASE = ROOT / "output" / "pdtx"
GOLD_DIR = ROOT / "tasks" / "pdtx" / "gold"
REPORT_DIR = ROOT / "reports" / "pdtx"

TASKS = [
    "small_molecule/sm_gba1_ambroxol_analog", "small_molecule/sm_negative_herg_bbb",
    "gene_therapy/gt_aav_gba1", "gene_therapy/gt_negative_snca_panbrain",
    "cell_therapy/ct_ipsc_da_neurons", "cell_therapy/ct_negative_residual_pluripotency",
    "evidence_reasoning/ev_ambroxol_dmt_claim", "evidence_reasoning/ev_negative_mouse_to_clinical",
]

# Rubric criterion weights for display (mirrors the gold rubric files).


def _newest_run(task: str) -> Path | None:
    runs = sorted((OUT_BASE / task).glob("run_*"), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None


def _load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _render(value, depth=0) -> list[str]:
    """Recursively render a JSON value as markdown (handles each family's shape)."""
    ind = "  " * depth
    lines = []
    if isinstance(value, dict):
        for k, v in value.items():
            label = f"**{k}**"
            if isinstance(v, (dict, list)):
                lines.append(f"{ind}- {label}:")
                lines += _render(v, depth + 1)
            else:
                lines.append(f"{ind}- {label}: {v}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{ind}-")
                lines += _render(item, depth + 1)
            else:
                lines.append(f"{ind}- {item}")
    else:
        lines.append(f"{ind}{value}")
    return lines


def _scan_log(log: Path) -> dict:
    info = {"tool_counts": {}, "queries": [], "model": "?", "effort": "?", "provider": "?",
            "steps": "?", "tokens": "?", "failures": "?", "tools_loaded": "?"}
    if not log.exists():
        return info
    text = log.read_text(errors="ignore")
    for m in re.findall(r"🔧 ([a-zA-Z_]+)", text):
        info["tool_counts"][m] = info["tool_counts"].get(m, 0) + 1
    info["queries"] = re.findall(r"query=([^\n,}]{8,140})", text)[:18]
    for pat, key in [(r"LLM Provider:\s*(\w+)", "provider"), (r"Model:\s*([^\s|]+)", "model"),
                     (r"Reasoning:\s*(\w+)", "effort"), (r"(\d+) tools loaded", "tools_loaded"),
                     (r"Steps:\s*(\d+)", "steps"), (r"Total tokens consumed:\s*([\d,]+)", "tokens"),
                     (r"Failures:\s*(\d+)", "failures")]:
        mm = re.search(pat, text)
        if mm:
            info[key] = mm.group(1)
    return info


def _citation_table(deliverable) -> list[str]:
    """Build a verification table from any 'evidence_used' / 'evidence' list."""
    ev = None
    if isinstance(deliverable, dict):
        ev = deliverable.get("evidence_used") or deliverable.get("evidence")
    if not isinstance(ev, list) or not ev:
        return ["_No structured `evidence_used` field in the deliverable; check `reasoning.txt` and "
                "`agent.log` for cited sources._"]
    rows = ["| # | Source (as given) | Used for / finding | Verified? |", "|---|---|---|:--:|"]
    for i, e in enumerate(ev, 1):
        if isinstance(e, dict):
            src = e.get("source") or e.get("source_id") or e.get("pmid_or_id") or "?"
            used = e.get("used_for") or e.get("finding") or e.get("claim_supported") or e.get("type") or ""
        else:
            src, used = str(e), ""
        src = str(src).replace("|", "\\|")[:160]
        used = str(used).replace("|", "\\|")[:200]
        rows.append(f"| {i} | {src} | {used} | ☐ |")
    return rows


def build_report(run: Path, task: str) -> str:
    category, task_id = task.split("/")
    ev = _load_json(run / "evaluation.json") or {}
    deliv = _load_json(run / "result.json")
    reasoning = (run / "reasoning.txt").read_text().strip() if (run / "reasoning.txt").exists() else "_(none)_"
    gold = _load_json(GOLD_DIR / f"{task_id}.json") or {}
    log = _scan_log(run / "agent.log")

    crit = ev.get("criterion_scores", [])
    tool_summary = ", ".join(f"{k} ×{v}" for k, v in sorted(log["tool_counts"].items(), key=lambda x: -x[1]))

    L = []
    L.append(f"# PD-TxBench Expert Review Report — {task_id}")
    L.append("")
    L.append(f"**Task:** `{task_id}`  ·  **Family:** {category}  ·  "
             f"**Type:** {'negative control' if gold.get('is_negative_control') else 'positive'}")
    L.append("")
    L.append("> Packaged for **independent expert review**. The automated LLM-judge score (§5) is a "
             "starting point, not the verdict — complete the worksheet in §7. Treat every factual claim "
             "and citation below as **the agent's assertion, to be verified**.")
    L.append("")
    # 1. Provenance
    L.append("## 1. Provenance")
    L.append("")
    L.append(f"| Field | Value |\n|---|---|")
    L.append(f"| Run | `{run.name}` |")
    L.append(f"| Agent model | `{ev.get('model','?')}` (provider: {ev.get('provider', log['provider'])}) |")
    L.append(f"| Reasoning effort | {log['effort']} |")
    L.append(f"| Mode | {ev.get('mode','?')} |")
    L.append(f"| Steps / tools loaded | {log['steps']} steps, {log['tools_loaded']} tools (failures: {log['failures']}) |")
    L.append(f"| Tokens | {log['tokens']} |")
    L.append(f"| Judge | `{ev.get('judge_model','?')}` (provider: {ev.get('judge_provider','?')}) |")
    L.append(f"| Artifacts | `{run.relative_to(ROOT)}/` (result.json, reasoning.txt, agent.log, verification_notebook.ipynb) |")
    L.append("")
    # 2. Question
    L.append("## 2. Question posed")
    L.append("")
    L.append(f"See the full task prompt at `tasks/pdtx/{task}.md`. The agent had to work the full "
             "therapeutic-reasoning chain and return a decision.")
    L.append("")
    # 3. Decision
    L.append("## 3. Agent's decision")
    L.append("")
    decision = ev.get("decision_found") or (deliv.get("go_no_go") or deliv.get("classification") if isinstance(deliv, dict) else "?")
    conf = deliv.get("confidence") if isinstance(deliv, dict) else None
    L.append(f"> **Decision: {decision}**" + (f"  ·  **Confidence: {conf}**" if conf is not None else ""))
    L.append("")
    # 4. Deliverable
    L.append("## 4. Agent's deliverable (full structured output)")
    L.append("")
    if isinstance(deliv, dict):
        L += _render(deliv)
    else:
        L.append("_result.json could not be parsed as an object._")
    L.append("")
    L.append("### Agent reasoning narrative (`reasoning.txt`)")
    L.append("")
    L.append("> " + reasoning.replace("\n", "\n> "))
    L.append("")
    # 5. Evidence/method
    L.append("## 5. Evidence base and methods (audit trail)")
    L.append("")
    L.append(f"**Methodology:** {log['steps']} steps — tool use: {tool_summary or 'n/a'}.")
    L.append("")
    if log["queries"]:
        L.append("Representative search queries:")
        for q in log["queries"][:12]:
            L.append(f"- `{q.strip()[:130]}`")
        L.append("")
    L.append("**Citations the agent relied on — verify each supports the stated claim:**")
    L.append("")
    L += _citation_table(deliv)
    L.append("")
    L.append("> The most common LLM failure mode is a plausible-but-wrong citation: confirm each "
             "PMID/DOI exists, matches title/author/year, and supports the claim.")
    L.append("")
    # 6. Automated eval
    L.append("## 5b. Automated evaluation (LLM-as-judge) — validate, don't trust")
    L.append("")
    L.append(f"Judge `{ev.get('judge_model','?')}`, rubric `{ev.get('rubric_id','?')}`. "
             f"**Final score {ev.get('final_score','?')}**, decision_match = **{ev.get('decision_match','?')}** "
             f"(gold = {gold.get('preferred_decision','?')}), schema-valid: {ev.get('schema_valid','?')}, "
             f"red flags: {ev.get('red_flags_triggered') or 'none'}.")
    L.append("")
    L.append("| Criterion | Score /5 | Judge justification (abridged) |\n|---|:--:|---|")
    for c in crit:
        j = str(c.get("justification", "")).replace("|", "\\|")[:170]
        L.append(f"| {c.get('name')} | {c.get('score')} | {j} |")
    L.append("")
    if ev.get("judge_provider") and ev.get("judge_provider") == ev.get("provider"):
        L.append("> ⚠️ **Self-grading caveat:** agent and judge are the same provider/model — risk of "
                 "self-consistency bias. The expert score (§7) is authoritative; cross-provider judging "
                 "(`--judge-provider`) can reduce this.")
        L.append("")
    # 7. Gold
    L.append("## 6. Gold reference (calibration)")
    L.append("")
    L.append(f"- **Preferred decision:** {gold.get('preferred_decision','?')} "
             f"(acceptable: {gold.get('acceptable_decisions') or '—'})")
    L.append(f"- **Required concepts:** {', '.join(gold.get('required_concepts', [])) or '—'}")
    L.append(f"- **Red flags (should NOT occur):** {'; '.join(gold.get('red_flags', [])) or '—'}")
    if gold.get("gold_rationale"):
        L.append(f"- **Gold rationale:** {gold['gold_rationale']}")
    L.append("")
    # 8. Worksheet
    L.append("## 7. Expert review worksheet *(to complete)*")
    L.append("")
    L.append("**A. Factual accuracy / hallucination check**")
    L.append("- Citations verified (exist + support claim)? ☐ all ✓  ☐ issues: ____________________")
    L.append("- Domain facts correct (mechanism, markers, trials, numbers)? ☐ ✓  ☐ ____________________")
    L.append("- Any fabricated sources/assays/data? ☐ none  ☐ ____________________")
    L.append("")
    L.append("**B. Per-criterion expert score (0–5)** — override the automated scores")
    L.append("| Criterion | Expert /5 | Note |\n|---|:--:|---|")
    for c in crit:
        L.append(f"| {c.get('name')} | ☐ | |")
    L.append("")
    L.append(f"**C. Decision** — agree with **{decision}**? ☐ Agree ☐ Disagree → your call: ____________")
    L.append("**D. Most important omission or error (if any):** ____________________")
    L.append("**E. Trust as a first-pass assessment?** ☐ Yes ☐ With edits ☐ No")
    L.append("**F. Overall expert grade (0–5): ____  Reviewer: ______  Date: ______  Specialty: ______**")
    L.append("")
    # 9. Audit
    L.append("## 8. Audit pointers")
    L.append(f"- Structured output: `{run.relative_to(ROOT)}/result.json`")
    L.append(f"- Tool-by-tool trace: `{run.relative_to(ROOT)}/agent.log`")
    L.append("- Methodology & scoring: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md`")
    L.append(f"- Task definition: `docs/pdtx_task_definitions.md` → `{task_id}`")
    L.append("")
    return "\n".join(L)


def emit(task: str):
    run = _newest_run(task)
    if run is None:
        print(f"  no runs for {task}; skipping")
        return
    task_id = task.split("/")[1]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"{task_id}_expert_review.md"
    out.write_text(build_report(run, task))
    print(f"  wrote {out.relative_to(ROOT)}  (from {run.name})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", help="<category>/<task_id> (newest run)")
    ap.add_argument("--run", help="explicit run dir")
    ap.add_argument("--all", action="store_true", help="newest run of every task")
    a = ap.parse_args()
    if a.all:
        for t in TASKS:
            emit(t)
    elif a.run:
        run = Path(a.run)
        # infer task from path output/pdtx/<cat>/<id>/run_*
        parts = run.resolve().relative_to(OUT_BASE).parts
        emit(f"{parts[0]}/{parts[1]}")
    elif a.task:
        emit(a.task)
    else:
        ap.error("one of --task / --run / --all required")


if __name__ == "__main__":
    main()
