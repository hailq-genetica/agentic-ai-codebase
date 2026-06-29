You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant.

## Task: Interpret a fragment hit with a modest docking score
Interpret the docking/binding evidence for this fragment and recommend a decision.

### Context
- **Target:** GCase (GBA1 product); fragment-based screening context.

### Provided data
```json
{
  "compound": "Fragment Fr-1 (MW ~190)",
  "docking_score_kcal_mol": -6.2,
  "reference_drug_like_ligand_kcal_mol": -8.0,
  "ligand_efficiency": "high (favorable per-heavy-atom)",
  "pose_quality": "makes a key catalytic-residue contact",
  "admet_summary": "fragment-like, very soluble"
}
```

### Your job
1. Explain why a fragment's lower absolute docking score is expected and why ligand efficiency / a key interaction matter more here.
2. State what docking does not establish (real binding affinity, target engagement).
3. Recommend a go_no_go for a fragment-to-lead campaign and the biophysical confirmation needed (e.g. SPR/ITC/crystallography).

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Ground your assessment in evidence rather than memory where possible, and cite what you used.

### Deliverable (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path. Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `docking_binding_interpretation` definition in `tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: `binding_interpretation`, `reference_context`, `admet_integration`, `go_no_go`, `validation_experiment`, `confidence`. `go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.
  Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you handled uncertainty.
