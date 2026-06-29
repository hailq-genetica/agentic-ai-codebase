You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Mechanism error: 'restoring dopamine modifies the disease'
Evaluate the following mechanistic argument and identify what is wrong with it.

### Context
- **Argument:** "Parkinson's motor symptoms come from dopamine deficiency, so a small molecule that restores dopamine (e.g. enhancing synthesis or replacing it) is disease-modifying."

### Your job
1. Explain the difference between correcting the dopaminergic deficit (symptomatic) and altering the underlying neurodegeneration (disease-modifying).
2. Note that dopaminergic therapies improve symptoms but do not halt neuronal loss.
3. State what a disease-modifying mechanism would have to do instead.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `target_mechanism_reasoning` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `mechanism_explanation`, `target_relevance`, `key_uncertainties`, `overclaiming_check`, `confidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
