You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a therapeutic claim using evidence. **[Negative control task — claim refuted by trial evidence]**

### Claim to evaluate
> "Coenzyme Q10 (CoQ10) slows clinical disease progression in Parkinson's disease."

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it with evidence. Your appraisal must:
1. Describe the original rationale and early signal (mitochondrial/antioxidant mechanism; a small early-phase study that suggested possible slowing of decline).
2. Summarize the **definitive clinical trial evidence**, especially the **large, well-powered randomized controlled trial(s)** (e.g. the NINDS QE3 Phase 3 trial of CoQ10 in early PD) that **found no benefit** on progression and were stopped for futility.
3. Distinguish an encouraging early/underpowered signal from the subsequent **definitive negative RCT** that **refutes** the progression claim.
4. State the resulting evidence-based conclusion and any residual uncertainty.

A correct appraisal classifies the claim as **Contradicted**: a large, well-powered RCT failed to show that CoQ10 slows PD progression, which directly refutes the claim (at most *Unsupported*). Do not revive the claim on the basis of the early underpowered signal or mechanistic plausibility.

### Available tools
Clinical-trials lookup, literature/web search (PubMed/Scholar/web), databases (OpenTargets, Monarch), and `run_python_repl`. Ground your appraisal in the actual trial evidence; cite sources. Do not rely solely on memory.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). Include `claim`, `evidence_used`, `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining why the definitive RCT evidence refutes the progression claim.
