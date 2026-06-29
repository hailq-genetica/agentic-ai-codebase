You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Evaluate a 5-HT2A inverse agonist for PD psychosis
Evaluate this small molecule as a Parkinson's disease therapeutic and frame its indication correctly.

### Context
- **Disease context:** Parkinson's disease psychosis (hallucinations/delusions) — a non-motor complication.
- **Proposed target / MoA:** selective serotonin 5-HT2A inverse agonist/antagonist (non-dopaminergic, so it does not worsen motor symptoms).

### Provided data
```json
{
  "candidate_name": "Pimavanserin (5-HT2A inverse agonist, approved for PD psychosis)",
  "smiles": "CC(C)COC1=CC=C(C=C1)CNC(=O)N(CC2=CC=C(C=C2)F)C3CCN(CC3)C",
  "known_or_hypothetical": "known"
}
```

### Your job
1. Assess the 5-HT2A MoA and why a non-dopaminergic agent is advantageous for PD psychosis.
2. Assess CNS exposure and ADMET, including the QT-prolongation caution.
3. Frame the indication: symptomatic non-motor benefit, not disease modification.
4. Give a calibrated go_no_go for the PD-psychosis indication and a next step.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
