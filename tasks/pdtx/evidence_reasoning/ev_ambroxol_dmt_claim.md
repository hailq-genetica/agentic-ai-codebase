You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence.

### Claim to evaluate
> "Ambroxol is a disease-modifying therapy for Parkinson's disease."

### Your job
Classify the claim as exactly one of:
- **A. Supported**
- **B. Partially supported**
- **C. Unsupported**
- **D. Contradicted**

and justify the classification with evidence. Your appraisal must:
1. Describe ambroxol's mechanistic rationale (GCase chaperone → lysosomal function → α-synuclein), especially in GBA-associated PD.
2. Summarize the actual clinical evidence to date (e.g. early-phase / proof-of-concept trials) and its limitations (size, endpoints, biomarker vs clinical outcomes).
3. **Explicitly distinguish mechanistic plausibility and biomarker effects from proven disease modification / clinical efficacy.**
4. State the uncertainty and what evidence would be needed to upgrade the claim.

A strong answer classifies this as **Partially supported**: ambroxol has genuine mechanistic relevance and encouraging early data, but current evidence does **not** conclusively establish disease modification. Avoid both overclaiming ("Supported"/proven DMT) and dismissiveness ("Unsupported"/no rationale).

### Available tools
Literature/web search (PubMed, Scholar, web), clinical-trials lookup, databases (OpenTargets, Monarch), and `run_python_repl`. Ground your appraisal in retrieved evidence; cite sources. Do not rely solely on memory.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json`. Required keys: `classification` (one of `Supported`/`Partially supported`/`Unsupported`/`Contradicted`), `rationale`, `confidence` (0–1). Include `claim`, `preclinical_vs_clinical`, `evidence_used`, `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up of the evidence appraisal behind the classification.
