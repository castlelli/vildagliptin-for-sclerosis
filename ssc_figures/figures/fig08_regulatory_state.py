"""Figure 08. DPP4-positive fibroblasts occupy a distinct regulatory state

**Question:** Is the DPP4-positive fibroblast state the one with maximal canonical profibrotic signaling?

**Data:** GSE138669 + GSE249279 human skin fibroblast pseudobulk
**Analysis:** pathway and transcription-factor activity inference
**Analysis tools:** decoupler · PROGENy · CollecTRI · ULM · paired donor-level comparison
**Replication:** two independent human SSc single-cell cohorts
**Visualization:** Matplotlib

**How to read the figure:** color and symbol identify the independent human cohort; filled markers indicate q < 0.05; open markers indicate q ≥ 0.05. In Panel A, horizontal lines represent 95% confidence intervals.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from ssc_figures.io import OUTPUT_DIR, load_tsv

# ============================================================
# LOAD RESULTS
# ============================================================

disease = load_tsv("R12_disease_regulatory_activity.tsv")

replication = load_tsv("R12_cross_cohort_replication.tsv")


# ============================================================
# COLUMN HELPERS
# ============================================================


def first_existing(df, candidates):
    """Return the first candidate column present in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Table to search.
    candidates : list of str
        Column names in order of preference.

    Returns
    -------
    str
        The first name in ``candidates`` that is a column of ``df``.

    Raises
    ------
    KeyError
        If none of the candidates is present.
    """

    for column in candidates:
        if column in df.columns:
            return column

    raise KeyError("Missing expected columns: " + ", ".join(candidates))


disease_effect_col = first_existing(disease, ["beta_SSc", "beta_SSc_SD", "beta", "effect"])

disease_ci_low_col = first_existing(disease, ["CI_low", "ci_low"])

disease_ci_high_col = first_existing(disease, ["CI_high", "ci_high"])

disease_q_col = first_existing(disease, ["q_BH", "q", "FDR"])


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for column in [disease_effect_col, disease_ci_low_col, disease_ci_high_col, disease_q_col]:
    disease[column] = pd.to_numeric(disease[column], errors="coerce")


for column in ["R2_mean_delta", "R11_mean_delta", "R2_q", "R11_q", "meta_q"]:
    if column in replication.columns:
        replication[column] = pd.to_numeric(replication[column], errors="coerce")


# ============================================================
# PANEL A DATA
# Disease-wide TGFβ / SMAD activity
# ============================================================

targets = ["TGFb", "SMAD2", "SMAD3", "SMAD4"]


d = disease[disease["regulator"].isin(targets)].copy()


# ============================================================
# PANEL B DATA
# DPP4+ vs DPP4− regulatory activity
# ============================================================

pathways = ["TGFb", "MAPK", "NFkB", "JAK-STAT", "PI3K"]


r = replication[
    (replication["family"] == "Pathway") & (replication["regulator"].isin(pathways))
].copy()


# ============================================================
# DISPLAY LABELS
# ============================================================

COHORTS = {
    "R2": {"label": "GSE138669", "color": "#2563EB", "marker": "o"},
    "R11": {"label": "GSE249279", "color": "#F97316", "marker": "s"},
}


REGULATOR_LABELS = {
    "TGFb": "TGFβ",
    "SMAD2": "SMAD2",
    "SMAD3": "SMAD3",
    "SMAD4": "SMAD4",
    "MAPK": "MAPK",
    "NFkB": "NFκB",
    "JAK-STAT": "JAK–STAT",
    "PI3K": "PI3K",
}


# ============================================================
# BIOLOGICAL ORDER
# ============================================================

reg_order_A = ["TGFb", "SMAD2", "SMAD3", "SMAD4"]


pathway_order_B = ["TGFb", "MAPK", "NFkB", "JAK-STAT", "PI3K"]


# ============================================================
# FIGURE LAYOUT
#
# Dedicated rows:
#   1 = title / subtitle
#   2 = plots
#   3 = legend / interpretation
# ============================================================

fig = plt.figure(figsize=(14.8, 7.8), dpi=180, facecolor="white")


gs = GridSpec(
    nrows=3,
    ncols=2,
    figure=fig,
    height_ratios=[0.13, 0.73, 0.14],
    width_ratios=[1, 1],
    hspace=0.27,
    wspace=0.38,
)


ax_header = fig.add_subplot(gs[0, :])

ax1 = fig.add_subplot(gs[1, 0])

ax2 = fig.add_subplot(gs[1, 1])

ax_footer = fig.add_subplot(gs[2, :])


ax_header.axis("off")

ax_footer.axis("off")


# ============================================================
# HEADER
# ============================================================

ax_header.text(
    0.5,
    0.72,
    "DPP4-positive fibroblasts occupy a distinct regulatory state",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold",
    color="#172033",
)


ax_header.text(
    0.5,
    0.27,
    (
        "Two independent human cohorts replicate disease-wide TGFβ/SMAD activation, "
        "but DPP4-positive fibroblasts show a distinct signaling profile"
    ),
    ha="center",
    va="center",
    fontsize=11.2,
    color="#64748B",
)


# ============================================================
# PANEL A
# Is the SSc fibroblast environment TGFβ / SMAD active?
# ============================================================

y_base_A = {regulator: len(reg_order_A) - 1 - i for i, regulator in enumerate(reg_order_A)}


cohort_offset = {"R2": +0.09, "R11": -0.09}


for cohort in ["R2", "R11"]:
    sub = d[d["cohort"].astype(str) == cohort].copy()

    for _, row in sub.iterrows():
        regulator = str(row["regulator"])

        if regulator not in y_base_A:
            continue

        effect = float(row[disease_effect_col])

        ci_low = float(row[disease_ci_low_col])

        ci_high = float(row[disease_ci_high_col])

        q = float(row[disease_q_col])

        significant = q < 0.05

        y = y_base_A[regulator] + cohort_offset[cohort]

        color = COHORTS[cohort]["color"]

        marker = COHORTS[cohort]["marker"]

        ax1.errorbar(
            effect,
            y,
            xerr=np.array([[effect - ci_low], [ci_high - effect]]),
            fmt=marker,
            markersize=7.5,
            markerfacecolor=(color if significant else "white"),
            markeredgecolor=color,
            markeredgewidth=1.5,
            ecolor=color,
            elinewidth=1.35,
            capsize=0,
            alpha=(1.0 if significant else 0.55),
            zorder=3,
        )


ax1.axvline(0, linestyle="--", linewidth=1.1, color="#94A3B8")


ax1.set_yticks([y_base_A[regulator] for regulator in reg_order_A])


ax1.set_yticklabels([REGULATOR_LABELS[regulator] for regulator in reg_order_A], fontsize=11)


ax1.set_xlabel("SSc − control inferred activity", fontsize=10.5, labelpad=8)


ax1.set_title(
    "A  Is the SSc fibroblast environment TGFβ/SMAD-active?",
    loc="left",
    fontsize=12.5,
    fontweight="bold",
    pad=18,
)


ax1.text(
    0.0,
    1.015,
    "Right of zero = higher inferred activity in SSc",
    transform=ax1.transAxes,
    fontsize=9.2,
    color="#64748B",
    ha="left",
    va="bottom",
)


ax1.grid(axis="x", alpha=0.15)


ax1.set_axisbelow(True)


ax1.spines["top"].set_visible(False)


ax1.spines["right"].set_visible(False)


# ============================================================
# PANEL B
# Is DPP4+ the state with maximal canonical signaling?
# ============================================================

y_base_B = {pathway: len(pathway_order_B) - 1 - i for i, pathway in enumerate(pathway_order_B)}


for _, row in r.iterrows():
    pathway = str(row["regulator"])

    if pathway not in y_base_B:
        continue

    y0 = y_base_B[pathway]

    x_r2 = float(row["R2_mean_delta"])

    x_r11 = float(row["R11_mean_delta"])

    # --------------------------------------------------------
    # Connector:
    # same pathway estimated in both independent cohorts
    # --------------------------------------------------------

    ax2.plot([x_r2, x_r11], [y0 + 0.09, y0 - 0.09], color="#CBD5E1", linewidth=1.5, zorder=1)

    for cohort, x, q_col, y_offset in [("R2", x_r2, "R2_q", +0.09), ("R11", x_r11, "R11_q", -0.09)]:
        q = float(row[q_col])

        significant = q < 0.05

        color = COHORTS[cohort]["color"]

        marker = COHORTS[cohort]["marker"]

        ax2.scatter(
            x,
            y0 + y_offset,
            s=62,
            marker=marker,
            facecolor=(color if significant else "white"),
            edgecolor=color,
            linewidth=1.5,
            alpha=(1.0 if significant else 0.60),
            zorder=4,
        )


ax2.axvline(0, linestyle="--", linewidth=1.1, color="#94A3B8")


ax2.set_yticks([y_base_B[pathway] for pathway in pathway_order_B])


ax2.set_yticklabels([REGULATOR_LABELS[pathway] for pathway in pathway_order_B], fontsize=11)


# ============================================================
# SYMMETRIC X-AXIS
# ============================================================

all_values = np.concatenate(
    [r["R2_mean_delta"].dropna().values, r["R11_mean_delta"].dropna().values]
)


absmax = max(np.abs(all_values).max(), 0.6)


ax2.set_xlim(-absmax * 1.22, absmax * 1.22)


ax2.set_xlabel("DPP4+ − DPP4− inferred activity", fontsize=10.5, labelpad=8)


ax2.set_title(
    "B  Is DPP4+ the state with maximal canonical signaling?",
    loc="left",
    fontsize=12.5,
    fontweight="bold",
    pad=18,
)


# ============================================================
# DIRECTION LABELS
# ============================================================

ax2.text(
    0.01,
    1.015,
    "← lower in DPP4+",
    transform=ax2.transAxes,
    fontsize=9.2,
    color="#64748B",
    ha="left",
    va="bottom",
)


ax2.text(
    0.99,
    1.015,
    "higher in DPP4+ →",
    transform=ax2.transAxes,
    fontsize=9.2,
    color="#64748B",
    ha="right",
    va="bottom",
)


ax2.grid(axis="x", alpha=0.15)


ax2.set_axisbelow(True)


ax2.spines["top"].set_visible(False)


ax2.spines["right"].set_visible(False)


# ============================================================
# LEGEND
# ============================================================

cohort_legend = [
    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="None",
        markerfacecolor=COHORTS["R2"]["color"],
        markeredgecolor=COHORTS["R2"]["color"],
        markersize=8,
        label="GSE138669",
    ),
    Line2D(
        [0],
        [0],
        marker="s",
        linestyle="None",
        markerfacecolor=COHORTS["R11"]["color"],
        markeredgecolor=COHORTS["R11"]["color"],
        markersize=8,
        label="GSE249279",
    ),
]


# ============================================================
# FOOTER — HOW TO READ
# ============================================================

ax_footer.text(
    0.5,
    0.79,
    (
        "How to read: color + symbol = independent human cohort  ·  "
        "filled marker = q < 0.05  ·  open marker = q ≥ 0.05  ·  "
        "Panel A horizontal line = 95% CI"
    ),
    ha="center",
    va="center",
    fontsize=9.4,
    color="#475569",
)


ax_footer.legend(
    handles=cohort_legend,
    loc="center",
    bbox_to_anchor=(0.5, 0.50),
    ncol=2,
    frameon=False,
    fontsize=10,
    columnspacing=2.5,
)


ax_footer.text(
    0.5,
    0.16,
    (
        "Take-home: SSc-wide TGFβ/SMAD activation is replicated, "
        "but DPP4-positive fibroblasts represent a distinct regulatory state "
        "rather than the state with maximal canonical TGFβ signaling."
    ),
    ha="center",
    va="center",
    fontsize=10.6,
    fontweight="bold",
    color="#172033",
)


# ============================================================
# FINAL SPACING
# ============================================================

fig.subplots_adjust(left=0.10, right=0.98, top=0.97, bottom=0.04)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_08_DPP4_regulatory_state_explained.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight", facecolor="white")


plt.show()


# ============================================================
# RESULT HELPERS
# ============================================================


def get_row(regulator):
    """Return the cross-cohort replication row for one regulator.

    Reads the module-level table ``r`` built in this cell.

    Parameters
    ----------
    regulator : str
        Regulator/pathway name, e.g. ``"TGFb"``.

    Returns
    -------
    pandas.Series or None
        The first matching row, or ``None`` if absent.
    """

    x = r[r["regulator"].astype(str) == regulator]

    if len(x) == 0:
        return None

    return x.iloc[0]


def fmt_pair(row):
    """Format DPP4+ minus DPP4- activity for both cohorts.

    Parameters
    ----------
    row : pandas.Series or None
        Row with ``R2_mean_delta`` and ``R11_mean_delta`` columns.

    Returns
    -------
    str
        ``"GSE138669 <x>; GSE249279 <y>"``, or ``"NA"`` if ``row`` is None.
    """

    if row is None:
        return "NA"

    return f"GSE138669 {row['R2_mean_delta']:.2f}; GSE249279 {row['R11_mean_delta']:.2f}"


tgfb = get_row("TGFb")

mapk = get_row("MAPK")

nfkb = get_row("NFkB")

jakstat = get_row("JAK-STAT")

pi3k = get_row("PI3K")


# ============================================================
# INTERPRETATION
# ============================================================

display(
    HTML(
        f"""
        <div style="
            border-left:4px solid #666;
            padding:13px 17px;
            margin-top:10px;
            line-height:1.52;
        ">

        <b>Result</b><br>

        Two independent human single-cell cohorts show a
        <b>replicated disease-wide TGFβ/SMAD regulatory environment</b>
        in systemic sclerosis fibroblasts.

        <br><br>

        However, DPP4-positive fibroblasts are <b>not</b> the state with
        maximal canonical profibrotic signaling.

        Relative to DPP4-negative fibroblasts:

        <ul style="
            margin-top:7px;
            margin-bottom:7px;
        ">

          <li>
            TGFβ is lower:
            <b>{fmt_pair(tgfb)}</b>
          </li>

          <li>
            MAPK is lower:
            <b>{fmt_pair(mapk)}</b>
          </li>

          <li>
            NFκB is lower:
            <b>{fmt_pair(nfkb)}</b>
          </li>

          <li>
            JAK-STAT is lower:
            <b>{fmt_pair(jakstat)}</b>
          </li>

          <li>
            PI3K is higher:
            <b>{fmt_pair(pi3k)}</b>
          </li>

        </ul>

        <b>Interpretation:</b><br>

        The two independent cohorts replicate the same overall direction:
        DPP4 identifies a <b>distinct progenitor/ECM-associated fibroblast
        regulatory state</b>, rather than simply marking the fibroblast
        population with maximal canonical TGFβ/SMAD activity.

        <br><br>

        This is an <b>observational state comparison</b>.
        It does not contradict experimental studies showing that
        pharmacological or genetic perturbation of DPP4 can modulate
        profibrotic signaling.

        <br><br>

        <b>Verdict:</b><br>

        SSc-WIDE TGFβ/SMAD ACTIVATION —
        <b>STRONGLY SUPPORTED</b><br>

        DPP4+ = MAXIMAL CANONICAL TGFβ STATE —
        <b>CONTRADICTED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
