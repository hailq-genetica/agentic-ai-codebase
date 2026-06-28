#!/usr/bin/env python3
"""Generate the PD-TxBench Phase 2.5 seed dataset (small-molecule benchmark).

Phase 2.5 reuses the Phase 2 runner/judge (run_pdtx.py + src/pdtx_eval) but adds
eight small-molecule task families. This script is the single build step for the
seed slice: from the TASKS spec below it writes, for every task,

    tasks/pdtx/phase2_5/<family>/<id>.md      # the agent prompt
    tasks/pdtx/phase2_5/gold/<id>.json        # gold + rubric (schema: rubric_schema_v2 + phase2_5 fields)
    config/pdtx/phase2_5/<family>/<id>.yaml   # runnable config

and a manifest at tasks/pdtx/phase2_5/manifest.jsonl (one line per task, toward the
plan's JSONL dataset splits).

Rubric criteria are pulled from tasks/pdtx/schemas/rubric_phase2_5.json and the
deliverable required-keys from tasks/pdtx/schemas/output_schema_phase2_5.json, so
prompts, gold rubrics, and validation stay in sync. Re-run after editing TASKS.

    python scripts/build_phase2_5_seed.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "tasks" / "pdtx" / "schemas"
TASK_DIR = ROOT / "tasks" / "pdtx" / "phase2_5"
GOLD_DIR = TASK_DIR / "gold"
CONFIG_DIR = ROOT / "config" / "pdtx" / "phase2_5"

AGENT_PROVIDER = "anthropic"
AGENT_MODEL = "claude-opus-4-8"

# task_family -> rubric_id (must exist in rubric_phase2_5.json)
FAMILY_RUBRIC = {
    "target_mechanism_reasoning": "pdtx25_target_mechanism_v1",
    "evidence_verification": "pdtx25_evidence_verification_v1",
    "candidate_smiles_evaluation": "pdtx25_candidate_smiles_v1",
    "admet_cns_assessment": "pdtx25_admet_cns_v1",
    "docking_binding_interpretation": "pdtx25_docking_binding_v1",
    "lead_optimization": "pdtx25_lead_optimization_v1",
    "repurposing_translatability": "pdtx25_repurposing_v1",
    "agentic_smiles_episode": "pdtx25_agentic_episode_v1",
}

# task_family -> the decision field + allowed values stated in the prompt.
DECISION_NOTE = {
    "evidence_verification": "`claim_classification` must be one of "
    "`Supported` / `Partially Supported` / `Unsupported` / `Contradicted` / `Insufficient Evidence`.",
    "candidate_smiles_evaluation": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "admet_cns_assessment": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "docking_binding_interpretation": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "repurposing_translatability": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
    "agentic_smiles_episode": "`go_no_go` must be one of `Go` / `No-Go` / `Conditional Go`.",
}

TOOLS_PHARM = "external_pharmacology, external_database"
TOOLS_DB = "external_database"

# ---------------------------------------------------------------------------
# Task specification (seed slice). Each task -> one .md + gold + config.
# ---------------------------------------------------------------------------
TASKS = [
    # ---- Family 1: target-mechanism reasoning ----------------------------
    {
        "id": "p25_tmr_gba1_gcase",
        "family": "target_mechanism_reasoning",
        "difficulty": "easy",
        "neg": False,
        "title": "GCase enhancement in GBA1-associated Parkinson's disease",
        "intro": "Explain the therapeutic rationale for a GCase-enhancing small molecule and identify the main uncertainties.",
        "context": [
            "**Disease context:** GBA1-associated Parkinson's disease (carriers of *GBA1* variants).",
            "**Proposed target / MoA:** enhance glucocerebrosidase (GCase) activity (e.g. pharmacological chaperone or activator).",
        ],
        "job": [
            "Describe the GBA1 -> GCase -> lysosome -> alpha-synuclein axis and how the target relates to PD.",
            "State why GCase is a therapeutically relevant target and which patient subgroup it addresses.",
            "Identify the main mechanistic and evidentiary uncertainties.",
            "Be explicit that mechanistic plausibility is not proven clinical disease modification.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Mechanistically plausible target; not proven disease-modifying",
        "gold_rationale": "GBA1 encodes GCase; reduced GCase activity impairs lysosomal function and is linked to alpha-synuclein accumulation, defining a GBA1-associated PD subgroup. GCase enhancement is therefore mechanistically plausible, but clinical disease modification has not been established and must not be claimed.",
        "required_concepts": [
            "GBA1", "glucocerebrosidase", "lysosomal", "alpha-synuclein",
            "GBA1-associated subgroup", "pharmacological chaperone", "disease modification not proven",
        ],
        "acceptable_variants": [
            "GCase", "lysosome", "a-synuclein", "α-synuclein", "synuclein",
            "GBA1 carriers", "patient subgroup", "not proven", "unproven clinically",
        ],
        "red_flags": [
            "claims proven disease modification without sufficient clinical evidence",
            "confuses symptomatic effect with disease modification",
        ],
    },
    {
        "id": "p25_tmr_neg_maob_symptomatic",
        "family": "target_mechanism_reasoning",
        "difficulty": "medium",
        "neg": True,
        "title": "MAO-B inhibition: symptomatic vs disease-modifying",
        "intro": "Explain the role of MAO-B inhibition in Parkinson's disease and whether it modifies the disease course.",
        "context": [
            "**Disease context:** idiopathic Parkinson's disease, symptomatic management.",
            "**Proposed target / MoA:** small-molecule MAO-B inhibition to raise synaptic dopamine.",
        ],
        "job": [
            "Explain how MAO-B inhibition affects dopamine metabolism and symptoms.",
            "State whether the mechanism is symptomatic or disease-modifying, with justification.",
            "Identify the main uncertainties and what evidence would be needed for a disease-modification claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Symptomatic dopaminergic mechanism; not disease-modifying",
        "gold_rationale": "MAO-B inhibition reduces dopamine breakdown and gives symptomatic benefit. Trials designed to show neuroprotection/disease modification have not established it; a strong answer keeps this symptomatic and does not claim disease modification.",
        "required_concepts": [
            "MAO-B", "dopamine metabolism", "symptomatic", "not disease-modifying",
            "neuroprotection not established",
        ],
        "acceptable_variants": [
            "monoamine oxidase B", "symptomatic benefit", "dopamine breakdown",
            "disease modification not proven", "no disease modification",
        ],
        "red_flags": [
            "claims MAO-B inhibition is disease-modifying or neuroprotective",
            "confuses symptomatic effect with disease modification",
        ],
    },
    # ---- Family 2: evidence verification ---------------------------------
    {
        "id": "p25_ev_ambroxol_dmt_claim",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": False,
        "title": "Claim check: ambroxol as a disease-modifying PD therapy",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Ambroxol is a proven disease-modifying therapy for Parkinson's disease.\"",
            "**Background:** ambroxol is a GCase chaperone with mechanistic plausibility and early/biomarker clinical signals; definitive randomized disease-modification outcomes are not established (e.g. confirmatory phase 3 ongoing).",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Summarize supporting and limiting evidence and state the highest evidence level reached.",
            "State the main uncertainty and why the word 'proven' is or is not justified.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Partially Supported",
        "acceptable_decisions": ["Insufficient Evidence"],
        "gold_label": "Partially Supported — mechanistic + early clinical signals, not proven disease modification",
        "gold_rationale": "There is mechanistic plausibility and early/biomarker clinical investigation, but no definitive randomized outcome establishing disease modification. The claim of a 'proven' disease-modifying therapy is therefore only partially supported; calling it proven is an overclaim.",
        "required_concepts": [
            "GCase chaperone", "early clinical evidence", "not proven", "disease modification",
            "main uncertainty",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "biomarker evidence", "phase 3 ongoing", "no definitive RCT",
            "randomized outcome", "overclaim",
        ],
        "red_flags": [
            "treats early or biomarker clinical evidence as proven disease modification",
            "classifies the 'proven' claim as fully Supported",
        ],
    },
    {
        "id": "p25_ev_neg_caffeine_causation",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": True,
        "title": "Claim check: caffeine as a disease-modifying treatment (association vs causation)",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Because higher caffeine intake is associated with lower Parkinson's disease risk, caffeine is a disease-modifying treatment for PD.\"",
            "**Background:** the evidence is observational/epidemiological association; an interventional trial of caffeine did not show symptomatic or disease-modifying benefit.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Explain the association-versus-causation distinction and the evidence level.",
            "State what evidence would be required to support a disease-modifying treatment claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Unsupported",
        "acceptable_decisions": ["Contradicted", "Insufficient Evidence"],
        "gold_label": "Unsupported — epidemiological association does not establish a disease-modifying treatment",
        "gold_rationale": "A protective epidemiological association is not evidence of a treatment effect; causation cannot be inferred from observational association, and interventional data do not support benefit. The treatment claim is unsupported.",
        "required_concepts": [
            "association is not causation", "observational", "epidemiological",
            "interventional trial", "disease modification not supported",
        ],
        "acceptable_variants": [
            "correlation", "confounding", "no causal", "randomized trial", "no benefit",
            "reverse causation",
        ],
        "red_flags": [
            "infers causation from an observational association",
            "treats epidemiological association as clinical treatment efficacy",
        ],
    },
    # ---- Family 3: candidate SMILES evaluation ---------------------------
    {
        "id": "p25_smiles_gba1_chaperone",
        "family": "candidate_smiles_evaluation",
        "difficulty": "medium",
        "neg": False,
        "title": "Evaluate a GCase chaperone candidate for GBA1-associated PD",
        "intro": "Evaluate whether this small-molecule candidate should progress to experimental validation.",
        "context": [
            "**Disease context:** GBA1-associated Parkinson's disease.",
            "**Proposed target / MoA:** GCase pharmacological chaperone.",
        ],
        "data_block": {
            "candidate_name": "Ambroxol analog A",
            "smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Br)Br)N)O",
            "known_or_hypothetical": "analog",
        },
        "job": [
            "Assess PD relevance (GBA1 -> GCase -> lysosome -> alpha-synuclein) and MoA plausibility.",
            "Assess CNS drug-likeness and BBB penetration likelihood (this is a CNS target).",
            "Assess ADMET and safety liabilities (solubility, clearance, CYP, hERG, AMES, DILI).",
            "Give a calibrated go_no_go decision and the single most informative next experiment.",
            "Distinguish mechanistic plausibility from proven disease modification.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go — plausible chaperone, conditional on CNS exposure + ADMET clearance",
        "gold_rationale": "A GCase chaperone is mechanistically well-aligned with GBA1-associated PD. Progression should be conditional on confirming CNS/BBB exposure and clearing standard ADMET/safety liabilities; mechanistic plausibility is not proven disease modification.",
        "required_concepts": [
            "GCase", "GBA1", "lysosomal", "alpha-synuclein", "pharmacological chaperone",
            "blood-brain barrier", "ADMET", "safety liability", "next experiment",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "BBB", "blood brain barrier", "a-synuclein", "α-synuclein",
            "synuclein", "chaperone", "CNS penetration", "GCase activity assay", "target engagement",
        ],
        "red_flags": [
            "claims proven disease modification without sufficient clinical evidence",
            "ignores blood-brain barrier / CNS penetration",
            "ignores ADMET or safety liabilities",
            "treats docking/binding as proof of efficacy",
        ],
    },
    {
        "id": "p25_smiles_neg_herg_bbb",
        "family": "candidate_smiles_evaluation",
        "difficulty": "hard",
        "neg": True,
        "title": "Candidate with strong docking but poor BBB and hERG liability",
        "intro": "Evaluate whether this small-molecule candidate should progress to experimental validation.",
        "context": [
            "**Disease context:** Parkinson's disease, CNS target.",
            "**Proposed target / MoA:** CNS enzyme modulation (binding hypothesis from docking).",
        ],
        "data_block": {
            "candidate_name": "Compound H",
            "smiles": "O=C(Nc1ccc(cc1)C(F)(F)F)c1ccc2c(c1)cccc2-c1ccccc1",
            "docking": {"score_kcal_mol": -10.2, "reference_ligand_kcal_mol": -7.8},
            "admet": {"bbb": "low", "herg": "high risk", "solubility": "poor"},
        },
        "job": [
            "Assess whether the docking score justifies progression on its own.",
            "Weigh the poor predicted BBB penetration for a CNS target and the hERG liability.",
            "Give a calibrated go_no_go decision and the next experiment if any.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — strong docking cannot rescue poor CNS exposure + hERG liability",
        "gold_rationale": "A favourable docking score does not prove activity or CNS exposure. With low predicted BBB penetration for a CNS target and a hERG cardiotoxicity liability, the candidate should not progress as-is; docking must not override exposure and safety.",
        "required_concepts": [
            "docking is not proof of efficacy", "blood-brain barrier", "CNS exposure",
            "hERG", "No-Go",
        ],
        "acceptable_variants": [
            "BBB", "brain penetration", "cardiotoxicity", "hERG liability", "poor exposure",
            "binding is not engagement",
        ],
        "red_flags": [
            "recommends Go based on the docking score despite poor BBB",
            "ignores the hERG liability",
            "treats docking score as proof of efficacy",
        ],
    },
    # ---- Family 4: ADMET / CNS assessment --------------------------------
    {
        "id": "p25_admet_neg_herg_cyp",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": True,
        "title": "ADMET review of a chronic-use PD candidate with multiple liabilities",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress for chronic PD use.",
        "context": [
            "**Therapeutic context:** chronic, long-term disease-modifying therapy for Parkinson's disease (CNS target).",
        ],
        "data_block": {
            "candidate": "Compound X",
            "predicted_properties": {
                "bbb": "low",
                "caco2": "high",
                "ames": "negative",
                "herg": "high risk",
                "cyp3a4_inhibitor": "yes",
                "solubility": "poor",
            },
        },
        "job": [
            "Interpret BBB/CNS exposure for a brain target.",
            "Interpret the toxicology and PK liabilities (hERG, CYP3A4, solubility) for chronic dosing.",
            "Give a calibrated go_no_go that follows from the ADMET profile, not from target relevance alone.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go (or Conditional Go only after substantial optimization)",
        "gold_rationale": "Low BBB undermines a CNS target; hERG high risk, CYP3A4 inhibition (DDI risk), and poor solubility are serious liabilities for a chronic therapy. Target relevance does not justify a Go; the profile warrants No-Go or optimization first.",
        "required_concepts": [
            "low BBB", "CNS exposure", "hERG", "CYP3A4 drug-drug interaction", "poor solubility",
            "chronic-use safety", "No-Go",
        ],
        "acceptable_variants": [
            "blood-brain barrier", "brain penetration", "cardiotoxicity", "DDI", "CYP inhibition",
            "long-term safety", "optimization required",
        ],
        "red_flags": [
            "recommends Go on target relevance while ignoring the ADMET liabilities",
            "ignores the low BBB for a CNS target",
            "ignores the hERG liability",
            "ignores the CYP3A4 drug-drug interaction risk",
        ],
    },
    {
        "id": "p25_admet_lrrk2_balanced",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": False,
        "title": "ADMET review of a brain-penetrant LRRK2 inhibitor",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress.",
        "context": [
            "**Therapeutic context:** LRRK2 kinase inhibition for LRRK2-associated Parkinson's disease (CNS target, chronic dosing).",
        ],
        "data_block": {
            "candidate": "LRRK2-inh B",
            "predicted_properties": {
                "bbb": "moderate-high",
                "ames": "negative",
                "herg": "low risk",
                "cyp3a4_inhibitor": "no",
                "solubility": "moderate",
            },
            "class_note": "LRRK2 inhibitors as a class carry peripheral on-target concerns (e.g. lung type II pneumocyte / kidney changes).",
        },
        "job": [
            "Interpret the CNS exposure and core ADMET profile.",
            "Address the LRRK2 class peripheral on-target safety concern and a therapeutic-window strategy.",
            "Give a calibrated go_no_go with the next safety experiment.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go — clean core ADMET, conditional on managing LRRK2 peripheral safety window",
        "gold_rationale": "Core ADMET is acceptable (moderate-high BBB, AMES negative, low hERG, no CYP3A4 issue). The principal risk is the LRRK2 class peripheral on-target effect; progression is conditional on a therapeutic-window / peripheral-safety strategy.",
        "required_concepts": [
            "LRRK2", "CNS exposure", "peripheral on-target safety", "therapeutic window",
            "Conditional Go",
        ],
        "acceptable_variants": [
            "blood-brain barrier", "brain penetration", "lung safety", "type II pneumocyte",
            "kidney", "safety margin", "selectivity",
        ],
        "red_flags": [
            "ignores the LRRK2 peripheral / lung on-target safety concern",
            "overclaims disease modification from a clean ADMET profile",
        ],
    },
    # ---- Family 5: docking / binding interpretation ----------------------
    {
        "id": "p25_docking_gcase_interpretation",
        "family": "docking_binding_interpretation",
        "difficulty": "medium",
        "neg": False,
        "title": "Interpret a GCase docking result without overclaiming",
        "intro": "Interpret the docking/binding evidence for this compound and recommend a decision.",
        "context": [
            "**Target:** GCase (GBA1 product), ambroxol-like pocket.",
        ],
        "data_block": {
            "compound": "Compound Y",
            "docking_score_kcal_mol": -8.7,
            "reference_ligand_score_kcal_mol": -7.9,
            "binding_site": "ambroxol-like pocket",
            "admet_summary": "poor predicted BBB and hERG risk",
        },
        "job": [
            "State what the docking score does and does not establish relative to the reference ligand.",
            "Integrate the ADMET concerns (BBB, hERG) into the interpretation.",
            "Recommend a go_no_go and a biochemical/cellular target-engagement validation experiment.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["No-Go"],
        "gold_label": "Conditional Go — binding hypothesis only; requires target-engagement validation and ADMET fixes",
        "gold_rationale": "A docking score modestly better than the reference supports a binding hypothesis but does not prove activity, target engagement, CNS exposure, or efficacy. With poor BBB and hERG risk, progression is conditional on biochemical/cellular validation and ADMET mitigation.",
        "required_concepts": [
            "docking is not proof of efficacy", "reference ligand", "target engagement",
            "blood-brain barrier", "hERG", "validation experiment",
        ],
        "acceptable_variants": [
            "binding hypothesis", "pose quality", "BBB", "brain penetration", "cardiotoxicity",
            "GCase activity assay", "cellular assay", "biochemical assay",
        ],
        "red_flags": [
            "treats the docking score as proof of efficacy",
            "ignores the reference ligand context",
            "ignores ADMET in the interpretation",
            "claims disease modification from docking alone",
        ],
    },
    # ---- Family 6: lead optimization -------------------------------------
    {
        "id": "p25_leadopt_gcase_chaperone",
        "family": "lead_optimization",
        "difficulty": "medium",
        "neg": False,
        "title": "Optimize a GCase chaperone analog with solubility and hERG liabilities",
        "intro": "Propose a rational lead-optimization strategy for this scaffold.",
        "context": [
            "**Scaffold:** GCase pharmacological chaperone analog (CNS target).",
            "**Profile:** good predicted target binding, but poor solubility and high hERG risk.",
        ],
        "job": [
            "State the optimization goal and the liabilities to address.",
            "Propose chemistry-aware modifications, each with an explicit rationale, expected benefit, and risk.",
            "Preserve the pharmacophore and CNS penetration while fixing the liabilities.",
            "List the properties to re-check and the experimental validation step.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Rational, pharmacophore-preserving optimization addressing solubility and hERG",
        "gold_rationale": "A strong answer targets the named liabilities with justified medicinal-chemistry changes (e.g. add polarity/ionizable group to improve solubility, remove basic/lipophilic hERG-associated features) while preserving the chaperone pharmacophore and CNS penetration, then re-checks properties and validates experimentally. Arbitrary changes without rationale are penalized.",
        "required_concepts": [
            "solubility", "hERG", "preserve pharmacophore", "CNS penetration",
            "rationale for each modification", "recheck properties", "experimental validation",
        ],
        "acceptable_variants": [
            "lipophilicity", "logP", "polarity", "ionizable group", "reduce basicity",
            "blood-brain barrier", "brain penetration", "target engagement", "re-test",
        ],
        "red_flags": [
            "proposes arbitrary chemical modifications without rationale",
            "destroys CNS penetration / pharmacophore while fixing a liability",
        ],
    },
    # ---- Family 7: repurposing / translatability -------------------------
    {
        "id": "p25_repurpose_lysosomal",
        "family": "repurposing_translatability",
        "difficulty": "medium",
        "neg": False,
        "title": "Repurposing a marketed lysosomal-modulating drug for PD",
        "intro": "Evaluate whether this marketed drug is a strong repurposing candidate for Parkinson's disease.",
        "context": [
            "**Candidate:** a marketed small molecule with an established human safety/dosing record that modulates lysosomal/autophagy function.",
            "**Hypothesis:** lysosomal enhancement could be relevant to GBA1-associated / lysosomal-dysfunction PD.",
        ],
        "job": [
            "Give the repurposing rationale and mechanism match to PD.",
            "Use the existing human safety and dosing data; reason about CNS exposure at tolerated human doses.",
            "Interpret available clinical evidence and distinguish symptomatic from disease-modifying use.",
            "Propose endpoints/biomarkers and patient-subgroup selection; give a calibrated go_no_go.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go", "No-Go"],
        "gold_label": "Conditional Go — leverage human safety, conditional on CNS exposure + subgroup/biomarker strategy",
        "gold_rationale": "Repurposing benefits from existing human safety/dosing, but the case hinges on confirming CNS exposure at tolerated doses, a mechanism-matched patient subgroup (e.g. GBA1/lysosomal), and a biomarker/endpoint strategy. Disease modification must not be assumed; default is Conditional Go pending CNS-exposure and subgroup data.",
        "required_concepts": [
            "human safety data", "dosing", "CNS exposure", "mechanism match", "biomarker",
            "patient subgroup", "symptomatic vs disease-modifying",
        ],
        "acceptable_variants": [
            "tolerated dose", "blood-brain barrier", "brain penetration", "GBA1 subgroup",
            "endpoint", "drug-drug interaction", "trial design",
        ],
        "red_flags": [
            "assumes CNS exposure without data",
            "overclaims disease modification from a marketed-drug mechanism",
        ],
    },
    # ---- Family 8: agentic small-molecule episode ------------------------
    {
        "id": "p25_agentic_gba1_smiles",
        "family": "agentic_smiles_episode",
        "difficulty": "hard",
        "neg": False,
        "title": "Agentic evaluation of a new small molecule for GBA1-associated PD",
        "intro": "Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.",
        "context": [
            "**Goal:** evaluate a new small molecule as a candidate for GBA1-associated Parkinson's disease.",
            "**Proposed target / MoA:** GCase modulation.",
        ],
        "data_block": {
            "candidate_name": "Compound Z",
            "smiles": "C1CC(CCC1NCC2=C(C(=CC(=C2)Cl)Cl)N)O",
            "proposed_target": "GCase",
        },
        "job": [
            "Form a PD mechanism hypothesis for the candidate.",
            "Use tools (literature, knowledge graph, docking, ADMET, patent/novelty, clinical) and build an evidence_table integrating the findings.",
            "Assess ADMET/safety and IP/novelty risk.",
            "Give a calibrated go_no_go with decision_rationale and the next experiment.",
            "Keep the workflow auditable: record which tools were used and why.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["No-Go", "Go"],
        "gold_label": "Conditional Go — evidence-grounded, conditional on CNS exposure + ADMET/IP clearance",
        "gold_rationale": "A strong episode forms a correct GCase/GBA1 mechanism hypothesis, integrates tool/literature evidence into a table, assesses ADMET/safety and novelty/IP, and reaches a calibrated decision with a decision-relevant next experiment (e.g. GCase target-engagement assay). The default is Conditional Go pending CNS exposure and ADMET/IP clearance; no overclaiming of disease modification.",
        "required_concepts": [
            "GCase", "GBA1", "evidence table", "ADMET", "blood-brain barrier",
            "novelty or patent risk", "go_no_go", "next experiment",
        ],
        "acceptable_variants": [
            "glucocerebrosidase", "BBB", "brain penetration", "IP risk", "patent",
            "target engagement", "GCase activity assay", "tool trace",
        ],
        "red_flags": [
            "skips ADMET / CNS exposure assessment",
            "claims proven disease modification without sufficient clinical evidence",
            "reaches a decision without proposing a validation experiment",
        ],
    },

    # =====================================================================
    # Additional hand-authored, verified tasks (expansion batch).
    # Clinical-fact tasks carry source_ids and review_status="reviewed";
    # trial outcomes were verified against the cited primary sources.
    # =====================================================================

    # ---- Family 2: evidence verification (verified clinical facts) -------
    {
        "id": "p25_ev_neg_exenatide_dmt",
        "family": "evidence_verification",
        "difficulty": "hard",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["Lancet 2024 Exenatide-PD3 (S0140-6736(24)02808-3)", "Athauda et al. Lancet 2017 (phase 2)"],
        "title": "Claim check: exenatide as a disease-modifying PD therapy",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Exenatide is a proven disease-modifying therapy for Parkinson's disease.\"",
            "**Background:** exenatide is a GLP-1 receptor agonist. An encouraging phase 2 trial (2017) suggested a possible effect, but the definitive phase 3 **Exenatide-PD3** (n=194, 96 weeks; Lancet 2024) found **no difference** vs placebo (MDS-UPDRS III worsened +5.7 with exenatide vs +4.5 placebo) and no benefit on cognition, non-motor, or imaging endpoints.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Weigh the positive phase 2 against the definitive negative phase 3 and give the highest evidence level reached.",
            "State the main uncertainty and why 'proven disease-modifying' is not justified.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Contradicted",
        "acceptable_decisions": ["Unsupported"],
        "gold_label": "Contradicted — definitive phase 3 (Exenatide-PD3) was negative",
        "gold_rationale": "A definitive phase 3 RCT (Exenatide-PD3, Lancet 2024) found no disease-modifying effect, overriding the earlier positive phase 2 signal. The claim of a proven disease-modifying therapy is contradicted by the highest-quality evidence.",
        "required_concepts": [
            "GLP-1 receptor agonist", "phase 3", "Exenatide-PD3", "randomized controlled trial",
            "MDS-UPDRS", "no disease modification",
        ],
        "acceptable_variants": [
            "GLP-1", "Exenatide PD3", "negative trial", "no benefit", "definitive RCT", "placebo",
        ],
        "red_flags": [
            "cites the positive phase 2 as proof while ignoring the negative phase 3",
            "classifies the 'proven' claim as Supported",
        ],
    },
    {
        "id": "p25_ev_neg_isradipine_dmt",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["STEADY-PD III, Ann Intern Med 2020 (NCT02168842)"],
        "title": "Claim check: isradipine slows Parkinson's disease progression",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Isradipine slows Parkinson's disease progression.\"",
            "**Background:** isradipine is a dihydropyridine calcium-channel blocker; the preclinical rationale is Cav1.3-mediated calcium stress in dopamine neurons. The phase 3 **STEADY-PD III** (n=336, 36 months; Ann Intern Med 2020) showed no effect on UPDRS progression.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Distinguish the preclinical rationale from the clinical result and state the evidence level.",
            "State what the negative phase 3 implies for the claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Contradicted",
        "acceptable_decisions": ["Unsupported"],
        "gold_label": "Contradicted — phase 3 STEADY-PD III was negative",
        "gold_rationale": "Despite a plausible calcium-stress rationale, the phase 3 STEADY-PD III trial found no slowing of progression. The clinical claim is contradicted by the definitive randomized evidence.",
        "required_concepts": [
            "calcium channel blocker", "STEADY-PD III", "phase 3", "UPDRS", "no disease modification",
        ],
        "acceptable_variants": [
            "dihydropyridine", "Cav1.3", "calcium stress", "negative trial", "no benefit", "isradipine",
        ],
        "red_flags": [
            "relies on the preclinical calcium-toxicity rationale over the negative phase 3",
            "classifies the claim as Supported",
        ],
    },
    {
        "id": "p25_ev_neg_inosine_dmt",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["SURE-PD3, JAMA 2021 (NCT02642393)"],
        "title": "Claim check: urate-elevating inosine is neuroprotective in PD",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Urate-elevating inosine is neuroprotective and slows Parkinson's disease.\"",
            "**Background:** higher serum urate is epidemiologically associated with lower PD risk/progression. The phase 3 **SURE-PD3** trial (n=298; JAMA 2021) raised urate as intended but was stopped for **futility** with no clinical benefit.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Separate the epidemiological association and target engagement (urate elevation) from clinical benefit.",
            "State the evidence level and the implication of the futility result.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Contradicted",
        "acceptable_decisions": ["Unsupported"],
        "gold_label": "Contradicted — phase 3 SURE-PD3 stopped for futility",
        "gold_rationale": "Inosine elevated urate (target engagement) but produced no clinical benefit and was halted for futility in phase 3. Neither the epidemiological association nor target engagement establishes neuroprotection; the claim is contradicted.",
        "required_concepts": [
            "inosine", "urate", "SURE-PD3", "futility", "target engagement is not clinical benefit",
            "no disease modification",
        ],
        "acceptable_variants": [
            "uric acid", "antioxidant", "epidemiological association", "no benefit", "phase 3",
        ],
        "red_flags": [
            "treats the urate-PD association or urate elevation as proof of neuroprotection",
            "ignores the phase 3 futility result",
        ],
    },
    {
        "id": "p25_ev_neg_coq10_dmt",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["QE3 trial, JAMA Neurology 2014"],
        "title": "Claim check: high-dose coenzyme Q10 slows PD progression",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"High-dose coenzyme Q10 slows Parkinson's disease progression.\"",
            "**Background:** CoQ10 targets mitochondrial bioenergetics/oxidative stress. The phase 3 **QE3** trial (n=267, 1200 and 2400 mg/d; JAMA Neurology 2014) was terminated for **futility** with no evidence of benefit.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Distinguish the mitochondrial/antioxidant rationale from the clinical outcome.",
            "State the evidence level and the implication of the futility termination.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Contradicted",
        "acceptable_decisions": ["Unsupported"],
        "gold_label": "Contradicted — phase 3 QE3 terminated for futility",
        "gold_rationale": "The phase 3 QE3 trial found no benefit and was stopped for futility. A mitochondrial/antioxidant rationale does not establish clinical disease modification; the claim is contradicted.",
        "required_concepts": [
            "coenzyme Q10", "mitochondrial", "antioxidant", "QE3", "futility", "no benefit",
        ],
        "acceptable_variants": [
            "CoQ10", "oxidative stress", "bioenergetics", "phase 3", "no disease modification",
        ],
        "red_flags": [
            "treats the mitochondrial/antioxidant rationale as clinical proof",
            "classifies the claim as Supported",
        ],
    },
    {
        "id": "p25_ev_neg_deferiprone_dmt",
        "family": "evidence_verification",
        "difficulty": "hard",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["FAIRPARK-II, NEJM 2022 (NEJMoa2209254)"],
        "title": "Claim check: iron chelation (deferiprone) is disease-modifying in PD",
        "intro": "Classify the following therapeutic claim using the available evidence.",
        "context": [
            "**Claim:** \"Iron chelation with deferiprone is a disease-modifying treatment for Parkinson's disease.\"",
            "**Background:** brain iron accumulation is implicated in PD. In the phase 2/3 **FAIRPARK-II** trial (n=372, 9 months; NEJM 2022), deferiprone lowered brain iron (target engagement) but **worsened** motor outcomes — 22.0% of the deferiprone group progressed to needing levodopa vs 2.7% on placebo.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "Explain why target engagement (iron lowering) did not translate to benefit, and note the harm signal.",
            "State the evidence level and the implication for the claim.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Contradicted",
        "acceptable_decisions": ["Unsupported"],
        "gold_label": "Contradicted — FAIRPARK-II showed worsening, not benefit",
        "gold_rationale": "Deferiprone engaged its target (lowered brain iron) yet clinical outcomes worsened in a randomized trial. Target engagement is not clinical benefit; the disease-modification claim is contradicted, and the harm signal is decision-critical.",
        "required_concepts": [
            "deferiprone", "iron chelation", "FAIRPARK-II", "worsened outcomes", "harm signal",
            "target engagement is not clinical benefit", "no disease modification",
        ],
        "acceptable_variants": [
            "brain iron", "chelator", "harm", "worsening", "phase 3", "randomized trial",
        ],
        "red_flags": [
            "treats iron lowering (target engagement) as clinical benefit",
            "ignores the worsening / harm signal from the randomized trial",
        ],
    },
    {
        "id": "p25_ev_gba1_risk_supported",
        "family": "evidence_verification",
        "difficulty": "medium",
        "neg": False,
        "review_status": "reviewed",
        "sources": ["Sidransky et al. NEJM 2009 (multicenter GBA analysis)"],
        "title": "Claim check: GBA1 variants are a major genetic risk factor for PD",
        "intro": "Classify the following claim using the available evidence.",
        "context": [
            "**Claim:** \"GBA1 variants are a major genetic risk factor for Parkinson's disease.\"",
            "**Background:** a large multicenter analysis (Sidransky et al., NEJM 2009) found GBA1 mutations markedly increase PD risk (odds ratio ~5), and GBA1 is the most common known genetic risk factor for PD. Penetrance is incomplete — most carriers do not develop PD.",
        ],
        "job": [
            "Classify the claim (claim_classification).",
            "State the evidence level (human genetic association) and the effect size.",
            "State the main uncertainty (incomplete penetrance; risk factor, not deterministic cause).",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Supported",
        "acceptable_decisions": [],
        "gold_label": "Supported — strong human genetic evidence; GBA1 is the most common genetic risk factor",
        "gold_rationale": "Large human genetic studies establish GBA1 as the most common genetic risk factor for PD (OR ~5). The claim is supported, with the key caveat of incomplete penetrance — it is a risk factor, not a deterministic cause.",
        "required_concepts": [
            "GBA1", "genetic risk factor", "odds ratio", "most common genetic risk factor",
            "incomplete penetrance",
        ],
        "acceptable_variants": [
            "GBA mutation", "glucocerebrosidase", "genetic association", "risk variant", "OR ~5",
        ],
        "red_flags": [
            "conflates a risk factor with a deterministic cause / overstates penetrance",
            "classifies strong genetic evidence as merely associational / Insufficient Evidence",
        ],
    },

    # ---- Family 1: target-mechanism reasoning ----------------------------
    {
        "id": "p25_tmr_lrrk2_kinase",
        "family": "target_mechanism_reasoning",
        "difficulty": "medium",
        "neg": False,
        "title": "LRRK2 kinase inhibition rationale in Parkinson's disease",
        "intro": "Explain the therapeutic rationale for a small-molecule LRRK2 kinase inhibitor and identify the main uncertainties.",
        "context": [
            "**Disease context:** LRRK2-associated Parkinson's disease; LRRK2 G2019S is the most common known genetic cause of familial and sporadic PD.",
            "**Proposed target / MoA:** small-molecule inhibition of LRRK2 kinase activity.",
        ],
        "job": [
            "Explain how G2019S increases LRRK2 kinase activity and the downstream (e.g. Rab GTPase) consequences relevant to PD.",
            "Justify kinase inhibition as a therapeutic strategy and the relevant patient subgroup.",
            "Identify the main uncertainties, including peripheral on-target safety (e.g. lung) and whether inhibition modifies disease.",
            "Be explicit that the strategy is not proven disease-modifying.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Mechanistically grounded kinase target; peripheral safety + unproven disease modification are key uncertainties",
        "gold_rationale": "G2019S is a gain-of-function mutation that elevates LRRK2 kinase activity (increased Rab phosphorylation); inhibition is a rational strategy for LRRK2-associated (and possibly idiopathic) PD. Key uncertainties are peripheral on-target effects (lung type II pneumocytes), CNS exposure/selectivity, and the absence of proven clinical disease modification.",
        "required_concepts": [
            "LRRK2", "G2019S", "kinase activity", "kinase inhibition", "peripheral on-target safety",
            "disease modification not proven",
        ],
        "acceptable_variants": [
            "gain of function", "Rab GTPase", "Rab10", "lung", "type II pneumocyte", "selectivity",
            "brain penetration", "not proven",
        ],
        "red_flags": [
            "claims LRRK2 inhibition is proven disease-modifying",
            "ignores peripheral / lung on-target safety",
        ],
    },
    {
        "id": "p25_tmr_asyn_aggregation",
        "family": "target_mechanism_reasoning",
        "difficulty": "medium",
        "neg": False,
        "title": "Targeting alpha-synuclein aggregation with a small molecule",
        "intro": "Explain the rationale for a small-molecule alpha-synuclein aggregation inhibitor and identify the main uncertainties.",
        "context": [
            "**Disease context:** Parkinson's disease with alpha-synuclein (Lewy) pathology.",
            "**Proposed target / MoA:** small molecule that inhibits alpha-synuclein misfolding/aggregation or stabilizes non-toxic species.",
        ],
        "job": [
            "Explain the role of alpha-synuclein aggregation in PD pathology.",
            "Justify aggregation inhibition as a strategy and the challenge of defining/engaging the toxic species.",
            "Identify the main uncertainties: which species is pathogenic, demonstrating target engagement in vivo, and CNS exposure.",
            "Be explicit that the strategy is not proven disease-modifying.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Plausible disease-relevant target; toxic-species definition, target engagement, and CNS exposure are key uncertainties",
        "gold_rationale": "Alpha-synuclein aggregation is central to Lewy pathology, so small-molecule aggregation inhibition is mechanistically relevant. The major uncertainties are which conformer/oligomer is pathogenic, how to demonstrate in vivo target engagement, and achieving CNS exposure; clinical disease modification is unproven.",
        "required_concepts": [
            "alpha-synuclein", "aggregation", "Lewy pathology", "toxic species", "target engagement",
            "disease modification not proven",
        ],
        "acceptable_variants": [
            "a-synuclein", "α-synuclein", "synuclein", "oligomer", "fibril", "misfolding",
            "brain penetration", "not proven",
        ],
        "red_flags": [
            "claims aggregation inhibition is proven disease-modifying",
            "assumes a single toxic species with no uncertainty",
        ],
    },
    {
        "id": "p25_tmr_neg_antioxidant_general",
        "family": "target_mechanism_reasoning",
        "difficulty": "medium",
        "neg": True,
        "review_status": "reviewed",
        "sources": ["QE3 (CoQ10) JAMA Neurol 2014", "SURE-PD3 (inosine) JAMA 2021"],
        "title": "Mechanism overgeneralization: 'antioxidants are disease-modifying in PD'",
        "intro": "Evaluate the following mechanistic argument and identify what is wrong with it.",
        "context": [
            "**Argument:** \"Oxidative stress contributes to dopaminergic neuron death in PD, therefore any antioxidant small molecule will be disease-modifying.\"",
            "**Background:** multiple antioxidant/bioenergetic candidates with sound rationale have failed in phase 3 (e.g. coenzyme Q10 / QE3; urate-elevating inosine / SURE-PD3).",
        ],
        "job": [
            "Explain why a general mechanistic class does not guarantee clinical disease modification.",
            "Cite the relevant failed antioxidant trials as a counterexample.",
            "State what would actually be required (target engagement + a positive clinical outcome in the right population).",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Invalid overgeneralization — class-level mechanism does not imply clinical benefit; antioxidant trials failed",
        "gold_rationale": "A class-level mechanistic rationale (antioxidant) does not predict clinical benefit; specific antioxidant candidates (CoQ10, inosine) engaged their rationale yet failed in phase 3. Disease modification requires demonstrated target engagement plus a positive clinical outcome, not a mechanistic syllogism.",
        "required_concepts": [
            "oxidative stress", "antioxidant", "mechanism does not guarantee clinical benefit",
            "failed antioxidant trials", "target engagement", "not disease-modifying",
        ],
        "acceptable_variants": [
            "CoQ10", "coenzyme Q10", "inosine", "class effect", "overgeneralization", "no benefit",
        ],
        "red_flags": [
            "infers clinical disease modification from a general mechanistic class",
            "ignores the failed antioxidant trials (CoQ10 / inosine)",
        ],
    },

    # ---- Family 3: candidate SMILES evaluation ---------------------------
    {
        "id": "p25_smiles_lrrk2_inhibitor",
        "family": "candidate_smiles_evaluation",
        "difficulty": "medium",
        "neg": False,
        "review_status": "reviewed",
        "sources": ["PubChem: PF-06447475 (C17H15N5O)"],
        "title": "Evaluate a LRRK2 kinase inhibitor candidate",
        "intro": "Evaluate whether this small-molecule LRRK2 kinase inhibitor should progress to experimental validation.",
        "context": [
            "**Disease context:** LRRK2-associated Parkinson's disease (e.g. G2019S carriers).",
            "**Proposed target / MoA:** ATP-competitive LRRK2 kinase inhibition.",
        ],
        "data_block": {
            "candidate_name": "PF-06447475 (LRRK2 tool inhibitor)",
            "smiles": "C1COCCN1C2=NC=NC3=C2C(=CN3)C4=CC=CC(=C4)C#N",
            "known_or_hypothetical": "known",
        },
        "job": [
            "Assess the kinase-inhibition MoA and the importance of kinome selectivity.",
            "Assess CNS drug-likeness / BBB penetration and the LRRK2 peripheral (lung) on-target safety concern.",
            "Assess ADMET/safety liabilities and developability (this is a tool compound).",
            "Give a calibrated go_no_go and a target-engagement next experiment (e.g. pRab10 / pSer935).",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go", "No-Go"],
        "gold_label": "Conditional Go — valid MoA, conditional on selectivity, CNS exposure, peripheral safety, and developability",
        "gold_rationale": "LRRK2 kinase inhibition is a rational MoA for LRRK2-associated PD. Progression should be conditional on kinome selectivity, confirmed CNS exposure, a peripheral (lung) safety strategy, and developability (PF-06447475 is a tool compound). A pRab10 target-engagement assay is the informative next step; biochemical potency is not efficacy.",
        "required_concepts": [
            "LRRK2", "kinase inhibition", "selectivity", "blood-brain barrier",
            "peripheral on-target safety", "target engagement", "next experiment",
        ],
        "acceptable_variants": [
            "kinome selectivity", "brain penetration", "lung", "Rab10", "pRab10", "pSer935",
            "developability", "tool compound",
        ],
        "red_flags": [
            "ignores LRRK2 peripheral / lung on-target safety",
            "treats biochemical potency as proof of efficacy",
            "overclaims disease modification",
        ],
    },
    {
        "id": "p25_smiles_a2a_istradefylline",
        "family": "candidate_smiles_evaluation",
        "difficulty": "medium",
        "neg": False,
        "review_status": "reviewed",
        "sources": ["PubChem: istradefylline (C20H24N4O4)", "FDA approval 2019 (adjunct to levodopa/carbidopa)"],
        "title": "Evaluate an adenosine A2A antagonist for Parkinson's disease",
        "intro": "Evaluate this small molecule as a Parkinson's disease therapeutic and frame its therapeutic role correctly.",
        "context": [
            "**Disease context:** Parkinson's disease with motor fluctuations (OFF episodes).",
            "**Proposed target / MoA:** adenosine A2A receptor antagonism (non-dopaminergic modulation of basal-ganglia output).",
        ],
        "data_block": {
            "candidate_name": "Istradefylline (A2A antagonist, approved adjunct)",
            "smiles": "CCN1C2=C(C(=O)N(C1=O)CC)N(C(=N2)/C=C/C3=CC(=C(C=C3)OC)OC)C",
            "known_or_hypothetical": "known",
        },
        "job": [
            "Assess the A2A-antagonist MoA and how it reduces OFF time as an adjunct to levodopa.",
            "Assess CNS exposure and ADMET (note CYP3A4 metabolism and photosensitivity considerations).",
            "Critically frame the indication: symptomatic adjunct vs disease-modifying.",
            "Give a calibrated go_no_go for the symptomatic indication and a next step.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go for a symptomatic adjunct indication — not disease-modifying",
        "gold_rationale": "A2A antagonism is a validated non-dopaminergic symptomatic mechanism (approved adjunct to levodopa for OFF time). A strong answer supports a symptomatic indication while explicitly not claiming disease modification, and accounts for CYP3A4 metabolism/DDI and CNS exposure.",
        "required_concepts": [
            "adenosine A2A receptor antagonist", "symptomatic", "OFF time", "adjunct to levodopa",
            "not disease-modifying", "blood-brain barrier", "CYP3A4",
        ],
        "acceptable_variants": [
            "A2A", "istradefylline", "non-dopaminergic", "symptomatic benefit", "brain penetration",
            "drug-drug interaction",
        ],
        "red_flags": [
            "claims the A2A antagonist is disease-modifying or neuroprotective",
            "confuses symptomatic OFF-time benefit with disease modification",
        ],
    },
    {
        "id": "p25_smiles_neg_ames_genotoxic",
        "family": "candidate_smiles_evaluation",
        "difficulty": "hard",
        "neg": True,
        "title": "Candidate with a genotoxicity structural alert",
        "intro": "Evaluate whether this small-molecule candidate should progress to experimental validation.",
        "context": [
            "**Disease context:** Parkinson's disease, chronic (long-term) therapy.",
            "**Proposed target / MoA:** the proposed target is relevant to PD, but assess the molecule on its own merits.",
        ],
        "data_block": {
            "candidate_name": "Hypothetical compound N (illustrative)",
            "smiles": "O=[N+]([O-])c1ccc(cc1)CCNC(=O)C2CCNCC2",
            "note": "Contains an aromatic nitro group — a recognized structural alert.",
            "known_or_hypothetical": "hypothetical",
        },
        "job": [
            "Identify the structural alert in the molecule and the toxicology it predicts.",
            "Reason about genotoxicity/mutagenicity risk for a chronic-use therapy.",
            "Give a calibrated go_no_go; do not let target relevance override a genotoxicity liability.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — aromatic nitro structural alert predicts mutagenicity/genotoxicity",
        "gold_rationale": "An aromatic nitro group is a well-recognized structural alert for mutagenicity (AMES-positive / genotoxic risk via nitroreduction). For a chronic PD therapy this is disqualifying regardless of target relevance; the alert must be removed (No-Go as-is).",
        "required_concepts": [
            "structural alert", "nitroaromatic", "AMES", "mutagenicity", "genotoxicity",
            "chronic-use safety", "No-Go",
        ],
        "acceptable_variants": [
            "nitro group", "toxicophore", "mutagenic", "Ames positive", "nitroreduction",
        ],
        "red_flags": [
            "ignores the genotoxicity / nitroaromatic structural alert",
            "recommends Go on target relevance despite the mutagenicity liability",
        ],
    },

    # ---- Family 4: ADMET / CNS assessment --------------------------------
    {
        "id": "p25_admet_clean_go",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": False,
        "title": "ADMET review of a brain-penetrant candidate with a clean profile",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress.",
        "context": [
            "**Therapeutic context:** disease-modifying therapy for Parkinson's disease (CNS target, chronic dosing).",
        ],
        "data_block": {
            "candidate": "Compound C",
            "predicted_properties": {
                "bbb": "high",
                "ames": "negative",
                "herg": "low risk",
                "cyp3a4_inhibitor": "no",
                "solubility": "good",
                "clearance": "moderate",
            },
        },
        "job": [
            "Interpret the CNS exposure and core ADMET/safety profile.",
            "State residual risks and that in silico ADMET predictions require experimental confirmation.",
            "Give a calibrated go_no_go that follows from the profile, without overclaiming efficacy.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "Go — clean predicted ADMET profile, pending experimental confirmation",
        "gold_rationale": "High BBB, AMES negative, low hERG, no CYP3A4 issue, good solubility support progression. A strong answer still notes that in silico predictions need experimental confirmation and that a clean ADMET profile does not establish efficacy or disease modification.",
        "required_concepts": [
            "blood-brain barrier", "clean ADMET profile", "in silico predictions need confirmation",
            "Go", "no efficacy claim from ADMET",
        ],
        "acceptable_variants": [
            "brain penetration", "favorable ADMET", "experimental validation", "predicted properties",
        ],
        "red_flags": [
            "overclaims efficacy or disease modification from a clean ADMET profile",
            "treats in silico ADMET predictions as definitive",
        ],
    },
    {
        "id": "p25_admet_neg_ames_dili",
        "family": "admet_cns_assessment",
        "difficulty": "medium",
        "neg": True,
        "title": "ADMET review of a candidate with genotoxicity and hepatotoxicity risk",
        "intro": "Interpret the predicted ADMET profile and decide whether the candidate should progress for chronic PD use.",
        "context": [
            "**Therapeutic context:** chronic, long-term therapy for Parkinson's disease (CNS target).",
        ],
        "data_block": {
            "candidate": "Compound D",
            "predicted_properties": {
                "bbb": "moderate",
                "ames": "positive",
                "dili": "high",
                "herg": "low risk",
                "cyp3a4_inhibitor": "no",
                "solubility": "moderate",
            },
        },
        "job": [
            "Interpret the genotoxicity (AMES) and hepatotoxicity (DILI) signals for chronic dosing.",
            "Weigh these against the otherwise acceptable BBB/hERG/CYP profile.",
            "Give a calibrated go_no_go driven by the safety profile, not by adequate BBB.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — AMES-positive + high DILI are disqualifying for chronic use",
        "gold_rationale": "AMES positivity (genotoxicity) and high predicted DILI are serious, often disqualifying liabilities for a chronic therapy, even though BBB, hERG, and CYP are acceptable. Adequate brain penetration does not justify a Go; the profile warrants No-Go.",
        "required_concepts": [
            "AMES positive", "genotoxicity", "DILI", "hepatotoxicity", "chronic-use safety", "No-Go",
        ],
        "acceptable_variants": [
            "mutagenicity", "liver toxicity", "drug-induced liver injury", "long-term safety",
            "blood-brain barrier",
        ],
        "red_flags": [
            "ignores the AMES / genotoxicity signal",
            "ignores the DILI / hepatotoxicity risk",
            "recommends Go because BBB is adequate",
        ],
    },

    # ---- Family 5: docking / binding interpretation ----------------------
    {
        "id": "p25_docking_good_admet_engagement",
        "family": "docking_binding_interpretation",
        "difficulty": "medium",
        "neg": False,
        "title": "Interpret a strong docking result with a good ADMET profile",
        "intro": "Interpret the docking/binding evidence for this compound and recommend a decision.",
        "context": [
            "**Target:** GCase (GBA1 product).",
        ],
        "data_block": {
            "compound": "Compound E",
            "docking_score_kcal_mol": -9.1,
            "reference_ligand_score_kcal_mol": -7.9,
            "binding_site": "active-site cleft, key catalytic contacts present",
            "pose_quality": "good (consistent across replicas)",
            "admet_summary": "moderate-high BBB, low hERG, AMES negative",
        },
        "job": [
            "State what the strong docking score + good pose + good ADMET do and do not establish.",
            "Contextualize against the reference ligand.",
            "Recommend a go_no_go and a biochemical/cellular target-engagement experiment.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go — encouraging binding hypothesis + good ADMET, still requires target-engagement validation",
        "gold_rationale": "A score better than the reference with a good pose and clean ADMET strengthens the binding hypothesis and de-risks exposure/safety, but docking still does not prove target engagement or efficacy. Progression is conditional on a biochemical/cellular engagement assay (e.g. GCase activity).",
        "required_concepts": [
            "docking is not proof of target engagement", "reference ligand", "pose quality",
            "target engagement assay", "blood-brain barrier",
        ],
        "acceptable_variants": [
            "binding hypothesis", "GCase activity assay", "cellular assay", "brain penetration",
            "in vitro validation",
        ],
        "red_flags": [
            "treats a good docking score + good ADMET as proof of efficacy",
            "skips target-engagement validation",
        ],
    },
    {
        "id": "p25_docking_neg_poor_pose_decoy",
        "family": "docking_binding_interpretation",
        "difficulty": "hard",
        "neg": True,
        "title": "High docking score with an implausible pose (likely artifact)",
        "intro": "Interpret the docking/binding evidence for this compound and recommend a decision.",
        "context": [
            "**Target:** GCase (GBA1 product).",
        ],
        "data_block": {
            "compound": "Compound F",
            "docking_score_kcal_mol": -10.5,
            "reference_ligand_score_kcal_mol": -8.0,
            "binding_site": "scored outside the catalytic pocket; key catalytic contacts NOT made",
            "pose_quality": "poor / inconsistent across replicas; strained conformation",
            "chemotype_note": "matches a known promiscuous-binder / frequent-hitter scaffold",
            "admet_summary": "acceptable",
        },
        "job": [
            "Judge whether the high score is trustworthy given the pose and chemotype.",
            "Explain docking false positives (artifacts, promiscuity) vs a real binding hypothesis.",
            "Recommend a go_no_go and, if any, an orthogonal validation step.",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — high score with an implausible pose and promiscuity hallmarks is likely a docking artifact",
        "gold_rationale": "A high docking score that comes from an implausible pose (no catalytic contacts, strained/inconsistent) and a frequent-hitter chemotype is most likely a scoring artifact / false positive. The score must not drive progression; reject or require orthogonal biophysical confirmation before any further work.",
        "required_concepts": [
            "docking artifact", "false positive", "poor pose", "no key interactions",
            "promiscuous binder", "No-Go",
        ],
        "acceptable_variants": [
            "implausible pose", "frequent hitter", "scoring artifact", "non-specific binding",
            "orthogonal validation", "decoy",
        ],
        "red_flags": [
            "treats the high docking score as proof despite the implausible pose",
            "ignores the promiscuity / artifact signals",
        ],
    },

    # ---- Family 6: lead optimization -------------------------------------
    {
        "id": "p25_leadopt_cyp_metabolic",
        "family": "lead_optimization",
        "difficulty": "medium",
        "neg": False,
        "title": "Optimize a CNS lead with high CYP3A4 metabolism and DDI risk",
        "intro": "Propose a rational lead-optimization strategy for this scaffold.",
        "context": [
            "**Scaffold:** a CNS-penetrant PD lead with good target potency.",
            "**Profile:** rapid CYP3A4-mediated metabolism (high clearance, short half-life) and CYP3A4 inhibition (drug-drug-interaction risk).",
        ],
        "job": [
            "State the optimization goal and the liabilities to address.",
            "Propose chemistry-aware modifications (e.g. block the metabolic soft spot, reduce CYP3A4 affinity), each with rationale, expected benefit, and risk.",
            "Preserve target potency and CNS penetration.",
            "List the properties to re-check (clearance, CYP panel, permeability) and the experimental validation step (e.g. microsomal stability).",
        ],
        "tools": "external_pharmacology",
        "preferred_decision": "N/A",
        "acceptable_decisions": [],
        "gold_label": "Block the metabolic soft spot and reduce CYP3A4 affinity while preserving potency and CNS penetration",
        "gold_rationale": "A strong answer identifies/blocks the site of metabolism (e.g. fluorination or a metabolically stable bioisostere at the soft spot), reduces CYP3A4 affinity to lower DDI risk, and explicitly preserves target potency and CNS penetration; then re-checks clearance/CYP/permeability and validates with microsomal stability. Arbitrary changes without rationale are penalized.",
        "required_concepts": [
            "metabolic soft spot", "CYP3A4", "clearance", "drug-drug interaction", "preserve potency",
            "preserve CNS penetration", "recheck properties", "experimental validation",
        ],
        "acceptable_variants": [
            "site of metabolism", "fluorination", "bioisostere", "metabolic stability", "microsomal",
            "permeability", "half-life", "brain penetration",
        ],
        "red_flags": [
            "proposes arbitrary modifications without rationale",
            "fixes metabolism at the cost of CNS penetration or potency",
        ],
    },

    # ---- Family 7: repurposing / translatability -------------------------
    {
        "id": "p25_repurpose_neg_no_cns",
        "family": "repurposing_translatability",
        "difficulty": "medium",
        "neg": True,
        "title": "Repurposing a peripherally-restricted drug for a CNS PD mechanism",
        "intro": "Evaluate whether this marketed drug is a strong repurposing candidate for Parkinson's disease.",
        "context": [
            "**Candidate:** a marketed small molecule with an excellent human safety record whose target is mechanistically relevant to PD.",
            "**Key property:** it is peripherally restricted — a P-glycoprotein substrate with negligible brain penetration at tolerated doses.",
        ],
        "job": [
            "Give the repurposing rationale and mechanism match.",
            "Reason explicitly about CNS exposure: can it engage a brain target at tolerated human doses?",
            "Give a calibrated go_no_go; do not let the human safety record substitute for brain exposure.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — a peripherally-restricted drug cannot engage a CNS target despite a good safety record",
        "gold_rationale": "A good human safety record and mechanism match cannot overcome the fact that a P-gp-restricted, non-brain-penetrant drug will not engage a CNS target at tolerated doses. The default is No-Go (or a CNS-penetrant analog / delivery program) unless brain exposure can actually be demonstrated.",
        "required_concepts": [
            "CNS penetration", "P-glycoprotein efflux", "no brain exposure",
            "safety record is insufficient", "mechanism match", "No-Go",
        ],
        "acceptable_variants": [
            "peripherally restricted", "blood-brain barrier", "P-gp substrate", "brain exposure",
            "CNS-penetrant analog",
        ],
        "red_flags": [
            "assumes CNS exposure from the drug's peripheral safety record",
            "recommends Go without brain-exposure data",
        ],
    },
    {
        "id": "p25_repurpose_safinamide_symptomatic",
        "family": "repurposing_translatability",
        "difficulty": "medium",
        "neg": False,
        "review_status": "reviewed",
        "sources": ["PubChem: safinamide (C17H19FN2O2)", "Approved adjunct to levodopa for OFF episodes"],
        "title": "Repurposing framing for safinamide in Parkinson's disease",
        "intro": "Evaluate safinamide's role in Parkinson's disease and frame its translatability correctly.",
        "context": [
            "**Candidate:** safinamide — a reversible MAO-B inhibitor with glutamate/sodium-channel modulating activity; already approved as an adjunct to levodopa for motor fluctuations.",
            "**Question:** assess its translatability and whether it should be positioned as symptomatic or disease-modifying.",
        ],
        "data_block": {
            "candidate_name": "Safinamide",
            "smiles": "C[C@@H](C(=O)N)NCC1=CC=C(C=C1)OCC2=CC(=CC=C2)F",
            "known_or_hypothetical": "known",
        },
        "job": [
            "Give the rationale and mechanism (MAO-B + glutamatergic modulation).",
            "Use the existing human safety/dosing data and CNS exposure.",
            "Distinguish the symptomatic adjunct role from a disease-modifying claim; outline what a DMT claim would require.",
            "Give a calibrated go_no_go for the appropriate (symptomatic) positioning.",
        ],
        "tools": TOOLS_DB,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["Go"],
        "gold_label": "Conditional Go as a symptomatic adjunct — not disease-modifying without dedicated evidence",
        "gold_rationale": "Safinamide has strong human safety/dosing data, is CNS-penetrant, and works through symptomatic (dopaminergic + glutamatergic) mechanisms; it is appropriately positioned as a symptomatic adjunct. A disease-modification claim would require a dedicated trial with biomarkers and the right population; it should not be assumed.",
        "required_concepts": [
            "MAO-B inhibition", "symptomatic adjunct", "human safety data", "CNS penetration",
            "symptomatic vs disease-modifying", "not disease-modifying",
        ],
        "acceptable_variants": [
            "safinamide", "glutamate modulation", "levodopa adjunct", "dosing", "brain penetration",
        ],
        "red_flags": [
            "claims safinamide is disease-modifying",
            "confuses symptomatic adjunct benefit with neuroprotection",
        ],
    },

    # ---- Family 8: agentic small-molecule episode ------------------------
    {
        "id": "p25_agentic_lrrk2_episode",
        "family": "agentic_smiles_episode",
        "difficulty": "hard",
        "neg": False,
        "review_status": "reviewed",
        "sources": ["PubChem: PF-06447475 (C17H15N5O)"],
        "title": "Agentic evaluation of a LRRK2 inhibitor for LRRK2-associated PD",
        "intro": "Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.",
        "context": [
            "**Goal:** evaluate a LRRK2 kinase inhibitor as a candidate for LRRK2-associated Parkinson's disease.",
            "**Proposed target / MoA:** ATP-competitive LRRK2 kinase inhibition.",
        ],
        "data_block": {
            "candidate_name": "PF-06447475 (LRRK2 tool inhibitor)",
            "smiles": "C1COCCN1C2=NC=NC3=C2C(=CN3)C4=CC=CC(=C4)C#N",
            "proposed_target": "LRRK2",
        },
        "job": [
            "Form a LRRK2 kinase mechanism hypothesis for LRRK2-associated PD.",
            "Use tools (literature, knowledge graph, docking, ADMET, patent/novelty, clinical) and build an evidence_table that integrates the findings, including kinome selectivity and the peripheral (lung) safety signal.",
            "Assess ADMET/CNS exposure and IP/novelty risk.",
            "Give a calibrated go_no_go with decision_rationale and a target-engagement next experiment (e.g. pRab10).",
            "Keep the workflow auditable: record which tools were used and why.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "Conditional Go",
        "acceptable_decisions": ["No-Go", "Go"],
        "gold_label": "Conditional Go — valid MoA, conditional on selectivity, peripheral safety, and CNS exposure",
        "gold_rationale": "A strong episode forms a correct LRRK2 kinase mechanism hypothesis, integrates tool/literature evidence (kinome selectivity, pRab10 engagement biomarker, peripheral lung-safety class effect, IP), assesses ADMET/CNS exposure, and reaches a calibrated decision with a pRab10 target-engagement next experiment. Default is Conditional Go pending selectivity, peripheral safety, and CNS-exposure data; no overclaiming of disease modification.",
        "required_concepts": [
            "LRRK2", "kinase inhibition", "evidence table", "selectivity", "peripheral on-target safety",
            "blood-brain barrier", "target engagement", "go_no_go", "next experiment",
        ],
        "acceptable_variants": [
            "Rab10", "pRab10", "kinome", "lung", "IP risk", "patent", "brain penetration",
            "tool trace",
        ],
        "red_flags": [
            "skips ADMET / CNS exposure or peripheral-safety assessment",
            "claims proven disease modification without sufficient clinical evidence",
            "reaches a decision without proposing a target-engagement validation experiment",
        ],
    },
    {
        "id": "p25_agentic_neg_weak_target",
        "family": "agentic_smiles_episode",
        "difficulty": "hard",
        "neg": True,
        "title": "Agentic evaluation of a candidate with a weak target-disease link",
        "intro": "Run a full small-molecule discovery workflow for this candidate, using the available tools, and reach a decision.",
        "context": [
            "**Goal:** evaluate a small molecule proposed for Parkinson's disease.",
            "**Proposed rationale (to be checked):** the sponsor claims the target is relevant to PD, but the target-disease link is not established by PD genetics or disease biology — you must assess the strength of that link with the tools, not assume it.",
        ],
        "data_block": {
            "candidate_name": "Compound W (hypothetical)",
            "smiles": "O=C(Nc1ccccc1)c1ccc(cc1)N1CCOCC1",
            "proposed_target": "an enzyme with no established PD genetic or biological link",
        },
        "job": [
            "Use tools (literature, knowledge graph, clinical, genetics) to assess whether the target is actually linked to PD.",
            "Build an evidence_table; explicitly note the absence or weakness of supporting evidence.",
            "Do not be talked into progression by a confident-sounding but unsupported rationale.",
            "Give a calibrated go_no_go with decision_rationale and the next experiment that would resolve the key uncertainty.",
        ],
        "tools": TOOLS_PHARM,
        "preferred_decision": "No-Go",
        "acceptable_decisions": ["Conditional Go"],
        "gold_label": "No-Go — the target-disease link is weak/unsupported; do not progress on an unsupported rationale",
        "gold_rationale": "A strong episode uses the tools to test the target-disease rationale, finds it weak or absent (no PD genetics/biology), and reaches No-Go (or a low-confidence Conditional Go gated on first establishing target validity). The failure mode is being talked into progression and/or fabricating supporting evidence; absence of evidence must be reported as such.",
        "required_concepts": [
            "weak target-disease link", "evidence table", "knowledge graph", "absence of evidence",
            "target validation", "No-Go", "next experiment",
        ],
        "acceptable_variants": [
            "unsupported rationale", "no genetic link", "target validity", "low confidence",
            "literature search", "PD genetics",
        ],
        "red_flags": [
            "progresses despite a weak or unsupported target-disease link",
            "fabricates or assumes supporting evidence that the tools do not provide",
            "claims disease modification on an unvalidated target",
        ],
    },
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def _load(path):
    with open(path) as f:
        return json.load(f)


def render_prompt(task, required_keys, decision_note):
    family = task["family"]
    lines = [
        "You are a medicinal-chemistry and Parkinson's disease (PD) drug-discovery expert acting "
        "as a therapeutic-discovery assistant.",
        "",
        f"## Task: {task['title']}",
        task["intro"],
        "",
        "### Context",
    ]
    lines += [f"- {c}" for c in task["context"]]

    if task.get("data_block"):
        lines += ["", "### Provided data", "```json", json.dumps(task["data_block"], indent=2), "```"]

    lines += ["", "### Your job"]
    lines += [f"{i}. {step}" for i, step in enumerate(task["job"], 1)]

    lines += [
        "",
        "### Available tools",
        "You have programmatic tools (pharmacology: ADMET prediction, physicochemical properties, "
        "docking/binding affinity, drug-repurposing knowledge graph; databases: OpenTargets, Monarch, "
        "ClinVar, GWAS, ChEMBL/GtoPdb, clinical trials, FDA safety), literature/web search, and "
        "`run_python_repl`. Ground your assessment in evidence rather than memory where possible, and "
        "cite what you used.",
        "",
        "### Deliverable (write to the run's output directory)",
        "> **Output path:** `output_dir` is already defined in `run_python_repl` and points to your run "
        "directory. Do **not** reassign it or invent a path. Write exactly to `f\"{output_dir}/result.json\"` "
        "and `f\"{output_dir}/reasoning.txt\"`.",
        f"- **`result.json`** — a JSON object matching the `{family}` definition in "
        f"`tasks/pdtx/schemas/output_schema_phase2_5.json`. Required keys: "
        f"{', '.join('`' + k + '`' for k in required_keys)}.",
    ]
    if decision_note:
        lines[-1] = lines[-1] + f" {decision_note}"
    lines += [
        "  Generate the file programmatically (e.g. `json.dump(..., open(f\"{output_dir}/result.json\",\"w\"))`); "
        "do not hand-write it.",
        "- **`reasoning.txt`** — a ~150-word write-up of the analysis behind your answer, including how you "
        "handled uncertainty.",
        "",
    ]
    return "\n".join(lines)


def render_gold(task, rubric_catalog):
    family = task["family"]
    rubric_id = FAMILY_RUBRIC[family]
    criteria = rubric_catalog["rubrics"][rubric_id]["criteria"]
    return {
        "task_id": task["id"],
        "phase": "phase2_5",
        "category": "small_molecule",
        "task_family": family,
        "is_negative_control": task["neg"],
        "rubric_id": rubric_id,
        "gold_label": task["gold_label"],
        "preferred_decision": task["preferred_decision"],
        "acceptable_decisions": task["acceptable_decisions"],
        "gold_rationale": task["gold_rationale"],
        "required_concepts": task["required_concepts"],
        "acceptable_variants": task["acceptable_variants"],
        "red_flags": task["red_flags"],
        "rubric": {"criteria": criteria},
        "metadata": {
            "curator": "phase2_5 seed (hand-authored)",
            "review_status": task.get("review_status", "draft"),
            "source_ids": task.get("sources", []),
        },
    }


def render_config(task):
    family = task["family"]
    tid = task["id"]
    return (
        f"task_file: tasks/pdtx/phase2_5/{family}/{tid}.md\n"
        f"gold_file: tasks/pdtx/phase2_5/gold/{tid}.json\n"
        f"category: small_molecule\n"
        f"task_family: {family}\n"
        f"tool_category: {task['tools']}\n"
        f"reasoning_effort: high\n"
        f"interactive: false        # overridden by run_pdtx.py --mode\n"
        f"capture_telemetry: true\n"
        f"output_base_dir: output/pdtx/phase2_5/{family}/{tid}/\n"
        f"\n"
        f"llm:\n"
        f"  provider: {AGENT_PROVIDER}\n"
        f"  model: {AGENT_MODEL}\n"
        f"logging:\n"
        f"  enabled: false          # set true (+ project/entity) to log to W&B/Weave\n"
    )


def main():
    rubric_catalog = _load(SCHEMA_DIR / "rubric_phase2_5.json")
    output_schema = _load(SCHEMA_DIR / "output_schema_phase2_5.json")

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    manifest_lines = []
    seen = set()

    for task in TASKS:
        tid, family = task["id"], task["family"]
        if tid in seen:
            raise ValueError(f"duplicate task_id: {tid}")
        seen.add(tid)
        if family not in FAMILY_RUBRIC:
            raise ValueError(f"{tid}: unknown family {family}")
        required_keys = output_schema["definitions"][family]["required"]

        (TASK_DIR / family).mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / family).mkdir(parents=True, exist_ok=True)

        (TASK_DIR / family / f"{tid}.md").write_text(
            render_prompt(task, required_keys, DECISION_NOTE.get(family, ""))
        )
        (GOLD_DIR / f"{tid}.json").write_text(
            json.dumps(render_gold(task, rubric_catalog), indent=2) + "\n"
        )
        (CONFIG_DIR / family / f"{tid}.yaml").write_text(render_config(task))

        manifest_lines.append(json.dumps({
            "task_id": tid,
            "phase": "phase2_5",
            "category": "small_molecule",
            "task_family": family,
            "difficulty": task["difficulty"],
            "is_negative_control": task["neg"],
            "review_status": task.get("review_status", "draft"),
            "preferred_decision": task["preferred_decision"],
            "task_file": f"tasks/pdtx/phase2_5/{family}/{tid}.md",
            "gold_file": f"tasks/pdtx/phase2_5/gold/{tid}.json",
            "config_file": f"config/pdtx/phase2_5/{family}/{tid}.yaml",
        }))

    (TASK_DIR / "manifest.jsonl").write_text("\n".join(manifest_lines) + "\n")

    n_neg = sum(1 for t in TASKS if t["neg"])
    families = sorted({t["family"] for t in TASKS})
    print(f"Wrote {len(TASKS)} Phase 2.5 seed tasks ({n_neg} negative controls) "
          f"across {len(families)} families:")
    for fam in families:
        ids = [t["id"] for t in TASKS if t["family"] == fam]
        print(f"  - {fam}: {len(ids)} ({', '.join(ids)})")
    print(f"Manifest: {TASK_DIR / 'manifest.jsonl'}")


if __name__ == "__main__":
    main()
