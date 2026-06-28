# Evaluating agentic AI for biological discovery in autonomous and copilot settings

Code for the **Multistep Multimodal Multiomic Agentic (M3A)** framework — an evaluation framework for measuring how LLMs perform data-driven reasoning over complex computational biology workflows.

M3A enforces constraints across five core dimensions to enable rigorous tracing of agent behavior: (i) a standardized execution environment for reproducible baseline conditions; (ii) a unified tool suite spanning literature retrieval, programmatic analysis, terminal access, and domain-specific single-cell pipelines; (iii) recursive multimodal context integration across steps; (iv) persistent data state maintained across tool invocations; and (v) step-level telemetry capturing intent, tool selection, and outcomes at each decision point.

We applied M3A to evaluate a Claude Opus 4.6 (Feb 6, 2026) based agent across multi-step, multi-omic reasoning tasks with predefined evaluation endpoints spanning molecular profiling data from multiple cancer types.

## Quick start

```bash
# HAI experiment (interactive)
python run_agent.py --config config/hai/jyates_eac.yaml --name your-name

# HTAN experiment (batch)
python run_agent_htan.py --config config/htan/opus-4-6/brca/celltype_annotation.yaml
```

Interactive mode: add `--interactive`. List available tools: `--list-tools`.

## PD-TxBench (Phase 2 MVP)

An agentic benchmark for **Parkinson's disease therapeutic discovery** built on top of the same
agent loop. It evaluates whether the model can reason across mechanism → target → modality →
evidence → safety → Go/No-Go → next experiment across three therapy modalities (small molecule,
gene therapy, cell therapy) plus evidence-verification tasks, including **negative controls** that
test for safe No-Go / anti-overclaiming behavior.

```bash
# Run + judge-score one PD task (autonomous):
python run_pdtx.py --config config/pdtx/small_molecule/sm_gba1_ambroxol_analog.yaml --mode autonomous

# Run all PD tasks human-in-the-loop:
python run_pdtx.py --config config/pdtx --mode hitl

# Score an existing deliverable offline (no agent, no API key):
python run_pdtx.py --eval-only --offline \
    --deliverable output/pdtx/.../result.json --gold tasks/pdtx/gold/sm_gba1_ambroxol_analog.json

# Aggregate leaderboard report:
python run_pdtx.py --report
```

Tasks live in `tasks/pdtx/`, configs in `config/pdtx/`, the LLM-as-judge scorer in `src/pdtx_eval/`.
See `tasks/pdtx/README.md` and `docs/pdtx_scoring_guide.md`.

### PD-TxBench Phase 2.5 (small-molecule deep-dive)

A small-molecule-focused slice that reuses the same runner/judge with **8 small-molecule
task families** (target-mechanism reasoning, evidence verification, candidate-SMILES
evaluation, ADMET/CNS assessment, docking/binding interpretation, lead optimization,
repurposing/translatability, and agentic episodes). Phase 2.5 golds keep
`category: small_molecule` and add `phase: phase2_5` + `task_family`, which route
deliverable validation to a per-family schema and add a per-family leaderboard breakdown.

```bash
python scripts/build_phase2_5_seed.py        # (re)generate the seed dataset from the spec
python scripts/validate_phase2_5.py          # offline end-to-end validation (no API key)
python run_pdtx.py --config config/pdtx/phase2_5   # run + judge-score all Phase 2.5 tasks
```

The current pass is a runnable **seed slice** (12 tasks across all 8 families, 4 negative
controls). See `docs/pdtx_phase2_5_taxonomy.md` for the contract and `pd_txbench_phase2.5.md`
for the full plan.

## Config

Each run is driven by a YAML config. Key fields:

```yaml
task_file: tasks/hai/jyates_eac.md        # analysis task prompt
scrna_data_path: data/.../scrna.h5ad       # scRNA-seq input
scatac_data_path: data/.../scatac.h5ad     # scATAC-seq input
output_base_dir: output/                   # run outputs written here
tool_category: scselected_scrna, scselected_scatac, external_database
reasoning_effort: medium                   # low / medium / high
interactive: true                          # prompt user after each tool call
llm:
  provider: anthropic
  model: claude-opus-4-6
logging:
  enabled: true
  project: my-wandb-project
  entity: my-wandb-entity
```

**Env:** set `ANTHROPIC_API_KEY`. For W&B logging also set `WANDB_API_KEY`.

## Layout

- `run_agent.py` — main entry point (HAI / interactive experiments)
- `run_agent_htan.py` — entry point for HTAN batch experiments (adds cNMF data loading)
- `src/` — agent loop, LLM client, tool registry, hooks, observability (W&B, Weave)
- `config/` — YAML configs (`hai/` for HAI datasets, `htan/opus-4-6/` for HTAN cancer types)
- `tasks/` — task prompt files (`.md` / `.txt`) referenced by configs
- `data/` — input datasets (see `data/README.md` for expected structure)
- `output/` — agent run results (see `output/README.md` for structure)
- `scripts/` — utility scripts for tool registry and MCP server generation
