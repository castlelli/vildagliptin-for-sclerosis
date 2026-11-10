"""Figure 11. Functional studies provide a causal antifibrotic bridge from DPP4 to vildagliptin

**Question:** Does experimental DPP4 inhibition reduce fibroblast activation and fibrosis, and is this effect observed with vildagliptin itself?

**Evidence:** human dermal fibroblasts · genetic/pharmacological DPP4 perturbation · SSc-relevant fibrosis models · vildagliptin treatment
**Key mechanistic anchor:** Soare et al. · PMID 31350829
**Analysis:** curated functional and translational evidence synthesis
**Analysis tools:** PubMed evidence curation · Python
**Visualization:** mechanistic evidence bridge · Matplotlib
"""

from ssc_figures.io import OUTPUT_DIR, load_tsv

import matplotlib.pyplot as plt

from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from pathlib import Path
from IPython.display import display, HTML


# ============================================================
# VALIDATE CURATED EVIDENCE TABLES
# ============================================================

preclinical = load_tsv("R5b_preclinical_evidence_audit.tsv")

ladder = load_tsv("R5b_translational_evidence_ladder.tsv")

# NOTE: `preclinical` and `ladder` are loaded (fail fast if missing) but not
# used below; the figure and verdict text in this cell are hardcoded.


# ============================================================
# PALETTE
# ============================================================

C = {
    "drug": "#E69F00",
    "target": "#2C7FB8",
    "cell": "#41AE76",
    "matrix": "#8064A2",
    "fibrosis": "#CB4B4B",
    "supported": "#2E8B57",
    "preclinical": "#2C7FB8",
    "replication": "#8064A2",
    "untested": "#9B684A",
    "text": "#17212B",
    "muted": "#64717D",
    "line": "#929CA6",
    "soft": "#F5F7F8",
    "border": "#C8D0D7",
}


# ============================================================
# FIGURE
#
# Compact layout:
#
# title
# ↓
# causal chain
# ↓
# evidence labels
# ↓
# key evidence cards
# ↓
# translational status
#
# ============================================================

fig, ax = plt.subplots(figsize=(14.4, 5.0), dpi=180)


fig.subplots_adjust(left=0.025, right=0.985, top=0.82, bottom=0.055)


ax.set_xlim(0, 1)

ax.set_ylim(0, 1)

ax.axis("off")


# ============================================================
# GLOBAL TITLE
# ============================================================

fig.suptitle(
    ("Experimental perturbation supports an antifibrotic DPP4 mechanism"),
    fontsize=16,
    fontweight="bold",
    y=0.965,
)


fig.text(
    0.5,
    0.915,
    ("Vildagliptin → DPP4 inhibition → fibroblast suppression → reduced fibrotic output"),
    ha="center",
    va="center",
    fontsize=10.4,
    color=C["muted"],
)


# ============================================================
# HELPERS
# ============================================================


def draw_box(x, y, width, height, title, subtitle, color):
    """Draw a titled, centered rounded box on the module-level ``ax``.

    Parameters
    ----------
    x, y : float
        Box center in axes coordinates.
    width, height : float
        Box size in axes coordinates.
    title : str
        Bold title text.
    subtitle : str
        Smaller text under the title.
    color : str
        Border color.
    """

    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle=("round,pad=0.012,rounding_size=0.018"),
        facecolor="white",
        edgecolor=color,
        linewidth=2.0,
        zorder=3,
    )

    ax.add_patch(box)

    ax.text(
        x,
        y + 0.025,
        title,
        ha="center",
        va="center",
        fontsize=11.2,
        fontweight="bold",
        color=C["text"],
        zorder=4,
    )

    ax.text(
        x,
        y - 0.035,
        subtitle,
        ha="center",
        va="center",
        fontsize=8.5,
        color=C["muted"],
        linespacing=1.18,
        zorder=4,
    )


def draw_arrow(x1, x2, y):
    """Draw a horizontal arrow on the module-level ``ax``.

    Parameters
    ----------
    x1, x2 : float
        Start and end x positions in axes coordinates.
    y : float
        Vertical position in axes coordinates.
    """

    arrow = FancyArrowPatch(
        (x1, y),
        (x2, y),
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=1.8,
        color=C["line"],
        zorder=2,
    )

    ax.add_patch(arrow)


def draw_chip(x, y, text, color, width):
    """Draw a translucent label chip centered at ``(x, y)``.

    Parameters
    ----------
    x, y : float
        Chip center in axes coordinates.
    text : str
        Label text.
    color : str
        Chip and text color.
    width : float
        Chip width in axes coordinates.
    """

    chip = FancyBboxPatch(
        (x - width / 2, y - 0.027),
        width,
        0.054,
        boxstyle=("round,pad=0.005,rounding_size=0.012"),
        facecolor=color,
        edgecolor=color,
        linewidth=1.0,
        alpha=0.12,
        zorder=2,
    )

    ax.add_patch(chip)

    ax.text(
        x, y, text, ha="center", va="center", fontsize=8.2, fontweight="bold", color=color, zorder=3
    )


def draw_info_card(x, y, width, height, heading, title, text, accent):
    """Draw an evidence card with heading, title and body text.

    Parameters
    ----------
    x, y : float
        Lower-left corner in axes coordinates.
    width, height : float
        Card size in axes coordinates.
    heading : str
        Small colored heading.
    title : str
        Bold title.
    text : str
        Body text along the bottom of the card.
    accent : str
        Border and heading color.
    """

    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=("round,pad=0.010,rounding_size=0.016"),
        facecolor=C["soft"],
        edgecolor=accent,
        linewidth=1.25,
    )

    ax.add_patch(card)

    ax.text(
        x + 0.018,
        y + height - 0.027,
        heading,
        ha="left",
        va="top",
        fontsize=8.8,
        fontweight="bold",
        color=accent,
    )

    ax.text(
        x + 0.018,
        y + height - 0.060,
        title,
        ha="left",
        va="top",
        fontsize=10.1,
        fontweight="bold",
        color=C["text"],
    )

    ax.text(x + 0.018, y + 0.023, text, ha="left", va="bottom", fontsize=8.2, color=C["muted"])


# ============================================================
# MAIN CAUSAL CHAIN
# ============================================================

centers = [0.10, 0.30, 0.50, 0.70, 0.90]


box_width = 0.165
box_height = 0.205

main_y = 0.675


draw_box(
    centers[0],
    main_y,
    box_width,
    box_height,
    "Vildagliptin",
    ("Approved DPP4 inhibitor\nclinically achievable exposure"),
    C["drug"],
)


draw_box(
    centers[1],
    main_y,
    box_width,
    box_height,
    "DPP4 / CD26",
    ("Pharmacological +\ngenetic perturbation"),
    C["target"],
)


draw_box(
    centers[2],
    main_y,
    box_width,
    box_height,
    "Fibroblast activation",
    ("↓ activation markers\n↓ profibrotic phenotype"),
    C["cell"],
)


draw_box(
    centers[3],
    main_y,
    box_width,
    box_height,
    "Collagen / ECM",
    ("↓ matrix-associated\nfibrotic output"),
    C["matrix"],
)


draw_box(
    centers[4],
    main_y,
    box_width,
    box_height,
    "Tissue fibrosis",
    ("Reduced fibrosis in\npreclinical models"),
    C["fibrosis"],
)


# ============================================================
# ARROWS
# ============================================================

for i in range(len(centers) - 1):
    draw_arrow(centers[i] + box_width / 2 + 0.006, centers[i + 1] - box_width / 2 - 0.006, main_y)


# ============================================================
# EVIDENCE TYPE CHIPS
# ============================================================

chip_y = 0.475


draw_chip(0.20, chip_y, "drug-specific evidence", C["drug"], 0.155)


draw_chip(0.40, chip_y, "genetic + pharmacological", C["target"], 0.175)


draw_chip(0.60, chip_y, "human dermal fibroblasts", C["cell"], 0.170)


draw_chip(0.80, chip_y, "SSc-relevant in vivo models", C["fibrosis"], 0.175)


# ============================================================
# KEY EVIDENCE CARDS
#
# Immediately below the causal chain.
# ============================================================

draw_info_card(
    x=0.055,
    y=0.245,
    width=0.54,
    height=0.135,
    heading=("KEY DIRECT MECHANISTIC ANCHOR"),
    title=("Soare et al. · PMID 31350829"),
    text=(
        "DPP4/CD26 perturbation reduces fibroblast activation "
        "and fibrosis in SSc-relevant experimental systems."
    ),
    accent=C["target"],
)


draw_info_card(
    x=0.625,
    y=0.245,
    width=0.32,
    height=0.135,
    heading=("INDEPENDENT REPLICATION"),
    title=("Pulmonary fibrosis models"),
    text=(
        "Vildagliptin also shows antifibrotic activity in an independent fibrotic organ context."
    ),
    accent=C["replication"],
)


# ============================================================
# TRANSLATIONAL STATUS
# ============================================================

ax.text(
    0.055,
    0.175,
    "Translational status",
    ha="left",
    va="center",
    fontsize=10.4,
    fontweight="bold",
    color=C["text"],
)


statuses = [
    {"x": 0.12, "label": "DPP4 causal biology", "status": "SUPPORTED", "color": C["supported"]},
    {
        "x": 0.38,
        "label": "Vildagliptin antifibrotic activity",
        "status": "PRECLINICAL",
        "color": C["preclinical"],
    },
    {
        "x": 0.67,
        "label": "Cross-organ replication",
        "status": "SUPPORTED",
        "color": C["replication"],
    },
    {"x": 0.89, "label": "Human SSc efficacy", "status": "UNTESTED", "color": C["untested"]},
]


for item in statuses:
    ax.scatter(item["x"], 0.115, s=82, color=item["color"], zorder=3)

    ax.text(
        item["x"], 0.078, item["label"], ha="center", va="center", fontsize=8.2, color=C["text"]
    )

    ax.text(
        item["x"],
        0.045,
        item["status"],
        ha="center",
        va="center",
        fontsize=8.4,
        fontweight="bold",
        color=item["color"],
    )


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_11_functional_causal_bridge.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight")


plt.show()


# ============================================================
# RESULT
# ============================================================

display(
    HTML(
        """
        <div style="
            border-left:4px solid #666;
            padding:13px 17px;
            margin-top:10px;
            line-height:1.52;
        ">

        <b>Result</b><br>

        Experimental perturbation provides the causal link that
        observational human omics alone cannot establish.

        <br><br>

        Genetic and pharmacological inhibition of
        <b>DPP4/CD26</b> reduces fibroblast activation and
        fibrotic phenotypes, including evidence from
        <b>human dermal fibroblasts</b> and
        <b>SSc-relevant in vivo systems</b>.

        <br><br>

        Crucially, this evidence is not restricted to target biology:
        <b>vildagliptin itself shows antifibrotic activity
        preclinically</b>.

        <br><br>

        The strongest direct mechanistic anchor is
        <b>Soare et al. (PMID 31350829)</b>.
        Independent pulmonary-fibrosis experiments provide
        additional cross-organ support.

        <br><br>

        <b>Important:</b>
        these data support experimental plausibility,
        not therapeutic efficacy in patients with SSc.

        <br><br>

        <b>Verdict:</b><br>

        CAUSAL DPP4 ANTIFIBROTIC BIOLOGY —
        <b>SUPPORTED</b><br>

        VILDAGLIPTIN-SPECIFIC ANTIFIBROTIC ACTIVITY —
        <b>SUPPORTED PRECLINICALLY</b><br>

        HUMAN SSc EFFICACY —
        <b>UNTESTED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
