You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Claim check: GBA1 variants are a major genetic risk factor for PD
Classify the following claim using the available evidence.

### Context
- **Claim:** "GBA1 variants are a major genetic risk factor for Parkinson's disease."
- **Background:** a large multicenter analysis (Sidransky et al., NEJM 2009) found GBA1 mutations markedly increase PD risk (odds ratio ~5), and GBA1 is the most common known genetic risk factor for PD. Penetrance is incomplete — most carriers do not develop PD.

### Your job
1. Classify the claim (claim_classification).
2. State the evidence level (human genetic association) and the effect size.
3. State the main uncertainty (incomplete penetrance; risk factor, not deterministic cause).

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_verification` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `claim_classification`, `evidence_summary`, `evidence_level`, `main_uncertainty`, `confidence`. `claim_classification` must be one of `Supported` / `Partially Supported` / `Unsupported` / `Contradicted` / `Insufficient Evidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
