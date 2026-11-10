"""Figure 13. The opportunity is translational rather than biologically novel

**Question:** Is vildagliptin for systemic sclerosis a new biological hypothesis, or an unresolved translational opportunity?

**Sources:** PubMed · ClinicalTrials.gov · Cortellis review
**Analysis:** structured precedent and development-gap audit
**Analysis tools:** literature curation · ClinicalTrials.gov queries · Cortellis intelligence review · Python
**Interpretation:** absence claims are restricted to the records reviewed
"""

from ssc_figures.io import OUTPUT_DIR, load_tsv

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path
from IPython.display import display, HTML

# ============================================================
# LOAD CURATED RESULTS
# ============================================================

pubmed = load_tsv("R6b_PubMed_evidence_class_summary.tsv")

ct_skin = load_tsv("R6a_ClinicalTrials_skin_dermal_fibrosis.tsv")

ct_scleroderma = load_tsv("R6a_ClinicalTrials_localized_scleroderma.tsv")

# NOTE: these three tables are loaded but not used below; the figure and
# verdict text in this cell are hardcoded.

# ============================================================
# FIGURE
# ============================================================

fig, ax = plt.subplots(figsize=(13.5, 4.8), dpi=180)

fig.subplots_adjust(left=0.035, right=0.98, top=0.80, bottom=0.08)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# ============================================================
# COLORS
# ============================================================

C = {
    "known": "#2C7FB8",
    "preclinical": "#41AE76",
    "gap": "#E69F00",
    "clinical": "#CB4B4B",
    "text": "#17212B",
    "muted": "#66727D",
    "line": "#949DA6",
    "soft": "#F5F7F8",
}

# ============================================================
# TITLE
# ============================================================

fig.suptitle(
    "The innovation is closing a translational gap", fontsize=15, fontweight="bold", y=0.96
)

fig.text(
    0.5,
    0.90,
    (
        "Antifibrotic DPP4 biology already has preclinical precedent; "
        "clinical development in SSc remains unresolved"
    ),
    ha="center",
    fontsize=10,
)

# ============================================================
# HELPERS
# ============================================================


def box(x, title, subtitle, color, status):
    """Draw one stage of the translational continuum.

    The box has a fixed size and vertical position (y = 0.57).

    Parameters
    ----------
    x : float
        Box center x position in axes coordinates.
    title : str
        Bold title.
    subtitle : str
        Description under the title.
    color : str
        Border and status color.
    status : str
        Status label drawn at the bottom of the box.
    """

    w = 0.195
    h = 0.28
    y = 0.57

    p = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor="white",
        edgecolor=color,
        linewidth=2,
    )

    ax.add_patch(p)

    ax.text(
        x,
        y + 0.065,
        title,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=C["text"],
    )

    ax.text(
        x,
        y - 0.005,
        subtitle,
        ha="center",
        va="center",
        fontsize=8.7,
        color=C["muted"],
        linespacing=1.25,
    )

    ax.text(x, y - 0.105, status, ha="center", fontsize=9, fontweight="bold", color=color)


def arrow(x1, x2):
    """Draw a horizontal arrow at y = 0.57 between continuum boxes.

    Parameters
    ----------
    x1, x2 : float
        Start and end x positions in axes coordinates.
    """

    ax.add_patch(
        FancyArrowPatch(
            (x1, 0.57),
            (x2, 0.57),
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=1.7,
            color=C["line"],
        )
    )


# ============================================================
# TRANSLATIONAL CONTINUUM
# ============================================================

centers = [0.12, 0.37, 0.62, 0.87]

box(
    centers[0],
    "DPP4 antifibrotic biology",
    ("Fibroblast activation and\nfibrosis mechanisms reported"),
    C["known"],
    "ESTABLISHED PRECEDENT",
)

box(
    centers[1],
    "Vildagliptin preclinical evidence",
    ("Drug-specific antifibrotic\nactivity already reported"),
    C["preclinical"],
    "PRECLINICAL SUPPORT",
)

box(
    centers[2],
    "Human SSc development",
    ("No interventional clinical\ndevelopment identified in\nthe reviewed records"),
    C["gap"],
    "TRANSLATIONAL GAP",
)

box(
    centers[3],
    "Human efficacy",
    ("Effect on skin fibrosis or\nmRSS remains untested"),
    C["clinical"],
    "UNRESOLVED",
)

for i in range(3):
    arrow(centers[i] + 0.105, centers[i + 1] - 0.105)

# ============================================================
# NOVELTY MESSAGE
# ============================================================

ax.text(
    0.50,
    0.22,
    ("Innovation ≠ discovering that DPP4 can influence fibrosis"),
    ha="center",
    fontsize=10.5,
    fontweight="bold",
    color=C["text"],
)

ax.text(
    0.50,
    0.15,
    (
        "Innovation = translating an approved DPP4 inhibitor into a "
        "human SSc fibroblast-state framework with explicit PK/PD and "
        "proof-of-mechanism criteria"
    ),
    ha="center",
    fontsize=9.3,
    color=C["muted"],
)

# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_13_translational_gap.png")

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

        The antifibrotic biology of DPP4 is <b>not biologically novel</b>.
        Direct preclinical work already links DPP4 inhibition — including
        vildagliptin — to reduced fibroblast activation and fibrosis.

        <br><br>

        However, across the reviewed <b>PubMed, ClinicalTrials.gov and
        Cortellis records</b>, we did not identify human interventional
        development of vildagliptin for systemic sclerosis.

        <br><br>

        <b>Therefore, the opportunity is translational:</b><br>
        move an approved, systemically target-engaging drug from
        preclinical antifibrotic precedent into a
        <b>human SSc fibroblast-state and dermal proof-of-mechanism framework</b>.

        <br><br>

        <b>Important:</b>
        this should not be phrased as a universal claim that no patent,
        program or prior attempt exists. The conclusion applies to the
        <b>records reviewed</b>.

        <br><br>

        <b>Verdict:</b><br>

        BIOLOGICAL NOVELTY —
        <b>LOW</b><br>

        CLINICAL SSc REPURPOSING GAP —
        <b>SUPPORTED</b><br>

        TRANSLATIONAL OPPORTUNITY —
        <b>SUPPORTED</b>

        </div>
        """
    )
)

print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
