# PD-TxBench Phase 2.5: A Small-Molecule Benchmark for Evaluating AI Systems in Parkinson’s Disease Therapeutic Discovery

**Authors:** [TO FILL]
**Affiliations:** [TO FILL]
**Correspondence:** [TO FILL]

## Abstract

AI systems are increasingly used to assist therapeutic discovery, but current biomedical benchmarks rarely test whether models can make disease-specific, translationally useful drug-development decisions. Parkinson’s disease presents a challenging small-molecule discovery setting because candidate evaluation requires reasoning across disease mechanism, target biology, molecular structure, blood–brain barrier penetration, pharmacokinetics, toxicology, clinical evidence, and experimental validation.

We introduce **PD-TxBench Phase 2.5**, a focused small-molecule benchmark for evaluating AI systems in Parkinson’s disease therapeutic discovery. Phase 2.5 separates small-molecule evaluation from the broader PD-TxBench Phase 2 framework, allowing deeper assessment of compound-level reasoning before expanding to gene therapy and cell therapy. The benchmark evaluates whether AI systems can assess Parkinson’s disease small-molecule candidates across target relevance, mechanism of action, docking or binding plausibility, ADMET properties, safety liabilities, patent or novelty risk, clinical translatability, Go/No-Go decision-making, and next-experiment planning.

PD-TxBench Phase 2.5 includes static tasks, evidence-grounded reasoning tasks, compound evaluation tasks, negative controls, lead-optimization tasks, repurposing tasks, and agentic tool-use episodes. Each task is paired with structured output requirements, gold rationales, required concepts, red-flag errors, and rubric-based scoring. Agentic tasks evaluate whether models can use controlled tools such as literature search, knowledge graph query, docking reader, ADMET reader, patent signal reader, and clinical trial lookup.

The benchmark is designed to expose small-molecule-specific AI failure modes, including over-prioritizing docking scores, ignoring brain penetration, overclaiming clinical efficacy, missing toxicology liabilities, confusing symptomatic and disease-modifying effects, and recommending chemically or translationally implausible candidates. PD-TxBench Phase 2.5 provides a practical intermediate step toward evaluating AI systems as Parkinson’s disease therapeutic discovery copilots.

---

## 1. Introduction

Large language models and AI agents are increasingly being applied to biomedical research and drug discovery. These systems can summarize literature, generate hypotheses, reason over molecular data, interact with computational tools, and support multi-step therapeutic evaluation. However, existing benchmarks often focus on general biomedical question answering rather than disease-specific therapeutic decision-making.

Parkinson’s disease is an important test case for AI-assisted therapeutic discovery. It is biologically heterogeneous and involves multiple disease mechanisms, including α-synuclein pathology, lysosomal dysfunction, mitochondrial dysfunction, neuroinflammation, dopaminergic neuron vulnerability, GBA1/GCase dysfunction, LRRK2 signaling, and related pathways. Small-molecule discovery for Parkinson’s disease requires more than identifying a plausible target. A useful AI system must reason across target biology, chemical structure, brain exposure, pharmacokinetics, safety, disease subtype, clinical evidence, and experimental validation.

PD-TxBench Phase 2 introduced a broad agentic benchmark framework covering small molecules, gene therapy, and cell therapy. However, each therapeutic modality requires distinct scientific reasoning and evaluation criteria. Small molecules are the most practical starting point because they can be evaluated through relatively standardized inputs such as SMILES strings, molecular descriptors, docking results, ADMET predictions, toxicity alerts, clinical evidence, and patent signals.

We therefore propose **PD-TxBench Phase 2.5**, a small-molecule-focused benchmark for evaluating AI systems in Parkinson’s disease therapeutic discovery. Phase 2.5 is designed as an intermediate release between Phase 2 and a full agentic therapeutic discovery benchmark. Its goal is to deeply evaluate whether AI systems can make reliable compound-level decisions in Parkinson’s disease.

The central question of PD-TxBench Phase 2.5 is:

**Can an AI system evaluate a small molecule as a Parkinson’s disease therapeutic candidate in a scientifically grounded, safety-aware, and translationally useful way?**

---

## 2. Why a Separate Small-Molecule Phase Is Needed

Small-molecule therapeutic evaluation is sufficiently complex to require its own benchmark. A single compound evaluation may require the model to answer several linked questions:

1. Is the proposed target relevant to Parkinson’s disease?
2. Is the mechanism of action plausible?
3. Is the compound likely to reach the brain?
4. Does the molecule have acceptable ADMET properties?
5. Are there major toxicity liabilities?
6. Does docking or binding evidence support the hypothesis?
7. Is the evidence preclinical, clinical, or speculative?
8. Is the compound novel or already patented?
9. Should the compound receive a Go, No-Go, or Conditional Go decision?
10. What experiment should be performed next?

General biomedical QA benchmarks do not test this full reasoning chain. Broad therapeutics benchmarks may include small molecules, but they are usually not specific to Parkinson’s disease biology. PD-TxBench Phase 2.5 addresses this gap by combining disease-specific biological reasoning with compound-level translational evaluation.

---

## 3. Benchmark Scope

PD-TxBench Phase 2.5 focuses only on small molecules for Parkinson’s disease.

### 3.1 Included therapeutic contexts

The benchmark includes tasks related to:

* GBA1/GCase modulation
* LRRK2 kinase inhibition
* α-synuclein aggregation modulation
* lysosomal/autophagy enhancement
* mitochondrial protection
* neuroinflammation modulation
* MAO-B inhibition
* dopamine metabolism and symptomatic therapy
* repurposed small molecules
* lead optimization of PD-relevant scaffolds
* blood–brain barrier and CNS exposure
* ADMET and toxicology evaluation
* patent and novelty assessment
* clinical translatability

### 3.2 Excluded from Phase 2.5

Phase 2.5 does not evaluate:

* gene therapy design
* AAV or viral-vector delivery
* CRISPR or gene editing
* ASO/siRNA therapeutic design
* cell therapy release criteria
* iPSC-derived dopaminergic neuron protocols
* surgical interventions
* deep brain stimulation
* non-pharmacological interventions

These areas remain part of broader PD-TxBench Phase 2 or later phases.

---

## 4. Benchmark Task Families

PD-TxBench Phase 2.5 contains eight small-molecule task families.

```text
PD-TxBench Phase 2.5
│
├── 1. Target-mechanism reasoning
├── 2. Evidence-grounded claim verification
├── 3. Candidate SMILES evaluation
├── 4. ADMET and CNS-drug-likeness assessment
├── 5. Docking and binding interpretation
├── 6. Lead optimization and analog reasoning
├── 7. Repurposing and clinical translatability
└── 8. Agentic small-molecule evaluation episodes
```

---

## 5. Task Family 1: Target-Mechanism Reasoning

### Purpose

Evaluate whether the model understands how a small-molecule target relates to Parkinson’s disease biology.

### Example task

**Input:**
A small molecule is proposed to enhance GCase activity in GBA1-associated Parkinson’s disease. Explain the therapeutic rationale and identify the main uncertainties.

### Expected output

The model should explain:

* GBA1 encodes glucocerebrosidase.
* Reduced GCase activity can impair lysosomal function.
* Lysosomal dysfunction may contribute to α-synuclein accumulation.
* GBA1-associated Parkinson’s disease may define a patient subgroup.
* GCase-enhancing small molecules may be mechanistically plausible.
* Clinical disease modification should not be claimed without sufficient evidence.

### Scoring dimensions

| Dimension                    | Weight |
| ---------------------------- | -----: |
| PD mechanism correctness     |    30% |
| Therapeutic target relevance |    25% |
| Disease-subtype reasoning    |    15% |
| Evidence uncertainty         |    15% |
| Avoidance of overclaiming    |    15% |

---

## 6. Task Family 2: Evidence-Grounded Claim Verification

### Purpose

Evaluate whether the model can judge therapeutic claims using evidence.

### Example task

**Claim:**
“Ambroxol is a proven disease-modifying therapy for Parkinson’s disease.”

**Expected answer:**
The model should classify this as **not fully supported**. It may recognize mechanistic plausibility and clinical investigation, but should not claim proven disease modification unless supported by definitive clinical outcome data.

### Output schema

```json
{
  "claim_classification": "Supported | Partially Supported | Unsupported | Contradicted | Insufficient Evidence",
  "evidence_summary": "...",
  "evidence_level": "in vitro | animal | biomarker | early clinical | randomized clinical | approved therapy",
  "main_uncertainty": "...",
  "overclaiming_risk": "...",
  "confidence": 0.0
}
```

### Scoring dimensions

| Dimension                                | Weight |
| ---------------------------------------- | -----: |
| Correct claim classification             |    30% |
| Evidence-level distinction               |    25% |
| Use of supporting and limiting evidence  |    20% |
| Uncertainty handling                     |    15% |
| Avoidance of unsupported clinical claims |    10% |

---

## 7. Task Family 3: Candidate SMILES Evaluation

### Purpose

Evaluate whether the model can assess a candidate compound from molecular input and therapeutic context.

### Example task

**Input:**

```json
{
  "candidate_smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O",
  "disease_context": "GBA1-associated Parkinson's disease",
  "proposed_target": "GCase",
  "task": "Evaluate whether this compound should progress to experimental validation."
}
```

### Expected reasoning

The model should evaluate:

* structural similarity to known compounds if relevant
* target/MoA plausibility
* CNS drug-likeness
* BBB penetration likelihood
* docking or binding plausibility if data are provided
* ADMET risk
* toxicity risk
* novelty or patent risk
* Go/No-Go decision
* next validation assay

### Output schema

```json
{
  "candidate_summary": "...",
  "mechanism_hypothesis": "...",
  "target_relevance": "...",
  "structure_based_observations": "...",
  "cns_drug_likeness": "...",
  "admet_risks": {
    "bbb": "...",
    "solubility": "...",
    "cyp": "...",
    "herg": "...",
    "ames": "...",
    "dili": "..."
  },
  "go_no_go": "Go | No-Go | Conditional Go",
  "main_reasons": ["..."],
  "next_experiment": "...",
  "confidence": 0.0
}
```

---

## 8. Task Family 4: ADMET and CNS-Drug-Likeness Assessment

### Purpose

Evaluate whether models correctly interpret pharmacokinetic and toxicology constraints for Parkinson’s disease small molecules.

### Example task

**Input:**

```json
{
  "candidate": "Compound X",
  "predicted_properties": {
    "bbb": "low",
    "caco2": "high",
    "ames": "negative",
    "herg": "high risk",
    "cyp3a4_inhibitor": "yes",
    "solubility": "poor"
  },
  "therapeutic_context": "chronic disease-modifying therapy for Parkinson's disease"
}
```

### Expected answer

The model should not recommend simple Go based only on target relevance. It should identify poor BBB penetration, hERG liability, CYP interaction risk, poor solubility, and chronic-use safety concerns. A strong answer would recommend No-Go or Conditional Go only after substantial optimization.

### Scoring dimensions

| Dimension                       | Weight |
| ------------------------------- | -----: |
| BBB/CNS exposure interpretation |    25% |
| Toxicology interpretation       |    25% |
| PK/solubility reasoning         |    15% |
| Chronic-use safety reasoning    |    15% |
| Decision quality                |    15% |
| Uncertainty                     |     5% |

---

## 9. Task Family 5: Docking and Binding Interpretation

### Purpose

Evaluate whether models correctly interpret docking or binding evidence without overclaiming.

### Example task

**Input:**

```json
{
  "target": "GCase",
  "compound": "Compound Y",
  "docking_score": "-8.7 kcal/mol",
  "reference_ligand_score": "-7.9 kcal/mol",
  "binding_site": "ambroxol-like pocket",
  "admet_summary": "poor BBB and hERG risk"
}
```

### Expected answer

The model should recognize that docking may support a binding hypothesis but does not prove biological activity, target engagement, CNS exposure, or disease modification. It should integrate ADMET concerns into the final recommendation.

### Red-flag errors

* Treating docking score as proof of efficacy
* Ignoring reference ligand context
* Ignoring pose quality
* Ignoring ADMET
* Claiming disease modification from docking alone
* Failing to recommend biochemical or cellular validation

---

## 10. Task Family 6: Lead Optimization and Analog Reasoning

### Purpose

Evaluate whether models can suggest rational small-molecule optimization strategies.

### Example task

**Input:**
A GCase chaperone analog has good predicted binding but poor solubility and high hERG risk. Suggest optimization priorities.

### Expected output

The model should propose cautious, chemistry-aware directions, such as:

* reduce lipophilicity if excessive
* improve polarity without destroying CNS penetration
* reduce hERG-associated features
* preserve pharmacophore interactions
* check metabolic liabilities
* maintain target engagement
* validate changes experimentally

The benchmark should penalize models that suggest arbitrary chemical changes without explaining why they improve the molecule.

### Output schema

```json
{
  "optimization_goal": "...",
  "liability_to_address": ["..."],
  "proposed_modifications": [
    {
      "modification": "...",
      "rationale": "...",
      "expected_benefit": "...",
      "risk": "..."
    }
  ],
  "properties_to_recheck": ["..."],
  "next_experiment": "...",
  "confidence": 0.0
}
```

---

## 11. Task Family 7: Repurposing and Clinical Translatability

### Purpose

Evaluate whether models can assess repurposed small molecules for Parkinson’s disease.

### Example task

**Input:**
A marketed drug is proposed for repurposing in Parkinson’s disease because it modulates lysosomal function. Evaluate whether it is a strong repurposing candidate.

### Expected reasoning

The model should assess:

* existing human safety data
* known dosing range
* CNS exposure
* disease-mechanism match
* biomarker strategy
* drug–drug interaction risk
* clinical endpoint feasibility
* whether evidence supports symptomatic or disease-modifying use
* patient subgroup selection

### Scoring dimensions

| Dimension                        | Weight |
| -------------------------------- | -----: |
| Repurposing rationale            |    20% |
| Human safety/dosing awareness    |    20% |
| CNS exposure reasoning           |    15% |
| Clinical evidence interpretation |    20% |
| Trial-design relevance           |    15% |
| Uncertainty                      |    10% |

---

## 12. Task Family 8: Agentic Small-Molecule Evaluation Episodes

### Purpose

Evaluate whether AI agents can perform a full small-molecule discovery workflow.

### Example agentic task

**Goal:**
Evaluate a new small molecule as a candidate for GBA1-associated Parkinson’s disease.

**Available tools:**

1. literature_search
2. pd_knowledge_graph_query
3. docking_reader
4. admet_reader
5. patent_signal_reader
6. clinical_trial_lookup
7. experiment_planner

**Required output:**

1. mechanism hypothesis
2. evidence table
3. docking/binding interpretation
4. ADMET/safety assessment
5. patent/novelty assessment
6. Go/No-Go decision
7. next experiment

### Agentic output schema

```json
{
  "task_id": "...",
  "model_id": "...",
  "mode": "autonomous | human_on_loop | human_in_loop",
  "mechanism_hypothesis": "...",
  "evidence_table": [
    {
      "evidence_type": "literature | docking | ADMET | clinical | patent",
      "finding": "...",
      "supports_or_limits": "...",
      "reliability": "low | medium | high"
    }
  ],
  "tool_trace": [
    {
      "tool_name": "...",
      "input_summary": "...",
      "output_summary": "...",
      "used_in_decision": true
    }
  ],
  "risk_assessment": {
    "scientific_risk": "...",
    "admet_risk": "...",
    "toxicity_risk": "...",
    "clinical_translation_risk": "...",
    "ip_or_novelty_risk": "..."
  },
  "go_no_go": "Go | No-Go | Conditional Go",
  "decision_rationale": "...",
  "next_experiment": "...",
  "confidence": 0.0
}
```

---

## 13. Controlled Tool Sandbox

Official evaluation should use frozen tools instead of live web search to ensure reproducibility.

### Recommended tools

| Tool                     | Purpose                                              |
| ------------------------ | ---------------------------------------------------- |
| literature_search        | retrieve curated PD/small-molecule evidence snippets |
| pd_knowledge_graph_query | return target-pathway-disease relationships          |
| docking_reader           | return precomputed docking scores and pose notes     |
| admet_reader             | return predicted or curated ADMET values             |
| patent_signal_reader     | return novelty/IP risk category                      |
| clinical_trial_lookup    | return curated trial status and evidence level       |
| experiment_planner       | suggest assay menu, not final answer                 |

### Tool-use metrics

| Metric                  | What it measures                               |
| ----------------------- | ---------------------------------------------- |
| Tool selection accuracy | Did the model use the right tools?             |
| Query quality           | Did it ask the right question?                 |
| Evidence integration    | Did it use tool outputs correctly?             |
| Tool efficiency         | Did it avoid unnecessary calls?                |
| Error recovery          | Did it notice missing or conflicting evidence? |
| Trace auditability      | Can reviewers follow the workflow?             |

---

## 14. Dataset Design

### 14.1 MVP dataset size

For Phase 2.5 MVP:

| Task family                          | Suggested count |
| ------------------------------------ | --------------: |
| Target-mechanism reasoning           |              40 |
| Evidence-grounded claim verification |              40 |
| Candidate SMILES evaluation          |              50 |
| ADMET/CNS assessment                 |              40 |
| Docking/binding interpretation       |              30 |
| Lead optimization                    |              30 |
| Repurposing/translatability          |              30 |
| Negative controls                    |              40 |
| Agentic episodes                     |              15 |

Total: **300 static tasks + 15 agentic episodes**

### 14.2 Full dataset size

For a stronger release:

| Task family                          | Suggested count |
| ------------------------------------ | --------------: |
| Target-mechanism reasoning           |              80 |
| Evidence-grounded claim verification |              80 |
| Candidate SMILES evaluation          |             120 |
| ADMET/CNS assessment                 |             100 |
| Docking/binding interpretation       |              80 |
| Lead optimization                    |              80 |
| Repurposing/translatability          |              60 |
| Negative controls                    |              80 |
| Agentic episodes                     |              40 |

Total: **680 static tasks + 40 agentic episodes**

---

## 15. Dataset Splits

Recommended files:

```text
pdtxbench_phase2_5_dev.jsonl
pdtxbench_phase2_5_public_test.jsonl
pdtxbench_phase2_5_hidden_inputs.jsonl
pdtxbench_phase2_5_hidden_gold.jsonl
pdtxbench_phase2_5_agentic_episodes.jsonl
```

Recommended split:

| Split                | Percentage |
| -------------------- | ---------: |
| Development          |        20% |
| Public test          |        30% |
| Hidden test          |        40% |
| Expert challenge set |        10% |

---

## 16. Task Schema

```json
{
  "task_id": "pdtx_sm_0001",
  "version": "phase2_5_v1",
  "category": "small_molecule",
  "task_family": "candidate_smiles_evaluation",
  "difficulty": "easy | medium | hard | expert",
  "input": {
    "disease_context": "...",
    "candidate": {
      "name": "...",
      "smiles": "...",
      "known_or_hypothetical": "known | hypothetical | analog"
    },
    "proposed_target": "...",
    "available_evidence": {
      "literature": [],
      "docking": {},
      "admet": {},
      "clinical": {},
      "patent": {}
    }
  },
  "expected_output_format": {
    "mechanism_hypothesis": "string",
    "admet_assessment": "object",
    "risk_assessment": "object",
    "go_no_go": "string",
    "next_experiment": "string"
  },
  "gold": {
    "preferred_decision": "Go | No-Go | Conditional Go",
    "gold_rationale": "...",
    "required_concepts": [],
    "acceptable_variants": [],
    "red_flags": []
  },
  "scoring": {
    "rubric_id": "pdtx_sm_eval_v1",
    "expert_required": true,
    "automatic_metrics": [
      "schema_validity",
      "required_concept_coverage",
      "red_flag_detection",
      "go_no_go_agreement"
    ]
  },
  "metadata": {
    "source_ids": [],
    "curator": "...",
    "review_status": "draft | reviewed | finalized"
  }
}
```

---

## 17. Scoring Rubric

### 17.1 Global score

```text
Final Score =
0.20 PD mechanism relevance
+ 0.15 target/MoA reasoning
+ 0.15 evidence grounding
+ 0.15 ADMET and CNS interpretation
+ 0.15 safety-risk identification
+ 0.10 Go/No-Go decision quality
+ 0.05 next-experiment actionability
+ 0.05 uncertainty calibration
```

### 17.2 Expert scoring scale

| Score | Meaning                                       |
| ----: | --------------------------------------------- |
|     0 | Incorrect, unsafe, or unsupported             |
|     1 | Mostly wrong with major omissions             |
|     2 | Partially correct but weak                    |
|     3 | Acceptable and mostly correct                 |
|     4 | Strong, evidence-grounded, useful             |
|     5 | Expert-level, actionable, and well-calibrated |

---

## 18. Negative Controls

PD-TxBench Phase 2.5 should strongly emphasize negative controls.

### Negative-control examples

| Scenario                            | Expected behavior                       |
| ----------------------------------- | --------------------------------------- |
| Strong docking but poor BBB         | Conditional Go or No-Go                 |
| Good target relevance but hERG risk | No-Go or optimization required          |
| Good BBB but AMES positive          | No-Go                                   |
| Mechanistic evidence only           | Do not claim clinical efficacy          |
| Animal-model benefit only           | Do not claim human disease modification |
| MAO-B symptomatic therapy           | Do not overclaim disease modification   |
| Patent-blocked analog               | Flag novelty/IP risk                    |
| Poor solubility and high clearance  | Optimization required                   |
| Weak target-disease link            | No-Go or low confidence                 |
| Conflicting literature evidence     | Conditional decision with uncertainty   |

---

## 19. Baseline Evaluation Plan

Models should be evaluated in four modes:

1. Closed-book LLM
2. Retrieval-augmented LLM
3. Tool-using agent
4. Human-copilot agent

### Model groups

| Group               | Examples                      |
| ------------------- | ----------------------------- |
| General LLMs        | GPT, Claude, Gemini           |
| Biomedical LLMs     | Bio-specialized open models   |
| Therapeutics models | TxGemma, Tx-LLM-style systems |
| Chemistry models    | molecule-aware models         |
| Agentic systems     | tool-using discovery agents   |

### Reported metrics

* overall score
* score by task family
* score by target class
* Go/No-Go accuracy
* negative-control failure rate
* overclaiming rate
* ADMET interpretation score
* tool-use quality
* evidence-grounding score
* expert-review score

---

## 20. Expected Failure Modes

PD-TxBench Phase 2.5 is designed to reveal whether models:

1. Over-prioritize docking scores
2. Ignore blood–brain barrier penetration
3. Ignore chronic-use toxicity
4. Overclaim disease modification
5. Confuse symptomatic and disease-modifying therapies
6. Ignore hERG, AMES, DILI, CYP, or solubility liabilities
7. Treat preclinical evidence as clinical proof
8. Recommend compounds without experimental validation
9. Fail to identify weak target-disease relationships
10. Generate arbitrary chemical modifications
11. Miss patent or novelty risk
12. Give high-confidence decisions under weak evidence

---

## 21. Implementation Plan

### Week 1: Scope freeze

Deliverables:

```text
task_taxonomy_phase2_5.md
schema_phase2_5.json
rubric_phase2_5.json
```

### Weeks 2–3: Dataset drafting

Deliverables:

```text
pdtxbench_phase2_5_draft.jsonl
negative_controls_phase2_5.jsonl
source_evidence_table.csv
```

### Weeks 4–5: Tool sandbox

Deliverables:

```text
literature_search.py
pd_knowledge_graph_query.py
docking_reader.py
admet_reader.py
patent_signal_reader.py
clinical_trial_lookup.py
```

### Week 6: Evaluation scripts

Deliverables:

```text
validate_schema.py
run_benchmark.py
run_agentic_eval.py
rubric_eval.py
compute_metrics.py
safety_eval.py
```

### Week 7: Baseline runs

Deliverables:

```text
baseline_results_phase2_5.json
model_comparison_phase2_5.md
```

### Week 8: Expert review and release

Deliverables:

```text
RELEASE_phase2_5.md
benchmark_card_phase2_5.md
scoring_guide_phase2_5.md
pdtxbench_phase2_5_dev.jsonl
pdtxbench_phase2_5_public_test.jsonl
pdtxbench_phase2_5_hidden_inputs.jsonl
```

---

## 22. Discussion

PD-TxBench Phase 2.5 provides a focused benchmark for evaluating small-molecule reasoning in Parkinson’s disease therapeutic discovery. By narrowing the scope to small molecules, the benchmark can go deeper into compound-level evaluation, including SMILES interpretation, docking, ADMET, safety, patent risk, and translational feasibility.

This focus is useful because small-molecule discovery is often the first area where AI systems are applied in practical drug discovery workflows. It also provides a bridge between simple biomedical QA and fully agentic therapeutic discovery. A model that performs well on general Parkinson’s disease questions may still fail at small-molecule evaluation if it ignores brain exposure, toxicology, or evidence strength.

The benchmark’s main contribution is the evaluation of decision quality. The goal is not only to determine whether a model can describe a molecule, but whether it can make a responsible Go/No-Go recommendation and suggest the next validation experiment. This is closer to the real needs of a therapeutic discovery team.

---

## 23. Limitations

PD-TxBench Phase 2.5 evaluates reasoning quality, not actual biological efficacy. In silico predictions, docking outputs, and ADMET estimates are imperfect and must be validated experimentally. Expert scoring may introduce subjectivity, although structured rubrics and adjudication can reduce inconsistency. Frozen tool snapshots improve reproducibility but may require periodic updates as new Parkinson’s disease small-molecule evidence emerges.

---

## 24. Conclusion

PD-TxBench Phase 2.5 is a small-molecule-focused benchmark for evaluating AI systems in Parkinson’s disease therapeutic discovery. It tests whether AI systems can reason across disease biology, molecular structure, target relevance, ADMET, safety, evidence strength, patent risk, and translational feasibility. By emphasizing Go/No-Go decision-making, negative controls, and agentic tool use, Phase 2.5 provides a practical and rigorous intermediate step toward a full Parkinson’s disease therapeutic discovery benchmark.

The benchmark’s central evaluation question is:

**Can an AI system responsibly evaluate whether a small molecule should progress as a Parkinson’s disease therapeutic candidate?**

---

## References

[1] Hendrycks et al. Measuring Massive Multitask Language Understanding.
[2] Jin et al. PubMedQA: A Dataset for Biomedical Research Question Answering.
[3] Chaves et al. Tx-LLM: A Large Language Model for Therapeutics.
[4] Wang et al. TxGemma: Efficient and Agentic LLMs for Therapeutics.
[5] Johri et al. Evaluating agentic AI for biological discovery in autonomous and copilot settings.
[6] Han et al. SMDD-Bench: Can LLMs Solve Real-World Small Molecule Drug Design Tasks?
[7] Toffoli et al. Protocol of ASPro-PD: a phase 3 trial of ambroxol to slow progression in Parkinson’s disease.
[8] Silveira et al. Ambroxol as a Treatment for Parkinson Disease Dementia.
[9] Karami et al. Recent advances in targeting LRRK2 for Parkinson’s disease.
[10] Tan et al. Monoamine Oxidase-B Inhibitors for the Treatment of Parkinson’s Disease.

