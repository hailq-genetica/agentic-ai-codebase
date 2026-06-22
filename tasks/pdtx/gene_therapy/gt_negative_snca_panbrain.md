You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD. **[Negative control task]**

### Therapeutic context
A team proposes **non-specific, constitutive knockdown of *SNCA* (α-synuclein) across all brain regions** — e.g. a broadly biodistributed AAV delivering an shRNA against *SNCA* with a ubiquitous promoter, no regional restriction and no dose titration — for idiopathic Parkinson's disease.

### Your job
Evaluate the safety and feasibility of this strategy and give a Go / No-Go / Conditional Go decision. Reason through:
1. Whether α-synuclein has essential physiological functions (synaptic/vesicular) such that broad, constitutive suppression is harmful.
2. Off-target / pan-neuronal consequences of expressing the knockdown construct everywhere.
3. Lack of reversibility and dose control with constitutive shRNA.
4. Known toxicity of AAV-delivered shRNA at high expression (saturation of endogenous RNAi machinery).
5. Absence of patient stratification.
6. What a safer redesign would look like (regional targeting, regulatable/tunable expression, allele- or aggregate-selective approaches).

A correct assessment identifies the major safety problems of indiscriminate pan-brain *SNCA* suppression and does **not** issue an unqualified Go. Do not assume "lowering α-synuclein" is automatically safe or beneficial.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS), literature/web search, and `run_python_repl`. Use them to check α-synuclein physiology and shRNA gene-therapy safety precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go`, `confidence`). `key_risks` must enumerate the major safety problems. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision and naming the redesign that would be needed.
