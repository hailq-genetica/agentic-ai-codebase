You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Evaluate an alpha-synuclein aggregation-modulator candidate
Evaluate whether this small-molecule candidate should progress to experimental validation.

### Context
- **Disease context:** Parkinson's disease with alpha-synuclein aggregation.
- **Proposed target / MoA:** small molecule proposed to bind aggregated alpha-synuclein and modulate fibril formation.

### Provided data
```json
{
  "candidate_name": "Hypothetical compound S (benzothiazole aggregation binder)",
  "smiles": "Nc1ccc(cc1)-c1nc2ccccc2s1",
  "known_or_hypothetical": "hypothetical"
}
```

### Your job
1. Assess the aggregation-modulation MoA and the central challenge of defining/engaging the toxic species.
2. Assess CNS drug-likeness/BBB and selectivity (aggregation binders can be non-specific / amyloid-pan-binders).
3. Give a calibrated go_no_go and a target-engagement next experiment (e.g. cellular aggregation/seeding assay).

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
