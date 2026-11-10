"""Figure 16. Integrated evidence and final translational decision

**Decision question:** Does the complete evidence package justify advancing vildagliptin for cutaneous systemic sclerosis?

**Evidence integration:** human transcriptomics · independent single-cell replication · fibroblast-state biology · network medicine · human PK/PD · functional perturbation · clinical relevance · translational precedent
**Stress tests:** LINCS perturbational transcriptomics · human genetics
**Decision level:** disease-relevant proof-of-mechanism — **not clinical efficacy**
**Visualization:** interactive evidence landscape · Plotly
"""

from ssc_figures.io import OUTPUT_DIR

import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from IPython.display import display, HTML


# ============================================================
# FINAL EVIDENCE LANDSCAPE
#
# x-position indicates the ROLE of each result in the decision.
# It is NOT a quantitative score or ranking.
# ============================================================

evidence = [
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


df = pd.DataFrame(evidence)


# ============================================================
# DECISION AXIS
#
# Categorical only — NOT an evidence-strength scale.
# ============================================================

ROLE_ORDER = [
    "Supports hypothesis",
    "Refines model",
    "No additional support",
    "Requires experiment",
]

ROLE_X = {role: i for i, role in enumerate(ROLE_ORDER)}


df["x"] = df["decision_role"].map(ROLE_X)


# ============================================================
# ROW ORDER
# ============================================================

DOMAIN_ORDER = [
    "Human disease",
    "Target & mechanism",
    "Drug & pharmacology",
    "Translation",
    "Model refinement",
    "Stress test",
    "Experimental gate",
]


df["domain"] = pd.Categorical(df["domain"], categories=DOMAIN_ORDER, ordered=True)


df = df.sort_values(["domain", "evidence"], ascending=[True, True]).reset_index(drop=True)


# Reverse so first item appears at top
df["y"] = len(df) - 1 - df.index


# ============================================================
# DOMAIN COLORS
#
# Color = independent evidence domain
# Position = decision role
# ============================================================

DOMAIN_COLORS = {
    "Human disease": "#3572B8",
    "Target & mechanism": "#2E8B57",
    "Drug & pharmacology": "#E69F00",
    "Translation": "#8064A2",
    "Model refinement": "#D28A2D",
    "Stress test": "#B85450",
    "Experimental gate": "#9B684A",
}


# ============================================================
# FIGURE
# ============================================================

fig = go.Figure()


for domain in DOMAIN_ORDER:
    sub = df[df["domain"] == domain]

    if len(sub) == 0:
        continue

    fig.add_trace(
        go.Scatter(
            x=sub["x"],
            y=sub["y"],
            mode="markers",
            name=domain,
            marker=dict(size=15, color=DOMAIN_COLORS[domain], line=dict(color="white", width=1.2)),
            customdata=sub[["evidence", "status", "finding", "basis", "decision_role"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br><br>"
                "<b>Role:</b> %{customdata[4]}"
                "<br>"
                "<b>Status:</b> %{customdata[1]}"
                "<br><br>"
                "<b>Finding:</b><br>%{customdata[2]}"
                "<br><br>"
                "<b>Evidence / tool:</b><br>%{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )


# ============================================================
# Y LABELS
# ============================================================

tickvals = df["y"].tolist()

ticktext = df["evidence"].tolist()


# ============================================================
# DOMAIN SEPARATORS
# ============================================================

shapes = []


for i in range(len(df) - 1):
    current_domain = str(df.loc[i, "domain"])

    next_domain = str(df.loc[i + 1, "domain"])

    if current_domain != next_domain:
        separator_y = df.loc[i, "y"] - 0.5

        shapes.append(
            dict(
                type="line",
                x0=-0.45,
                x1=3.45,
                y0=separator_y,
                y1=separator_y,
                line=dict(color="#D9DEE3", width=1),
            )
        )


# ============================================================
# DECISION REGION BACKGROUNDS
# ============================================================

ROLE_BACKGROUNDS = ["#F0F8F3", "#FFF7E8", "#FCF0EF", "#F8F1EB"]


for i, color in enumerate(ROLE_BACKGROUNDS):
    shapes.append(
        dict(
            type="rect",
            x0=i - 0.42,
            x1=i + 0.42,
            y0=-0.8,
            y1=len(df) - 0.2,
            fillcolor=color,
            opacity=0.50,
            line=dict(width=0),
            layer="below",
        )
    )


# ============================================================
# LAYOUT
# ============================================================

fig.update_layout(
    title=dict(
        text=(
            "<b>Integrated evidence landscape</b>"
            "<br>"
            "<sup>"
            "Position indicates the role of each result in the decision — "
            "not quantitative evidence strength"
            "</sup>"
        ),
        x=0.5,
        xanchor="center",
    ),
    height=680,
    margin=dict(l=260, r=35, t=90, b=85),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(size=12, color="#18212B"),
    xaxis=dict(
        tickmode="array",
        tickvals=[0, 1, 2, 3],
        ticktext=[
            "<b>SUPPORTS<br>HYPOTHESIS</b>",
            "<b>REFINES<br>MODEL</b>",
            "<b>NO ADDITIONAL<br>SUPPORT</b>",
            "<b>REQUIRES<br>EXPERIMENT</b>",
        ],
        range=[-0.48, 3.48],
        side="top",
        tickfont=dict(size=11),
        showgrid=False,
        zeroline=False,
        fixedrange=True,
    ),
    yaxis=dict(
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        tickfont=dict(size=10),
        showgrid=False,
        zeroline=False,
        fixedrange=True,
    ),
    legend=dict(orientation="h", y=-0.10, x=0.5, xanchor="center", title=None, font=dict(size=10)),
    shapes=shapes,
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
)


fig.show()


# ============================================================
# SAVE INTERACTIVE FIGURE
# ============================================================

OUTPUT_HTML = Path(OUTPUT_DIR / "Figure_16_integrated_evidence_landscape.html")


fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn")


# ============================================================
# FINAL DECISION CARD
# ============================================================

display(
    HTML(
        """
        <div style="
            border:2px solid #2E8B57;
            background:#F1F8F4;
            border-radius:12px;
            padding:17px 22px;
            margin-top:10px;
            text-align:center;
        ">

        <div style="
            font-size:12px;
            font-weight:700;
            color:#2E8B57;
            letter-spacing:0.7px;
        ">
        FINAL TRANSLATIONAL DECISION
        </div>

        <div style="
            font-size:22px;
            font-weight:800;
            margin-top:5px;
            color:#18212B;
        ">
        ADVANCE TO DISEASE-RELEVANT PROOF-OF-MECHANISM
        </div>

        <div style="
            max-width:1000px;
            margin:9px auto 0 auto;
            font-size:14px;
            line-height:1.5;
            color:#4F5B66;
        ">

        Independent human disease biology, fibroblast-state replication,
        network medicine, functional DPP4 perturbation and human
        pharmacology converge on a testable repurposing opportunity.

        <br><br>

        The critical remaining gate is
        <b>human dermal DPP4 target engagement and suppression of
        disease-relevant fibroblast fibrotic activity</b>.

        </div>

        <div style="
            margin-top:10px;
            color:#A34D47;
            font-size:13px;
            font-weight:700;
        ">
        This is not a clinical efficacy claim.
        </div>

        </div>
        """
    )
)


# ============================================================
# CONCISE FINAL CONCLUSION
# ============================================================

display(
    HTML(
        """
        <div style="
            border-left:4px solid #666;
            padding:14px 18px;
            margin-top:14px;
            line-height:1.55;
        ">

        <b>Integrated conclusion</b><br>

        The evidence supports a
        <b>mechanistically grounded and pharmacologically plausible
        opportunity to test vildagliptin for cutaneous fibrosis in
        systemic sclerosis</b>.

        <br><br>

        Human SSc datasets define a reproducible fibroblast/ECM context
        for DPP4, downstream fibrotic programs track mRSS, experimental
        perturbation provides causal antifibrotic support, and human
        pharmacology supports systemic target engagement.

        <br><br>

        The analyses also refine the original model:
        DPP4 is not globally increased, is not a positive severity
        biomarker, and does not define a simple linear fibroblast
        trajectory or the state with maximal canonical TGFβ signaling.

        <br><br>

        LINCS reversal and human genetics did not add independent
        positive support and are retained as explicit limitations.

        <br><br>

        Human dermal pharmacology has been
        <b>partially de-risked</b>:
        the required skin exposure has been quantified, but actual
        dermal exposure and DPP4 target engagement remain to be measured.

        <br><br>

        <b>
        The project therefore advances from computational/mechanistic
        validation to disease-relevant experimental proof-of-mechanism.
        </b>

        </div>
        """
    )
)


print("\nInteractive evidence landscape saved to:")

print(OUTPUT_HTML)
