You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD.

### Therapeutic context
A team proposes **AAV-mediated *PRKN* (parkin) gene addition** for **autosomal-recessive, early-onset Parkinson's disease caused by biallelic loss-of-function *PRKN* mutations**. Parkin is an E3 ubiquitin ligase acting with PINK1 in mitochondrial quality control (mitophagy); biallelic *PRKN* loss causes a relatively pure, slowly progressive, levodopa-responsive parkinsonism with prominent nigral dopaminergic loss but typically little Lewy pathology. The intent is **disease-modifying**: restore parkin function in at-risk neurons.

### Your job
Critique the strategy and assess whether it should progress. Reason explicitly through:
1. Genetic rationale: biallelic *PRKN* loss-of-function → impaired mitophagy/mitochondrial QC → selective nigral degeneration; why **gene addition is the mechanistically correct modality** for an autosomal-recessive loss-of-function disease (contrast with dominant gain-of-function targets that need lowering, not addition).
2. Cargo / intervention type (parkin coding-sequence addition; transgene size vs AAV packaging limit).
3. Delivery route and CNS targeting (nigrostriatal regions; serotype/tropism; coverage of substantia nigra/striatum).
4. **Overexpression risk:** supraphysiologic parkin and dose control.
5. Reversibility (effectively permanent transgene).
6. Immune response to capsid and to parkin transgene.
7. **Patient population / stratification:** this is a rare, genetically defined population (biallelic *PRKN* carriers) — small numbers, need for genetic confirmation, and the value of treating early given slow progression.
8. Biomarkers and endpoints (mitochondrial/mitophagy markers, DAT/F-DOPA PET, UPDRS) and trial-design challenges in a rare disease.
9. Preclinical model(s) (PRKN/PINK1 models, noting their mild phenotypes).
10. Clinical translation challenges (rare population, slow progression, endpoint sensitivity).
11. A Go / No-Go / Conditional Go decision.

Distinguish a clean loss-of-function genetic rationale from demonstrated efficacy/safety; note the rare-population and slow-progression trial-design difficulties.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS, clinical trials, FDA safety), pharmacology tools, literature/web search, and `run_python_repl`. Use them to ground the *PRKN*/PINK1 mitophagy mechanism, the recessive genetic architecture, and gene-addition precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go` (`Go`/`No-Go`/`Conditional Go`), `confidence` (0–1). Include `target_gene`, `patient_population`, `biomarkers`, `preclinical_validation`, `clinical_translation_challenges`, `uncertainty`, `evidence_used` where possible. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the analysis behind your decision and your handling of uncertainty.
