# Scientific Data Analysis Agent

Agentic AI for scientific data analysis with multi-provider LLM support (Azure OpenAI, Anthropic) and tool calling.

## Quick start

```bash
python run_agent.py --config config/test.yaml --name your-name
```

Interactive mode: add `--interactive`. List tools: `--list-tools`.

## Config

Set your config YAML (e.g. `config/test.yaml`) with `task_file`, `data_path`, `output_dir`, and LLM provider. Example:

```yaml
llm:
  provider: anthropic   # or azure_openai
  model: claude-3-5-sonnet-20241022
```

**Env:** `ANTHROPIC_API_KEY` or `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` (see config for details).

## Layout

- `run_agent.py` — main entry
- `src/` — agent loop, config, tool registry, hooks, observability (W&B, Weave)
- `config/` — YAML configs
- `prompts/` — task prompts
