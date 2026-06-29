You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Candidate with a genotoxicity structural alert
Evaluate whether this small-molecule candidate should progress to experimental validation.

### Context
- **Disease context:** Parkinson's disease, chronic (long-term) therapy.
- **Proposed target / MoA:** the proposed target is relevant to PD, but assess the molecule on its own merits.

### Provided data
```json
{
  "candidate_name": "Hypothetical compound N (illustrative)",
  "smiles": "O=[N+]([O-])c1ccc(cc1)CCNC(=O)C2CCNCC2",
  "note": "Contains an aromatic nitro group \u2014 a recognized structural alert.",
  "known_or_hypothetical": "hypothetical"
}
```

### Your job
1. Identify the structural alert in the molecule and the toxicology it predicts.
2. Reason about genotoxicity/mutagenicity risk for a chronic-use therapy.
3. Give a calibrated go_no_go; do not let target relevance override a genotoxicity liability.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `candidate_smiles_evaluation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `candidate_summary`, `mechanism_hypothesis`, `cns_drug_likeness`, `admet_risks`, `go_no_go`, `main_reasons`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
