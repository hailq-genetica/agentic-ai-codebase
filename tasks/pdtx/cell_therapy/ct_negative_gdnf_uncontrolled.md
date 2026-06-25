You are a cell-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Judge the translational readiness of an **engineered (gene-modified) cell** PD product. **[Negative control task]**

### Therapeutic context
A team proposes an **engineered cell graft** for **putaminal transplantation in Parkinson's disease** and asserts it is ready for first-in-human use, with this profile:
- iPSC-derived cells engineered with a **strong constitutive promoter driving very high, unregulated GDNF over-secretion**, integrated by **random lentiviral integration** (no defined safe-harbor locus, no integration-site analysis).
- **No inducible on/off control, no dose titration, and no retrieval/reversibility mechanism** — once grafted, secretion cannot be turned down or stopped.
- The graft's **dopaminergic / midbrain identity is only partially characterized** (TH reported; FOXA2/LMX1A and residual-pluripotency QC not shown), and **no in vivo tumorigenicity or biodistribution study** was done.
- The team argues "GDNF is neuroprotective, so more is better" and that high secretion guarantees graft and host neuron survival.

### Your job
Decide whether this product is ready for transplantation and give a Go / No-Go / Conditional Go decision. Reason through the transgene design, GDNF-specific safety, integration risk, identity/tumorigenicity gaps, and release criteria.

A correct assessment recognizes that **unregulated, irreversible, very high constitutive GDNF over-secretion is unsafe and "more is better" is wrong**: prior GDNF clinical/preclinical experience shows dose-dependent off-target effects (aberrant axonal sprouting, downregulation of host TH, weight loss, cerebellar toxicity in primate toxicology) and anti-GDNF immunogenicity, and an irreversible graft removes any ability to manage these. **Random lentiviral integration without integration-site analysis adds insertional-mutagenesis risk**, and identity/pluripotency/tumorigenicity characterization is incomplete with no in vivo data. The decision should be **No-Go** (re-engineer for regulated/inducible, dose-controlled, reversible/retrievable secretion using a defined safe-harbor integration, and complete identity, tumorigenicity, biodistribution, and dose-ranging studies). Do not accept "neuroprotective, so more is better."

### Available tools
Databases (OpenTargets, Monarch), literature/web search, and `run_python_repl`. Use them to ground prior GDNF trial outcomes and dose-dependent toxicity, transgene-regulation/safe-harbor strategies, and tumorigenicity/integration-safety standards. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `cell_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `cell_product`, `identity_assessment`, `safety_assessment`, `release_criteria`, `go_no_go`, `confidence`). `safety_assessment` must address unregulated/irreversible GDNF over-secretion, integration-site/insertional-mutagenesis risk, and the missing identity/tumorigenicity data. Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision, rejecting the "more GDNF is better" premise and weighing the controllability/integration/characterization gaps.
