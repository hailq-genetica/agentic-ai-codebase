# Evaluating Agentic AI on PD Therapeutic-Discovery Tasks

This document describes **how PD-TxBench evaluates an AI agent** on Parkinson's disease (PD)
therapeutic-discovery tasks — what is measured, how it is scored, and how to run and interpret it.
For the per-criterion scoring mechanics see [`pdtx_scoring_guide.md`](pdtx_scoring_guide.md); for the
task catalog and quick-start see [`../tasks/pdtx/README.md`](../tasks/pdtx/README.md).

---

## 1. What "agentic evaluation" means here

Most biomedical benchmarks score a single answer to a single question. PD-TxBench instead evaluates
whether a model can **behave like a useful PD therapeutic-discovery assistant** — running a multi-step
workflow over real tools and producing a structured, decision-bearing deliverable. The unit of
evaluation is not an answer string but an **episode**: the agent receives a problem and the project's
tool suite, then must drive the full reasoning chain itself:

```
PD mechanism → therapeutic target → modality choice → evidence strength
→ safety / liability → translational feasibility → Go/No-Go decision → next experiment
```

This rides on the existing M3A agent loop (`run_agent.py`): the model issues tool calls one at a time,
results (including generated plots/files) are fed back, and per-step telemetry is captured. PD-TxBench
adds the task suite, the deliverable contract, and the scorer (`run_pdtx.py` + `src/pdtx_eval/`).

---

## 2. What is evaluated

Each episode is judged on both the **scientific content** and the **agentic behavior** behind it:

| Dimension | What it captures |
|---|---|
| **Mechanistic understanding** | Correct PD biology (e.g. GBA1→GCase→lysosome→α-synuclein), target relevance |
| **Evidence grounding** | Did the agent *retrieve and use* real evidence (literature, trials, databases, predictions) rather than answer from memory? |
| **Therapeutic reasoning** | Modality-appropriate analysis (small molecule / gene / cell therapy) |
| **Safety / risk analysis** | ADMET liabilities, immunogenicity, tumorigenicity, off-target — surfaced, not ignored |
| **Decision quality** | A calibrated Go / No-Go / Conditional Go (or claim classification) that matches the evidence |
| **Uncertainty calibration** | Distinguishes mechanistic plausibility / biomarker effects from proven efficacy; states what would change the verdict |
| **Anti-overclaiming** | Does *not* treat preclinical or biomarker signals as proven clinical efficacy |
| **Tool use** | Chose relevant tools, integrated their outputs, handled failures gracefully (e.g. excluded a failed docking run rather than fabricating a result) |

---

## 3. The task suite

Four therapy families, each with a **positive** case and a **negative control** (8 seed tasks; see
`tasks/pdtx/`):

| Family | Positive | Negative control |
|---|---|---|
| Small molecule | GCase chaperone candidate for GBA1-PD | strong docking but poor BBB + hERG liability |
| Gene therapy | AAV-GBA1 delivery | non-specific pan-brain SNCA knockdown |
| Cell therapy | iPSC-derived midbrain DA neurons | TH+ product with residual OCT4/NANOG (tumor risk) |
| Evidence reasoning | "Ambroxol is a DMT for PD" claim | a mouse motor result claimed as proven clinical efficacy |

**Negative controls are the core of the design.** A fluent model can rationalize almost any proposal;
the benchmark specifically tests whether the agent can say **No-Go / Contradicted** when the evidence
demands it (an undeliverable molecule, an unsafe vector, a tumorigenic cell product, an overclaim).
Decision accuracy on the negative controls is the headline robustness signal.

Each task ships a **gold/rubric file** (`tasks/pdtx/gold/<id>.json`) with the preferred decision,
required concepts, acceptable variants, red flags, and a per-family weighted rubric.

---

## 4. The deliverable contract

Every task asks the agent to write, to its run directory:

- **`result.json`** — structured output validated against the per-category definition in
  `tasks/pdtx/schemas/output_schema_v2.json`. Validation enforces the *structural contract*: required
  keys present, the decision field a valid enum, `confidence` a 0–1 number. Descriptive/content fields
  accept any JSON shape (a model may return richer structure than a plain string).
- **`reasoning.txt`** — a short prose write-up of the analysis behind the decision.

`output_dir` is injected into `run_python_repl`, and the runner locates the deliverable in the run
directory (with a fallback search) so a stray write path still gets scored.

---

## 5. Tools and runtime

Agents draw on the M3A tool suite, gated per task via `tool_category`:

- **Always available:** literature/web search (PubMed, Scholar, web), `run_python_repl`, `run_terminal`.
- **Databases (`external_database`):** OpenTargets, Monarch, ClinVar, GWAS, ChEMBL, PubChem, UniProt,
  PDB, ClinicalTrials, FDA, etc.
- **Pharmacology (`external_pharmacology`):** ADMET / binding-affinity models (DeepPurpose), AutoDock
  Vina, DiffDock, physicochemical properties — used by the small-molecule tasks.

Two reproducible runtimes are provided (`docker/`):
- **CPU** (`Dockerfile.pdtx`) — agent loop + databases/literature; sufficient for gene/cell/evidence tasks.
- **GPU** (`Dockerfile.pdtx-gpu`) — adds CUDA torch + DeepPurpose ADMET/binding, Vina + `prepare_receptor`,
  and the Docker CLI so DiffDock runs as a GPU sibling container.

> **Reproducibility caveat:** the MVP uses *live* tools (real APIs / model downloads), so results are
> not byte-reproducible across time. All tool calls are logged. A frozen-snapshot tool sandbox is
> future work.

---

## 6. Evaluation modes

Set per run via `run_pdtx.py --mode`:

- **Autonomous** (`--mode autonomous`, `interactive: false`) — the agent completes the episode alone.
  This is the primary scored mode.
- **Human-in-the-loop** (`--mode hitl`, `interactive: true`) — the loop prompts after each tool call so
  a human can steer; used to measure whether human guidance improves the outcome.

*(Human-on-the-loop / milestone checkpoints are documented as a future extension.)*

---

## 7. Scoring

Scoring is **LLM-as-judge** (`src/pdtx_eval/rubric_eval.py`). A judge model scores each rubric criterion
0–5, identifies which gold red flags the deliverable commits, and assesses the decision against the gold
preferred decision. Scores combine into a weighted **0–1 `final_score`** (each criterion normalized and
weighted; weights sum to 1.0) with a small per-red-flag penalty. Rubric scale and per-family weights are
in [`pdtx_scoring_guide.md`](pdtx_scoring_guide.md).

Reported per episode (`<run>/evaluation.json`):

| Field | Meaning |
|---|---|
| `final_score` | Weighted rubric score (0–1), after red-flag penalty |
| `decision_match` | `match` / `acceptable` / `mismatch` / `missing` vs the gold decision |
| `criterion_scores` | Per-criterion 0–5 with justifications |
| `red_flags_triggered` | Which failure modes the deliverable commits |
| `schema_valid` | Whether `result.json` meets the structural contract |
| `provider` / `model` / `judge_provider` / `judge_model` | Provenance |

An **offline fallback** (`--offline`) scores without any API call — schema validation + required-concept
and red-flag string matching. It is indicative only (for pipeline testing), not for ranking models.

### Aggregate metrics

`run_pdtx.py --report` renders `output/pdtx/leaderboard.json` into a table — overall and by category /
mode:

- **Mean final score** — overall quality.
- **Decision accuracy** — fraction reaching the correct (or acceptable) decision; the most important
  single metric, especially on negative controls.
- **Red-flag rate** — fraction committing a flagged failure mode (overclaiming, ignoring a liability).
- **Schema-valid rate** — fraction producing a well-formed deliverable.

---

## 8. Cross-provider and cross-judge evaluation

Both the **agent** and the **judge** can run on Anthropic or OpenAI, selected independently:

- Agent provider/model: per-config `llm:` block, or runtime overrides `--provider` / `--model`.
- Judge provider/model: `--judge-provider` / `--judge-model` (defaults to the agent's provider).

This supports two useful analyses:
- **Agent A/B:** same task, different agent models — compare scientific quality and tool use.
- **Judge variance:** same deliverable, different judge — quantify grading disagreement. (Observed
  judge variance is small and benign: e.g. on the ambroxol claim, the Anthropic judge scored an
  Anthropic-produced deliverable 1.0 and the OpenAI judge scored the same deliverable 0.95 — same
  decision, one criterion docked for an unverifiable recent citation.)

---

## 9. Running and interpreting

```bash
# One task, autonomous (CPU image; gene/cell/evidence):
docker run --rm --env-file ~/.config/pdtx/openai.env -v "$PWD":/workspace -w /workspace \
  pdtx-runtime:local python run_pdtx.py --config config/pdtx/cell_therapy/ct_ipsc_da_neurons.yaml --mode autonomous

# Small-molecule (GPU image — ADMET/docking; mount the docker socket for DiffDock):
docker run --rm --gpus all --env-file ~/.config/pdtx/openai.env \
  -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD":/workspace -w /workspace \
  pdtx-runtime:gpu python run_pdtx.py --config config/pdtx/small_molecule/sm_gba1_ambroxol_analog.yaml --mode autonomous

# Whole suite, agent + judge on a chosen provider:
... python run_pdtx.py --config config/pdtx --provider openai --model <id> --mode autonomous

# Aggregate report:
... python run_pdtx.py --report
```

**Interpreting a result:**
- Start with **decision accuracy**, especially on the negative controls — a high mean score with a
  wrong No-Go is worse than a slightly lower score with the right call.
- Check **`red_flags_triggered`** — an empty list across the suite means the agent avoided overclaiming
  and ignored-liability failure modes.
- Read **`reasoning.txt`** and the **`tool_trace`** in `agent.log` — strong episodes retrieve real
  evidence (PMIDs, DB records, model outputs) and *exclude* failed tool results rather than inventing
  them.
- Treat a single episode as one sample — agent behavior is stochastic; aggregate across runs for ranking.

---

## 10. Telemetry and audit trail

Every run directory holds: `agent.log` (full tool-call trace + model responses), `result.json` +
`reasoning.txt` (deliverables), `evaluation.json` (scores), and a `verification_notebook.ipynb`
reconstructing the episode. This makes each score auditable back to the evidence the agent actually used.

---

## 11. Validity considerations and limitations

- **Negative controls are the robustness test** — fluency is cheap; correctly refusing weak/unsafe
  proposals is the discriminating signal.
- **Judge caution** — LLM judges may dock points for recent citations they cannot verify; report
  cross-judge results when ranking, not a single judge.
- **Live tools** — not byte-reproducible; a frozen snapshot is future work.
- **Schema is a structural contract, not full field documentation** — expected sub-fields live in the
  task prompts; the schema validates shape, not completeness of every descriptive field.
- **Transfer / scope** — the seed suite is small (8 tasks). It demonstrates the methodology; a larger
  curated, expert-reviewed set (per `pd_txbench_plan.md`) is the path to a publishable benchmark.
