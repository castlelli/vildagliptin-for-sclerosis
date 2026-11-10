"""Figure 06. Independent human scRNA-seq replicates a state-linked DPP4 model

**Question:** Within the fibroblast compartment, how does SSc alter fibroblast states, and which states remain associated with DPP4-positive fibroblasts?

**Data:** GSE249279 independent human skin single-cell RNA-seq
**Analysis:** donor-level fibroblast state scoring + robust regression
**Analysis tools:** Python · Scanpy · AnnData · statsmodels
**Visualization:** Matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ============================================================
# BUILD FIGURE — PITCH-OPTIMIZED LAYOUT
# ============================================================
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

from ssc_figures.io import OUTPUT_DIR

fig = plt.figure(figsize=(15.5, 8.6), facecolor="white")

# ------------------------------------------------------------
# Dedicated rows:
#   1 = title/subtitle
#   2 = actual plots
#   3 = interpretation + legend
# ------------------------------------------------------------

gs = GridSpec(
    nrows=3,
    ncols=2,
    figure=fig,
    height_ratios=[0.13, 0.72, 0.15],
    width_ratios=[1, 1],
    hspace=0.28,
    wspace=0.48,
)

ax_header = fig.add_subplot(gs[0, :])
ax_a = fig.add_subplot(gs[1, 0])
ax_b = fig.add_subplot(gs[1, 1])
ax_footer = fig.add_subplot(gs[2, :])

ax_header.axis("off")
ax_footer.axis("off")


# ============================================================
# COLORS
# ============================================================

BLUE = "#2563EB"
GREEN = "#10B981"
RED = "#EF4444"
GRAY = "#CBD5E1"

TEXT = "#172033"
MUTED = "#64748B"
GRID = "#E5E7EB"


# ============================================================
# HEADER
# ============================================================

ax_header.text(
    0.5,
    0.72,
    "Independent human scRNA-seq replicates a state-linked DPP4 model",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold",
    color=TEXT,
)

ax_header.text(
    0.5,
    0.28,
    (
        "SSc fibroblasts shift toward activated / ECM programs, "
        "while DPP4-positive fibroblasts remain linked to progenitor and ECM states"
    ),
    ha="center",
    va="center",
    fontsize=11.5,
    color=MUTED,
)


# ============================================================
# LABEL HELPER
# ============================================================


def compact_q(q):
    """Format a q-value as a compact plot label.

    Parameters
    ----------
    q : float or None
        FDR-adjusted q-value; missing values are allowed.

    Returns
    -------
    str
        ``"q = NA"``, ``"q < 0.001"``, or ``"q = <value>"``.
    """
    if pd.isna(q):
        return "q = NA"
    q = float(q)
    if q < 0.001:
        return "q < 0.001"
    if q < 0.01:
        return f"q = {q:.3f}"
    return f"q = {q:.2f}"


def annotate_bar(ax, value, y, q, bar_color, axis_span):
    """Write a beta / q-value label on a horizontal bar.

    Large bars (``|value| >= 0.55``) get the label inside the bar; small bars
    get it just outside the bar end.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes containing the bar.
    value : float
        Bar length (effect size, beta in SD units).
    y : float
        Bar position on the y axis.
    q : float
        FDR-adjusted q-value shown under the beta.
    bar_color : str
        Bar color; colored bars get white bold text when labeled inside.
    axis_span : float
        Width of the x axis, used to scale label offsets.
    """

    txt = f"β = {value:.2f}\n{compact_q(q)}"

    # threshold relative to axis scale
    large_bar = abs(value) >= 0.55

    if large_bar:
        # Keep text INSIDE the bar
        if value > 0:
            x = value - axis_span * 0.025
            ha = "right"
        else:
            x = value + axis_span * 0.025
            ha = "left"

        # significant colored bars can take white text
        text_color = "white" if bar_color in [BLUE, GREEN, RED] else TEXT

        ax.text(
            x,
            y,
            txt,
            ha=ha,
            va="center",
            fontsize=9.0,
            color=text_color,
            fontweight="bold" if text_color == "white" else "normal",
            linespacing=1.15,
        )

    else:
        # Small bars: put annotation just outside endpoint
        offset = axis_span * 0.018

        if value >= 0:
            x = value + offset
            ha = "left"
        else:
            x = value - offset
            ha = "right"

        ax.text(x, y, txt, ha=ha, va="center", fontsize=8.7, color=TEXT, linespacing=1.15)


# NOTE: `d` (beta_SSc_SD, q_BH, color, label) and `a` (beta_exposure_SD,
# q_BH, color, label) were built by a cell that is missing from the Colab
# export, so Figure 06's values cannot be traced in this repository. The
# drawing code below is kept as presented; it runs only if a caller
# supplies both tables in the module namespace.
if "d" not in globals() or "a" not in globals():
    raise NotImplementedError(
        "Figure 06 needs two tables (`d`: beta_SSc_SD, q_BH, color, label; "
        "`a`: beta_exposure_SD, q_BH, color, label) whose loader is missing "
        "from the original Colab export."
    )

# ============================================================
# PANEL A — DISEASE EFFECT
# ============================================================

y_a = np.arange(len(d))

ax_a.barh(y_a, d["beta_SSc_SD"], color=d["color"], height=0.62, edgecolor="none")

ax_a.axvline(0, color="#94A3B8", linestyle="--", linewidth=1.1)

ax_a.set_yticks(y_a)
ax_a.set_yticklabels(d["label"], fontsize=10.5)

ax_a.invert_yaxis()

# Extra room prevents annotations from touching labels
ax_a.set_xlim(-2.75, 2.05)

ax_a.set_xlabel("SSc effect size (β SD)", fontsize=10.5, labelpad=8)

ax_a.set_title(
    "A  What changes in SSc fibroblasts?",
    loc="left",
    fontsize=13,
    fontweight="bold",
    pad=20,
    color=TEXT,
)

ax_a.text(
    0.0,
    1.025,
    "Positive = higher in SSc     |     Negative = lower in SSc",
    transform=ax_a.transAxes,
    ha="left",
    va="bottom",
    fontsize=9.2,
    color=MUTED,
)

ax_a.grid(axis="x", color=GRID, linewidth=0.8)

ax_a.set_axisbelow(True)

# remove unnecessary frame
ax_a.spines["top"].set_visible(False)
ax_a.spines["right"].set_visible(False)

span_a = ax_a.get_xlim()[1] - ax_a.get_xlim()[0]

for i, row in d.iterrows():
    annotate_bar(
        ax=ax_a,
        value=float(row["beta_SSc_SD"]),
        y=i,
        q=row["q_BH"],
        bar_color=row["color"],
        axis_span=span_a,
    )


# ============================================================
# PANEL B — DPP4 STATE COUPLING
# ============================================================

y_b = np.arange(len(a))

ax_b.barh(y_b, a["beta_exposure_SD"], color=a["color"], height=0.62, edgecolor="none")

ax_b.axvline(0, color="#94A3B8", linestyle="--", linewidth=1.1)

ax_b.set_yticks(y_b)
ax_b.set_yticklabels(a["label"], fontsize=10.5)

ax_b.invert_yaxis()

ax_b.set_xlim(-1.35, 1.35)

ax_b.set_xlabel("Association with DPP4-positive fraction (β SD)", fontsize=10.5, labelpad=8)

ax_b.set_title(
    "B  Which fibroblast states track DPP4 positivity?",
    loc="left",
    fontsize=13,
    fontweight="bold",
    pad=20,
    color=TEXT,
)

ax_b.text(
    0.0,
    1.025,
    "Positive = tracks DPP4+ fraction     |     Gray = not significant",
    transform=ax_b.transAxes,
    ha="left",
    va="bottom",
    fontsize=9.2,
    color=MUTED,
)

ax_b.grid(axis="x", color=GRID, linewidth=0.8)

ax_b.set_axisbelow(True)

ax_b.spines["top"].set_visible(False)
ax_b.spines["right"].set_visible(False)

span_b = ax_b.get_xlim()[1] - ax_b.get_xlim()[0]

for i, row in a.iterrows():
    annotate_bar(
        ax=ax_b,
        value=float(row["beta_exposure_SD"]),
        y=i,
        q=row["q_BH"],
        bar_color=row["color"],
        axis_span=span_b,
    )


# ============================================================
# FOOTER — INTERPRETATION
# ============================================================

ax_footer.text(
    0.5,
    0.72,
    (
        "DPP4 abundance decreases overall in SSc fibroblasts, "
        "but DPP4-positive fibroblasts remain specifically associated "
        "with progenitor and ECM programs."
    ),
    ha="center",
    va="center",
    fontsize=11.2,
    color=TEXT,
    fontweight="bold",
)

ax_footer.text(
    0.5,
    0.42,
    (
        "Take-home: DPP4 behaves as a fibroblast-state marker, "
        "not as a simple whole-compartment overexpression marker."
    ),
    ha="center",
    va="center",
    fontsize=10.6,
    color=MUTED,
    style="italic",
)


# ============================================================
# COMPACT LEGEND
# ============================================================

legend_handles = [
    Patch(facecolor=BLUE, label="Higher in SSc"),
    Patch(facecolor=RED, label="Lower in SSc"),
    Patch(facecolor=GREEN, label="Positive DPP4-state association"),
    Patch(facecolor=GRAY, label="Not significant"),
]

ax_footer.legend(
    handles=legend_handles,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.03),
    ncol=4,
    frameon=False,
    fontsize=9.3,
    columnspacing=2.2,
    handlelength=1.7,
)


# ============================================================
# FINAL SPACING
# ============================================================

fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.055)


# ============================================================
# EXPORT
# ============================================================

out_png = OUTPUT_DIR / "Figure_06_Independent_scRNA_visual_summary_final.png"

fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")

plt.show()

print(f"High-resolution figure saved to:\n{out_png}")
