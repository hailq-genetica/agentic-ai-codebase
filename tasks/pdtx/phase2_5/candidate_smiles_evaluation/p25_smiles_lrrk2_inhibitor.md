You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Evaluate a LRRK2 kinase inhibitor candidate
Evaluate whether this small-molecule LRRK2 kinase inhibitor should progress to experimental validation.

### Context
- **Disease context:** LRRK2-associated Parkinson's disease (e.g. G2019S carriers).
- **Proposed target / MoA:** ATP-competitive LRRK2 kinase inhibition.

### Provided data
```json
{
  "candidate_name": "PF-06447475 (LRRK2 tool inhibitor)",
  "smiles": "C1COCCN1C2=NC=NC3=C2C(=CN3)C4=CC=CC(=C4)C#N",
  "known_or_hypothetical": "known"
}
```

### Your job
1. Assess the kinase-inhibition MoA and the importance of kinome selectivity.
2. Assess CNS drug-likeness / BBB penetration and the LRRK2 peripheral (lung) on-target safety concern.
3. Assess ADMET/safety liabilities and developability (this is a tool compound).
4. Give a calibrated go_no_go and a target-engagement next experiment (e.g. pRab10 / pSer935).

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
