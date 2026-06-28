# PD-TxBench Phase 2.5 — task taxonomy (scope freeze)

Phase 2.5 is a **small-molecule-only** benchmark for Parkinson's disease (PD)
therapeutic discovery. It splits small-molecule evaluation out of PD-TxBench
Phase 2 so compound-level reasoning can be assessed more deeply (target biology,
chemical structure, BBB/CNS exposure, ADMET, safety, evidence strength, patent
risk, translatability, Go/No-Go). The narrative motivation is in
`pd_txbench_phase2.5.md`; this file is the implementation contract.

Phase 2.5 **reuses the Phase 2 runner and judge** (`run_pdtx.py`, `src/pdtx_eval`).
Every task is a small molecule, so each gold keeps `category: small_molecule` and
adds two Phase 2.5 fields — `phase: "phase2_5"` and `task_family` — which route
deliverable validation to the per-family Phase 2.5 output schema and add a
per-task-family breakdown to the leaderboard.

## Files

| Artifact | Path |
|---|---|
| Output schema (per task_family) | `tasks/pdtx/schemas/output_schema_phase2_5.json` |
| Rubric catalog (per task_family) | `tasks/pdtx/schemas/rubric_phase2_5.json` |
| Task prompts | `tasks/pdtx/phase2_5/<family>/<id>.md` |
| Gold + rubric | `tasks/pdtx/phase2_5/gold/<id>.json` |
| Configs | `config/pdtx/phase2_5/<family>/<id>.yaml` |
| Dataset manifest | `tasks/pdtx/phase2_5/manifest.jsonl` |
| Seed-dataset generator | `scripts/build_phase2_5_seed.py` |
| Validator (offline, no API) | `scripts/validate_phase2_5.py` |

The generator is the single build step: edit the `TASKS` spec, run it, and the
`.md` / gold / config / manifest are regenerated. Rubric criteria come from the
catalog and deliverable required-keys from the output schema, so prompts, golds,
and validation stay in sync.

## Task families

| # | task_family | Decision field | Rubric id |
|---|---|---|---|
| 1 | `target_mechanism_reasoning` | none (N/A) | `pdtx25_target_mechanism_v1` |
| 2 | `evidence_verification` | `claim_classification` | `pdtx25_evidence_verification_v1` |
| 3 | `candidate_smiles_evaluation` | `go_no_go` | `pdtx25_candidate_smiles_v1` |
| 4 | `admet_cns_assessment` | `go_no_go` | `pdtx25_admet_cns_v1` |
| 5 | `docking_binding_interpretation` | `go_no_go` | `pdtx25_docking_binding_v1` |
| 6 | `lead_optimization` | none (N/A) | `pdtx25_lead_optimization_v1` |
| 7 | `repurposing_translatability` | `go_no_go` | `pdtx25_repurposing_v1` |
| 8 | `agentic_smiles_episode` | `go_no_go` | `pdtx25_agentic_episode_v1` |

### Decision vocabularies

- `go_no_go` ∈ {`Go`, `No-Go`, `Conditional Go`}
- `claim_classification` ∈ {`Supported`, `Partially Supported`, `Unsupported`, `Contradicted`, `Insufficient Evidence`}
- Families with no decision set gold `preferred_decision: "N/A"`; the decision
  criterion is not scored for them.

### Deliverable required keys (by family)

Defined in `output_schema_phase2_5.json`. Validation enforces the structural
contract only (required keys present, decision enum valid, `confidence` ∈ [0,1]);
descriptive fields accept any JSON shape.

| task_family | required keys |
|---|---|
| target_mechanism_reasoning | mechanism_explanation, target_relevance, key_uncertainties, overclaiming_check, confidence |
| evidence_verification | claim_classification, evidence_summary, evidence_level, main_uncertainty, confidence |
| candidate_smiles_evaluation | candidate_summary, mechanism_hypothesis, cns_drug_likeness, admet_risks, go_no_go, main_reasons, next_experiment, confidence |
| admet_cns_assessment | bbb_assessment, toxicology_assessment, pk_assessment, go_no_go, main_risks, confidence |
| docking_binding_interpretation | binding_interpretation, reference_context, admet_integration, go_no_go, validation_experiment, confidence |
| lead_optimization | optimization_goal, liability_to_address, proposed_modifications, properties_to_recheck, next_experiment, confidence |
| repurposing_translatability | repurposing_rationale, human_safety_dosing, cns_exposure, clinical_evidence_interpretation, go_no_go, confidence |
| agentic_smiles_episode | mechanism_hypothesis, evidence_table, risk_assessment, go_no_go, decision_rationale, next_experiment, confidence |

## Negative controls

Negative controls are the design centrepiece: they test whether the model says
**No-Go / Unsupported / Contradicted** instead of being talked into an unsafe or
overclaimed answer. The current slice is **~45% negative controls** spanning every
decision-making family — strong docking + poor BBB, hERG/AMES/DILI/CYP liabilities,
genotoxicity structural alerts, docking artifacts (implausible pose / frequent
hitter), association≠causation, target-engagement≠clinical-benefit, symptomatic≠
disease-modifying, no-CNS-exposure repurposing, and weak target–disease links. The
full set follows the matrix in `pd_txbench_phase2.5.md` §18.

## Seed slice (this pass)

**33 tasks** covering all 8 families (15 negative controls ≈45%; 11 source-verified).
This is a runnable, balanced slice that proves the pipeline end-to-end; it is **not**
yet the full §14.1 MVP (≈300 static + 15 agentic). Scale up by adding entries to the
generator's `TASKS` spec — no code changes needed.

### Authoring & verification workflow

Tasks are **hand-authored** in the `TASKS` spec in `scripts/build_phase2_5_seed.py`
(one dict per task) and **verified before inclusion**:

- **Clinical-fact tasks** (mostly `evidence_verification`) cite primary sources in a
  `sources` list and are marked `review_status: "reviewed"`; their trial outcomes
  were checked against the cited publications. Examples in this slice: Exenatide-PD3
  (Lancet 2024, negative), STEADY-PD III (Ann Intern Med 2020, negative), SURE-PD3
  (JAMA 2021, futility), QE3 CoQ10 (JAMA Neurol 2014, futility), FAIRPARK-II
  deferiprone (NEJM 2022, worsened), GBA1 risk (Sidransky NEJM 2009, Supported anchor).
- **Real-compound tasks** embed canonical SMILES pulled from PubChem (e.g.
  istradefylline, safinamide, the LRRK2 tool inhibitor PF-06447475).
- `sources`/`review_status` are emitted into each gold's `metadata` and the manifest.

To add tasks: append dicts to `TASKS`, run the build script, then the validator. The
validator prints a dataset summary (per-family counts, negative-control coverage,
decision distribution, verified count) and warns when a decision family lacks a
negative control or decision diversity.

Build, validate, and run:

```bash
# Regenerate tasks / gold / config / manifest from the TASKS spec:
python scripts/build_phase2_5_seed.py

# Offline end-to-end validation of the seed dataset (no API key):
python scripts/validate_phase2_5.py

# Run + judge-score one Phase 2.5 task (needs runtime + API key):
python run_pdtx.py --config config/pdtx/phase2_5/candidate_smiles_evaluation/p25_smiles_gba1_chaperone.yaml

# Run + score every Phase 2.5 task:
python run_pdtx.py --config config/pdtx/phase2_5

# Score an existing deliverable offline (no agent, no API key):
python run_pdtx.py --eval-only --offline \
    --deliverable <result.json> --gold tasks/pdtx/phase2_5/gold/<id>.json
```

## Roadmap (not yet built)

- Scale to the §14.1 MVP counts (target-mechanism 40, evidence 40, SMILES 50,
  ADMET 40, docking 30, lead-opt 30, repurposing 30, negative controls 40,
  agentic 15).
- Frozen controlled tool sandbox (§13): `literature_search`,
  `pd_knowledge_graph_query`, `docking_reader`, `admet_reader`,
  `patent_signal_reader`, `clinical_trial_lookup`, `experiment_planner` — for
  reproducible scoring without live web access.
- Dataset splits (§15): dev / public-test / hidden-input / hidden-gold /
  agentic-episodes JSONL from the manifest.
