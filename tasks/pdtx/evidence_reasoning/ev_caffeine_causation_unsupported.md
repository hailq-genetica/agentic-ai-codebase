You are a Parkinson's disease (PD) evidence-appraisal expert acting as a therapeutic-discovery assistant. Verify a claim using evidence. **[Negative control task — association vs causation]**

### Claim to evaluate
> "Caffeine prevents Parkinson's disease, because people who drink coffee have a lower incidence of PD."

### Your job
Classify the claim as exactly one of **Supported / Partially supported / Unsupported / Contradicted**, and justify it with evidence. Your appraisal must:
1. Acknowledge the **real epidemiological association**: multiple observational/prospective studies report an **inverse association** between caffeine/coffee intake and PD risk (and there is some supportive A2A-receptor mechanistic plausibility).
2. Identify the **logical flaw in the claim**: it infers **causation ("prevents") from observational association**. Discuss confounding, reverse causation (prodromal PD can reduce the appetite for coffee / changes in caffeine intake years before diagnosis), and selection effects.
3. Note that **interventional evidence** that caffeine *prevents* or modifies PD is lacking (e.g. trials of caffeine for PD have not established a disease-preventive or disease-modifying effect), so the causal/preventive claim is not established.
4. State what evidence would be required (well-designed prospective/Mendelian-randomization and interventional data) to support a causal preventive claim.

A correct appraisal classifies the **causal "prevents" claim** as **Unsupported** (an observational association does not establish causation/prevention); a defensible alternative is *Partially supported* **only if** the answer makes clear that the support is for an association, not for causation/prevention. Do not classify it as **Supported** (that would endorse the association-to-causation leap), and do not dismiss the genuine association entirely.

### Available tools
Literature/web search (PubMed/Scholar/web), clinical-trials lookup, databases (OpenTargets, Monarch), and `run_python_repl`. Ground your appraisal in retrieved evidence; cite sources. Do not rely solely on memory.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `evidence_reasoning` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `classification`, `rationale`, `confidence`). Include `claim`, `evidence_used`, `uncertainty`. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up explaining the association-vs-causation distinction and why the preventive claim is not established.
