#!/usr/bin/env python3
"""Validate the PD-TxBench Phase 2.5 seed dataset end-to-end (no API key needed).

Checks, for every task in tasks/pdtx/phase2_5/manifest.jsonl:
  1. the gold/<id>.json loads (keys present, category valid, rubric weights sum to 1.0);
  2. it carries phase=="phase2_5" and a task_family that exists in the Phase 2.5
     output schema, with a rubric_id matching the rubric catalog and criteria that
     match it exactly;
  3. the config YAML exists and references the task_file + gold_file that exist;
  4. the offline scorer runs: a synthetic "good" deliverable validates against the
     per-family schema and scores well, while an empty deliverable fails schema
     validation and scores ~0. This proves the schema routing + scoring pipeline.

Exit code is non-zero if any check fails.

    python scripts/validate_phase2_5.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pdtx_eval import evaluate_deliverable, load_gold  # noqa: E402
from src.pdtx_eval import schemas  # noqa: E402

MANIFEST = ROOT / "tasks" / "pdtx" / "phase2_5" / "manifest.jsonl"

errors: list[str] = []


def check(cond, msg):
    if not cond:
        errors.append(msg)
    return cond


def synthetic_deliverable(gold, required_keys):
    """A plausible passing deliverable: all required keys + decision + concepts text."""
    d = {k: f"placeholder for {k}" for k in required_keys}
    # Decision fields set to the gold's preferred decision when applicable.
    pref = gold.get("preferred_decision", "")
    if "go_no_go" in required_keys:
        d["go_no_go"] = pref if pref in ("Go", "No-Go", "Conditional Go") else "Conditional Go"
    if "claim_classification" in required_keys:
        d["claim_classification"] = pref if pref not in ("", "N/A") else "Partially Supported"
    if "confidence" in required_keys:
        d["confidence"] = 0.6
    # Array-typed required fields must be arrays.
    for k in ("liability_to_address", "proposed_modifications", "properties_to_recheck",
              "main_reasons", "main_risks", "evidence_table"):
        if k in d:
            d[k] = [d[k]] if not isinstance(d[k], list) else d[k]
    # Surface every required concept/variant so the offline concept matcher can find them.
    d["_concepts_for_validation"] = " ; ".join(
        gold.get("required_concepts", []) + gold.get("acceptable_variants", [])
    )
    return d


def main():
    if not MANIFEST.exists():
        print(f"❌ manifest not found: {MANIFEST}. Run scripts/build_phase2_5_seed.py first.")
        return 1

    output_schema = schemas.load_output_schema_phase2_5()
    rubric_catalog = json.loads((ROOT / "tasks/pdtx/schemas/rubric_phase2_5.json").read_text())
    tasks = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    print(f"Validating {len(tasks)} Phase 2.5 tasks from {MANIFEST.relative_to(ROOT)}\n")

    n_ok = 0
    for t in tasks:
        tid = t["task_id"]
        gold_path = ROOT / t["gold_file"]
        cfg_path = ROOT / t["config_file"]
        task_path = ROOT / t["task_file"]
        ctx = f"[{tid}]"

        if not check(gold_path.exists(), f"{ctx} missing gold file {t['gold_file']}"):
            continue
        try:
            gold = load_gold(gold_path)  # validates keys + weight sum
        except Exception as e:  # noqa: BLE001
            errors.append(f"{ctx} load_gold failed: {e}")
            continue

        family = gold.get("task_family", "")
        check(gold.get("phase") == "phase2_5", f"{ctx} gold.phase != phase2_5")
        check(family in output_schema["definitions"],
              f"{ctx} task_family '{family}' not in output schema")
        rid = gold.get("rubric_id")
        check(rid in rubric_catalog["rubrics"], f"{ctx} rubric_id '{rid}' not in catalog")
        if rid in rubric_catalog["rubrics"]:
            check(gold["rubric"]["criteria"] == rubric_catalog["rubrics"][rid]["criteria"],
                  f"{ctx} rubric criteria differ from catalog (re-run the build script)")

        check(task_path.exists(), f"{ctx} missing task_file {t['task_file']}")
        check(cfg_path.exists(), f"{ctx} missing config {t['config_file']}")
        if cfg_path.exists():
            cfg_text = cfg_path.read_text()
            check(t["task_file"] in cfg_text, f"{ctx} config task_file path mismatch")
            check(t["gold_file"] in cfg_text, f"{ctx} config gold_file path mismatch")
            check(f"task_family: {family}" in cfg_text, f"{ctx} config task_family mismatch")

        if family not in output_schema["definitions"]:
            continue
        required_keys = output_schema["definitions"][family]["required"]

        # --- offline pipeline: good deliverable should pass + score; empty should fail ---
        good = evaluate_deliverable("(validation)", synthetic_deliverable(gold, required_keys),
                                    gold, client=None)
        check(good["schema_valid"], f"{ctx} synthetic deliverable failed schema: {good['schema_errors']}")
        check(good["final_score"] > 0.0, f"{ctx} synthetic deliverable scored 0")
        check(good["decision_match"] in ("match", "n/a"),
              f"{ctx} synthetic decision_match={good['decision_match']} (expected match/n/a)")

        empty = evaluate_deliverable("(validation)", {}, gold, client=None)
        check(not empty["schema_valid"], f"{ctx} empty deliverable unexpectedly schema-valid")

        if not any(tid in e for e in errors):
            n_ok += 1
            print(f"  ✅ {tid:32s} {family:32s} good={good['final_score']} empty={empty['final_score']}")

    print()
    if errors:
        print(f"❌ {len(errors)} problem(s):")
        for e in errors:
            print(f"   - {e}")
        return 1
    print(f"✅ All {n_ok} Phase 2.5 tasks valid (schema, gold, config, offline scoring).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
