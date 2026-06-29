You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: ADMET review: very high plasma protein binding and low free fraction
Interpret the predicted ADMET profile and decide whether the candidate should progress.

### Context
- **Therapeutic context:** Parkinson's disease, CNS target; moderate target potency (mid-nanomolar).

### Provided data
```json
{
  "candidate": "Compound B2",
  "predicted_properties": {
    "plasma_protein_binding": "99.9% (free fraction ~0.1%)",
    "bbb": "moderate",
    "potency": "mid-nanomolar",
    "ames": "negative",
    "herg": "low risk",
    "solubility": "low"
  }
}
```

### Your job
1. Explain why the unbound (free) concentration — not total — drives target engagement, and the impact of 99.9% PPB.
2. Combine the very low free fraction with mid-nanomolar potency and low solubility to judge whether a sufficient free brain concentration is achievable.
3. Give a calibrated go_no_go.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `admet_cns_assessment` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `bbb_assessment`, `toxicology_assessment`, `pk_assessment`, `go_no_go`, `main_risks`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
