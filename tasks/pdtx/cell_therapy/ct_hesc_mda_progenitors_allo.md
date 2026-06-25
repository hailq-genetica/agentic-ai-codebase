You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of an **allogeneic** PD cell-therapy product.

### Therapeutic context
A protocol generates **allogeneic human embryonic stem cell (hESC)-derived midbrain dopaminergic (mDA) progenitors** from a single GMP master cell bank, intended for **bilateral putaminal transplantation in moderate Parkinson's disease**. Release-relevant profile:
- Cells cryopreserved at the **progenitor** stage (post-floor-plate patterning, pre-terminal-maturation).
- Midbrain floor-plate lineage markers (FOXA2, LMX1A, OTX2, EN1) co-expressed in the majority of cells; dopaminergic commitment markers (TH, NURR1/NR4A2) emerging on maturation.
- Residual pluripotency markers (OCT4, LIN28, NANOG) below assay detection by qPCR/flow.
- One **allogeneic, HLA-mismatched** master line for all patients; the protocol specifies **~12 months of transient systemic immunosuppression** post-graft.
- In vivo efficacy (motor recovery) and survival shown in 6-OHDA rodent and MPTP primate models.

### Your job
Assess whether this allogeneic product is ready for **clinical translation (first-in-human)** and give a Go / No-Go / Conditional Go decision. Reason explicitly through:
1. Dopaminergic / midbrain (A9) lineage identity and the rationale for grafting at the **progenitor** vs terminally differentiated stage.
2. Purity / proportion of on-target cells and off-target contamination.
3. Residual pluripotency and tumorigenicity risk.
4. **Allogeneic immune compatibility:** HLA mismatch, graft rejection, the transient-immunosuppression strategy and its adequacy/duration.
5. Functional maturity and expected in vivo dopaminergic maturation/innervation.
6. Graft survival, integration, and the imaging/clinical endpoints (e.g. DAT/F-DOPA PET) that would confirm engraftment.
7. Batch reproducibility / manufacturing from a single master bank (a scale advantage of the allogeneic approach).
8. Clinical release criteria and potency assays.

Distinguish strong preclinical characterization from a de-risked clinical product, and be explicit about what the **allogeneic / HLA-mismatch** setting adds to the risk profile relative to an autologous product.

### Available tools
Databases (OpenTargets, Monarch), literature/web search, and `run_python_repl`. Use them to ground identity markers, HLA/immunosuppression precedents for CNS grafts, tumorigenicity testing standards, and release-criteria precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `cell_product`, `identity_assessment` (with `dopaminergic_markers`, `midbrain_markers`, `pluripotency_markers`), `safety_assessment`, `release_criteria`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). `safety_assessment` must address both tumorigenicity and the allogeneic immune-rejection risk. Include `functional_assessment`, `manufacturing_risks`, `next_validation_step`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
