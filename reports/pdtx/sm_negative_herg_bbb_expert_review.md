# PD-TxBench Expert Review Report — sm_negative_herg_bbb

**Task:** `sm_negative_herg_bbb`  ·  **Family:** small_molecule  ·  **Type:** negative control

> Packaged for **independent expert review**. The automated LLM-judge score (§5) is a starting point, not the verdict — complete the worksheet in §7. Treat every factual claim and citation below as **the agent's assertion, to be verified**.

## 1. Provenance

| Field | Value |
|---|---|
| Run | `run_20260623_084935` |
| Agent model | `gpt-5.5-2026-04-23` (provider: openai) |
| Reasoning effort | high |
| Mode | autonomous |
| Steps / tools loaded | 10 steps, 82 tools (failures: 0) |
| Tokens | 107,105 |
| Judge | `gpt-5.5-2026-04-23` (provider: openai) |
| Artifacts | `output/pdtx/small_molecule/sm_negative_herg_bbb/run_20260623_084935/` (result.json, reasoning.txt, agent.log, verification_notebook.ipynb) |

## 2. Question posed

See the full task prompt at `tasks/pdtx/small_molecule/sm_negative_herg_bbb.md`. The agent had to work the full therapeutic-reasoning chain and return a decision.

## 3. Agent's decision

> **Decision: No-Go**  ·  **Confidence: 0.88**

## 4. Agent's deliverable (full structured output)

- **mechanism_hypothesis**:
  - **summary**: Compound X is proposed to bind/modulate glucocerebrosidase (GCase/GBA1), a genetically and biologically relevant lysosomal target in GBA1-associated Parkinson's disease.
  - **target_plausibility**: Mechanistically plausible: improving GCase function could address lysosomal dysfunction and alpha-synuclein biology in GBA1-PD.
  - **docking_interpretation**: A favorable GCase docking score supports possible target engagement but is only a hypothesis; it does not demonstrate cellular lysosomal activity, brain exposure, or safety margin.
- **admet_assessment**:
  - **bbb**:
    - **assessment**: Poor / not acceptable for a CNS PD therapeutic
    - **rationale**: Provided ADMET predicts poor BBB penetration and likely P-gp efflux. Independent physicochemical sanity check gives high TPSA (132.8 Å^2), MW 467.5, 7 HBA, 2 HBD, and a carboxylic acid/sulfonamide-rich scaffold, all unfavorable for passive CNS exposure. Any generic model output suggesting possible BBB permeation is outweighed by the CNS property profile and provided P-gp/BBB liability.
    - **impact**: Low probability of achieving sufficient unbound brain concentration to modulate lysosomal GCase in neurons.
  - **herg**:
    - **assessment**: High-risk / development-stopping liability
    - **rationale**: Provided ADMET predicts strong hERG inhibition liability. For a chronic PD therapy, QT-prolongation risk requires a wide safety margin; predicted strong hERG activity is not rescued by docking affinity.
    - **impact**: Serious cardiac safety concern and likely medicinal-chemistry redesign requirement.
  - **other**:
    - **physicochemical**: Calculated properties: MW 467.51 g/mol, cLogP 1.94, TPSA 132.8 Å^2, HBD 2, HBA 7, rotatable bonds 6.
    - **permeability_efflux**: Low Caco-2/permeability concern and likely P-gp substrate behavior are inconsistent with robust brain delivery.
    - **developability**: Solubility is moderate-to-poor predicted; acidic/high-polarity features may reduce CNS free fraction and increase transporter effects.
  - **evidence_sources**:
    - User-provided docking and ADMET evidence for poor BBB, P-gp efflux, and strong hERG liability
    - calculate_physicochemical_properties tool on the supplied SMILES
    - predict_admet_properties (DeepPurpose/MPNN) sanity check, interpreted cautiously and not allowed to override the provided BBB/P-gp and hERG liabilities
- **go_no_go**: No-Go
- **main_risks**:
  - Insufficient CNS exposure because of poor predicted BBB penetration, high TPSA, and likely P-gp efflux
  - Strong hERG inhibition liability with potential QT/cardiac safety risk
  - Docking-only efficacy evidence may not translate to biochemical, cellular, lysosomal, or in vivo target engagement
  - High polarity/acidic functionality may limit permeability and medicinal-chemistry optimization space
- **next_experiment**:
  - **recommendation**: Do not progress to PD efficacy studies. If the chemotype is retained, run a developability kill/diagnostic package: manual patch-clamp hERG plus bidirectional MDCK-MDR1/LLC-PK1 or PAMPA-BBB/brain-homogenate binding to quantify efflux and unbound brain exposure, then redesign analogs to reduce hERG and improve CNS MPO before repeating GCase assays.
  - **decision_gate**: Only analogs with acceptable hERG margin and demonstrated high passive permeability/low efflux and adequate unbound brain exposure should re-enter GCase functional testing.
- **confidence**: 0.88

### Agent reasoning narrative (`reasoning.txt`)

> Compound X has a mechanistically attractive rationale: GBA1-PD is linked to deficient glucocerebrosidase (GCase) activity, so a brain-penetrant GCase modulator could be disease-relevant. The favorable docking score therefore supports a target-engagement hypothesis, but docking is not sufficient evidence for a CNS therapeutic. The key developability signals are adverse. Provided ADMET predicts poor BBB penetration and likely P-gp efflux; a physicochemical check of the supplied SMILES is consistent with this concern (TPSA 132.8 Å², MW 467.5, multiple H-bond acceptors/donors, acidic/polar sulfonamide/carboxylate features). Thus the compound is unlikely to achieve adequate unbound neuronal/lysosomal exposure. More importantly, the provided prediction of strong hERG inhibition is a serious cardiac/QT liability for a chronic PD drug and is not offset by strong predicted GCase binding. Decision: No-Go. Next step should not be efficacy progression, but a kill/diagnostic package—manual patch-clamp hERG and bidirectional BBB/P-gp permeability—to guide redesign only if the chemotype is retained.

## 5. Evidence base and methods (audit trail)

**Methodology:** 10 steps — tool use: run_python_repl ×8, calculate_physicochemical_properties ×1, predict_admet_properties ×1.

**Citations the agent relied on — verify each supports the stated claim:**

_No structured `evidence_used` field in the deliverable; check `reasoning.txt` and `agent.log` for cited sources._

> The most common LLM failure mode is a plausible-but-wrong citation: confirm each PMID/DOI exists, matches title/author/year, and supports the claim.

## 5b. Automated evaluation (LLM-as-judge) — validate, don't trust

Judge `gpt-5.5-2026-04-23`, rubric `pdtx_sm_candidate_eval_v1`. **Final score 1.0**, decision_match = **match** (gold = No-Go), schema-valid: True, red flags: none.

| Criterion | Score /5 | Judge justification (abridged) |
|---|:--:|---|
| pd_mechanism_relevance | 5 | Clearly identifies GCase/GBA1 as a relevant lysosomal target in GBA1-associated PD and connects it to lysosomal dysfunction and alpha-synuclein biology. |
| target_moa_reasoning | 5 | Correctly treats favorable docking as only a hypothesis for target engagement and explicitly states it does not demonstrate cellular activity, brain exposure, or safety m |
| admet_interpretation | 5 | Directly and strongly weighs poor BBB penetration, high TPSA, P-gp efflux, and unfavorable CNS physicochemical features as incompatible with a CNS PD therapeutic. |
| safety_risk_identification | 5 | Explicitly flags strong hERG inhibition as a high-risk/development-stopping cardiac liability requiring redesign and not rescued by docking. |
| go_no_go_quality | 5 | Reaches the preferred No-Go decision for exactly the gold-reference reasons: inadequate CNS exposure and serious hERG liability despite mechanistic plausibility/docking. |
| next_experiment_quality | 5 | Appropriately recommends not progressing to efficacy studies and, if pursued, focusing on hERG patch clamp, permeability/efflux and unbound brain exposure assays plus red |
| uncertainty_handling | 5 | Well-calibrated throughout; avoids overclaiming from docking and frames computational/ADMET evidence cautiously while prioritizing major liabilities. |

> ⚠️ **Self-grading caveat:** agent and judge are the same provider/model — risk of self-consistency bias. The expert score (§7) is authoritative; cross-provider judging (`--judge-provider`) can reduce this.

## 6. Gold reference (calibration)

- **Preferred decision:** No-Go (acceptable: ['Conditional Go'])
- **Required concepts:** blood-brain barrier, hERG, CNS penetration, safety liability, docking is not sufficient, GCase
- **Red flags (should NOT occur):** issues a Go driven by docking score despite BBB and hERG liabilities; ignores blood-brain barrier / CNS penetration; ignores hERG / cardiac safety liability; treats strong binding as sufficient for progression
- **Gold rationale:** Despite strong predicted GCase binding, the molecule has poor BBB penetration (cannot reach a CNS target) and a strong hERG cardiac liability. Strong docking does not rescue an undeliverable, unsafe molecule. The correct decision is No-Go, or at most a Conditional Go contingent on major redesign to fix CNS exposure and hERG.

## 7. Expert review worksheet *(to complete)*

**A. Factual accuracy / hallucination check**
- Citations verified (exist + support claim)? ☐ all ✓  ☐ issues: ____________________
- Domain facts correct (mechanism, markers, trials, numbers)? ☐ ✓  ☐ ____________________
- Any fabricated sources/assays/data? ☐ none  ☐ ____________________

**B. Per-criterion expert score (0–5)** — override the automated scores
| Criterion | Expert /5 | Note |
|---|:--:|---|
| pd_mechanism_relevance | ☐ | |
| target_moa_reasoning | ☐ | |
| admet_interpretation | ☐ | |
| safety_risk_identification | ☐ | |
| go_no_go_quality | ☐ | |
| next_experiment_quality | ☐ | |
| uncertainty_handling | ☐ | |

**C. Decision** — agree with **No-Go**? ☐ Agree ☐ Disagree → your call: ____________
**D. Most important omission or error (if any):** ____________________
**E. Trust as a first-pass assessment?** ☐ Yes ☐ With edits ☐ No
**F. Overall expert grade (0–5): ____  Reviewer: ______  Date: ______  Specialty: ______**

## 8. Audit pointers
- Structured output: `output/pdtx/small_molecule/sm_negative_herg_bbb/run_20260623_084935/result.json`
- Tool-by-tool trace: `output/pdtx/small_molecule/sm_negative_herg_bbb/run_20260623_084935/agent.log`
- Methodology & scoring: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md`
- Task definition: `docs/pdtx_task_definitions.md` → `sm_negative_herg_bbb`
