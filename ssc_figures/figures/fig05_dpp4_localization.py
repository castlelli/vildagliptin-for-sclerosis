"""Figure 05. DPP4 localizes to a fibroblast-relevant compartment in human skin

**Question:** If DPP4 is not globally increased in SSc skin, which cell compartments express it?

**Data:** GSE138669 human skin single-cell RNA-seq
**Analysis:** Cell-type annotation + DPP4 single-cell expression
**Analysis tools:** Scanpy · AnnData · Harmony representation
**Visualization:** DaVinci UMAP outputs + Matplotlib descriptive summary
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display
from PIL import Image as PILImage

from ssc_figures.io import OUTPUT_DIR, data_file, load_tsv
from ssc_figures.style import crop_white_margin

# ============================================================
# LOAD PROCESSED DAVINCI RESULTS
# ============================================================

celltype_dpp4 = load_tsv("R2b_DPP4_celltype_descriptive_summary.tsv")


# ============================================================
# IMAGE PREPARATION
#
# The UMAPs were calculated and rendered previously on DaVinci.
# Here we only crop unused white margins and enlarge the raster
# for clearer notebook/presentation display.
# ============================================================


def upscale_image(image, factor=2):
    """Upscale an image for display quality only.

    This does not create new biological information.

    Parameters
    ----------
    image : PIL.Image.Image
        Image to enlarge.
    factor : int, default 2
        Integer scale factor applied to width and height.

    Returns
    -------
    PIL.Image.Image
        Image resized with Lanczos resampling.
    """

    return image.resize((image.width * factor, image.height * factor), PILImage.Resampling.LANCZOS)


celltype_img = PILImage.open(data_file("R2b_UMAP_celltypes.png"))

dpp4_img = PILImage.open(data_file("R2b_UMAP_DPP4.png"))


celltype_img = upscale_image(crop_white_margin(celltype_img), factor=2)

dpp4_img = upscale_image(crop_white_margin(dpp4_img), factor=2)


# ============================================================
# DESCRIPTIVE CELL-TYPE SUMMARY
#
# Original results are stratified by condition and chemistry.
# Chemistry strata are collapsed descriptively within condition.
#
# This is NOT the formal donor-level disease test.
# ============================================================

summary = celltype_dpp4.groupby(["cell_type", "condition"], as_index=False).agg(
    median_DPP4_positive=("median_fraction_DPP4_positive", "median"),
    median_DPP4_expression=("median_DPP4_logexpr", "median"),
    cells=("total_cells", "sum"),
)


summary["DPP4_positive_percent"] = summary["median_DPP4_positive"] * 100


# Order compartments by overall DPP4-positive fraction.
cell_order = (
    summary.groupby("cell_type")["DPP4_positive_percent"]
    .median()
    .sort_values(ascending=True)
    .index.tolist()
)


# ============================================================
# HIGH-RESOLUTION COMPOSITE FIGURE
#
# Layout:
#
# ┌──────────────────┬───────────────────────────────┐
# │ Cell landscape   │                               │
# │                  │ DPP4-positive fraction        │
# ├──────────────────┤                               │
# │ DPP4 expression  │                               │
# └──────────────────┴───────────────────────────────┘
#
# ============================================================

fig = plt.figure(figsize=(18, 10), dpi=150)


gs = fig.add_gridspec(
    nrows=2,
    ncols=2,
    width_ratios=[1.10, 1.45],
    height_ratios=[1, 1],
    left=0.04,
    right=0.98,
    top=0.88,
    bottom=0.08,
    wspace=0.20,
    hspace=0.20,
)


ax_cell = fig.add_subplot(gs[0, 0])

ax_dpp4 = fig.add_subplot(gs[1, 0])

ax_bar = fig.add_subplot(gs[:, 1])


# ============================================================
# PANEL A — CELLULAR LANDSCAPE
# ============================================================

ax_cell.imshow(celltype_img, interpolation="lanczos")

ax_cell.set_title("Cellular landscape", fontsize=15, fontweight="bold", pad=10)

ax_cell.axis("off")


# ============================================================
# PANEL B — DPP4 EXPRESSION
# ============================================================

ax_dpp4.imshow(dpp4_img, interpolation="lanczos")

ax_dpp4.set_title("DPP4 expression", fontsize=15, fontweight="bold", pad=10)

ax_dpp4.axis("off")


# ============================================================
# PANEL C — DPP4-POSITIVE CELLS BY COMPARTMENT
# ============================================================

conditions = summary["condition"].dropna().unique().tolist()


y = np.arange(len(cell_order))


n_conditions = len(conditions)


# Side-by-side horizontal bars.
total_height = 0.70
bar_height = total_height / max(n_conditions, 1)


offsets = np.linspace(
    -total_height / 2 + bar_height / 2, total_height / 2 - bar_height / 2, n_conditions
)


for offset, condition in zip(offsets, conditions):
    sub = summary[summary["condition"] == condition].set_index("cell_type").reindex(cell_order)

    values = sub["DPP4_positive_percent"].fillna(0).values

    ax_bar.barh(y + offset, values, height=bar_height, label=str(condition))


ax_bar.set_yticks(y)

ax_bar.set_yticklabels(cell_order, fontsize=12)


ax_bar.set_xlabel("Median fraction of DPP4-positive cells (%)", fontsize=12, labelpad=10)


ax_bar.set_title("DPP4-positive cells by compartment", fontsize=15, fontweight="bold", pad=14)


ax_bar.grid(axis="x", alpha=0.20)


ax_bar.set_axisbelow(True)


ax_bar.legend(frameon=False, loc="lower right", fontsize=11)


# Add some space beyond the longest bar.
max_value = summary["DPP4_positive_percent"].max()

ax_bar.set_xlim(0, max_value * 1.12)


# Remove unnecessary borders.
ax_bar.spines["top"].set_visible(False)

ax_bar.spines["right"].set_visible(False)


# ============================================================
# MAIN TITLE
# ============================================================

fig.suptitle(
    "DPP4 shows a fibroblast-enriched distribution in human skin",
    fontsize=19,
    fontweight="bold",
    y=0.965,
)


fig.text(
    0.5,
    0.925,
    ("Single-cell localization in GSE138669 · descriptive cellular distribution"),
    ha="center",
    fontsize=11,
)


# ============================================================
# EXPORT HIGH-RESOLUTION FIGURE
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_05_DPP4_cellular_localization.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight")


plt.show()


# ============================================================
# RESULT SUMMARY
# ============================================================

fib = summary[summary["cell_type"] == "Fibroblast"]


if len(fib) > 0:
    fibroblast_range = (fib["DPP4_positive_percent"].min(), fib["DPP4_positive_percent"].max())

else:
    fibroblast_range = (np.nan, np.nan)


display(
    HTML(
        f"""
        <div style="
            border-left:4px solid #777;
            padding:14px 18px;
            margin-top:12px;
            line-height:1.55;
        ">

        <b>Result</b><br>

        DPP4 is heterogeneously distributed across human skin and
        is most prominent in the <b>fibroblast compartment</b>.

        <br><br>

        Across the descriptive strata represented here,
        approximately
        <b>{fibroblast_range[0]:.1f}–{fibroblast_range[1]:.1f}%</b>
        of fibroblasts are DPP4-positive.

        <br><br>

        This supports a <b>cell-state model</b> rather than a
        requirement for whole-skin DPP4 overexpression.

        <br><br>

        <b>Important:</b>
        this panel is descriptive.
        Disease effects and DPP4–fibroblast-state relationships
        are tested using <b>donor-level inference</b> in the
        next analysis.

        <br><br>

        <b>Verdict:</b>
        CELLULAR LOCALIZATION —
        <b>SUPPORTED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
