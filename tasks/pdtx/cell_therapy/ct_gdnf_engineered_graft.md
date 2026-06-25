You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of an **engineered (gene-modified) cell** PD product.

### Therapeutic context
A protocol generates **iPSC-derived midbrain dopaminergic (mDA) progenitors engineered to secrete GDNF** (glial cell line-derived neurotrophic factor) as a combined "cells + trophic support" graft for **putaminal transplantation in Parkinson's disease**. The rationale is that locally secreted GDNF will improve graft DA-neuron survival and promote host striatal reinnervation. Release-relevant profile:
- mDA identity (TH, NURR1, FOXA2, LMX1A) and low residual pluripotency, comparable to a standard mDA graft.
- A transgene cassette drives GDNF secretion; in the current design the promoter is **constitutive** and the construct has **no inducible on/off control and no built-in retrieval/reversibility mechanism**.
- In vitro GDNF secretion confirmed; improved graft survival in 6-OHDA rodents.
- Prior **direct intraputamenal GDNF protein/AAV-GDNF clinical experience** is mixed: dosing/biodistribution difficulties, anti-GDNF antibodies, off-target effects, and cerebellar toxicity in primate toxicology at high exposure.

### Your job
Assess whether this engineered cell product is ready for **clinical translation** and give a Go / No-Go / Conditional Go decision. Reason explicitly through:
1. Dopaminergic / midbrain identity and the standard mDA-graft considerations (purity, pluripotency, tumorigenicity).
2. The **scientific rationale** for adding GDNF (trophic support for graft and host).
3. **Controllability of the transgene:** constitutive vs inducible/regulatable expression, dose control, and **reversibility/retrievability** if adverse effects occur.
4. GDNF-specific safety: biodistribution/spread, off-target sprouting, downregulation of host TH, weight loss, cerebellar toxicity, and immunogenicity (anti-GDNF antibodies) — informed by prior GDNF clinical/preclinical experience.
5. Insertional-mutagenesis / genomic-integration risk from the engineering step.
6. Functional maturity, graft survival, and imaging/clinical endpoints.
7. Clinical release criteria and potency assays (including a GDNF-secretion specification).

Distinguish a plausible, mechanistically attractive enhancement from a de-risked product. A strong answer credits the GDNF rationale but treats **uncontrolled, irreversible, constitutive trophic-factor secretion** as a major liability that must be engineered down (dose control, reversibility, biodistribution) before clinical use.

### Available tools
Databases (OpenTargets, Monarch), literature/web search, and `run_python_repl`. Use them to ground the GDNF mechanism, prior GDNF trial outcomes, transgene-control strategies, and tumorigenicity/release standards. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `cell_product`, `identity_assessment` (with `dopaminergic_markers`, `midbrain_markers`, `pluripotency_markers`), `safety_assessment`, `release_criteria`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). `safety_assessment` must address GDNF-transgene controllability/reversibility and GDNF-specific off-target risks. Include `functional_assessment`, `manufacturing_risks`, `next_validation_step`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
