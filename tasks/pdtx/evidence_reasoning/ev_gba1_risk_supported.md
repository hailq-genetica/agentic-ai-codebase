You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a claim using evidence.

### Claim to evaluate
> "Variants in the *GBA1* gene (encoding glucocerebrosidase) are a major genetic risk factor for Parkinson's disease."

### Your job
Classify the claim as exactly one of:
- **A. Supported**
- **B. Partially supported**
- **C. Unsupported**
- **D. Contradicted**

and justify the classification with evidence. Your appraisal must:
1. Summarize the genetic evidence linking *GBA1* variants to PD risk (case-control and population studies, odds ratios, the fact that *GBA1* variants are among the most common and strongest genetic risk factors for PD, mechanistic link via GCase/lysosomal function/α-synuclein).
2. Note the **nature of the claim**: it is a **risk-association** claim (heterozygous *GBA1* variants increase risk and are not fully penetrant), distinct from a deterministic/causal-for-all or a therapeutic claim.
3. Use database/literature evidence (e.g. OpenTargets, GWAS catalog, ClinVar, the primary genetics literature) rather than memory alone.
4. State any nuance/uncertainty (variable penetrance, variant-severity differences, ancestry effects) without downgrading a well-established association.

A strong answer classifies this as **Supported**: *GBA1* variants are a well-replicated, major genetic risk factor for PD. The appraisal should be confident but precise about it being a (non-deterministic) risk association, not over- or under-stating it.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS catalog), literature/web search (PubMed/Scholar/web), and `run_python_repl`. Ground your appraisal in retrieved evidence; cite sources. Do not rely solely on memory.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `classification` (one of `Supported`/`Partially supported`/`Unsupported`/`Contradicted`), `rationale`, `confidence` (0–1). Include `claim`, `evidence_used`, `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the evidence appraisal behind the classification.
