You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence. **[Negative control task — biomarker-to-clinical overclaim]**

### Claim to evaluate
> "In a small open-label study, Drug Y reduced a CSF target-engagement biomarker in PD patients. Therefore Drug Y is a disease-modifying therapy for Parkinson's disease."

### Provided evidence
- A small, **open-label (uncontrolled)** study reporting that Drug Y **engaged its target / moved a CSF biomarker** (e.g. reduced a pathway analyte) over a few weeks.
- **No** placebo control, **no** randomization, **no** pre-specified clinical endpoint, and **no** demonstration of slowed clinical progression (UPDRS/disability over time).

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it. Your appraisal must:
1. Recognize that a **biomarker / target-engagement effect is pharmacodynamic evidence**, not evidence of a **clinical disease-modifying** effect.
2. Explain why an **open-label, uncontrolled** biomarker change cannot establish disease modification (no control, placebo effects, biomarker ≠ validated surrogate for clinical progression).
3. Identify the claim's logical leap (**"moved a biomarker, therefore disease-modifying"**) as **overclaiming**.
4. State what evidence would actually be required: a randomized, controlled, adequately powered trial with a pre-specified clinical progression endpoint (and, ideally, a validated surrogate).

A correct appraisal classifies the stated **"therefore disease-modifying"** claim as **Contradicted** (the inference is invalid; target engagement does not establish disease modification), or at most **Unsupported**. Do not endorse the biomarker-to-clinical leap, and do not treat target engagement as proof of clinical benefit.

### Available tools
Literature/web search, clinical-trials lookup, databases (OpenTargets, Monarch), and `run_python_repl`. Use them to ground the distinction between target engagement / biomarker effects and validated clinical disease modification, and the limits of open-label data. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). The `preclinical_vs_clinical` field must articulate the target-engagement-vs-clinical-efficacy gap. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining why the biomarker result does not establish disease modification and what would be required.
