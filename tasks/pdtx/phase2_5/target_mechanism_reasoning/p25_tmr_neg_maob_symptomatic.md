You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: MAO-B inhibition: symptomatic vs disease-modifying
Explain the role of MAO-B inhibition in Parkinson's disease and whether it modifies the disease course.

### Context
- **Disease context:** idiopathic Parkinson's disease, symptomatic management.
- **Proposed target / MoA:** small-molecule MAO-B inhibition to raise synaptic dopamine.

### Your job
1. Explain how MAO-B inhibition affects dopamine metabolism and symptoms.
2. State whether the mechanism is symptomatic or disease-modifying, with justification.
3. Identify the main uncertainties and what evidence would be needed for a disease-modification claim.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `target_mechanism_reasoning` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `mechanism_explanation`, `target_relevance`, `key_uncertainties`, `overclaiming_check`, `confidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
