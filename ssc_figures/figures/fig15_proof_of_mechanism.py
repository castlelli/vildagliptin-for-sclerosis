"""Figure 15. A disease-relevant proof-of-mechanism experiment is the decisive next step

**Question:** What experiment would most directly determine whether vildagliptin should advance for cutaneous SSc?

**Design:** primary human SSc dermal fibroblasts · TGFβ1 challenge · exposure-informed vildagliptin · DPP4 knockdown · antifibrotic readouts
**Logic:** distinguish pharmacological failure from target/mechanistic failure
**Primary endpoints:** DPP4 activity · PRSS23/THBS1 · ACTA2/TAGLN · collagen/ECM · matrix contraction
**Analysis basis:** integrated human omics · pharmacology · functional literature · stress tests
**Visualization:** translational go/no-go experiment · Matplotlib
"""

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from IPython.display import HTML, display
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from ssc_figures.io import OUTPUT_DIR

# ============================================================
# PALETTE
# ============================================================

C = {
    "sample": "#3572B8",
    "challenge": "#8064A2",
    "intervention": "#E69F00",
    "measurement": "#3C91A3",
    "go": "#2E8B57",
    "drug_fail": "#D97732",
    "target_fail": "#B85450",
    "text": "#1E2732",
    "muted": "#6B7682",
    "line": "#98A2AD",
    "soft": "#F6F8FA",
    "soft2": "#EEF2F5",
    "border": "#C9D1D9",
}


# ============================================================
# FIGURE
# ============================================================

fig, ax = plt.subplots(figsize=(14.8, 7.0), dpi=180)
fig.subplots_adjust(left=0.025, right=0.985, top=0.83, bottom=0.05)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


# ============================================================
# TITLES
# ============================================================

fig.suptitle(
    "The decisive next step is a human SSc proof-of-mechanism experiment",
    fontsize=16,
    fontweight="bold",
    y=0.965,
)

fig.text(
    0.5,
    0.918,
    (
        "Test whether exposure-relevant vildagliptin engages DPP4 "
        "and suppresses fibrotic activity in primary dermal fibroblasts"
    ),
    ha="center",
    fontsize=10,
    color=C["muted"],
)


# ============================================================
# HELPERS
# ============================================================


def wrap_text(text, width):
    """Wrap text to a fixed line width.

    Parameters
    ----------
    text : str
        Text to wrap.
    width : int
        Maximum characters per line.

    Returns
    -------
    str
        Text with newline-separated lines.
    """
    return "\n".join(textwrap.wrap(text, width=width))


def rounded_box(
    x,
    y,
    w,
    h,
    title,
    subtitle,
    edge,
    fill="white",
    title_size=10.2,
    subtitle_size=8.3,
    subtitle_width=28,
):
    """Draw a rounded box with a title and wrapped subtitle.

    Parameters
    ----------
    x, y : float
        Lower-left corner in axes coordinates.
    w, h : float
        Box size in axes coordinates.
    title : str
        Bold title.
    subtitle : str
        Description, wrapped to ``subtitle_width`` characters.
    edge : str
        Border color.
    fill : str, default "white"
        Fill color.
    title_size, subtitle_size : float
        Font sizes.
    subtitle_width : int, default 28
        Wrap width for the subtitle.
    """
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor=fill,
        edgecolor=edge,
        linewidth=1.7,
    )
    ax.add_patch(patch)

    ax.text(
        x + w / 2,
        y + h * 0.63,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color=C["text"],
    )

    ax.text(
        x + w / 2,
        y + h * 0.29,
        wrap_text(subtitle, subtitle_width),
        ha="center",
        va="center",
        fontsize=subtitle_size,
        color=C["muted"],
        linespacing=1.15,
    )


def small_chip(x, y, w, h, text, edge=C["border"]):
    """Draw a small labeled chip (text wrapped at 14 characters).

    Parameters
    ----------
    x, y : float
        Lower-left corner in axes coordinates.
    w, h : float
        Chip size in axes coordinates.
    text : str
        Label text.
    edge : str, default ``C["border"]``
        Border color.
    """
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.004,rounding_size=0.009",
        facecolor=C["soft"],
        edgecolor=edge,
        linewidth=1.0,
    )
    ax.add_patch(patch)

    ax.text(
        x + w / 2,
        y + h / 2,
        wrap_text(text, 14),
        ha="center",
        va="center",
        fontsize=7.7,
        color=C["text"],
        linespacing=1.08,
    )


def horizontal_arrow(x1, x2, y):
    """Draw a horizontal arrow on the module-level ``ax``.

    Parameters
    ----------
    x1, x2 : float
        Start and end x positions in axes coordinates.
    y : float
        Vertical position in axes coordinates.
    """
    ax.add_patch(
        FancyArrowPatch(
            (x1, y), (x2, y), arrowstyle="-|>", mutation_scale=15, linewidth=1.5, color=C["line"]
        )
    )


def decision_box(x, y, w, h, heading, rule, color):
    """Draw a go/no-go decision box with a heading and wrapped rule.

    Parameters
    ----------
    x, y : float
        Lower-left corner in axes coordinates.
    w, h : float
        Box size in axes coordinates.
    heading : str
        Bold colored heading.
    rule : str
        Decision rule, wrapped at 43 characters.
    color : str
        Border and heading color.
    """
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.010,rounding_size=0.015",
        facecolor="white",
        edgecolor=color,
        linewidth=1.5,
    )
    ax.add_patch(patch)

    ax.text(
        x + 0.016,
        y + h - 0.022,
        heading,
        ha="left",
        va="top",
        fontsize=10.0,
        fontweight="bold",
        color=color,
    )

    ax.text(
        x + 0.016,
        y + h - 0.052,
        wrap_text(rule, 43),
        ha="left",
        va="top",
        fontsize=8.2,
        color=C["text"],
        linespacing=1.18,
    )


# ============================================================
# SECTION 1 — EXPERIMENTAL DESIGN
# ============================================================

ax.text(0.04, 0.79, "1  Experimental design", fontsize=11.6, fontweight="bold", color=C["text"])

x_positions = [0.045, 0.285, 0.525, 0.765]
box_w = 0.19
box_h = 0.125
box_y = 0.585

rounded_box(
    x_positions[0],
    box_y,
    box_w,
    box_h,
    "Primary dermal fibroblasts",
    "SSc lesional samples + healthy donor controls",
    C["sample"],
    title_size=10.0,
    subtitle_size=8.2,
    subtitle_width=26,
)

rounded_box(
    x_positions[1],
    box_y,
    box_w,
    box_h,
    "Fibrotic challenge",
    "± TGFβ1 stimulation to induce fibrotic activity",
    C["challenge"],
    title_size=10.0,
    subtitle_size=8.2,
    subtitle_width=26,
)

rounded_box(
    x_positions[2],
    box_y,
    box_w,
    box_h,
    "Experimental arms",
    "vehicle · vildagliptin · DPP4 KD · KD + drug · nintedanib",
    C["intervention"],
    title_size=10.0,
    subtitle_size=8.0,
    subtitle_width=28,
)

rounded_box(
    x_positions[3],
    box_y,
    box_w,
    box_h,
    "Mechanistic response",
    "target engagement + antifibrotic phenotype",
    C["measurement"],
    title_size=10.0,
    subtitle_size=8.2,
    subtitle_width=24,
)

horizontal_arrow(x_positions[0] + box_w, x_positions[1] - 0.008, box_y + box_h / 2)
horizontal_arrow(x_positions[1] + box_w, x_positions[2] - 0.008, box_y + box_h / 2)
horizontal_arrow(x_positions[2] + box_w, x_positions[3] - 0.008, box_y + box_h / 2)


# ============================================================
# EXPERIMENTAL ARM CHIPS
# ============================================================

arm_y = 0.485
chip_h = 0.045
chip_w = 0.088
chip_gap = 0.010
arm_start = 0.525

ax.text(
    0.62,
    0.545,
    "Experimental comparison arms",
    ha="center",
    fontsize=8.6,
    fontweight="bold",
    color=C["muted"],
)

arms = [
    "Vehicle",
    "Vildagliptin\nPK-informed",
    "DPP4\nknockdown",
    "KD +\nvildagliptin",
    "Nintedanib\npositive control",
]

for i, label in enumerate(arms):
    small_chip(arm_start + i * (chip_w + chip_gap), arm_y, chip_w, chip_h, label)


# ============================================================
# SECTION 2 — PRE-SPECIFIED MEASUREMENTS
# ============================================================

ax.text(
    0.04, 0.435, "2  Pre-specified measurements", fontsize=11.6, fontweight="bold", color=C["text"]
)

measure_y = 0.315
measure_w = 0.165
measure_h = 0.078
measure_x = [0.045, 0.235, 0.425, 0.615, 0.805]

measurements = [
    ("Target engagement", "DPP4 enzymatic activity", C["sample"]),
    ("Activated fibroblast", "PRSS23 · THBS1", C["challenge"]),
    ("Myofibroblast", "ACTA2 · TAGLN", C["intervention"]),
    ("ECM production", "COL1A1 · soluble collagen", C["measurement"]),
    ("Functional output", "matrix contraction", C["go"]),
]

for x, (title, subtitle, color) in zip(measure_x, measurements):
    rounded_box(
        x,
        measure_y,
        measure_w,
        measure_h,
        title,
        subtitle,
        color,
        title_size=9.0,
        subtitle_size=7.8,
        subtitle_width=22,
    )

ax.text(
    0.5,
    0.275,
    "Target engagement should be confirmed before interpreting the antifibrotic phenotype",
    ha="center",
    fontsize=8.5,
    color=C["muted"],
    style="italic",
)


# ============================================================
# SECTION 3 — DECISION LOGIC
# ============================================================

ax.text(0.04, 0.215, "3  Decision logic", fontsize=11.6, fontweight="bold", color=C["text"])

decision_y = 0.045
decision_h = 0.145
decision_w = 0.29

decision_box(
    0.045,
    decision_y,
    decision_w,
    decision_h,
    "GO — drug and mechanism supported",
    (
        "Vildagliptin reduces DPP4 activity and suppresses fibroblast "
        "activation, collagen/ECM output and matrix contraction at "
        "exposure-relevant concentrations."
    ),
    C["go"],
)

decision_box(
    0.357,
    decision_y,
    decision_w,
    decision_h,
    "DRUG FAILURE — target may remain valid",
    (
        "DPP4 knockdown suppresses the fibrotic phenotype, but "
        "exposure-relevant vildagliptin does not. The target remains "
        "plausible, but this repurposing fails."
    ),
    C["drug_fail"],
)

decision_box(
    0.669,
    decision_y,
    decision_w,
    decision_h,
    "TARGET / MECHANISM FAILURE",
    (
        "Neither DPP4 knockdown nor pharmacological inhibition produces "
        "a meaningful antifibrotic phenotype despite adequate "
        "experimental target assessment."
    ),
    C["target_fail"],
)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_15_decisive_proof_of_mechanism.png")

fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight")

plt.show()


# ============================================================
# INTERPRETATION
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

        <b>Why this experiment?</b><br>

        The current evidence supports a disease-relevant human fibroblast context,
        experimental antifibrotic DPP4 biology and clinically achievable systemic
        pharmacology.

        <br><br>

        The decisive unresolved question is whether
        <b>vildagliptin itself can engage DPP4 and suppress fibrotic activity
        in primary human SSc dermal fibroblasts at pharmacologically relevant exposure</b>.

        <br><br>

        <b>Interpretation logic:</b>

        <ul style="margin-top:7px; margin-bottom:7px;">
          <li><b>GO:</b> vildagliptin engages DPP4 and suppresses the fibrotic phenotype.</li>
          <li><b>Drug failure:</b> DPP4 knockdown works, but vildagliptin does not.</li>
          <li><b>Target/mechanism failure:</b> DPP4 perturbation itself fails to suppress fibrosis.</li>
        </ul>

        <b>Primary go/no-go measurements:</b><br>
        DPP4 activity · PRSS23/THBS1 · ACTA2/TAGLN · COL1A1/soluble collagen · matrix contraction

        <br><br>

        <b>Verdict:</b><br>
        DECISIVE NEXT STEP — <b>DISEASE-RELEVANT HUMAN PROOF-OF-MECHANISM</b>

        </div>
        """
    )
)

print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
