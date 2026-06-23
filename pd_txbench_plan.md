Below is a comprehensive implementation plan to turn the paper’s lesson into **PD-TxBench Phase 2: an agentic benchmark for evaluating AI in Parkinson’s disease therapeutic discovery**.

# 1. Target outcome

PD-TxBench should evolve from:

> **“Can the model answer PD therapy questions?”**

to:

> **“Can the model behave like a useful PD therapeutic discovery assistant?”**

That means evaluating whether an AI can:

1. Understand Parkinson’s disease biology.
2. Use evidence from literature and data.
3. Reason across mechanisms, targets, compounds, cells, genes, and clinical translation.
4. Make Go/No-Go decisions.
5. Explain uncertainty.
6. Suggest next experiments.
7. Work autonomously or as a human copilot.

The benchmark should cover your three therapy categories:

1. **Small molecule**
2. **Gene therapy**
3. **Cell therapy**

---

# 2. Core design principle from the paper

The paper is useful because it evaluates AI agents as **research workflow performers**, not only answer generators.

For PD-TxBench, this means each task should test:

```text
Input problem
→ evidence collection
→ biological reasoning
→ therapeutic decision
→ uncertainty analysis
→ next validation step
→ final structured output
```

So PD-TxBench Phase 2 should include both:

| Benchmark type                        | Purpose                                              |
| ------------------------------------- | ---------------------------------------------------- |
| **Static QA tasks**                   | Test PD knowledge                                    |
| **Evidence-grounded reasoning tasks** | Test whether the model can use papers/data correctly |
| **Therapeutic decision tasks**        | Test Go/No-Go judgment                               |
| **Agentic workflow tasks**            | Test tool use and multi-step reasoning               |
| **Human-copilot tasks**               | Test whether human steering improves model output    |

---

# 3. Recommended PD-TxBench Phase 2 structure

## Overall benchmark architecture

```text
PD-TxBench Phase 2
│
├── A. Core PD Knowledge Tasks
│   ├── mechanism QA
│   ├── target-pathway QA
│   ├── therapy modality QA
│   └── clinical translation QA
│
├── B. Evidence-Grounded Reasoning Tasks
│   ├── claim verification
│   ├── paper-to-decision reasoning
│   ├── conflicting evidence analysis
│   └── target prioritization
│
├── C. Therapy-Specific Decision Tasks
│   ├── small-molecule candidate evaluation
│   ├── gene-therapy strategy evaluation
│   └── cell-therapy protocol evaluation
│
├── D. Agentic Discovery Tasks
│   ├── multi-step tool-use episodes
│   ├── autonomous discovery episodes
│   ├── experiment planning episodes
│   └── hypothesis generation episodes
│
├── E. Human-Copilot Evaluation
│   ├── autonomous mode
│   ├── human-on-the-loop mode
│   └── human-in-the-loop mode
│
└── F. Expert Review and Validation
    ├── gold answer review
    ├── rubric scoring
    ├── negative controls
    └── hidden test set
```

---

# 4. Phase 2 task suite

I recommend building **five task families**.

## Task Family 1: PD mechanism understanding

These are simpler tasks, but still necessary as a foundation.

### Goal

Evaluate whether the model understands PD biology.

### Example tasks

| Task                | Example                                                                |
| ------------------- | ---------------------------------------------------------------------- |
| Target explanation  | “Explain how GBA1 dysfunction contributes to PD pathology.”            |
| Pathway reasoning   | “Connect lysosomal dysfunction to α-synuclein accumulation.”           |
| Therapy matching    | “Which PD subpopulation is most relevant for GCase chaperone therapy?” |
| Risk identification | “What are key risks of LRRK2 inhibition?”                              |

### Output format

```json
{
  "answer": "...",
  "mechanism": "...",
  "key_evidence": ["..."],
  "uncertainty": "...",
  "confidence": 0.0
}
```

### Metrics

| Metric                   | Description                            |
| ------------------------ | -------------------------------------- |
| Accuracy                 | Is the answer correct?                 |
| Mechanistic completeness | Does it explain the biological chain?  |
| Evidence support         | Does it cite or use relevant evidence? |
| Hallucination penalty    | Does it invent unsupported claims?     |

---

## Task Family 2: Evidence-grounded claim verification

This is very important for drug discovery AI.

### Goal

Evaluate whether the model can verify a therapeutic claim using evidence.

### Example task

```text
Claim:
“Ambroxol is a disease-modifying therapy for Parkinson’s disease.”

Evaluate this claim using available evidence.
Classify it as:
A. Supported
B. Partially supported
C. Unsupported
D. Contradicted
```

Expected strong answer:

```text
Partially supported.

Ambroxol has mechanistic relevance as a GCase chaperone and has been studied in PD contexts, especially GBA-associated PD. However, current evidence does not conclusively establish it as a disease-modifying therapy. The model should distinguish mechanistic plausibility from proven clinical efficacy.
```

### Why this matters

Many AI models overclaim. In PD drug discovery, that is dangerous because early mechanistic evidence is often not the same as clinical efficacy.

### Scoring

| Score component                                | Weight |
| ---------------------------------------------- | -----: |
| Correct classification                         |    30% |
| Evidence use                                   |    25% |
| Distinguishes preclinical vs clinical evidence |    20% |
| Handles uncertainty                            |    15% |
| Avoids overclaiming                            |    10% |

---

## Task Family 3: Small-molecule candidate evaluation

This should be one of the strongest parts of PD-TxBench.

### Goal

Evaluate whether an AI can assess a small molecule as a PD therapeutic candidate.

### Input

```json
{
  "category": "small_molecule",
  "disease_context": "GBA1-associated Parkinson's disease",
  "candidate_smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O",
  "target": "GCase",
  "available_evidence": [
    "literature_context",
    "docking_result",
    "ADMET_prediction",
    "patent_signal"
  ]
}
```

### Expected reasoning

The AI should evaluate:

1. Disease relevance.
2. Target/MoA plausibility.
3. Docking or binding evidence.
4. BBB penetration.
5. ADMET risks.
6. CYP liability.
7. hERG, AMES, DILI, carcinogenicity.
8. Patent/novelty risk.
9. Go/No-Go decision.
10. Next experiment.

### Output schema

```json
{
  "mechanism_hypothesis": "...",
  "target_relevance": "...",
  "docking_interpretation": "...",
  "admet_assessment": {
    "bbb": "...",
    "ames": "...",
    "herg": "...",
    "dili": "...",
    "cyp_risk": "...",
    "solubility": "...",
    "clearance": "..."
  },
  "patent_risk": "...",
  "go_no_go": "Go | No-Go | Conditional Go",
  "main_risks": ["..."],
  "next_experiment": "...",
  "confidence": 0.0
}
```

### Small-molecule scoring rubric

| Component                    | Weight |
| ---------------------------- | -----: |
| PD mechanism relevance       |    20% |
| Correct target/MoA reasoning |    15% |
| ADMET interpretation         |    20% |
| Safety risk identification   |    15% |
| Go/No-Go quality             |    15% |
| Next experiment quality      |    10% |
| Uncertainty handling         |     5% |

---

## Task Family 4: Gene therapy strategy evaluation

### Goal

Evaluate whether the AI can design or critique a gene therapy strategy for PD.

### Example task

```text
A team proposes AAV-mediated GBA1 delivery for GBA-associated Parkinson’s disease.

Evaluate the strategy.
Include target rationale, patient population, vector/delivery considerations, risks, biomarkers, and validation experiments.
```

### Expected reasoning

The AI should discuss:

1. Genetic subtype.
2. Disease mechanism.
3. Cargo or intervention type.
4. Delivery route.
5. CNS targeting.
6. Reversibility.
7. Immune response.
8. Overexpression risk.
9. Biomarkers.
10. Preclinical model.
11. Clinical translation challenges.

### Output schema

```json
{
  "therapy_type": "gene_therapy",
  "target_gene": "...",
  "patient_population": "...",
  "therapeutic_rationale": "...",
  "delivery_strategy": "...",
  "key_risks": ["..."],
  "biomarkers": ["..."],
  "preclinical_validation": ["..."],
  "clinical_translation_challenges": ["..."],
  "go_no_go": "Go | No-Go | Conditional Go",
  "confidence": 0.0
}
```

### Gene therapy scoring rubric

| Component                    | Weight |
| ---------------------------- | -----: |
| Genetic rationale            |    20% |
| Delivery feasibility         |    15% |
| Safety risk analysis         |    20% |
| Patient stratification       |    15% |
| Biomarker/endpoint selection |    10% |
| Validation plan              |    15% |
| Uncertainty                  |     5% |

---

## Task Family 5: Cell therapy protocol evaluation

### Goal

Evaluate whether the AI can judge the translational readiness of a PD cell therapy protocol.

### Example task

```text
A protocol generates iPSC-derived dopaminergic neurons for PD transplantation.

Evaluate whether the product is ready for preclinical translation.
Consider identity markers, purity, residual pluripotency, functional maturity, tumor risk, graft survival, immune compatibility, and release criteria.
```

### Expected reasoning

The model should check:

1. Dopaminergic neuron identity.
2. Midbrain lineage.
3. Purity.
4. Residual pluripotency.
5. Tumorigenicity.
6. Functional dopamine release.
7. Graft integration.
8. Batch reproducibility.
9. Potency assays.
10. Clinical release criteria.

### Output schema

```json
{
  "therapy_type": "cell_therapy",
  "cell_product": "...",
  "identity_assessment": {
    "dopaminergic_markers": ["TH", "NURR1", "PITX3"],
    "midbrain_markers": ["FOXA2", "LMX1A"],
    "pluripotency_markers": ["OCT4", "SOX2", "NANOG"]
  },
  "safety_assessment": "...",
  "functional_assessment": "...",
  "manufacturing_risks": ["..."],
  "release_criteria": ["..."],
  "go_no_go": "Go | No-Go | Conditional Go",
  "next_validation_step": "...",
  "confidence": 0.0
}
```

### Cell therapy scoring rubric

| Component                      | Weight |
| ------------------------------ | -----: |
| Cell identity reasoning        |    20% |
| Safety/tumorigenicity analysis |    20% |
| Functional maturity assessment |    15% |
| Manufacturing/reproducibility  |    15% |
| Release criteria               |    15% |
| Translational decision         |    10% |
| Uncertainty                    |     5% |

---

# 5. Add agentic benchmark episodes

This is where you directly apply the paper’s insight.

Instead of giving the model one question, give it a **research task**.

## Example agentic task

```text
You are evaluating a new small molecule for GBA1-associated Parkinson’s disease.

Use the available tools:
1. literature_search
2. target_knowledge_graph
3. docking_result_reader
4. admet_predictor
5. patent_check

Produce:
1. mechanism hypothesis
2. evidence table
3. risk assessment
4. Go/No-Go decision
5. next experiment
```

## Agentic task schema

```json
{
  "task_id": "pdtx_agent_sm_001",
  "version": "phase2_v1",
  "category": "small_molecule",
  "task_type": "agentic_candidate_evaluation",
  "difficulty": "hard",
  "input": {
    "disease_context": "GBA1-associated Parkinson's disease",
    "candidate": {
      "name": "Ambroxol analog A",
      "smiles": "..."
    },
    "target": "GCase",
    "tools_allowed": [
      "literature_search",
      "knowledge_graph",
      "docking_reader",
      "admet_predictor",
      "patent_check"
    ]
  },
  "expected_outputs": {
    "mechanism_hypothesis": true,
    "evidence_table": true,
    "risk_assessment": true,
    "go_no_go": true,
    "next_experiment": true
  },
  "gold": {
    "preferred_decision": "Conditional Go",
    "required_concepts": [
      "GCase chaperone",
      "lysosomal function",
      "GBA1-PD",
      "BBB",
      "safety liability",
      "experimental validation"
    ],
    "red_flags": [
      "claiming proven disease modification without sufficient evidence",
      "ignoring BBB",
      "ignoring toxicity"
    ]
  }
}
```

---

# 6. Evaluation modes

The benchmark should evaluate three modes.

## Mode 1: Autonomous

The AI receives the task and completes everything alone.

### Measures

| Metric             | Description                 |
| ------------------ | --------------------------- |
| Task completion    | Did it finish?              |
| Tool choice        | Did it use the right tools? |
| Reasoning quality  | Was the logic valid?        |
| Final decision     | Was Go/No-Go correct?       |
| Hallucination rate | Did it invent evidence?     |

---

## Mode 2: Human-on-the-loop

The AI works independently, but a human checks major milestones.

Example checkpoints:

```text
Checkpoint 1: mechanism hypothesis
Checkpoint 2: evidence table
Checkpoint 3: ADMET/safety interpretation
Checkpoint 4: final decision
```

### Measures

| Metric                 | Description                                  |
| ---------------------- | -------------------------------------------- |
| Human correction count | How many times did the human intervene?      |
| Error recovery         | Did the AI improve after feedback?           |
| Final quality delta    | Was the final answer better than autonomous? |

---

## Mode 3: Human-in-the-loop

The human actively guides the AI.

Example interaction:

```text
Human: Focus more on BBB and hERG risk.
AI: Revises ADMET interpretation.
Human: Compare against known GCase chaperones.
AI: Adds comparative evidence.
Human: Recommend one validation assay.
AI: Suggests GCase activity assay in patient-derived cells.
```

### Measures

| Metric                 | Description                               |
| ---------------------- | ----------------------------------------- |
| Copilot usefulness     | Did it help the human work faster/better? |
| Responsiveness         | Did it follow steering?                   |
| Scientific improvement | Did human feedback improve correctness?   |
| Expert satisfaction    | Would a scientist reuse the system?       |

---

# 7. Dataset design

## Recommended Phase 2 dataset size

For a strong but realistic Phase 2 release:

| Dataset part                    | Suggested size |
| ------------------------------- | -------------: |
| Core PD knowledge tasks         |            150 |
| Evidence verification tasks     |            120 |
| Small-molecule evaluation tasks |            100 |
| Gene therapy tasks              |             70 |
| Cell therapy tasks              |             70 |
| Agentic workflow episodes       |             45 |
| Human-copilot pilot episodes    |           9–15 |
| Negative control tasks          |             60 |

Total: around **550–600 benchmark items**, plus **45 agentic episodes**.

For an MVP, reduce this to:

| Dataset part            | MVP size |
| ----------------------- | -------: |
| Core PD knowledge tasks |       60 |
| Evidence tasks          |       40 |
| Small molecule          |       40 |
| Gene therapy            |       25 |
| Cell therapy            |       25 |
| Agentic episodes        |       15 |
| Negative controls       |       25 |

Total MVP: around **215 tasks + 15 agentic episodes**.

---

# 8. Dataset split

Use four splits.

```text
pdtxbench_phase2_dev.jsonl
pdtxbench_phase2_public_test.jsonl
pdtxbench_phase2_hidden_inputs.jsonl
pdtxbench_phase2_hidden_gold.jsonl
```

## Split purpose

| Split             | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| Dev               | Prompt development and debugging                 |
| Public test       | Public leaderboard-style evaluation              |
| Hidden input      | Models submit outputs without seeing gold labels |
| Hidden gold       | Used internally for scoring                      |
| Expert review set | Used for manual scoring and validation           |

## Suggested split ratio

```text
Dev: 20%
Public test: 30%
Hidden test: 40%
Expert review/challenge: 10%
```

---

# 9. Negative controls

This is critical.

AI models often sound convincing even when the therapeutic idea is weak. PD-TxBench should test whether the model can say **No-Go**.

## Negative control examples

### Small molecule

```text
A compound has strong docking to GCase but poor BBB penetration and strong hERG risk.
Should it progress?
```

Expected: likely **No-Go** or **Conditional Go only with major optimization**.

### Gene therapy

```text
A team proposes non-specific SNCA overexpression suppression in all brain regions.
Evaluate safety and feasibility.
```

Expected: identify major risks.

### Cell therapy

```text
A cell product expresses TH but also has high OCT4 and NANOG expression.
Is it ready for transplantation?
```

Expected: **No-Go** because of residual pluripotency/tumor risk.

### Evidence reasoning

```text
A preclinical mouse study improved motor behavior. The model claims this proves clinical efficacy in PD patients.
```

Expected: penalize overclaiming.

---

# 10. Gold answer and expert review process

For Phase 2, not all tasks can be scored automatically. You need a hybrid system.

## Gold answer layers

Each benchmark item should have:

```json
{
  "gold_label": "...",
  "gold_rationale": "...",
  "required_concepts": ["..."],
  "acceptable_variants": ["..."],
  "red_flags": ["..."],
  "scoring_rubric": {...}
}
```

## Expert review workflow

```text
Task drafted by curator
→ reviewed by PD biology expert
→ reviewed by therapeutic modality expert
→ reviewed by benchmark/evaluation lead
→ finalized into dev/test/hidden split
```

## Expert roles

| Expert type         | Review focus                     |
| ------------------- | -------------------------------- |
| PD biologist        | Disease mechanism correctness    |
| Medicinal chemist   | Small-molecule feasibility       |
| Gene therapy expert | Vector, cargo, safety            |
| Cell therapy expert | QC, release criteria, tumor risk |
| Benchmark engineer  | Schema, scoring, reproducibility |

---

# 11. Scoring system

PD-TxBench Phase 2 should use a **multi-metric evaluation**, not just accuracy.

## Global scoring formula

```text
Final Score =
0.20 Scientific correctness
+ 0.20 Evidence grounding
+ 0.15 Therapeutic reasoning
+ 0.15 Safety and risk analysis
+ 0.10 Tool-use quality
+ 0.10 Actionability
+ 0.05 Uncertainty calibration
+ 0.05 Format compliance
```

## Rubric scale

Use 0–5 for expert-scored components.

| Score | Meaning                                   |
| ----: | ----------------------------------------- |
|     0 | Completely wrong or unsafe                |
|     1 | Mostly wrong, many unsupported claims     |
|     2 | Partially correct but incomplete          |
|     3 | Mostly correct, acceptable reasoning      |
|     4 | Strong answer with good evidence          |
|     5 | Expert-level, actionable, well-calibrated |

---

# 12. Tool-use evaluation

For agentic tasks, evaluate the AI’s workflow.

## Available benchmark tools

For official evaluation, tools should be controlled and reproducible.

Recommended tools:

| Tool                    | Function                                             |
| ----------------------- | ---------------------------------------------------- |
| `literature_search`     | Retrieve curated paper snippets                      |
| `knowledge_graph_query` | Query PD target/pathway relationships                |
| `docking_reader`        | Read precomputed docking results                     |
| `admet_reader`          | Read precomputed or model-predicted ADMET values     |
| `clinical_trial_lookup` | Retrieve trial status/outcomes from curated snapshot |
| `patent_signal_reader`  | Return patent/novelty risk signals                   |
| `experiment_planner`    | Optional structured assay suggestions                |

Important: for official scoring, avoid live web calls. Use **frozen snapshots** so results are reproducible.

## Tool-use metrics

| Metric                 | Description                             |
| ---------------------- | --------------------------------------- |
| Correct tool selection | Did the model choose relevant tools?    |
| Tool efficiency        | Did it avoid unnecessary calls?         |
| Evidence integration   | Did it use tool outputs correctly?      |
| Error handling         | Did it notice missing/conflicting data? |
| Trace completeness     | Is the workflow auditable?              |

---

# 13. Repository structure

Recommended repo structure:

```text
PD-TxBench/
│
├── data/
│   ├── phase1/
│   ├── phase2/
│   │   ├── dev/
│   │   ├── public_test/
│   │   ├── hidden/
│   │   └── expert_review/
│
├── schemas/
│   ├── task_schema_v2.json
│   ├── output_schema_v2.json
│   ├── rubric_schema_v2.json
│   └── tool_trace_schema_v2.json
│
├── tasks/
│   ├── small_molecule/
│   ├── gene_therapy/
│   ├── cell_therapy/
│   ├── evidence_reasoning/
│   └── agentic/
│
├── tools/
│   ├── literature_search.py
│   ├── knowledge_graph_query.py
│   ├── docking_reader.py
│   ├── admet_reader.py
│   ├── patent_signal_reader.py
│   └── clinical_trial_lookup.py
│
├── evaluators/
│   ├── exact_match.py
│   ├── rubric_eval.py
│   ├── evidence_eval.py
│   ├── tool_use_eval.py
│   ├── safety_eval.py
│   └── aggregate_metrics.py
│
├── agents/
│   ├── base_agent.py
│   ├── openai_agent.py
│   ├── anthropic_agent.py
│   ├── local_model_agent.py
│   └── txgemma_agent.py
│
├── prompts/
│   ├── system_prompts/
│   ├── task_prompts/
│   └── judge_prompts/
│
├── scripts/
│   ├── validate_schema.py
│   ├── run_benchmark.py
│   ├── run_agentic_eval.py
│   ├── compute_metrics.py
│   ├── generate_report.py
│   └── package_release.py
│
├── docs/
│   ├── benchmark_card_v2.md
│   ├── task_definitions_v2.md
│   ├── scoring_guide_v2.md
│   ├── model_submission_guide.md
│   └── error_analysis_template.md
│
└── results/
    ├── baseline_runs/
    ├── leaderboard/
    └── expert_reviews/
```

---

# 14. Required schemas

## Task schema v2

```json
{
  "task_id": "string",
  "version": "phase2_v1",
  "category": "small_molecule | gene_therapy | cell_therapy | evidence_reasoning | agentic",
  "task_type": "string",
  "difficulty": "easy | medium | hard | expert",
  "input": {
    "disease_context": "string",
    "therapeutic_context": "string",
    "candidate": {},
    "evidence": [],
    "tools_allowed": []
  },
  "expected_output_format": {},
  "gold": {
    "gold_label": "string",
    "gold_rationale": "string",
    "required_concepts": [],
    "acceptable_answers": [],
    "red_flags": []
  },
  "scoring": {
    "rubric_id": "string",
    "automatic_metrics": [],
    "expert_required": true
  },
  "metadata": {
    "source_ids": [],
    "license": "string",
    "curator": "string",
    "review_status": "draft | reviewed | finalized"
  }
}
```

## Model output schema

```json
{
  "task_id": "string",
  "model_id": "string",
  "mode": "autonomous | human_on_loop | human_in_loop",
  "final_answer": "string",
  "structured_output": {},
  "evidence_used": [
    {
      "source_id": "string",
      "claim_supported": "string"
    }
  ],
  "tool_trace": [
    {
      "tool_name": "string",
      "input": {},
      "output_summary": "string",
      "success": true
    }
  ],
  "uncertainty": "string",
  "confidence": 0.0
}
```

## Rubric schema

```json
{
  "rubric_id": "pdtx_sm_candidate_eval_v1",
  "criteria": [
    {
      "name": "scientific_correctness",
      "weight": 0.20,
      "scale": "0-5"
    },
    {
      "name": "evidence_grounding",
      "weight": 0.20,
      "scale": "0-5"
    },
    {
      "name": "safety_reasoning",
      "weight": 0.15,
      "scale": "0-5"
    }
  ]
}
```

---

# 15. Baseline models to evaluate

You should benchmark multiple model types.

## Baseline groups

| Group                    | Examples                                            |
| ------------------------ | --------------------------------------------------- |
| General LLMs             | GPT, Claude, Gemini                                 |
| Biomedical LLMs          | BioMistral, Meditron, BioGPT-style models           |
| Drug-discovery models    | TxGemma, ChemLLM-style models                       |
| Local open-source models | Llama/Qwen/Mistral variants                         |
| Agentic systems          | Tool-using agents with retrieval and analysis tools |

## Baseline conditions

Run each model in:

```text
1. Closed-book mode
2. RAG mode
3. Tool-using agent mode
4. Human-copilot mode
```

This will show whether performance comes from model memory, retrieval, tools, or human guidance.

---

# 16. Implementation timeline

## Recommended 12-week plan

### Weeks 1–2: Benchmark design freeze

Deliverables:

```text
task_schema_v2.json
output_schema_v2.json
rubric_schema_v2.json
task_definitions_v2.md
scoring_guide_v2.md
```

Actions:

1. Finalize task taxonomy.
2. Finalize scoring rubric.
3. Define required output format.
4. Decide MVP task count.
5. Decide which tools are available in agentic mode.

---

### Weeks 3–5: Dataset construction

Deliverables:

```text
pdtxbench_phase2_draft.jsonl
source_evidence_table.csv
negative_controls.jsonl
```

Actions:

1. Curate small-molecule tasks.
2. Curate gene therapy tasks.
3. Curate cell therapy tasks.
4. Add evidence verification tasks.
5. Add negative controls.
6. Add gold rationales.
7. Assign difficulty levels.

Recommended MVP target:

```text
60 core PD tasks
40 evidence tasks
40 small-molecule tasks
25 gene therapy tasks
25 cell therapy tasks
15 agentic episodes
25 negative controls
```

---

### Weeks 6–7: Tool sandbox implementation

Deliverables:

```text
literature_search.py
knowledge_graph_query.py
docking_reader.py
admet_reader.py
clinical_trial_lookup.py
patent_signal_reader.py
```

Actions:

1. Build frozen tool datasets.
2. Create tool API wrappers.
3. Log every tool call.
4. Add deterministic outputs.
5. Create tool-use scoring.

Important design choice:

> Official benchmark tools should use frozen data snapshots, not live web, to keep evaluation reproducible.

---

### Week 8: Evaluation engine

Deliverables:

```text
run_benchmark.py
run_agentic_eval.py
compute_metrics.py
rubric_eval.py
tool_use_eval.py
safety_eval.py
```

Actions:

1. Validate model output format.
2. Compute automatic metrics.
3. Support expert scoring.
4. Generate aggregate reports.
5. Separate public and hidden scores.

---

### Week 9: Baseline model runs

Deliverables:

```text
baseline_results.json
model_comparison_report.md
error_analysis_v1.md
```

Actions:

1. Run general LLM baseline.
2. Run biomedical LLM baseline.
3. Run RAG baseline.
4. Run tool-using agent baseline.
5. Compare performance by task type and therapy category.

---

### Week 10: Expert review

Deliverables:

```text
expert_review_sheet.csv
adjudicated_gold.jsonl
rubric_calibration_report.md
```

Actions:

1. Have experts review gold labels.
2. Calibrate rubric scoring.
3. Identify ambiguous tasks.
4. Remove or revise weak tasks.
5. Finalize hidden set.

---

### Week 11: Stress testing and error analysis

Deliverables:

```text
stress_test_results.md
leakage_check_report.md
failure_modes.md
```

Actions:

1. Test misleading evidence.
2. Test negative controls.
3. Test overclaiming.
4. Test unsupported citations.
5. Test schema compliance.
6. Test reproducibility.

---

### Week 12: Release package

Deliverables:

```text
RELEASE_v2.md
benchmark_card_v2.md
pdtxbench_phase2_dev.jsonl
pdtxbench_phase2_public_test.jsonl
pdtxbench_phase2_hidden_inputs.jsonl
schema_v2.json
scoring_guide_v2.md
baseline_results.md
```

Actions:

1. Package dataset.
2. Publish documentation.
3. Publish baseline results.
4. Publish evaluation scripts.
5. Prepare paper/manuscript section.

---

# 17. Minimum viable implementation

The full plan is large. The fastest useful implementation would be:

## MVP scope

```text
1. 200–250 total tasks
2. 15 agentic episodes
3. 3 therapy categories
4. 1 controlled tool sandbox
5. 3 baseline models
6. 1 expert review round
```

## MVP deliverables

```text
pdtxbench_phase2_dev.jsonl
pdtxbench_phase2_public_test.jsonl
pdtxbench_phase2_hidden_inputs.jsonl
schema_v2.json
evaluate.py
compute_metrics.py
rubric_eval.py
benchmark_card_v2.md
task_definitions_v2.md
baseline_report.md
```

This is enough to make Phase 2 credible.

---

# 18. Concrete action items

## Scientific action items

| Priority | Action                                  |
| -------- | --------------------------------------- |
| P0       | Define canonical PD targets/pathways    |
| P0       | Define therapy-specific rubrics         |
| P0       | Build small-molecule candidate tasks    |
| P0       | Build gene therapy strategy tasks       |
| P0       | Build cell therapy protocol tasks       |
| P1       | Add clinical trial interpretation tasks |
| P1       | Add target prioritization tasks         |
| P1       | Add negative controls                   |
| P2       | Add wet-lab experiment design tasks     |

## Engineering action items

| Priority | Action                     |
| -------- | -------------------------- |
| P0       | Create schema v2           |
| P0       | Update validation script   |
| P0       | Build evaluation runner    |
| P0       | Build rubric scorer        |
| P0       | Build result aggregation   |
| P1       | Add tool-use logging       |
| P1       | Add agentic execution mode |
| P1       | Add hidden-set scoring     |
| P2       | Add leaderboard support    |

## Benchmark quality action items

| Priority | Action                        |
| -------- | ----------------------------- |
| P0       | Create expert review template |
| P0       | Add red-flag labels           |
| P0       | Add uncertainty scoring       |
| P1       | Run baseline models           |
| P1       | Perform error analysis        |
| P1       | Remove ambiguous tasks        |
| P2       | Add inter-rater agreement     |

---

# 19. What success looks like

PD-TxBench Phase 2 is successful if it can show:

1. Which models know PD biology.
2. Which models can reason across evidence.
3. Which models overclaim therapeutic efficacy.
4. Which models can make safe Go/No-Go decisions.
5. Which models are useful as drug-discovery copilots.
6. Which therapy category is hardest: small molecule, gene therapy, or cell therapy.
7. Whether tool use improves performance.
8. Whether human feedback improves performance.

---

# 20. Final recommended implementation path

I would implement Phase 2 in this order:

```text
Step 1: Freeze schema and rubric
Step 2: Build 200-task MVP dataset
Step 3: Add 15 agentic episodes
Step 4: Build frozen tool sandbox
Step 5: Run 3–5 baseline models
Step 6: Expert review and adjudication
Step 7: Publish Phase 2 public test + hidden benchmark
Step 8: Write PD-TxBench paper section on agentic evaluation
```

The most important thing is not dataset size. The most important thing is that PD-TxBench Phase 2 evaluates the full therapeutic reasoning chain:

```text
PD mechanism
→ therapeutic target
→ modality choice
→ evidence strength
→ safety risk
→ translational feasibility
→ Go/No-Go decision
→ next experiment
```

That is what will make PD-TxBench meaningfully different from general biomedical QA benchmarks.

