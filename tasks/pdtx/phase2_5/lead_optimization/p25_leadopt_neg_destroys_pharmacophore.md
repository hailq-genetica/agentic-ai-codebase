You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Critique a proposed 'optimization' that removes the key pharmacophore
Critically evaluate the proposed optimization and provide a corrected strategy.

### Context
- **Scaffold:** a GCase chaperone lead whose key interaction is a hydrogen bond from a hydroxyl to a catalytic residue.
- **Proposed change (to critique):** "to improve metabolic stability and logP, remove the hydroxyl group and the basic nitrogen."

### Your job
1. Judge whether the proposed change is sound; identify that removing the pharmacophore hydroxyl/basic center will likely abolish target engagement.
2. Explain the potency-vs-property trade-off and why this 'optimization' is counterproductive.
3. Provide a corrected strategy that fixes the liabilities while preserving the pharmacophore.
4. List the properties to re-check and an experimental validation step.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `lead_optimization` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `optimization_goal`, `liability_to_address`, `proposed_modifications`, `properties_to_recheck`, `next_experiment`, `confidence`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
