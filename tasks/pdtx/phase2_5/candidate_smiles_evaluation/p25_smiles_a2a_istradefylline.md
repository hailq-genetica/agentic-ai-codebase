You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Evaluate an adenosine A2A antagonist for Parkinson's disease
Evaluate this small molecule as a Parkinson's disease therapeutic and frame its therapeutic role correctly.

### Context
- **Disease context:** Parkinson's disease with motor fluctuations (OFF episodes).
- **Proposed target / MoA:** adenosine A2A receptor antagonism (non-dopaminergic modulation of basal-ganglia output).

### Provided data
```json
{
  "candidate_name": "Istradefylline (A2A antagonist, approved adjunct)",
  "smiles": "CCN1C2=C(C(=O)N(C1=O)CC)N(C(=N2)/C=C/C3=CC(=C(C=C3)OC)OC)C",
  "known_or_hypothetical": "known"
}
```

### Your job
1. Assess the A2A-antagonist MoA and how it reduces OFF time as an adjunct to levodopa.
2. Assess CNS exposure and ADMET (note CYP3A4 metabolism and photosensitivity considerations).
3. Critically frame the indication: symptomatic adjunct vs disease-modifying.
4. Give a calibrated go_no_go for the symptomatic indication and a next step.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
