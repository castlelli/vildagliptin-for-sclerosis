"""Figure 04. Human SSc skin shows a strong fibrotic/ECM program

**Question:** Is the biological process targeted by the repurposing hypothesis present in human systemic sclerosis skin?

**Data:** GSE58095 human skin transcriptomics
**Analysis:** SSc vs control differential expression + Reactome GSEA
**Analysis tools:** Python · scipy/statsmodels · Reactome/GSEA
**Visualization:** Plotly
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display
from plotly.subplots import make_subplots

from ssc_figures.io import OUTPUT_DIR, load_tsv

# ============================================================
# LOAD DATA
# ============================================================

genes = load_tsv("R1_target_gene_case_control.tsv")
reactome = load_tsv("R4b_Reactome_GSEA_delta.tsv")

# ============================================================
# PANEL A — PRE-SPECIFIED FIBROTIC GENES
# ============================================================

genes_of_interest = [
    "DPP4",
    "COL1A1",
    "COL1A2",
    "COL3A1",
    "CTGF",
    "CTHRC1",
    "PRSS23",
    "THBS1",
    "FNDC1",
    "SFRP2",
    "SFRP4",
    "ACTA2",
    "TAGLN",
]

g = genes[genes["gene"].isin(genes_of_interest)].copy()

for col in ["delta_log_expression", "q_BH"]:
    g[col] = pd.to_numeric(g[col], errors="coerce")

g["significant"] = g["q_BH"] < 0.05

# keep the same visual order as the previous version
g["gene"] = pd.Categorical(g["gene"], categories=genes_of_interest[::-1], ordered=True)
g = g.sort_values("gene")

sig = g[g["significant"]].copy()
ns = g[~g["significant"]].copy()

# ============================================================
# PANEL B — TOP REACTOME PATHWAYS
# ============================================================

r = reactome.copy()

for col in ["NES", "FDR_q"]:
    r[col] = pd.to_numeric(r[col], errors="coerce")

r_up = (
    r[(r["direction"] == "SSc_up") & (r["FDR_q"] < 0.05)]
    .sort_values("NES", ascending=False)
    .head(10)
    .copy()
)

# reverse for top-to-bottom plotting
r_up = r_up.iloc[::-1].copy()


# shorten long pathway labels a bit
def shorten_label(x, max_len=46):
    """Truncate a label to a maximum length, appending ``"..."``.

    Parameters
    ----------
    x : object
        Label; converted to ``str``.
    max_len : int, default 46
        Maximum length of the returned string.

    Returns
    -------
    str
        The label, truncated if longer than ``max_len``.
    """
    x = str(x)
    return x if len(x) <= max_len else x[: max_len - 3] + "..."


r_up["pathway_label"] = r_up["pathway_name"].map(shorten_label)

# ============================================================
# FIGURE LAYOUT — SAME STYLE, BETTER SPACING
# ============================================================

fig = make_subplots(
    rows=1,
    cols=2,
    horizontal_spacing=0.20,
    column_widths=[0.42, 0.58],
    subplot_titles=("Fibrotic genes in SSc skin", "Top Reactome pathways increased in SSc"),
)

# ============================================================
# LEFT PANEL — GENE-LEVEL EFFECTS
# ============================================================

# significant
fig.add_trace(
    go.Scatter(
        x=sig["delta_log_expression"],
        y=sig["gene"],
        mode="markers",
        name="FDR < 0.05",
        marker=dict(size=9, color="royalblue", line=dict(width=0.6, color="royalblue")),
        hovertemplate=("<b>%{y}</b><br>SSc − control: %{x:.3f}<br><extra></extra>"),
    ),
    row=1,
    col=1,
)

# non-significant
if len(ns) > 0:
    fig.add_trace(
        go.Scatter(
            x=ns["delta_log_expression"],
            y=ns["gene"],
            mode="markers",
            name="Not significant",
            marker=dict(size=9, color="tomato", line=dict(width=0.6, color="tomato")),
            hovertemplate=("<b>%{y}</b><br>SSc − control: %{x:.3f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )

# zero line
fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)

# ============================================================
# RIGHT PANEL — PATHWAY-LEVEL ENRICHMENT
# ============================================================

fig.add_trace(
    go.Bar(
        x=r_up["NES"],
        y=r_up["pathway_label"],
        orientation="h",
        name="Reactome",
        marker=dict(color="#18c59c"),
        hovertemplate=("<b>%{y}</b><br>NES: %{x:.2f}<br><extra></extra>"),
        showlegend=True,
    ),
    row=1,
    col=2,
)

# ============================================================
# AXES
# ============================================================

fig.update_xaxes(
    title_text="SSc − control expression",
    row=1,
    col=1,
    showgrid=True,
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False,
)

fig.update_yaxes(title_text="", row=1, col=1, automargin=True)

fig.update_xaxes(
    title_text="Normalized enrichment score (NES)",
    row=1,
    col=2,
    showgrid=True,
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False,
)

fig.update_yaxes(title_text="", row=1, col=2, automargin=True)

# ============================================================
# TITLES / STYLING
# ============================================================

fig.update_layout(
    width=1450,
    height=620,
    template="plotly_white",
    title=dict(
        text=(
            "<b>Human systemic sclerosis skin is molecularly fibrotic</b>"
            "<br><sup>Patient transcriptomics independently converge on collagen and extracellular-matrix remodeling</sup>"
        ),
        x=0.5,
        xanchor="center",
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0.0),
    margin=dict(l=70, r=60, t=110, b=80),
)

# ============================================================
# SHOW
# ============================================================

fig.show()

# optional export
out_png = OUTPUT_DIR / "Figure_04_Human_SSc_fibrotic_program.png"
try:
    fig.write_image(out_png, scale=2)
    print(f"Saved figure to: {out_png}")
except Exception as e:
    print("Static export skipped:", e)

# ============================================================
# RESULT SUMMARY
# ============================================================

n_total = len(g)
n_sig_up = int(((g["delta_log_expression"] > 0) & (g["q_BH"] < 0.05)).sum())

dpp4_row = g[g["gene"] == "DPP4"]
if len(dpp4_row) == 1:
    dpp4_delta = float(dpp4_row["delta_log_expression"].iloc[0])
    dpp4_q = float(dpp4_row["q_BH"].iloc[0])
else:
    dpp4_delta = np.nan
    dpp4_q = np.nan

display(
    HTML(
        f"""
        <div style="border-left:4px solid #666; padding:12px 16px; margin-top:14px; line-height:1.6;">
        <b>Result</b><br>
        <b>{n_sig_up} of {n_total}</b> pre-specified genes are significantly increased in SSc skin, with strong convergence on collagen/ECM pathways.<br><br>
        <b>DPP4 behaves differently:</b> Δ expression = <b>{dpp4_delta:.3f}</b>, FDR = <b>{dpp4_q:.3g}</b>. It is therefore <b>not globally increased</b> in SSc skin.<br><br>
        <b>Verdict:</b> <b>HUMAN FIBROTIC DISEASE CONTEXT — SUPPORTED</b>
        </div>
        """
    )
)
