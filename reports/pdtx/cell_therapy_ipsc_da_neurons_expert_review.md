# PD-TxBench Expert Review Report — Cell Therapy

**Task:** `ct_ipsc_da_neurons` — translational-readiness evaluation of an iPSC-derived midbrain
dopaminergic (mDA) neuron product for Parkinson's disease transplantation.
**Family:** cell_therapy (positive case)

> This report packages one agent episode for **independent expert review**. It contains the question
> posed, the agent's full deliverable, the evidence and methods it used, and an *automated* rubric score.
> The automated score is a starting point, **not** the verdict — Sections 7–8 are for the expert to
> fill in. Treat every factual claim and citation below as **the agent's assertion, to be verified**.

---

## 1. Provenance

| Field | Value |
|---|---|
| Run ID | `run_20260623_071311` |
| Agent model | `gpt-5.5-2026-04-23` (provider: openai, Responses API) |
| Reasoning effort | high |
| Mode | autonomous |
| Tools loaded | 52 (`external_database` + literature + support) |
| Steps / tool calls | 86 steps, 87 tool calls (1 tool failure, handled gracefully) |
| Tokens consumed | ~1.38M (peak context 24.4% of 128k) |
| Judge | `gpt-5.5-2026-04-23` (same model; see §6 caveat) |
| Artifacts | `output/pdtx/cell_therapy/ct_ipsc_da_neurons/run_20260623_071311/` (`result.json`, `reasoning.txt`, `agent.log`, `verification_notebook.ipynb`) |

---

## 2. The question posed to the agent

Judge whether an iPSC-derived midbrain dopaminergic neuron product is **ready for preclinical
translation**, given this QC profile, and return a Go / No-Go / Conditional Go decision:

- Dopaminergic markers **TH, NURR1/NR4A2, PITX3** expressed in the majority of cells
- Midbrain floor-plate markers **FOXA2, LMX1A** co-expressed
- Residual pluripotency markers **OCT4, SOX2, NANOG** below assay detection in QC
- **In vitro dopamine release** demonstrated

The agent had to reason across identity, purity, residual pluripotency/tumorigenicity, functional
maturity, graft survival, manufacturing reproducibility, potency assays, and release criteria.

---

## 3. Agent's decision

> **Decision: Conditional Go** — proceed to formal IND-enabling preclinical validation, **not** clinical
> dosing. **Confidence: 0.78.**

Headline rationale (agent's words): *"Encouraging in vitro characterization; suitable to enter formal
IND-enabling preclinical validation, but not yet a fully de-risked clinical product."*

---

## 4. Agent's deliverable (structured)

### 4.1 Identity — "supportive but incomplete"
- **DA markers:** TH+/NURR1/PITX3 in a majority supports DA fate; flagged that *"majority" is not a
  release spec* and called for per-batch quantitative thresholds + single-cell co-expression, plus
  DDC/AADC, DAT(SLC6A3), VMAT2(SLC18A2), MAP2/TUJ1, synaptic markers, electrophysiology.
- **Midbrain:** FOXA2/LMX1A supports ventral midbrain floor-plate lineage, **but A9/substantia-nigra
  identity is not proven** by these alone; recommends EN1/EN2, OTX2, CORIN, and A9-enriched markers
  (SOX6, ALDH1A1, KCNJ6/GIRK2, calbindin-low), benchmarked by scRNA-seq vs fetal ventral midbrain.
- **Pluripotency:** "below detection" is *necessary but not sufficient*; needs validated assay LOD,
  spike-in recovery, orthogonal assays (flow/qPCR/ddPCR, TRA-1-60/SSEA/LIN28, iPSC-specific miRNA), and
  control of residual proliferative progenitors (SOX1/PAX6/KI67).
- **Purity:** requires explicit on-target % and impurity caps (proliferative cells, residual iPSCs,
  early NPCs, serotonergic/cholinergic/GABAergic/glial/epithelial/endodermal contaminants) and viable
  post-thaw dose composition.

### 4.2 Function — "promising but not sufficient"
In vitro dopamine release is a key signal but not a stand-alone potency package. Asks for quantified
basal/stimulated (KCl-evoked) DA release by HPLC/LC-MS/MS with batch limits, mDA-consistent
electrophysiology/synaptic maturation, in vivo functional rescue in 6-OHDA rodents (± MPTP NHP), and
in vitro↔in vivo potency correlation. Recommends a **composite potency matrix**.

### 4.3 Safety — "no current red flag, but not safe for clinical dosing"
- Residual pluripotency below detection **reduces but does not eliminate** teratoma risk; "below
  detection" interpretable only with validated sensitivity/sampling at clinical dose.
- Requires: validated sensitive residual-iPSC assays (spike-in, LOD/LOQ, orthogonal); **long-term
  intracerebral tumorigenicity/overgrowth study** in immunodeficient mice at clinical + supratherapeutic
  doses with final lots + histology; genomic safety (karyotype/CNV/oncogenic-variant screen); GLP
  biodistribution + dose-ranging local toxicology; sterility/mycoplasma/endotoxin/adventitious agents.

### 4.4 Graft survival / integration — "not established by the provided profile"
Needs demonstrated survival of human TH+/FOXA2+/A9-like neurons after striatal grafting, axonal
outgrowth, in vivo DA release, host–graft synaptic integration, behavioral rescue, durable stability
without overgrowth/dyskinesia, under clinically relevant immunosuppression/immune-matching.

### 4.5 Manufacturing — "batch reproducibility unknown"
Flags lot-to-lot variability, scale-up/cryo/thaw/shipping/bedside effects, cell-bank/culture-duration
effects on tumorigenicity. Requires GMP xeno-free process, qualified MCB/WCB, **3–5 representative
GMP lots** meeting identical specs, in-process controls, post-thaw stability, comparability.

### 4.6 Proposed clinical release panel
Identity (FOXA2+/LMX1A+ + TH/NURR1/PITX3 at thresholds; A9 signature) · purity/impurities (on-target
min %, off-target max, KI67 limit, residual-iPSC negative by validated assay) · potency (quantitative
stimulated DA release + orthogonal maturation assay) · safety/quality (viability/dose, sterility panel,
karyotype/CNV/oncogenic profile, transport stability, delivery-compatible morphology).
**Status against release:** partially meets identity + preliminary potency, passes a *limited*
pluripotency screen; lacks validated quantitative thresholds, orthogonal tumor-risk assays, GMP
reproducibility, and in vivo safety/efficacy.

### 4.7 Stated uncertainties (agent's own)
No exact percentages/assay LOD/lot/culture-stage/dose/viability/post-thaw data; A9 identity inferred not
proven; no in vivo graft/tumor/biodistribution/immunogenicity/efficacy data for this product; unknown
manufacturing comparability.

---

## 5. Evidence base and methods (audit trail)

**Methodology:** 87 tool calls — `query_pubmed` ×16, `advanced_web_search_claude` ×3, `search_google` ×2,
`query_scholar` ×1, `query_clinicaltrials` ×1, `extract_url_content` ×1, plus 62 `run_python_repl`
(analysis/formatting). Representative literature queries: floor-plate FOXA2/LMX1A mDA specification;
Kriks engraftment; Kikuchi primate model; Doi GMP DAP preclinical package; residual-undifferentiated-cell
/ teratoma assays; FDA preclinical tumorigenicity/biodistribution guidance.

**Citations the agent relied on — VERIFY each supports the stated claim:**

| # | Citation (as given) | Used for | Verified? |
|---|---|---|:--:|
| 1 | Kriks et al., *Nature* 2011 — PMID 22056989; DOI 10.1038/nature10648 | Floor-plate hPSC mDA differentiation; in vivo survival/function; teratoma/overgrowth risk | ☐ |
| 2 | Kikuchi et al., *Nature* 2017 — PMID 28858313; DOI 10.1038/nature23664 | iPSC-DA neurons require primate-model function before clinical confidence | ☐ |
| 3 | Doi et al., *Nat Commun* 2020 — PMID 32632153; DOI 10.1038/s41467-020-17165-w | GMP DAP precedent: CORIN sort, FOXA2/TUJ1 purity, no residual iPSC, 52-wk NOG tumorigenicity, 6-OHDA efficacy | ☐ |
| 4 | Watanabe et al., *Cytotherapy* 2025 — PMID 40392167; DOI 10.1016/j.jcyt.2025.04.062 | Need sensitive residual-cell/teratoma assays beyond marker negativity | ☐ |
| 5 | Chung et al., *Cytotherapy* 2022 — PMID 35461759; DOI 10.1016/j.jcyt.2022.02.005 | iPSC-specific miRNA assay to detect rare residual undifferentiated cells | ☐ |

> Reviewer: confirm each PMID/DOI exists, matches the title/author/year, and actually supports the
> claim in the "Used for" column (the most common LLM failure mode is a plausible-but-wrong citation).

---

## 6. Automated evaluation (LLM-as-judge) — to be validated, not trusted

Judge `gpt-5.5-2026-04-23`, rubric `pdtx_cell_therapy_eval_v1`. **Final score 1.0**, decision_match =
**match** (gold = Conditional Go), schema-valid, **0 red flags**.

| Criterion (weight) | Score /5 | Judge justification (abridged) |
|---|:--:|---|
| Cell identity reasoning (0.20) | 5 | DA + floor-plate identity with A9/single-cell caveats; adds markers without overclaiming |
| Safety / tumorigenicity (0.20) | 5 | Residual pluripotency necessary-not-sufficient; LOD/spike-in/orthogonal; requires long-term in vivo tumorigenicity |
| Functional maturity (0.15) | 5 | DA release encouraging not sufficient; quantitative + electrophysiology + in vivo rescue |
| Manufacturing/reproducibility (0.15) | 5 | GMP/MCB-WCB, ≥3–5 lots, scale-up/cryo/comparability |
| Release criteria (0.15) | 5 | Comprehensive identity/purity/potency/safety panel |
| Translational decision (0.10) | 5 | Exactly the gold Conditional Go, well calibrated |
| Uncertainty handling (0.05) | 5 | Separates encouraging characterization from de-risked product; enumerates gaps |

Judge comment: *"Excellent deliverable that closely matches and expands on the gold rationale … makes
the preferred Conditional Go decision, avoids overclaiming clinical readiness … No red flags."*

> ⚠️ **Self-grading caveat:** agent and judge are the **same model** (`gpt-5.5`). This risks
> self-consistency bias; the expert score (§8) is the authoritative grade. Cross-provider judging
> (e.g. `--judge-provider anthropic`) is available to reduce this.

---

## 7. Gold reference (for calibration)

- **Preferred decision:** Conditional Go (acceptable: Go).
- **Required concepts:** DA identity (TH/NURR1/PITX3); midbrain floor-plate (FOXA2/LMX1A); residual
  pluripotency/tumorigenicity; functional dopamine release; graft survival/integration; release
  criteria; batch reproducibility.
- **Red flags (should NOT occur):** declaring clinical readiness without in vivo/tumorigenicity data;
  ignoring residual pluripotency/tumor risk; ignoring graft survival or potency/release criteria.
- **Gold rationale:** correct identity/floor-plate lineage + undetectable pluripotency + DA release are
  promising, but progression should be conditional on in vivo engraftment/survival, formal
  tumorigenicity, batch reproducibility, and defined potency/release criteria — encouraging
  characterization is not a de-risked product.

---

## 8. Expert review worksheet *(to complete)*

**A. Factual accuracy / hallucination check**
- Citations 1–5 verified (exist + support the claim)? ☐ all ✓  ☐ issues: ____________________
- Marker biology correct (TH/NURR1/PITX3, FOXA2/LMX1A, A9 markers SOX6/ALDH1A1/GIRK2)? ☐ ✓ ☐ ____
- Any fabricated assays, guidances, or numbers? ☐ none ☐ ____________________

**B. Per-criterion expert score (0–5)** — override the automated scores
| Criterion | Expert /5 | Note |
|---|:--:|---|
| Cell identity reasoning | ☐ | |
| Safety / tumorigenicity | ☐ | |
| Functional maturity | ☐ | |
| Manufacturing/reproducibility | ☐ | |
| Release criteria | ☐ | |
| Translational decision | ☐ | |
| Uncertainty handling | ☐ | |

**C. Decision** — Do you agree with **Conditional Go**? ☐ Agree ☐ Disagree → your call: ________
**D. Most important omission or error (if any):** ____________________
**E. Would you trust this as a first-pass assessment to build on?** ☐ Yes ☐ With edits ☐ No
**F. Overall expert grade (0–5): ____   Reviewer: __________   Date: __________   Specialty: __________**

---

## 9. Audit pointers

- Full structured output: `…/run_20260623_071311/result.json`
- Agent narrative: `…/reasoning.txt`
- Complete tool-by-tool trace + model responses: `…/agent.log`
- Reproduction notebook: `…/verification_notebook.ipynb`
- Methodology & scoring: `docs/pdtx_agentic_evaluation.md`, `docs/pdtx_scoring_guide.md`
- Task definition: `docs/pdtx_task_definitions.md` → `ct_ipsc_da_neurons`
