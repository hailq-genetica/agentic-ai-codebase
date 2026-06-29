You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Oversized, polar candidate failing CNS druglikeness for a brain target
Evaluate whether this small-molecule candidate should progress to experimental validation.

### Context
- **Disease context:** Parkinson's disease, **CNS target** (brain exposure required).
- **Proposed target / MoA:** PD-relevant CNS target.

### Provided data
```json
{
  "candidate_name": "Hypothetical compound M (illustrative)",
  "smiles": "O=C(NCCNC(=O)c1ccc(cc1)C(=O)O)c1ccc(cc1)S(=O)(=O)N1CCN(CC1)c1ccccc1",
  "descriptors": {
    "approx_MW": "~565",
    "approx_TPSA": "~140 A^2",
    "HBD": 3,
    "HBA": 9,
    "approx_clogP": "low"
  },
  "known_or_hypothetical": "hypothetical"
}
```

### Your job
1. Assess CNS drug-likeness against standard CNS property guidelines (e.g. MW, TPSA, HBD).
2. Reason about likely BBB penetration for a brain target given these descriptors.
3. Give a calibrated go_no_go; do not progress a CNS-targeted molecule unlikely to reach the brain.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
