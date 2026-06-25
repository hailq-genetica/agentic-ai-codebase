You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD.

### Therapeutic context
A team proposes **AAV-mediated delivery of aromatic L-amino acid decarboxylase (*DDC*/AADC)** by **stereotactic, MRI-guided intraputaminal infusion** for **moderate-to-advanced, levodopa-responsive idiopathic Parkinson's disease**. The rationale is that restoring AADC in the putamen lets administered levodopa be converted to dopamine locally, improving the dose–response to oral levodopa. This is a **symptomatic** dopamine-restoration approach, not a disease-modifying one.

### Your job
Critique the strategy and assess whether it should progress. Reason explicitly through:
1. Mechanistic rationale: AADC converts levodopa→dopamine; why putaminal AADC restoration improves levodopa responsiveness — and that this is **symptomatic, not disease-modifying** (does not stop neurodegeneration).
2. Cargo / intervention type (enzyme gene addition for a symptomatic effect).
3. Delivery route and CNS targeting: stereotactic intraputaminal infusion, **putaminal coverage/biodistribution** (a recurring limitation of CNS gene therapy), AAV serotype/tropism.
4. **Dose control of the expressed enzyme** and the risk of dyskinesias from ectopic/excess dopamine; need to titrate against oral levodopa.
5. Reversibility (an integrated/episomal AAV transgene is effectively permanent).
6. Immune response to capsid and transgene.
7. Patient population / stratification (levodopa-responsive advanced PD; pre-existing anti-AAV neutralizing antibodies).
8. Biomarkers and endpoints (AADC PET tracer e.g. F-DOPA, ON/OFF time, levodopa-equivalent dose, dyskinesia scales) — and the need for **sham-controlled** trials given placebo effects in PD.
9. Preclinical model(s).
10. Clinical translation challenges.
11. A Go / No-Go / Conditional Go decision.

Distinguish a mechanistically sound, clinically precedented symptomatic approach from demonstrated efficacy/safety; do not overclaim disease modification.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), pharmacology tools, literature/web search, and `run_python_repl`. Use them to ground the AADC/levodopa rationale, existing AADC gene-therapy trials and delivery precedents, and dyskinesia/biomarker endpoints. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). Include `target_gene`, `patient_population`, `biomarkers`, `preclinical_validation`, `clinical_translation_challenges`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
