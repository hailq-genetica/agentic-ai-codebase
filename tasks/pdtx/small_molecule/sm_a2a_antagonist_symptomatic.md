You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant. Evaluate a small-molecule candidate as a PD therapeutic.

### Therapeutic context
- **Disease context:** Parkinson's disease motor fluctuations — **symptomatic** treatment as an **adjunct to levodopa** in patients experiencing "OFF" episodes. This is a CNS indication.
- **Candidate:** "Compound A1", an istradefylline-like xanthine **adenosine A2A receptor antagonist**.
- **SMILES:** `CCn1c(=O)n(CC)c2c1n(C)c(/C=C/c1ccc(OC)c(OC)c1)n2`
- **Proposed target / MoA:** A2A receptors are enriched in striatal indirect-pathway (striatopallidal) neurons; A2A antagonism modulates basal-ganglia output to **reduce OFF time** without directly replacing dopamine. **Symptomatic, not disease-modifying.**
- **Provided profile:** good predicted CNS penetration; clean predicted ADMET (acceptable solubility/clearance, low hERG, AMES-negative); established A2A-antagonist class with a marketed precedent as a levodopa adjunct.

### Your job
Assess whether this candidate should progress. Reason explicitly through:
1. PD disease relevance and the **A2A / indirect-pathway** rationale for reducing OFF time.
2. Target / MoA plausibility (A2A antagonism as a non-dopaminergic symptomatic mechanism).
3. Binding/docking evidence (if you generate any).
4. Blood–brain barrier (BBB) penetration.
5. ADMET risks: solubility, clearance, CYP liability, hERG, AMES, DILI.
6. **The symptomatic-vs-disease-modifying distinction:** this reduces OFF time but does not slow neurodegeneration; set expectations and endpoints accordingly (OFF time, UPDRS), and consider dyskinesia and neuropsychiatric adjunct-class effects.
7. Patient population (levodopa-treated PD with motor fluctuations).
8. Patent / novelty risk (a well-precedented class — differentiation/novelty matters).
9. A Go / No-Go / Conditional Go decision.
10. The single most informative next experiment.

Critically distinguish a **well-precedented symptomatic adjunct** from a disease-modifying therapy — do not claim neuroprotection or disease modification.

### Available tools
Pharmacology tools (ADMET, physicochemical properties, docking/binding affinity, repurposing KG), databases (OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Use them to ground the A2A rationale and class precedent. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `small_molecule` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `mechanism_hypothesis`, `admet_assessment` (with `bbb`, `ames`, `herg`, `dili`, `cyp_risk`, `solubility`, `clearance`), `go_no_go` (one of `Go`/`No-Go`/`Conditional Go`), `main_risks`, `next_experiment`, `confidence` (0–1). Include `target_relevance`, `docking_interpretation`, `patent_risk`, `uncertainty`, and `evidence_used` where possible. Generate the file programmatically; do not hand-write it.
- **`reasoning.txt`** — ~150-word write-up of the analyses behind your decision, including how you handled uncertainty.
