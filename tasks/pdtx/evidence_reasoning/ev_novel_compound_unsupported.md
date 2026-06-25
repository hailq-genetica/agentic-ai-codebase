You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence. **[Negative control task — absence of evidence]**

### Claim to evaluate
> "BX-7724 (velparostat), a novel small molecule, is an effective therapy for Parkinson's disease."

### Context
"BX-7724 / velparostat" is presented as a new compound. You are asked to verify the efficacy claim against the available evidence base.

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it with evidence. Your appraisal must:
1. **Search the evidence base** (literature, clinical-trials registries, target/drug databases) for any data on this compound — mechanism, preclinical studies, or clinical trials.
2. Recognize that if **no credible published or registered evidence exists**, the efficacy claim is **Unsupported** — there is no basis to accept it. Note the important distinction: **absence of evidence (Unsupported) is not the same as evidence of absence (Contradicted)** — you have not found evidence that it fails, only no evidence that it works.
3. State exactly what evidence would be required to move the claim toward Supported (mechanism of action, preclinical efficacy/safety, then human trials).
4. Avoid fabricating or assuming results for a compound with no findable data.

A correct appraisal classifies the claim as **Unsupported**: with no findable credible evidence, an efficacy claim cannot be accepted. Do **not** classify it as Supported/Partially supported (no evidence to support it) and do **not** invent data; also avoid mislabeling it Contradicted, since no evidence refutes it either.

### Available tools
Literature/web search (PubMed/Scholar/web), clinical-trials lookup, databases (OpenTargets, Monarch, ChEMBL), and `run_python_repl`. Use them to confirm the absence (or presence) of evidence. Cite what you searched. Do not rely solely on memory, and do not fabricate sources.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). Include `claim`, `evidence_used` (what you searched and found), `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining why absence of credible evidence makes the claim Unsupported (not Supported, and not Contradicted), and what evidence would be required.
