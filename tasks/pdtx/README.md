# PD-TxBench Phase 2 (MVP)

An agentic benchmark that evaluates whether an AI can behave like a useful **Parkinson's
disease (PD) therapeutic-discovery assistant** — not just answer PD questions. It runs on the
existing M3A agent loop (`run_agent.py`) and is driven by `run_pdtx.py`.

Each task gives the agent a therapeutic problem and the project's tool suite, and asks it to
work through the full chain:

```
PD mechanism → therapeutic target → modality choice → evidence strength
→ safety risk → translational feasibility → Go/No-Go decision → next experiment
```

> This is a **runnable MVP slice** of the full plan in `pd_txbench_plan.md` (which targets
> 550–600 tasks, frozen tool snapshots, and multi-expert review). See "Extending" below.

## Task families (this MVP: 14 seed tasks)

| Family | Dir | Tasks | Negative control |
|---|---|---|---|
| Small molecule | `small_molecule/` | `sm_gba1_ambroxol_analog` | `sm_negative_herg_bbb` (strong docking, poor BBB + hERG) |
| Gene therapy | `gene_therapy/` | `gt_aav_gba1` | `gt_negative_snca_panbrain` (non-specific pan-brain SNCA knockdown) |
| Cell therapy | `cell_therapy/` | `ct_ipsc_da_neurons`, `ct_hesc_mda_progenitors_allo` (allogeneic HLA-mismatch), `ct_autologous_ipsc_mda` (autologous, per-line QC), `ct_gdnf_engineered_graft` (GDNF-secreting graft) | `ct_negative_residual_pluripotency` (TH+ but OCT4/NANOG high), `ct_negative_regional_misspecification` (TH+ but not A9, serotonergic→GID), `ct_negative_genomic_instability` (20q11.21/12p + TP53), `ct_negative_gdnf_uncontrolled` (unregulated, irreversible GDNF) |
| Evidence reasoning | `evidence_reasoning/` | `ev_ambroxol_dmt_claim` | `ev_negative_mouse_to_clinical` (preclinical→clinical overclaim) |

**Negative controls** test whether the model can say **No-Go / Contradicted** instead of being
talked into an unsafe or overclaimed answer — a core failure mode for drug-discovery AI.

## Deliverable

Each task instructs the agent to write, to its run output directory:
- **`result.json`** — structured output validated against the matching definition in
  `schemas/output_schema_v2.json` (`small_molecule` / `gene_therapy` / `cell_therapy` /
  `evidence_reasoning`). Every modality requires a decision field (`go_no_go` or
  `classification`) and a `confidence`.
- **`reasoning.txt`** — a short write-up of the analysis.

`output_dir` is available inside `run_python_repl`, so the agent saves with
`json.dump(..., open(f"{output_dir}/result.json", "w"))`.

## Gold + rubric

`gold/<task_id>.json` (schema: `schemas/rubric_schema_v2.json`) holds the gold decision,
`required_concepts`, `acceptable_variants`, `red_flags`, and a per-family weighted rubric.
Rubric weights per family follow `pd_txbench_plan.md` §3–4 and sum to 1.0.

## Evaluation modes

`run_pdtx.py --mode`:
- **autonomous** — `interactive: false`; the agent completes the task alone.
- **hitl** (human-in-the-loop) — `interactive: true`; the loop prompts after each tool call so a
  human can steer.

(*Human-on-the-loop / milestone checkpoints* are a documented future extension — the current
loop prompts after every tool, which covers autonomous + HITL.)

## Scoring

LLM-as-judge (`src/pdtx_eval`): a Claude judge scores each rubric criterion 0–5, flags which
`red_flags` the deliverable commits, and assesses the decision vs the gold. Scores combine into a
weighted 0–1 `final_score` (with a small red-flag penalty). See `docs/pdtx_scoring_guide.md`.
An `--offline` fallback scores via schema validation + concept/red-flag string matching (no API).

## Providers (Anthropic / OpenAI)

Both the **agent** and the **judge** can run on Anthropic or OpenAI.

- **Agent provider** is set per config under `llm:` (`provider: anthropic` + `model: claude-opus-4-8`, or `provider: openai` + `model: gpt-5`). See `evidence_reasoning/ev_ambroxol_dmt_claim.openai.yaml` for an OpenAI example.
- **Judge provider** defaults to the agent's provider; override with `run_pdtx.py --judge-provider {anthropic,openai}` (and `--judge-model`). This lets you run the agent on one provider and grade with the other.
- **Keys:** set `ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY` (whichever providers you use). With Docker, pass both env-files, e.g. `--env-file ~/.config/pdtx/anthropic.env --env-file ~/.config/pdtx/openai.env`.

The OpenAI path uses the Responses API (`reasoning.effort`); the judge's `submit_scores` tool is emitted in the correct per-provider format automatically.

## Running

```bash
# One task, autonomous, judge-scored (needs runtime + ANTHROPIC_API_KEY):
python run_pdtx.py --config config/pdtx/small_molecule/sm_gba1_ambroxol_analog.yaml --mode autonomous

# All PD tasks, human-in-the-loop:
python run_pdtx.py --config config/pdtx --mode hitl

# Score an existing deliverable offline (no agent, no API):
python run_pdtx.py --eval-only --offline \
    --deliverable output/pdtx/.../result.json \
    --gold tasks/pdtx/gold/sm_gba1_ambroxol_analog.json

# Print the aggregate leaderboard report:
python run_pdtx.py --report
```

Per-run scores are written to `<output_dir>/evaluation.json` and aggregated into
`output/pdtx/leaderboard.json` (keyed by task_id + mode + model).

## Extending

- **More tasks:** add `tasks/pdtx/<family>/<id>.md` + `tasks/pdtx/gold/<id>.json` +
  `config/pdtx/<family>/<id>.yaml`. No code changes needed.
- **Reproducibility:** the MVP uses live tools (all calls are logged). The plan's frozen-snapshot
  tool sandbox (§12) is future work.
- **Dataset splits / hidden test / leaderboard server:** future work (plan §8, §13).
