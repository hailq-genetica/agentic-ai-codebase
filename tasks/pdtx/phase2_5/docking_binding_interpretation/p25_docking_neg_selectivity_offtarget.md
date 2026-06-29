You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Docking that is strong at the target but also at an anti-target
Interpret the docking/binding evidence for this compound and recommend a decision.

### Context
- **Target:** a PD-relevant kinase.

### Provided data
```json
{
  "compound": "Compound K",
  "target_docking_kcal_mol": -9.3,
  "reference_ligand_kcal_mol": -8.1,
  "anti_target_docking": {
    "hERG_model": "favorable",
    "off_target_kinase": "comparable to on-target"
  },
  "pose_quality": "good at the target",
  "admet_summary": "acceptable"
}
```

### Your job
1. State what the strong on-target score establishes and why the anti-target/off-target docking matters.
2. Integrate selectivity (hERG and off-target kinase) into the interpretation.
3. Recommend a go_no_go and the selectivity experiment needed.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `docking_binding_interpretation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `binding_interpretation`, `reference_context`, `admet_integration`, `go_no_go`, `validation_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
