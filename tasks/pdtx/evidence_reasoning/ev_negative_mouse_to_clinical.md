You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence. **[Negative control task — overclaiming]**

### Claim to evaluate
> "A preclinical study reported that Compound Q improved motor behavior in a 6-OHDA mouse model of Parkinson's disease. Therefore Compound Q is proven to be clinically effective for Parkinson's disease patients."

### Provided evidence
- A single rodent study (6-OHDA lesion model) showing improved rotarod/motor scores after Compound Q.
- No human clinical trials. No information on BBB penetration, dose, safety, or pharmacokinetics in humans.

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it. Your appraisal must:
1. Recognize that a single animal-model motor-behavior result is **preclinical** evidence only.
2. Explain why preclinical efficacy in a toxin model does **not** establish clinical efficacy in patients (translational gap, model limitations, no human PK/safety/efficacy data).
3. Identify the claim's logical leap as **overclaiming**.
4. State what evidence would actually be required to support a clinical-efficacy claim.

A correct appraisal classifies the stated claim as **Contradicted** (or, at most, the underlying compound as *Unsupported* for clinical efficacy) and explicitly penalizes the inference that a mouse result "proves" clinical efficacy. Do not endorse the overclaim.

### Available tools
Literature/web search, clinical-trials lookup, and `run_python_repl`. You may confirm the absence of clinical evidence. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). The `preclinical_vs_clinical` field must articulate the translational gap. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining why the claim overreaches and what would be needed to support it.
