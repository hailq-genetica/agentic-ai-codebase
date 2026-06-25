You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD. **[Negative control task]**

### Therapeutic context
A team proposes **AAV delivery of aromatic L-amino acid decarboxylase (*DDC*/AADC)** for Parkinson's disease, asserting it is ready to advance, with this design:
- A **broadly biodistributed AAV** with a **strong ubiquitous promoter** driving **very high, constitutive AADC expression** — **not restricted to the putaminal target** (the vector reaches widespread cortical, limbic, and brainstem regions).
- **No dose control and no reversibility / shut-off mechanism.**
- Patients will **remain on their standard oral levodopa** doses, which the widespread AADC will convert to dopamine **throughout the brain**.
- The team argues "more AADC means better levodopa conversion, so a strong ubiquitous promoter and broad spread are advantages."

### Your job
Evaluate the safety and feasibility of this strategy and give a Go / No-Go / Conditional Go decision. Reason through:
1. Why **ectopic, non-target AADC expression** that converts circulating levodopa to dopamine in cortical/limbic/brainstem regions is dangerous (psychiatric effects, autonomic/cardiovascular effects, off-target neuromodulation).
2. **Runaway/uncontrolled dopamine and dyskinesia risk** when high constitutive AADC is combined with ongoing oral levodopa, with no ability to titrate the enzyme.
3. Lack of reversibility / shut-off for a permanent transgene if adverse effects occur.
4. Why **"more AADC is better" is wrong** and why **spatial restriction to the putamen and dose control** are essential (contrast with a properly targeted intraputaminal AADC approach).
5. Capsid/transgene immunity and broad-biodistribution safety.
6. Absence of patient stratification and of a sham-controlled plan.

A correct assessment identifies that **broad, uncontrolled, irreversible AADC overexpression combined with systemic levodopa is unsafe** — ectopic dopamine production and uncontrollable dyskinesia are predictable harms — and does **not** issue a Go. A safer redesign restricts expression to the putaminal target, controls dose, and adds reversibility. Do not accept "more AADC is better."

### Available tools
Databases (OpenTargets, Monarch, clinical trials, FDA safety), pharmacology tools, literature/web search, and `run_python_repl`. Use them to ground AADC/levodopa pharmacology, dopamine off-target effects, and targeted-delivery precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go`, `confidence`). `key_risks` must enumerate the major safety problems (ectopic dopamine, uncontrollable dyskinesia, irreversibility). Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, rejecting the "more AADC is better" premise and naming the safer redesign (putamen-restricted, dose-controlled, reversible).
