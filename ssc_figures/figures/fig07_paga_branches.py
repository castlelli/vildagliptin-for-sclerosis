"""Figure 07. Fibroblast-state organization is branch-aware

**Question:** Does the published DPP4/SFRP2 progenitor model behave as one obligatory fibrotic trajectory, or as part of a broader branch-aware fibroblast organization?

**Data:** GSE138669 human skin fibroblast single-cell RNA-seq
**Analysis:** fibroblast graph reconstruction + PAGA topology + donor-level disease-state occupancy
**Analysis tools:** Scanpy · Harmony · PAGA · NetworkX · statsmodels
**Literature anchor:** Tabib et al., *Nature Communications* (2021) · PMID 34282151
**Visualization:** single integrated PAGA network · Matplotlib

**How to read:** network structure represents PAGA connectivity; node color represents the adjusted SSc effect on donor-level cluster occupancy. Red = enriched in SSc; blue = depleted in SSc.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from IPython.display import HTML, display
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
from PIL import Image

from ssc_figures.io import OUTPUT_DIR, data_file
from ssc_figures.style import crop_white_margin

# ============================================================
# INPUT
#
# Use the disease-enrichment PAGA graph as the single network.
# The topology is identical to the state graph; therefore,
# there is no need to show the same network twice.
# ============================================================

img_enrichment = data_file("R9b_PAGA_SSc_enrichment.png")

network_img = Image.open(img_enrichment).convert("RGB")


# ============================================================
# CROP WHITE MARGINS
# ============================================================


network_img = crop_white_margin(network_img, padding=10)


# ============================================================
# COLORS
# ============================================================

TEXT = "#172033"
MUTED = "#64748B"

DPP4_COLOR = "#218C5A"
MYO_COLOR = "#8064A2"
SSC_COLOR = "#C94B4B"

SOFT_GREEN = "#EEF8F2"
SOFT_PURPLE = "#F4F1FA"
SOFT_RED = "#FCF0EF"

BORDER = "#D7DEE5"
SOFT_GRAY = "#F7F9FB"


# ============================================================
# FIGURE LAYOUT
#
# One network + interpretation panel.
# ============================================================

fig = plt.figure(figsize=(14.8, 7.5), dpi=180, facecolor="white")


gs = GridSpec(
    nrows=3,
    ncols=2,
    figure=fig,
    height_ratios=[0.14, 0.72, 0.14],
    width_ratios=[1.55, 0.45],
    hspace=0.22,
    wspace=0.12,
)


ax_header = fig.add_subplot(gs[0, :])

ax_network = fig.add_subplot(gs[1, 0])

ax_info = fig.add_subplot(gs[1, 1])

ax_footer = fig.add_subplot(gs[2, :])


ax_header.axis("off")
ax_network.axis("off")
ax_info.axis("off")
ax_footer.axis("off")


# ============================================================
# HEADER
# ============================================================

ax_header.text(
    0.5,
    0.73,
    "Human SSc fibroblast organization is branch-aware",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold",
    color=TEXT,
)


ax_header.text(
    0.5,
    0.27,
    (
        "The published DPP4/SFRP2 progenitor model is compatible with "
        "a broader non-linear fibroblast topology"
    ),
    ha="center",
    va="center",
    fontsize=11.3,
    color=MUTED,
)


# ============================================================
# MAIN NETWORK
# ============================================================

ax_network.imshow(network_img, interpolation="lanczos")


ax_network.axis("off")


ax_network.set_title(
    "Integrated fibroblast topology and SSc state occupancy",
    fontsize=13,
    fontweight="bold",
    pad=10,
    color=TEXT,
)


# ============================================================
# INFORMATION PANEL
# ============================================================

panel = FancyBboxPatch(
    (0.03, 0.04),
    0.94,
    0.92,
    boxstyle=("round,pad=0.018,rounding_size=0.025"),
    transform=ax_info.transAxes,
    facecolor=SOFT_GRAY,
    edgecolor=BORDER,
    linewidth=1.2,
)


ax_info.add_patch(panel)


# ============================================================
# HOW TO READ
# ============================================================

ax_info.text(
    0.10,
    0.90,
    "How to read the network",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=11.8,
    fontweight="bold",
    color=TEXT,
)


ax_info.text(
    0.10,
    0.835,
    (
        "Node color = SSc occupancy effect\n"
        "Red = enriched in SSc\n"
        "Blue = depleted in SSc\n"
        "Edges = PAGA state connectivity"
    ),
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=9.1,
    color=MUTED,
    linespacing=1.45,
)


# ============================================================
# BRANCH 1
# ============================================================

box1 = FancyBboxPatch(
    (0.08, 0.545),
    0.84,
    0.19,
    boxstyle=("round,pad=0.012,rounding_size=0.020"),
    transform=ax_info.transAxes,
    facecolor=SOFT_GREEN,
    edgecolor=DPP4_COLOR,
    linewidth=1.3,
)


ax_info.add_patch(box1)


ax_info.text(
    0.12,
    0.695,
    "DPP4-associated branch",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=10.8,
    fontweight="bold",
    color=DPP4_COLOR,
)


ax_info.text(
    0.12,
    0.635,
    "0  →  2  →  4",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=12,
    fontweight="bold",
    color=TEXT,
)


ax_info.text(
    0.12,
    0.585,
    ("DPP4-high / activated / ECM-related\norganization shares this route."),
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=8.9,
    color=TEXT,
    linespacing=1.3,
)


# ============================================================
# BRANCH 2
# ============================================================

box2 = FancyBboxPatch(
    (0.08, 0.325),
    0.84,
    0.17,
    boxstyle=("round,pad=0.012,rounding_size=0.020"),
    transform=ax_info.transAxes,
    facecolor=SOFT_PURPLE,
    edgecolor=MYO_COLOR,
    linewidth=1.3,
)


ax_info.add_patch(box2)


ax_info.text(
    0.12,
    0.455,
    "Partially distinct route",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=10.8,
    fontweight="bold",
    color=MYO_COLOR,
)


ax_info.text(
    0.12,
    0.400,
    "0  →  6  →  9",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=12,
    fontweight="bold",
    color=TEXT,
)


ax_info.text(
    0.12,
    0.350,
    "Myofibroblast-high state",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=8.9,
    color=TEXT,
)


# ============================================================
# DISEASE OCCUPANCY
# ============================================================

box3 = FancyBboxPatch(
    (0.08, 0.115),
    0.84,
    0.16,
    boxstyle=("round,pad=0.012,rounding_size=0.020"),
    transform=ax_info.transAxes,
    facecolor=SOFT_RED,
    edgecolor=SSC_COLOR,
    linewidth=1.3,
)


ax_info.add_patch(box3)


ax_info.text(
    0.12,
    0.235,
    "Disease remodeling",
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=10.8,
    fontweight="bold",
    color=SSC_COLOR,
)


ax_info.text(
    0.12,
    0.180,
    (
        "SSc preferentially enriches selected\n"
        "states rather than uniformly expanding\n"
        "the entire fibroblast graph."
    ),
    transform=ax_info.transAxes,
    ha="left",
    va="top",
    fontsize=8.8,
    color=TEXT,
    linespacing=1.3,
)


# ============================================================
# FOOTER — TAKE-HOME
# ============================================================

ax_footer.text(
    0.5,
    0.68,
    (
        "Take-home: DPP4-associated fibroblast states belong to a "
        "disease-relevant branch, but they do not define a single obligatory "
        "trajectory toward every fibrotic endpoint."
    ),
    ha="center",
    va="center",
    fontsize=11.2,
    fontweight="bold",
    color=TEXT,
)


ax_footer.text(
    0.5,
    0.25,
    (
        "PAGA describes connectivity between cellular states; "
        "it does not by itself prove lineage direction or causal differentiation."
    ),
    ha="center",
    va="center",
    fontsize=9.5,
    color=MUTED,
    style="italic",
)


# ============================================================
# FINAL SPACING
# ============================================================

fig.subplots_adjust(left=0.035, right=0.985, top=0.97, bottom=0.04)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_07_integrated_branch_aware_PAGA.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight", facecolor="white")


plt.show()


# ============================================================
# INTERPRETATION
# ============================================================

display(
    HTML(
        """
        <div style="
            border-left:4px solid #218C5A;
            padding:14px 18px;
            margin-top:10px;
            line-height:1.55;
        ">

        <b>Result</b><br>

        The PAGA reconstruction is consistent with and refines the
        fibroblast organization previously described in human systemic
        sclerosis.

        <br><br>

        Tabib et al. identified
        <b>SFRP2<sup>hi</sup>/DPP4-expressing fibroblasts as a
        progenitor-like population capable of contributing to
        fibrogenic differentiation</b>
        (Nature Communications, 2021; PMID 34282151).

        <br><br>

        Consistent with this biological framework, our reconstruction
        does <b>not</b> support one obligatory
        DPP4 → activated → myofibroblast → ECM sequence.

        Instead:

        <ul style="
            margin-top:8px;
            margin-bottom:8px;
        ">

          <li>
            DPP4-high, activated and ECM-associated organization
            shares the <b>0 → 2 → 4 branch</b>.
          </li>

          <li>
            The myofibroblast-high state occupies a
            <b>partially distinct 0 → 6 → 9 route</b>.
          </li>

          <li>
            SSc modifies occupancy of selected regions of this topology,
            rather than uniformly expanding all fibroblast states.
          </li>

        </ul>

        <b>Interpretation:</b><br>

        Our analysis therefore
        <b>supports and refines the published DPP4/SFRP2 progenitor model</b>.

        DPP4 is better interpreted as identifying a
        <b>disease-relevant fibroblast branch/state context</b>,
        rather than as a universal marker of a single terminal
        myofibroblast trajectory.

        <br><br>

        <b>Important:</b><br>

        PAGA estimates topological connectivity between cellular states.
        It does not by itself demonstrate lineage direction,
        temporal progression or causality.

        <br><br>

        <b>Verdict:</b><br>

        PUBLISHED DPP4/SFRP2 PROGENITOR MODEL —
        <b>SUPPORTED AND REFINED</b><br>

        BRANCH-AWARE FIBROBLAST ORGANIZATION —
        <b>SUPPORTED</b><br>

        SINGLE OBLIGATORY DPP4 → MYOFIBROBLAST → ECM TRAJECTORY —
        <b>NOT SUPPORTED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
