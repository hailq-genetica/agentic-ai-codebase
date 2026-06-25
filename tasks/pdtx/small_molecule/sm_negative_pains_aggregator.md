You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant. Evaluate a small-molecule candidate as a PD therapeutic. **[Negative control task]**

### Therapeutic context
- **Disease context:** GBA1-associated Parkinson's disease; the team is excited about a screening hit against GCase.
- **Candidate:** "Compound P", a rhodanine-based arylidene screening hit proposed as a GCase modulator.
- **SMILES:** `O=C1NC(=S)SC1=Cc1ccc(O)cc1`
- **Provided evidence:**
  - Docking: **strong predicted binding to GCase** and a low micromolar readout in a single biochemical assay.
  - Structural class: a **rhodanine / arylidene** scaffold with a catechol-like phenol — a well-known **pan-assay interference (PAINS)** motif; the compound is also flagged as a likely **colloidal aggregator** at assay concentrations.
  - No orthogonal confirmation: no detergent-controlled assay, no dose–response with aggregation controls, no SPR/ITC, no cellular target engagement.

### Your job
Decide whether this candidate should progress, reasoning through disease relevance, the **reliability of the binding/activity signal**, and developability, then give a Go / No-Go / Conditional Go decision and the next experiment.

A correct assessment recognizes that the molecule is a **PAINS / aggregator**, so the strong docking score and single-assay activity are **likely artifacts**, not genuine target engagement — and that progressing on this evidence would be chasing a false positive. Do **not** let a strong docking score drive a Go. The right move is to treat the readout as unconfirmed and either kill the hit or require orthogonal, aggregation-controlled validation before any progression.

### Available tools
Pharmacology tools (ADMET, physicochemical properties, docking/binding affinity, repurposing KG), databases (OpenTargets, Monarch, ChEMBL/GtoPdb), literature/web search, and `run_python_repl`. You may check the scaffold for PAINS/aggregator alerts and sanity-check the signal. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `small_molecule` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `mechanism_hypothesis`, `admet_assessment`, `go_no_go`, `main_risks`, `next_experiment`, `confidence`). `main_risks` must flag the PAINS/aggregator artifact risk, and `next_experiment` should be an orthogonal, aggregation-controlled validation (or killing the hit). Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, explaining why the docking/assay signal is unreliable for this scaffold.
