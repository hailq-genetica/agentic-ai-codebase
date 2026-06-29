You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Optimize a GCase chaperone analog with solubility and hERG liabilities
Propose a rational lead-optimization strategy for this scaffold.

### Context
- **Scaffold:** GCase pharmacological chaperone analog (CNS target).
- **Profile:** good predicted target binding, but poor solubility and high hERG risk.

### Your job
1. State the optimization goal and the liabilities to address.
2. Propose chemistry-aware modifications, each with an explicit rationale, expected benefit, and risk.
3. Preserve the pharmacophore and CNS penetration while fixing the liabilities.
4. List the properties to re-check and the experimental validation step.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `lead_optimization` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `optimization_goal`, `liability_to_address`, `proposed_modifications`, `properties_to_recheck`, `next_experiment`, `confidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
