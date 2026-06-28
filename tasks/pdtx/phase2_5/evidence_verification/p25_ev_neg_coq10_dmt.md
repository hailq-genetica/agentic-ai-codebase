You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Claim check: high-dose coenzyme Q10 slows PD progression
Classify the following therapeutic claim using the available evidence.

### Context
- **Claim:** "High-dose coenzyme Q10 slows Parkinson's disease progression."
- **Background:** CoQ10 targets mitochondrial bioenergetics/oxidative stress. The phase 3 **QE3** trial (n=267, 1200 and 2400 mg/d; JAMA Neurology 2014) was terminated for **futility** with no evidence of benefit.

### Your job
1. Classify the claim (claim_classification).
2. Distinguish the mitochondrial/antioxidant rationale from the clinical outcome.
3. State the evidence level and the implication of the futility termination.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_verification` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `claim_classification`, `evidence_summary`, `evidence_level`, `main_uncertainty`, `confidence`. `claim_classification` must be one of `Supported` / `Partially Supported` / `Unsupported` / `Contradicted` / `Insufficient Evidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
