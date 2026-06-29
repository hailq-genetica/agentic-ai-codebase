You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Claim check: exenatide as a disease-modifying PD therapy
Classify the following therapeutic claim using the available evidence.

### Context
- **Claim:** "Exenatide is a proven disease-modifying therapy for Parkinson's disease."
- **Background:** exenatide is a GLP-1 receptor agonist. An encouraging phase 2 trial (2017) suggested a possible effect, but the definitive phase 3 **Exenatide-PD3** (n=194, 96 weeks; Lancet 2024) found **no difference** vs placebo (MDS-UPDRS III worsened +5.7 with exenatide vs +4.5 placebo) and no benefit on cognition, non-motor, or imaging endpoints.

### Your job
1. Classify the claim (claim_classification).
2. Weigh the positive phase 2 against the definitive negative phase 3 and give the highest evidence level reached.
3. State the main uncertainty and why 'proven disease-modifying' is not justified.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_verification` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `claim_classification`, `evidence_summary`, `evidence_level`, `main_uncertainty`, `confidence`. `claim_classification` must be one of `Supported` / `Partially Supported` / `Unsupported` / `Contradicted` / `Insufficient Evidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
