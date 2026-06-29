You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Optimize a CNS lead with high CYP3A4 metabolism and DDI risk
Propose a rational lead-optimization strategy for this scaffold.

### Context
- **Scaffold:** a CNS-penetrant PD lead with good target potency.
- **Profile:** rapid CYP3A4-mediated metabolism (high clearance, short half-life) and CYP3A4 inhibition (drug-drug-interaction risk).

### Your job
1. State the optimization goal and the liabilities to address.
2. Propose chemistry-aware modifications (e.g. block the metabolic soft spot, reduce CYP3A4 affinity), each with rationale, expected benefit, and risk.
3. Preserve target potency and CNS penetration.
4. List the properties to re-check (clearance, CYP panel, permeability) and the experimental validation step (e.g. microsomal stability).

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `lead_optimization` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `optimization_goal`, `liability_to_address`, `proposed_modifications`, `properties_to_recheck`, `next_experiment`, `confidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
