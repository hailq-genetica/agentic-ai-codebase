You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: ADMET review: time-dependent CYP inhibition / reactive metabolite
Interpret the predicted ADMET profile and decide whether the candidate should progress for chronic PD use.

### Context
- **Therapeutic context:** chronic, long-term therapy for Parkinson's disease.

### Provided data
```json
{
  "candidate": "Compound T",
  "predicted_properties": {
    "bbb": "good",
    "ames": "negative",
    "herg": "low risk",
    "cyp3a4": "time-dependent (mechanism-based) inhibition",
    "structural_alert": "aniline -> predicted reactive metabolite",
    "solubility": "moderate"
  }
}
```

### Your job
1. Explain the risk from mechanism-based (time-dependent) CYP inhibition and a predicted reactive metabolite (idiosyncratic toxicity, unpredictable DDIs, covalent protein binding).
2. Weigh this against the otherwise good CNS/safety profile for a chronic therapy.
3. Give a calibrated go_no_go.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `admet_cns_assessment` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `bbb_assessment`, `toxicology_assessment`, `pk_assessment`, `go_no_go`, `main_risks`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
