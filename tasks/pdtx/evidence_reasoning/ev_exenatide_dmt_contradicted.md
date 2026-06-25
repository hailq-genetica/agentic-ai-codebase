You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence. **[Negative control task — claim refuted by trial evidence]**

### Claim to evaluate
> "Exenatide (a GLP-1 receptor agonist) is a proven disease-modifying therapy for Parkinson's disease."

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it with evidence. Your appraisal must:
1. Describe the rationale and the **encouraging earlier-phase evidence** (GLP-1 neuroprotection rationale; a positive/encouraging Phase 2 signal that generated substantial interest in exenatide as a repurposed disease-modifying candidate).
2. Summarize the **definitive later evidence**, especially the **large, well-powered Phase 3 randomized controlled trial (Exenatide-PD3)** that **did not show a disease-modifying benefit** on the primary endpoint.
3. Carefully separate the word **"proven"** in the claim from the actual state of evidence: an encouraging Phase 2 followed by a **negative pivotal Phase 3** means the "proven disease-modifying" claim is refuted, even though the hypothesis was once promising.
4. State residual uncertainty (subgroups, ongoing analyses) without rescuing the "proven" claim.

A correct appraisal classifies the stated claim as **Contradicted**: the definitive Phase 3 trial did not demonstrate disease modification, so calling exenatide a *proven* disease-modifying therapy is refuted (at most *Unsupported*). Do not let the earlier positive Phase 2 or the mechanistic rationale rescue the "proven" claim.

### Available tools
Clinical-trials lookup, literature/web search (PubMed/Scholar/web), databases (OpenTargets, Monarch), and `run_python_repl`. Ground your appraisal in the actual trial evidence; cite sources. Do not rely solely on memory.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). Include `claim`, `evidence_used`, `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining why the "proven disease-modifying" claim is refuted by the definitive Phase 3 evidence.
