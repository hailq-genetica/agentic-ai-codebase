You are a gene-therapy and Parkinson's disease (PD) expert acting as a therapeutic-discovery assistant. Evaluate a gene-therapy strategy for PD. **[Negative control task]**

### Therapeutic context
A team proposes lowering **LRRK2** to treat *LRRK2*-associated and idiopathic Parkinson's disease, asserting it is ready to advance, with this design:
- A **systemically administered (intravenous) AAV** delivering an shRNA against *LRRK2*, with a **ubiquitous promoter** and **broad biodistribution to peripheral organs** (lung, kidney, liver) as well as the CNS — i.e. **no CNS restriction and no cell-type targeting**.
- **Constitutive, non-regulatable knockdown** with no dose control and no reversibility.
- The team argues "LRRK2 kinase gain-of-function drives PD, so lowering LRRK2 everywhere is good," and does not address peripheral consequences.

### Your job
Evaluate the safety and feasibility of this strategy and give a Go / No-Go / Conditional Go decision. Reason through:
1. The LRRK2 rationale: *LRRK2* gain-of-function (e.g. G2019S) supports **lowering** as a direction — but the **route and biodistribution**, not just the direction, determine safety.
2. **Peripheral LRRK2 loss-of-function toxicity:** LRRK2 is highly expressed in lung (type II pneumocytes; lamellar-body/surfactant abnormalities reported with LRRK2 inhibition) and kidney, and is important in immune cells — broad peripheral knockdown risks **lung and kidney pathology** and immune effects. This is the central problem with a non-CNS-restricted approach.
3. Lack of **CNS restriction / cell-type targeting** — a systemic ubiquitous vector exposes peripheral organs unnecessarily.
4. Constitutive shRNA risks: no dose control, no reversibility, and potential **RNAi-saturation neurotoxicity** at high expression.
5. Absence of patient stratification (e.g. *LRRK2* variant carriers vs idiopathic).
6. Why a safer approach is **CNS-restricted, dose-controlled/regulatable, partial** LRRK2 lowering (or CNS-targeted delivery) rather than systemic constitutive knockdown — and that even approved/known LRRK2-lowering modalities are pursued with attention to the therapeutic window and peripheral safety.

A correct assessment recognizes that although **lowering LRRK2 is a valid direction**, a **systemic, non-CNS-restricted, constitutive, irreversible knockdown is unsafe** because of peripheral (lung/kidney/immune) LRRK2 loss-of-function toxicity and lack of control — and does **not** issue a Go. Do not let the correct target direction ("lower LRRK2") excuse an unsafe route/biodistribution.

### Available tools
Databases (OpenTargets, Monarch, ClinVar, GWAS, FDA safety), pharmacology tools, literature/web search, and `run_python_repl`. Use them to ground LRRK2 expression/biology, peripheral LRRK2-inhibition safety findings (lung/kidney), and shRNA gene-therapy precedents. Cite what you used.

### Deliverables (write to the run's output directory)
> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run directory. Do **not** reassign it or invent a path (e.g. `output_dir = "output/..."`). Write exactly to `f"{output_dir}/result.json"` and `f"{output_dir}/reasoning.txt"`.
- **`result.json`** — a JSON object matching the `gene_therapy` output schema in `tasks/pdtx/schemas/output_schema_v2.json` (required: `therapeutic_rationale`, `delivery_strategy`, `key_risks`, `go_no_go`, `confidence`). `key_risks` must enumerate the major safety problems (peripheral lung/kidney LRRK2-loss toxicity, no CNS restriction, no dose control/reversibility). Generate it programmatically to `f"{output_dir}/result.json"`.
- **`reasoning.txt`** — ~150-word write-up justifying the decision and naming the safer redesign (CNS-restricted, dose-controlled/regulatable, partial lowering).
