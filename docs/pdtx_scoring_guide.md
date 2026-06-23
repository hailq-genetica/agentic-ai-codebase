# PD-TxBench Phase 2 — Scoring Guide

How `src/pdtx_eval` turns an agent deliverable into a score.

## Inputs

- **Deliverable** — the agent's `result.json` (parsed dict) plus its `reasoning.txt`/text.
- **Gold/rubric** — `tasks/pdtx/gold/<task_id>.json`: `preferred_decision`,
  `acceptable_decisions`, `required_concepts`, `acceptable_variants`, `red_flags`, and a weighted
  `rubric` (criteria + weights summing to 1.0).

## Rubric scale (per criterion, 0–5)

| Score | Meaning |
|---:|---|
| 0 | Completely wrong or unsafe |
| 1 | Mostly wrong, many unsupported claims |
| 2 | Partially correct but incomplete |
| 3 | Mostly correct, acceptable reasoning |
| 4 | Strong answer with good evidence |
| 5 | Expert-level, actionable, well-calibrated |

## Per-family rubric weights

Weights follow `pd_txbench_plan.md` §3–4.

**Small molecule** (`pdtx_sm_candidate_eval_v1`): PD mechanism relevance 0.20 · target/MoA 0.15 ·
ADMET interpretation 0.20 · safety risk 0.15 · Go/No-Go quality 0.15 · next experiment 0.10 ·
uncertainty 0.05.

**Gene therapy** (`pdtx_gene_therapy_eval_v1`): genetic rationale 0.20 · delivery feasibility 0.15 ·
safety risk 0.20 · patient stratification 0.15 · biomarker/endpoint 0.10 · validation plan 0.15 ·
uncertainty 0.05.

**Cell therapy** (`pdtx_cell_therapy_eval_v1`): cell identity 0.20 · safety/tumorigenicity 0.20 ·
functional maturity 0.15 · manufacturing/reproducibility 0.15 · release criteria 0.15 ·
translational decision 0.10 · uncertainty 0.05.

**Evidence reasoning** (`pdtx_evidence_verification_v1`): correct classification 0.30 · evidence use
0.25 · preclinical-vs-clinical 0.20 · uncertainty 0.15 · avoids overclaiming 0.10.

## Score combination

1. **Rubric score** = Σ over criteria of `weight × (criterion_score / 5)` → 0–1.
2. **Red-flag penalty** = `min(1, 0.10 × #red_flags_triggered)`.
3. **Final score** = `rubric_score × (1 − penalty)` → 0–1.

The judge also returns `decision_match` (`match` / `acceptable` / `mismatch` / `missing`); the
aggregate report tracks **decision accuracy** (match or acceptable) separately from the score.

## Judge vs offline

- **Judge mode** (default, needs `ANTHROPIC_API_KEY`): a Claude judge (`submit_scores` tool,
  isolated call) does the per-criterion scoring and red-flag reasoning.
- **Offline mode** (`--offline`): no API. Approximates each criterion from required-concept
  coverage, checks schema validity, string-matches red flags and the decision. Indicative only —
  use it to validate the pipeline, not to rank models.

## Aggregate report

`run_pdtx.py --report` renders `output/pdtx/leaderboard.json` into a markdown table: mean final
score, decision accuracy, schema-valid rate, and red-flag rate — overall, by therapy category, and
by mode.

## Global score weighting (reference)

For cross-task reporting, `pd_txbench_plan.md` §11 suggests: scientific correctness 0.20 · evidence
grounding 0.20 · therapeutic reasoning 0.15 · safety/risk 0.15 · tool-use quality 0.10 ·
actionability 0.10 · uncertainty calibration 0.05 · format compliance 0.05. The per-family rubrics
above are the operational instantiation of these dimensions.
