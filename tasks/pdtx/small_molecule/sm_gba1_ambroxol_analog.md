You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant. Evaluate a small-molecule candidate as a PD therapeutic.

### Therapeutic context
- **Disease context:** GBA1-associated Parkinson's disease (carriers of *GBA1* variants; reduced glucocerebrosidase / GCase activity → lysosomal dysfunction → α-synuclein accumulation).
- **Candidate:** "Ambroxol analog A", a putative GCase pharmacological chaperone.
- **SMILES:** `C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O`
- **Proposed target / MoA:** GCase (GBA1 gene product) pharmacological chaperone — stabilize misfolded GCase, restore lysosomal trafficking and enzyme activity.

### Your job
Assess whether this candidate should progress. Reason explicitly through:
1. PD disease relevance (GBA1 → GCase → lysosome → α-synuclein axis).
2. Target / mechanism-of-action plausibility for a chaperone.
3. Binding/docking evidence (if you generate any).
4. Blood–brain barrier (BBB) penetration — this is a CNS target.
5. ADMET risks: solubility, clearance, CYP liability, hERG, AMES, DILI, carcinogenicity.
6. Patent / novelty risk.
7. A Go / No-Go / Conditional Go decision.
8. The single most informative next experiment.

Critically distinguish **mechanistic plausibility** from **proven disease modification** — do not overclaim clinical efficacy from preclinical or mechanistic signals.

### Available tools
You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and `run_python_repl`. Use them to ground your assessment in evidence rather than memory where possible. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `small_molecule` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `mechanism_hypothesis`, `admet_assessment` (with `bbb`, `ames`, `herg`, `dili`, `cyp_risk`, `solubility`, `clearance`), `go_no_go` (one of `Go`/`No-Go`/`Conditional Go`), `main_risks`, `next_experiment`, `confidence` (0–1). Include `target_relevance`, `docking_interpretation`, `patent_risk`, `uncertainty`, and `evidence_used` where possible. Generate the file programmatically (e.g. `json.dump(..., open(f"{output_dir}/result.json","w"))`); do not hand-write it.
- **`reasoning.txt`** — ~150-word write-up of the analyses behind your decision, including how you handled uncertainty.
