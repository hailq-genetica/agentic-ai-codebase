You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting as a therapeutic-discovery assistant. Evaluate a small-molecule candidate as a PD therapeutic. **[Negative control task]**

### Therapeutic context
- **Disease context:** Parkinson's disease — a **chronic** indication requiring **years of daily dosing** in an older population.
- **Candidate:** "Compound G", a brain-penetrant LRRK2 modulator hit.
- **SMILES:** `Nc1ccc(cc1)-c1ccc(cc1)[N+](=O)[O-]`
- **Provided evidence:**
  - Good predicted CNS penetration and reasonable potency at the intended target.
  - **Structural alerts:** the molecule contains an **aromatic nitro group** and an **aromatic (aniline) amine** — both classic mutagenicity/genotoxicity alerts that can form reactive nitrenium/nitroso intermediates.
  - **ADMET (predicted/measured):** **AMES-positive (mutagenic)**; positive in an in silico/in vitro genotoxicity flag; possible reactive-metabolite formation.

### Your job
Decide whether this candidate should progress, reasoning through disease relevance, target plausibility, CNS penetration, and **genotoxicity/mutagenicity safety**, then give a Go / No-Go / Conditional Go decision and the next experiment.

A correct assessment recognizes that an **AMES-positive, structurally-alerting genotoxic molecule is not developable for a chronic, lifelong CNS indication** regardless of good potency and brain penetration — mutagenicity is a fundamental, typically disqualifying liability that scaffold/series redesign (removing the nitro/aniline alerts) must address before any progression. Do **not** let good CNS penetration or target potency drive a Go past a genotoxicity signal.

### Available tools
Pharmacology tools (ADMET, physicochemical properties, structural-alert / toxicity prediction, docking), databases (OpenTargets, Monarch, ChEMBL/GtoPdb, FDA safety), literature/web search, and `run_python_repl`. You may check the structure for genotoxicity alerts and recompute ADMET. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `small_molecule` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `mechanism_hypothesis`, `admet_assessment`, `go_no_go`, `main_risks`, `next_experiment`, `confidence`). The `admet_assessment.ames` field must reflect the mutagenicity, and `main_risks` must flag genotoxicity as disqualifying for chronic dosing. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, explaining why a genotoxicity signal is disqualifying for a chronic CNS indication and what redesign is needed.
