You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of a PD cell-therapy product.

### Therapeutic context
A protocol generates **iPSC-derived midbrain dopaminergic (mDA) neurons** intended for **transplantation in Parkinson's disease**. Assume a standard differentiation protocol with the following release-relevant profile:
- Dopaminergic identity markers (TH, NURR1/NR4A2, PITX3) expressed in the majority of cells.
- Midbrain floor-plate lineage markers (FOXA2, LMX1A) co-expressed.
- Residual pluripotency markers (OCT4, SOX2, NANOG) below assay detection in QC.
- Functional dopamine release demonstrated in vitro.

### Your job
Assess whether the product is ready for **preclinical translation** and give a Go / No-Go / Conditional Go decision. Reason through:
1. Dopaminergic neuron identity and midbrain (A9) lineage.
2. Purity / proportion of on-target cells.
3. Residual pluripotency and tumorigenicity risk.
4. Functional maturity and dopamine release.
5. Graft survival and integration considerations.
6. Batch reproducibility / manufacturing.
7. Potency assays.
8. Clinical release criteria.

Distinguish encouraging characterization from a fully de-risked product; state what additional evidence (e.g. in vivo engraftment/tumor studies) is required before clinical translation.

### Available tools
Databases (OpenTargets, Monarch, literature/web search) and `run_python_repl`. Use them to ground identity markers, tumorigenicity testing standards, and release-criteria precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `cell_product`, `identity_assessment` (with `dopaminergic_markers`, `midbrain_markers`, `pluripotency_markers`), `safety_assessment`, `release_criteria`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). Include `functional_assessment`, `manufacturing_risks`, `next_validation_step`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
