You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Agentic evaluation of a LRRK2 inhibitor for LRRK2-associated PD
Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.

### Context
- **Goal:** evaluate a LRRK2 kinase inhibitor as a candidate for LRRK2-associated Parkinson's disease.
- **Proposed target / MoA:** ATP-competitive LRRK2 kinase inhibition.

### Provided data
```json
{
  "candidate_name": "PF-06447475 (LRRK2 tool inhibitor)",
  "smiles": "C1COCCN1C2=NC=NC3=C2C(=CN3)C4=CC=CC(=C4)C#N",
  "proposed_target": "LRRK2"
}
```

### Your job
1. Form a LRRK2 kinase mechanism hypothesis for LRRK2-associated PD.
2. Use tools (literature, knowledge graph, docking, ADMET, patent/novelty, clinical) and build an evidence_table that integrates the findings, including kinome selectivity and the peripheral (lung) safety signal.
3. Assess ADMET/CNS exposure and IP/novelty risk.
4. Give a calibrated go_no_go with decision_rationale and a target-engagement next experiment (e.g. pRab10).
5. Keep the workflow auditable: record which tools were used and why.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `agentic_smiles_episode` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `mechanism_hypothesis`, `evidence_table`, `risk_assessment`, `go_no_go`, `decision_rationale`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
