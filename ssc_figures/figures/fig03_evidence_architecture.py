"""Figure 03. Evidence architecture of the study

Visual overview of the independent evidence layers used to test the repurposing hypothesis.

Link widths represent **evidence layers only** and should not be interpreted as quantitative evidence strength.
"""

import plotly.graph_objects as go


# ============================================================
# NODES
# ============================================================

labels = [
    "<b>Repurposing hypothesis</b><br>Vildagliptin → DPP4/CD26 → cutaneous SSc",
    "<b>Human disease biology</b><br>R1 · R3 · R4b",
    "<b>Cellular localization</b><br>R2 · R11",
    "<b>Fibroblast organization</b><br>R9 · R12",
    "<b>Network medicine</b><br>R4a · R10",
    "<b>Drug & pharmacology</b><br>R5 · R8",
    "<b>Translational gap</b><br>R6",
    "<b>Stress tests</b><br>R16 · R17",
    "<b>Integrated decision</b><br>Advance to proof-of-mechanism?",
]


# ============================================================
# TOOL / METHOD DETAILS FOR HOVER
# ============================================================

customdata = [
    ("Drug: vildagliptin<br>Target: DPP4/CD26<br>Disease: systemic sclerosis"),
    ("Human bulk transcriptomics<br>Clinical mRSS association<br>Reactome pathway enrichment"),
    ("Human skin single-cell RNA-seq<br>Scanpy / AnnData<br>Independent cohort replication"),
    ("PAGA / pseudotime<br>PROGENy / CollecTRI<br>Fibroblast regulatory states"),
    ("STRING v12<br>Degree-matched permutation null<br>Network proximity"),
    ("Experimental literature<br>Human PK/PD<br>Dermal exposure sensitivity model"),
    ("PubMed<br>Cortellis<br>ClinicalTrials.gov"),
    ("LINCS perturbational signatures<br>GWAS Catalog<br>GTEx / Open Targets"),
    (
        "Cross-layer synthesis<br>"
        "Supporting + contrary evidence<br>"
        "Go / no-go translational decision"
    ),
]


# ============================================================
# LINKS
# ============================================================

source = [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7]

target = [1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8, 8]

value = [1] * len(source)


# ============================================================
# FIXED LAYOUT
# ============================================================

x = [0.01, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.92]

y = [0.48, 0.04, 0.19, 0.34, 0.49, 0.64, 0.79, 0.94, 0.48]


# ============================================================
# FIGURE
# ============================================================

fig = go.Figure(
    go.Sankey(
        arrangement="fixed",
        node=dict(
            label=labels,
            customdata=customdata,
            x=x,
            y=y,
            pad=18,
            thickness=21,
            line=dict(width=0.7),
            hovertemplate=("%{label}<br><br>%{customdata}<extra></extra>"),
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            hovertemplate=("Independent evidence layer<extra></extra>"),
        ),
    )
)


fig.update_layout(
    title=dict(
        text=(
            "<b>Evidence architecture of the repurposing study</b>"
            "<br>"
            "<sup>"
            "Independent human, mechanistic, pharmacological "
            "and contrary-evidence layers"
            "</sup>"
        ),
        x=0.5,
        xanchor="center",
    ),
    font=dict(size=13),
    height=650,
    margin=dict(l=20, r=20, t=85, b=25),
)


fig.show()
