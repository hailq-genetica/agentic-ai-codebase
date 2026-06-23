You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant. Evaluate a small-molecule candidate as a PD therapeutic. **[Negative control task]**

### Therapeutic context
- **Disease context:** GBA1-associated Parkinson's disease (a CNS indication — the drug must reach the brain).
- **Candidate:** "Compound X", proposed as a GCase modulator.
- **SMILES:** `O=C(O)c1ccc(cc1)C(=O)Nc1ccc(cc1)S(=O)(=O)N1CCN(CC1)c1ncccn1`
- **Available evidence (provided):**
  - Docking: strong predicted binding to GCase (favorable docking score).
  - ADMET (provided/predicted): **poor predicted BBB penetration**; **strong hERG inhibition liability**; high topological polar surface area; P-gp efflux substrate likely.

### Your job
Decide whether this candidate should progress, reasoning through disease relevance, target plausibility, the docking signal, **BBB penetration**, and **safety liabilities (hERG and others)**, then give a Go / No-Go / Conditional Go decision and the next experiment.

A correct assessment recognizes that strong target binding does **not** rescue a molecule that cannot reach the CNS and carries a serious cardiac (hERG) liability. Do not let a good docking score drive an unjustified Go. Distinguish mechanistic appeal from developability.

### Available tools
Pharmacology tools (ADMET, physicochemical properties, docking/binding affinity, repurposing KG), databases (OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. You may recompute or sanity-check the provided ADMET signals. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `small_molecule` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (same required keys as the other small-molecule tasks: `mechanism_hypothesis`, `admet_assessment`, `go_no_go`, `main_risks`, `next_experiment`, `confidence`). The `admet_assessment.bbb` and `admet_assessment.herg` fields must reflect the liabilities. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, explicitly weighing the BBB and hERG liabilities against the docking signal.
