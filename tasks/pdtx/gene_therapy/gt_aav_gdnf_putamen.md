You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD.

### Therapeutic context
A team proposes **AAV-mediated delivery of GDNF** (glial cell line-derived neurotrophic factor) to the **putamen by convection-enhanced delivery (CED)** for **moderate idiopathic Parkinson's disease**, intended to provide trophic support to surviving nigrostriatal dopaminergic neurons. The design specifies putamen-restricted infusion with intraoperative MRI tracking of distribution. The proposed promoter is **constitutive** in the current version, and the team has not yet defined a dose-control or shut-off strategy.

### Your job
Critique the strategy and assess whether it should progress. Reason explicitly through:
1. Mechanistic rationale: GDNF as trophic support for nigrostriatal neurons — neuroprotective/restorative intent vs symptomatic — and the gap between preclinical promise and prior clinical results.
2. **Prior GDNF / neurturin (CERE-120) clinical experience in PD**, which largely failed on efficacy, with **putaminal coverage/biodistribution** repeatedly implicated — a central design problem.
3. Delivery route and CNS targeting: CED, coverage of the putaminal target volume, AAV serotype/tropism, intraoperative distribution monitoring.
4. **Dose control and reversibility:** constitutive AAV-GDNF is effectively permanent and cannot be titrated or stopped; this matters given dose-dependent GDNF off-target effects (aberrant sprouting, downregulation of host TH, weight loss, cerebellar toxicity in primate toxicology) and anti-GDNF immunogenicity.
5. Immune response to capsid and transgene.
6. Patient population / stratification (disease stage; earlier vs advanced).
7. Biomarkers and endpoints (F-DOPA/DAT PET, UPDRS, sham-controlled design).
8. Preclinical model(s) and why prior preclinical-to-clinical translation failed.
9. Clinical translation challenges.
10. A Go / No-Go / Conditional Go decision.

Distinguish mechanistic appeal from demonstrated efficacy; a strong answer treats **coverage/biodistribution and the lack of dose control/reversibility** as the gating issues to resolve before progression, and avoids a "GDNF is neuroprotective, so it will work" assumption that prior trials already disproved.

### Available tools
Databases (OpenTargets, Monarch, clinical trials, FDA safety), pharmacology tools, literature/web search, and `run_python_repl`. Use them to ground the GDNF mechanism, prior GDNF/neurturin PD trial outcomes, CED/coverage precedents, and dose-dependent GDNF toxicity. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). Include `target_gene`, `patient_population`, `biomarkers`, `preclinical_validation`, `clinical_translation_challenges`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
