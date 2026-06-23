# PD-TxBench Expert Review Report — ev_negative_mouse_to_clinical

**Task:** `ev_negative_mouse_to_clinical`  ·  **Family:** evidence_reasoning  ·  **Type:** negative control

> Packaged for **independent expert review**. The automated LLM-judge score (§5) is a starting point, not the verdict — complete the worksheet in §7. Treat every factual claim and citation below as **the agent's assertion, to be verified**.

## 1. Provenance

| Field | Value |
|---|---|
| Run | `run_20260623_083912` |
| Agent model | `gpt-5.5-2026-04-23` (provider: openai) |
| Reasoning effort | high |
| Mode | autonomous |
| Steps / tools loaded | 21 steps, 52 tools (failures: 0) |
| Tokens | 153,841 |
| Judge | `gpt-5.5-2026-04-23` (provider: openai) |
| Artifacts | `output/pdtx/evidence_reasoning/ev_negative_mouse_to_clinical/run_20260623_083912/` (result.json, reasoning.txt, agent.log, verification_notebook.ipynb) |

## 2. Question posed

See the full task prompt at `tasks/pdtx/evidence_reasoning/ev_negative_mouse_to_clinical.md`. The agent had to work the full therapeutic-reasoning chain and return a decision.

## 3. Agent's decision

> **Decision: Contradicted**  ·  **Confidence: 0.96**

## 4. Agent's deliverable (full structured output)

- **classification**: Contradicted
- **rationale**: The evidence supports only the narrow statement that Compound Q improved rotarod/motor readouts in a single 6-OHDA-lesioned rodent Parkinson's disease model. It directly does not support—and penalizes—the stronger claim that the compound is 'proven' clinically effective in patients. The provided record contains no Parkinson's disease human efficacy trial, no clinical endpoint data, and no human pharmacokinetic, BBB-penetration, dose-selection, or safety information. A ClinicalTrials.gov v2 search for studies with the terms "Compound Q" and Parkinson returned no studies. Preclinical neurotoxin models are useful hypothesis-generating systems, but they are not equivalent to idiopathic human PD and cannot establish benefit-risk in patients. Therefore the stated inference is an overclaim and should be classified as contradicted as a clinical-efficacy assertion.
- **preclinical_vs_clinical**: A single animal-model motor-behavior result is preclinical evidence only. The 6-OHDA lesion model primarily captures dopaminergic toxin injury and motor deficits; it does not reproduce the full chronic, heterogeneous human disease, alpha-synuclein/Lewy pathology, non-motor features, comorbidities, placebo effects, or clinical safety constraints. Positive rotarod scores may reflect symptomatic or nonspecific motor effects and do not establish that adequate brain exposure, tolerable dosing, durable efficacy, or disease modification will occur in humans. Bridging evidence would require ADME/PK, BBB exposure, toxicology, dose-response and replication before randomized controlled human trials.
- **logical_leap**: Overclaiming: the conclusion changes from 'worked in one mouse toxin-model behavioral assay' to 'proven clinically effective for PD patients' without human efficacy or benefit-risk evidence.
- **evidence_required_for_clinical_efficacy_claim**:
  - Independent replication in relevant preclinical models with pharmacodynamic target engagement and dose-response.
  - Preclinical ADME/PK including BBB penetration/brain exposure, and GLP toxicology to justify human dosing.
  - Phase 1 human safety/tolerability and pharmacokinetics, including exposure at plausible therapeutic doses.
  - Adequately powered randomized, controlled Phase 2/3 Parkinson's disease trials with prespecified clinical endpoints (e.g., MDS-UPDRS motor/non-motor outcomes), durability, and safety monitoring.
- **sources_used**:
  -
    - **source**: Provided evidence in prompt
    - **finding**: One 6-OHDA rodent study with improved rotarod/motor scores; no human trials; no human BBB, dose, safety, or PK data.
  -
    - **source**: ClinicalTrials.gov API v2
    - **query**: /studies?query.term=%22Compound%20Q%22%20Parkinson&format=json&pageSize=10
    - **finding**: Returned studies: [] (no matching registered trials found by that exact query).
  -
    - **source**: PubMed/E-utilities
    - **citation**: Neurotoxin-Induced Rodent Models of Parkinson's Disease: Benefits and Drawbacks. Neurotoxicity Research. 2021. DOI: 10.1007/s12640-021-00356-8; PMID: 33765237.
    - **finding**: Review context: rodent neurotoxin models are preclinical tools with benefits and limitations, not direct proof of clinical efficacy.
- **confidence**: 0.96

### Agent reasoning narrative (`reasoning.txt`)

> The claim overreaches. The reported observation—better rotarod/motor behavior after Compound Q in one 6-OHDA mouse study—is preclinical, hypothesis-generating evidence. It may justify further study, but it does not prove that Compound Q is clinically effective for Parkinson’s disease patients. The 6-OHDA model is a toxin-lesion model focused on dopaminergic injury and motor readouts; it does not capture the full chronic, heterogeneous biology of human PD, including Lewy/alpha-synuclein pathology, non-motor symptoms, comorbidities, and clinical placebo and safety issues. Behavioral improvement in rodents can also arise from symptomatic or nonspecific effects and may fail to translate. The provided evidence contains no human pharmacokinetics, BBB penetration, dose rationale, safety/tolerability, or randomized clinical efficacy data; a ClinicalTrials.gov search for “Compound Q” plus Parkinson found no matching studies. To support a clinical-efficacy claim, Compound Q would need translational PK/PD and toxicology plus adequately powered randomized controlled PD trials with prespecified clinical endpoints and safety monitoring.

## 5. Evidence base and methods (audit trail)

**Methodology:** 21 steps — tool use: run_python_repl ×15, query_pubmed ×2, query_clinicaltrials ×2, advanced_web_search_claude ×1, search_google ×1.

Representative search queries:
- `6-OHDA mouse model Parkinson disease limitations translational clinical efficacy review`
- `6-hydroxydopamine lesion model Parkinson disease limitations review`
- `authoritative sources 6-OHDA rodent model Parkinson disease limitations translational gap preclinical animal models do not prove c`
- `6-OHDA model Parkinson disease limitations translational gap clinical efficacy animal model review`

**Citations the agent relied on — verify each supports the stated claim:**

_No structured `evidence_used` field in the deliverable; check `reasoning.txt` and `agent.log` for cited sources._

> The most common LLM failure mode is a plausible-but-wrong citation: confirm each PMID/DOI exists, matches title/author/year, and supports the claim.

## 5b. Automated evaluation (LLM-as-judge) — validate, don't trust

Judge `gpt-5.5-2026-04-23`, rubric `pdtx_evidence_verification_v1`. **Final score 1.0**, decision_match = **match** (gold = Contradicted), schema-valid: True, red flags: none.

| Criterion | Score /5 | Judge justification (abridged) |
|---|:--:|---|
| correct_classification | 5 | Classifies the claim as Contradicted and clearly rejects the assertion that a mouse study proves clinical efficacy in PD patients. |
| evidence_use | 5 | Accurately characterizes the evidence as a single 6-OHDA rodent motor-behavior study and notes absence of human trials, clinical endpoints, human PK, BBB penetration, dos |
| preclinical_vs_clinical | 5 | Explicitly and thoroughly articulates the translational gap, including limitations of the 6-OHDA toxin model versus idiopathic human PD and why behavioral motor readouts  |
| uncertainty_handling | 5 | Clearly states the evidence required to support a clinical-efficacy claim, including replication, ADME/PK/BBB exposure, toxicology, Phase 1 safety/PK, and randomized cont |
| avoids_overclaiming | 5 | Directly identifies the inference as overclaiming/logical leap and penalizes the preclinical-to-clinical proof claim without endorsing it. |

> ⚠️ **Self-grading caveat:** agent and judge are the same provider/model — risk of self-consistency bias. The expert score (§7) is authoritative; cross-provider judging (`--judge-provider`) can reduce this.

## 6. Gold reference (calibration)

- **Preferred decision:** Contradicted (acceptable: ['Unsupported'])
- **Required concepts:** preclinical / animal-model evidence only, translational gap (mouse to human), no human clinical trial data, overclaiming / unjustified inference, what evidence would be required (human RCT, PK, safety)
- **Red flags (should NOT occur):** endorses the claim that a mouse result proves clinical efficacy; classifies as Supported or Partially supported; fails to identify the preclinical-to-clinical overclaim; treats animal motor improvement as clinical proof
- **Gold rationale:** A single 6-OHDA mouse motor-behavior result is preclinical evidence only and does not establish clinical efficacy in patients. The stated claim ('therefore proven clinically effective') is an overclaim: the correct classification is Contradicted (the proof claim is false), or at most Unsupported for the underlying compound. The appraisal must penalize the preclinical-to-clinical inference and state what human evidence would be required.

## 7. Expert review worksheet *(to complete)*

**A. Factual accuracy / hallucination check**
- Citations verified (exist + support claim)? ☐ all ✓  ☐ issues: ____________________
- Domain facts correct (mechanism, markers, trials, numbers)? ☐ ✓  ☐ ____________________
- Any fabricated sources/assays/data? ☐ none  ☐ ____________________

**B. Per-criterion expert score (0–5)** — override the automated scores
| Criterion | Expert /5 | Note |
|---|:--:|---|
| correct_classification | ☐ | |
| evidence_use | ☐ | |
| preclinical_vs_clinical | ☐ | |
| uncertainty_handling | ☐ | |
| avoids_overclaiming | ☐ | |

**C. Decision** — agree with **Contradicted**? ☐ Agree ☐ Disagree → your call: ____________
**D. Most important omission or error (if any):** ____________________
**E. Trust as a first-pass assessment?** ☐ Yes ☐ With edits ☐ No
**F. Overall expert grade (0–5): ____  Reviewer: ______  Date: ______  Specialty: ______**

## 8. Audit pointers
- Structured output: `output/pdtx/evidence_reasoning/ev_negative_mouse_to_clinical/run_20260623_083912/result.json`
- Tool-by-tool trace: `output/pdtx/evidence_reasoning/ev_negative_mouse_to_clinical/run_20260623_083912/agent.log`
- Methodology & scoring: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md`
- Task definition: `docs/pdtx_task_definitions.md` → `ev_negative_mouse_to_clinical`
