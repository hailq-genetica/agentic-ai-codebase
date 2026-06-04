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
