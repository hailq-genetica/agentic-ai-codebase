You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Agentic evaluation of a candidate with a weak target-disease link
Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.

### Context
- **Goal:** evaluate a small molecule proposed for Parkinson's disease.
- **Proposed rationale (to be checked):** the sponsor claims the target is relevant to PD, but the target-disease link is not established by PD genetics or disease biology — you must assess the strength of that link with the tools, not assume it.

### Provided data
```json
{
  "candidate_name": "Compound W (hypothetical)",
  "smiles": "O=C(Nc1ccccc1)c1ccc(cc1)N1CCOCC1",
  "proposed_target": "an enzyme with no established PD genetic or biological link"
}
```

### Your job
1. Use tools (literature, knowledge graph, clinical, genetics) to assess whether the target is actually linked to PD.
2. Build an evidence_table; explicitly note the absence or weakness of supporting evidence.
3. Do not be talked into progression by a confident-sounding but unsupported rationale.
4. Give a calibrated go_no_go with decision_rationale and the next experiment that would resolve the key uncertainty.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `agentic_smiles_episode` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `mechanism_hypothesis`, `evidence_table`, `risk_assessment`, `go_no_go`, `decision_rationale`, `next_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
