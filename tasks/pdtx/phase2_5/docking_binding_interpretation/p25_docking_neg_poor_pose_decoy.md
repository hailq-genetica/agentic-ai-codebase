You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: High docking score with an implausible pose (likely artifact)
Interpret the docking/binding evidence for this compound and recommend a decision.

### Context
- **Target:** GCase (GBA1 product).

### Provided data
```json
{
  "compound": "Compound F",
  "docking_score_kcal_mol": -10.5,
  "reference_ligand_score_kcal_mol": -8.0,
  "binding_site": "scored outside the catalytic pocket; key catalytic contacts NOT made",
  "pose_quality": "poor / inconsistent across replicas; strained conformation",
  "chemotype_note": "matches a known promiscuous-binder / frequent-hitter scaffold",
  "admet_summary": "acceptable"
}
```

### Your job
1. Judge whether the high score is trustworthy given the pose and chemotype.
2. Explain docking false positives (artifacts, promiscuity) vs a real binding hypothesis.
3. Recommend a go_no_go and, if any, an orthogonal validation step.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `docking_binding_interpretation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `binding_interpretation`, `reference_context`, `admet_integration`, `go_no_go`, `validation_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
