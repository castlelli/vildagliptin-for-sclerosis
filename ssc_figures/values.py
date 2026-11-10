"""Every result that the figure code states as a literal rather than loading.

These are the only exact numbers in the repository that do not come from the
private results bundle. The project page reads the same values
(src/data/figures/*.json); tests/test_values.py checks that they agree.
"""

# Network proximity of DPP4 to the four SSc gene modules (Figure 09).
# Hardcoded from the DaVinci R10 primary run: STRING functional network,
# combined score >= 700, 1,000 degree-matched permutations. Figure 09 uses
# these only where its R10 tables lack a value, and labels such rows
# "validated R10 primary fallback".
NETWORK_PROXIMITY_R10 = {
    "module_id": ["M1", "M2", "M3", "M4"],
    "z": [-0.989, -1.711, -2.101, -4.520],
    "p": [0.179, 0.02597, 0.00999, 0.000999],
    "q": [0.195, 0.03896, 0.01998, 0.002398],
}


# Fibroblast programs vs baseline mRSS in GSE181549 (Figure 12).
# Frozen outputs of the DaVinci R3 analysis: Spearman rho, and the status
# from covariate-adjusted models. Nothing is recomputed here.
MRSS_R3 = [
    {"program": "Activated\nPRSS23 / THBS1", "rho": 0.704484, "adjusted_status": "SUPPORTED"},
    {"program": "Myofibroblast", "rho": 0.691531, "adjusted_status": "SUPPORTED"},
    {"program": "ECM", "rho": 0.551557, "adjusted_status": "SUPPORTED"},
    {"program": "Progenitor", "rho": 0.438975, "adjusted_status": "DIRECTIONAL"},
    {"program": "DPP4", "rho": -0.211494, "adjusted_status": "NOT SUPPORTED"},
]


# Final evidence landscape (Figure 16). x-position in the figure is the ROLE
# of each result in the decision, not a quantitative score or ranking.
EVIDENCE_LANDSCAPE = [
    # ========================================================
    # SUPPORTING HUMAN EVIDENCE
    # ========================================================
    {
        "domain": "Human disease",
        "evidence": "Human SSc fibrotic program",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "Human SSc skin shows strong collagen and ECM remodeling.",
        "basis": "GSE58095 · differential expression · Reactome/GSEA",
    },
    {
        "domain": "Human disease",
        "evidence": "DPP4 cellular localization",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "DPP4 localizes to a fibroblast-relevant cellular compartment.",
        "basis": "GSE138669 · human skin scRNA-seq",
    },
    {
        "domain": "Human disease",
        "evidence": "Independent scRNA replication",
        "decision_role": "Supports hypothesis",
        "status": "STRONGLY SUPPORTED",
        "finding": "DPP4 associations with progenitor and ECM fibroblast programs replicate independently.",
        "basis": "GSE138669 + GSE249279",
    },
    {
        "domain": "Human disease",
        "evidence": "Fibrotic programs ↔ mRSS",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "Activated, myofibroblast and ECM programs strongly track clinical skin severity.",
        "basis": "GSE181549 · donor-level mRSS analysis",
    },
    # ========================================================
    # TARGET / MECHANISM
    # ========================================================
    {
        "domain": "Target & mechanism",
        "evidence": "Branch-aware fibroblast organization",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "DPP4-high, activated and ECM-associated organization shares a fibroblast branch.",
        "basis": "PAGA · pseudotime · donor-level occupancy",
    },
    {
        "domain": "Target & mechanism",
        "evidence": "Network proximity",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "DPP4 lies closer than expected to multiple SSc fibrotic modules.",
        "basis": "STRING v12 · degree-matched empirical null",
    },
    {
        "domain": "Target & mechanism",
        "evidence": "Functional DPP4 perturbation",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "Genetic and pharmacological DPP4 inhibition reduces fibroblast activation and fibrosis.",
        "basis": "Human dermal fibroblasts + SSc-relevant experimental models",
    },
    {
        "domain": "Target & mechanism",
        "evidence": "SSc TGFβ/SMAD environment",
        "decision_role": "Supports hypothesis",
        "status": "STRONGLY SUPPORTED",
        "finding": "Canonical TGFβ/SMAD activity is reproducibly increased in SSc fibroblasts.",
        "basis": "PROGENy · CollecTRI · two independent human cohorts",
    },
    # ========================================================
    # DRUG / PHARMACOLOGY
    # ========================================================
    {
        "domain": "Drug & pharmacology",
        "evidence": "Vildagliptin antifibrotic activity",
        "decision_role": "Supports hypothesis",
        "status": "PRECLINICAL",
        "finding": "Vildagliptin itself reduces fibrotic phenotypes in preclinical models.",
        "basis": "Functional literature · Soare et al. + independent studies",
    },
    {
        "domain": "Drug & pharmacology",
        "evidence": "Human systemic DPP4 engagement",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED",
        "finding": "Clinically achievable human exposure strongly supports systemic DPP4 inhibition.",
        "basis": "Published human PK/PD · exposure-to-potency analysis",
    },
    {
        "domain": "Drug & pharmacology",
        "evidence": "Human-anchored plasma simulation",
        "decision_role": "Supports hypothesis",
        "status": "QUANTIFIED",
        "finding": "Repeated-dose plasma exposure was modeled from clinically anchored human PK.",
        "basis": "50 mg twice daily · repeated-dose PK simulation",
    },
    {
        "domain": "Drug & pharmacology",
        "evidence": "Dermal exposure requirement",
        "decision_role": "Supports hypothesis",
        "status": "QUANTIFIED",
        "finding": "Skin/plasma exposure required for sustained dermal DPP4 inhibition was quantified.",
        "basis": "R8 dermal PK/PD sensitivity analysis",
    },
    # ========================================================
    # TRANSLATIONAL OPPORTUNITY
    # ========================================================
    {
        "domain": "Translation",
        "evidence": "Clinical development gap",
        "decision_role": "Supports hypothesis",
        "status": "SUPPORTED GAP",
        "finding": "Human SSc development was not identified among the reviewed records.",
        "basis": "PubMed · ClinicalTrials.gov · Cortellis",
    },
    # ========================================================
    # MODEL REFINEMENTS
    # ========================================================
    {
        "domain": "Model refinement",
        "evidence": "Global DPP4 expression",
        "decision_role": "Refines model",
        "status": "NOT GLOBALLY INCREASED",
        "finding": "DPP4 is not globally increased in SSc skin.",
        "basis": "GSE58095 + GSE138669 + GSE249279",
    },
    {
        "domain": "Model refinement",
        "evidence": "DPP4 as severity biomarker",
        "decision_role": "Refines model",
        "status": "NOT SUPPORTED",
        "finding": "DPP4 itself does not behave as a positive mRSS severity biomarker.",
        "basis": "GSE181549",
    },
    {
        "domain": "Model refinement",
        "evidence": "Single linear trajectory",
        "decision_role": "Refines model",
        "status": "NOT SUPPORTED",
        "finding": "A universal DPP4 → activated → myofibroblast → ECM trajectory is not supported.",
        "basis": "Pseudotime + PAGA",
    },
    {
        "domain": "Model refinement",
        "evidence": "DPP4+ canonical signaling state",
        "decision_role": "Refines model",
        "status": "DISTINCT STATE",
        "finding": "DPP4-positive fibroblasts are not the state with maximal TGFβ/MAPK/NFκB activity.",
        "basis": "PROGENy + CollecTRI · R2 + R11",
    },
    # ========================================================
    # STRESS TESTS
    # ========================================================
    {
        "domain": "Stress test",
        "evidence": "Vildagliptin LINCS reversal",
        "decision_role": "No additional support",
        "status": "NOT REPLICATED",
        "finding": "Vildagliptin did not reproducibly reverse three human SSc transcriptomic signatures.",
        "basis": "LINCS/L1000 · primary 24 h, 1.11 µM analysis",
    },
    {
        "domain": "Stress test",
        "evidence": "DPP4 KO/KD LINCS reversal",
        "decision_role": "No additional support",
        "status": "NOT REPLICATED",
        "finding": "DPP4 genetic perturbation also failed to reproducibly reverse SSc signatures.",
        "basis": "LINCS CRISPR + shRNA",
    },
    {
        "domain": "Stress test",
        "evidence": "Human genetics",
        "decision_role": "No additional support",
        "status": "NOT IDENTIFIED",
        "finding": "Direct DPP4–SSc GWAS/locus/relevant-tissue eQTL support was not identified.",
        "basis": "GWAS Catalog · GTEx · Open Targets",
    },
    # ========================================================
    # EXPERIMENTAL GATE
    # ========================================================
    {
        "domain": "Experimental gate",
        "evidence": "Human dermal PK/PD",
        "decision_role": "Requires experiment",
        "status": "DIRECTLY TESTABLE",
        "finding": "Actual vildagliptin exposure and DPP4 inhibition in human SSc skin remain unmeasured.",
        "basis": "Paired plasma/skin PK + dermal DPP4 activity",
    },
    {
        "domain": "Experimental gate",
        "evidence": "Human SSc efficacy",
        "decision_role": "Requires experiment",
        "status": "UNTESTED",
        "finding": "Therapeutic effect on skin fibrosis or mRSS has not been established.",
        "basis": "Clinical testing only after successful proof-of-mechanism",
    },
]
