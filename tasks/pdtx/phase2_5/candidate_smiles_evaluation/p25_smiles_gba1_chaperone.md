You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Evaluate a GCase chaperone candidate for GBA1-associated PD
Evaluate whether this small-molecule candidate should progress to experimental validation.

### Context
- **Disease context:** GBA1-associated Parkinson's disease.
- **Proposed target / MoA:** GCase pharmacological chaperone.

### Provided data
```json
{
  "candidate_name": "Ambroxol analog A",
  "smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O",
  "known_or_hypothetical": "analog"
}
```

### Your job
1. Assess PD relevance (GBA1 -> GCase -> lysosome -> alpha-synuclein) and MoA plausibility.
2. Assess CNS drug-likeness and BBB penetration likelihood (this is a CNS target).
3. Assess ADMET and safety liabilities (solubility, clearance, CYP, hERG, AMES, DILI).
4. Give a calibrated go_no_go decision and the single most informative next experiment.
5. Distinguish mechanistic plausibility from proven disease modification.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
