#!/usr/bin/env python3
"""PD-TxBench Phase 2 runner.

Runs PD therapeutic-discovery tasks on the M3A agent loop and scores the resulting
deliverables with the LLM-as-judge rubric scorer (src/pdtx_eval).

Examples
--------
# Run + score one task autonomously (needs the runtime + ANTHROPIC_API_KEY):
python run_pdtx.py --config config/pdtx/small_molecule/sm_gba1_ambroxol_analog.yaml --mode autonomous

# Run every PD task in human-in-the-loop mode:
python run_pdtx.py --config config/pdtx --mode hitl

# Score an existing deliverable with no agent run, no API (offline string-match scorer):
python run_pdtx.py --eval-only --offline \
    --deliverable output/pdtx/.../result.json \
    --gold tasks/pdtx/gold/sm_gba1_ambroxol_analog.json

The agent run is lazily imported so the scoring path works in a bare environment
(the agent itself needs scanpy/snapatac2; the evaluator does not).
"""

import argparse
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pdtx_eval import evaluate_deliverable, load_gold, render_markdown, update_leaderboard

LEADERBOARD_PATH = Path("output/pdtx/leaderboard.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _load_yaml(path):
    import yaml  # local import so offline --eval-only needs no yaml
    with open(path) as f:
        return yaml.safe_load(f)


def _read_text(path) -> str:
    if not path:
        return ""
    p = Path(path)
    return p.read_text() if p.exists() else ""


def _find_deliverable(output_dir: Path, started_at: float | None = None,
                      search_roots: list[Path] | None = None):
    """Locate the agent's result.json.

    Search order:
      1. <output_dir>/result.json (the expected location)
      2. anything under <output_dir> (recursive)
      3. fallback: the most recently modified result.json under any of
         `search_roots` written at/after `started_at` — covers agents that
         wrote to a self-chosen path instead of the injected output_dir.
    """
    direct = output_dir / "result.json"
    if direct.exists():
        return direct
    matches = sorted(output_dir.rglob("result.json"))
    if matches:
        return matches[0]

    # Fallback: scan wider roots for a result.json produced by this run.
    candidates = []
    for root in (search_roots or []):
        if not root.exists():
            continue
        for p in root.rglob("result.json"):
            mtime = p.stat().st_mtime
            if started_at is None or mtime >= started_at - 1:  # 1s slack
                candidates.append((mtime, p))
    if candidates:
        newest = max(candidates, key=lambda c: c[0])[1]
        log_msg = f"⚠️  result.json not in run dir; using fallback {newest}"
        print(log_msg)
        return newest
    return None


def _load_deliverable(path):
    """Load result.json as a dict; fall back to raw text if not valid JSON."""
    text = Path(path).read_text()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# Default judge model per provider, used when --judge-model is not given and the
# agent's own model/provider can't be reused.
_DEFAULT_JUDGE_MODEL = {
    "anthropic": "claude-opus-4-8",
    "openai": "gpt-5",
    "azure_openai": "gpt-5",
}


def _make_judge_client(provider: str, model: str):
    from src.llm_client import LLMClient
    return LLMClient(provider=provider, model=model)


def _resolve_judge(judge_provider, judge_model, agent_provider, agent_model):
    """Pick (provider, model) for the judge.

    Provider precedence: explicit --judge-provider, else the agent's provider.
    Model precedence: explicit --judge-model, else the agent's model when the
    provider matches, else the provider default.
    """
    provider = (judge_provider or agent_provider or "anthropic").lower()
    if judge_model:
        model = judge_model
    elif agent_model and agent_model != "unknown" and provider == (agent_provider or "").lower():
        model = agent_model
    else:
        model = _DEFAULT_JUDGE_MODEL.get(provider, "claude-opus-4-8")
    return provider, model


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
def run_one(config_path, mode, user_name, skip_eval, offline, judge_model, judge_provider=None,
            provider=None, model=None):
    config = _load_yaml(config_path)

    # Runtime agent provider/model override (e.g. run an Anthropic config on OpenAI).
    if provider or model:
        llm = dict(config.get("llm") or {})
        if provider:
            llm["provider"] = provider
        if model:
            llm["model"] = model
        config["llm"] = llm

    # Resolve a deterministic output_dir so we know where the deliverable lands.
    output_dir = config.get("output_dir")
    if not output_dir:
        base = Path(config.get("output_base_dir", "output"))
        run_folder = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir = str((base / user_name / run_folder) if user_name else (base / run_folder))
    output_dir = Path(output_dir)

    # Apply runtime overrides (mode -> interactive) and pin output_dir, via a temp config.
    overridden = dict(config)
    overridden["interactive"] = (mode == "hitl")
    overridden["output_dir"] = str(output_dir)

    import yaml
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
        yaml.safe_dump(overridden, tf)
        temp_config_path = tf.name

    print(f"▶️  Running {Path(config_path).name} | mode={mode} | output={output_dir}")
    import time
    started_at = time.time()
    from run_agent import run_agent  # lazy: agent needs the single-cell stack
    run_agent(temp_config_path, user_name=user_name)

    if skip_eval:
        print(f"⏭️  Skipping evaluation (--skip-eval). Deliverable under {output_dir}")
        return None

    return _evaluate_run(config, output_dir, mode, offline, judge_model, judge_provider, started_at=started_at)


def _evaluate_run(config, output_dir, mode, offline, judge_model, judge_provider=None, started_at=None):
    gold_file = config.get("gold_file")
    if not gold_file:
        print("⚠️  No gold_file in config; cannot score. Skipping evaluation.")
        return None
    gold = load_gold(gold_file)

    # Fallback search roots, in case the agent wrote result.json to a self-chosen
    # path instead of the injected output_dir.
    search_roots = [Path(config.get("output_base_dir", "output")), Path("output/pdtx"), Path.cwd()]
    deliverable_path = _find_deliverable(output_dir, started_at=started_at, search_roots=search_roots)
    if deliverable_path is None:
        print(f"❌ No result.json found under {output_dir}; recording an empty (failed) deliverable.")
        deliverable = {}
    else:
        deliverable = _load_deliverable(deliverable_path)

    task_prompt = _read_text(config.get("task_file"))
    agent_llm = config.get("llm") or {}
    agent_model = agent_llm.get("model", "unknown")
    agent_provider = agent_llm.get("provider", "anthropic")

    jp, jm = _resolve_judge(judge_provider, judge_model, agent_provider, agent_model)
    client = None if offline else _make_judge_client(jp, jm)
    evaluation = evaluate_deliverable(task_prompt, deliverable, gold, client=client)

    evaluation.update({
        "task_id": gold["task_id"],
        "category": gold["category"],
        "mode": mode,
        "model": agent_model,
        "provider": agent_provider,
        "judge_provider": jp if not offline else None,
        "judge_model": jm if not offline else None,
        "deliverable_path": str(deliverable_path) if deliverable_path else None,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })

    (output_dir / "evaluation.json").write_text(json.dumps(evaluation, indent=2, default=str))
    update_leaderboard(LEADERBOARD_PATH, evaluation)
    print(f"✅ {gold['task_id']}: final_score={evaluation.get('final_score')} "
          f"decision={evaluation.get('decision_match')} method={evaluation.get('method')}")
    return evaluation


def eval_only(deliverable_path, gold_path, offline, judge_model, task_file, judge_provider=None):
    gold = load_gold(gold_path)
    deliverable = _load_deliverable(deliverable_path)
    task_prompt = _read_text(task_file)
    jp, jm = _resolve_judge(judge_provider, judge_model, agent_provider="anthropic", agent_model=None)
    client = None if offline else _make_judge_client(jp, jm)

    evaluation = evaluate_deliverable(task_prompt, deliverable, gold, client=client)
    evaluation.update({
        "task_id": gold["task_id"],
        "category": gold["category"],
        "mode": "eval_only",
        "model": None,
        "judge_provider": jp if not offline else None,
        "judge_model": jm if not offline else None,
        "deliverable_path": str(deliverable_path),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })

    out = Path(deliverable_path).parent / "evaluation.json"
    out.write_text(json.dumps(evaluation, indent=2, default=str))
    update_leaderboard(LEADERBOARD_PATH, evaluation)
    print(json.dumps(evaluation, indent=2, default=str))
    print(f"\n📝 Wrote {out}")
    return evaluation


# Provider-variant configs (e.g. foo.openai.yaml) are skipped in directory scans so
# a --provider override doesn't run the same task twice; pass them explicitly to use.
_PROVIDER_VARIANT_SUFFIXES = (".openai", ".anthropic", ".azure_openai")


def _gather_configs(config_arg) -> list:
    p = Path(config_arg)
    if p.is_dir():
        return [f for f in sorted(p.rglob("*.yaml"))
                if Path(f.stem).suffix not in _PROVIDER_VARIANT_SUFFIXES]
    return [p]


def main():
    ap = argparse.ArgumentParser(description="PD-TxBench Phase 2 runner")
    ap.add_argument("--config", "-c", help="Path to a PD config YAML or a directory of them")
    ap.add_argument("--mode", "-m", choices=["autonomous", "hitl"], default="autonomous",
                    help="autonomous (interactive off) or hitl (interactive on)")
    ap.add_argument("--name", "-n", default=None, help="User name (W&B grouping / output subdir)")
    ap.add_argument("--skip-eval", action="store_true", help="Run the agent but do not score")
    ap.add_argument("--offline", action="store_true",
                    help="Score without the LLM judge (schema + string-match fallback; no API)")
    ap.add_argument("--provider", default=None, choices=["anthropic", "openai", "azure_openai"],
                    help="Override the agent provider for all configs (e.g. run Anthropic configs on OpenAI)")
    ap.add_argument("--model", default=None, help="Override the agent model id for all configs")
    ap.add_argument("--judge-model", default=None, help="Model id for the judge (default: agent's model)")
    ap.add_argument("--judge-provider", default=None, choices=["anthropic", "openai", "azure_openai"],
                    help="LLM provider for the judge (default: the agent's provider; eval-only: anthropic)")
    # eval-only path
    ap.add_argument("--eval-only", action="store_true", help="Score an existing deliverable; no agent run")
    ap.add_argument("--deliverable", help="Path to a result.json (with --eval-only)")
    ap.add_argument("--gold", help="Path to a gold/rubric json (with --eval-only)")
    ap.add_argument("--task-file", help="Optional task .md to give the judge context (with --eval-only)")
    ap.add_argument("--report", action="store_true", help="Print the leaderboard markdown report and exit")
    args = ap.parse_args()

    if args.report:
        if not LEADERBOARD_PATH.exists():
            print("No leaderboard yet.")
            return
        summary = json.loads(LEADERBOARD_PATH.read_text()).get("summary", {})
        print(render_markdown(summary))
        return

    if args.eval_only:
        if not (args.deliverable and args.gold):
            ap.error("--eval-only requires --deliverable and --gold")
        eval_only(args.deliverable, args.gold, args.offline, args.judge_model, args.task_file,
                  judge_provider=args.judge_provider)
        return

    if not args.config:
        ap.error("--config is required (or use --eval-only / --report)")

    configs = _gather_configs(args.config)
    if not configs:
        ap.error(f"No config YAMLs found at {args.config}")
    for cfg in configs:
        run_one(str(cfg), args.mode, args.name, args.skip_eval, args.offline, args.judge_model,
                judge_provider=args.judge_provider, provider=args.provider, model=args.model)

    if not args.skip_eval and LEADERBOARD_PATH.exists():
        summary = json.loads(LEADERBOARD_PATH.read_text()).get("summary", {})
        print("\n" + render_markdown(summary))


if __name__ == "__main__":
    main()
