You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: ADMET review of a brain-penetrant candidate with a clean profile
Interpret the predicted ADMET profile and decide whether the candidate should progress.

### Context
- **Therapeutic context:** disease-modifying therapy for Parkinson's disease (CNS target, chronic dosing).

### Provided data
```json
{
  "candidate": "Compound C",
  "predicted_properties": {
    "bbb": "high",
    "ames": "negative",
    "herg": "low risk",
    "cyp3a4_inhibitor": "no",
    "solubility": "good",
    "clearance": "moderate"
  }
}
```

### Your job
1. Interpret the CNS exposure and core ADMET/safety profile.
2. State residual risks and that in silico ADMET predictions require experimental confirmation.
3. Give a calibrated go_no_go that follows from the profile, without overclaiming efficacy.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `admet_cns_assessment` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `bbb_assessment`, `toxicology_assessment`, `pk_assessment`, `go_no_go`, `main_risks`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
