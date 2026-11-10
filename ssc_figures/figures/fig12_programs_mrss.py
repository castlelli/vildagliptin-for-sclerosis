"""Figure 12. Fibrotic fibroblast programs track clinical skin severity

**Question:** Do the molecular fibroblast programs identified in SSc skin relate to clinical severity of cutaneous fibrosis?

**Data:** GSE181549 longitudinal human SSc skin transcriptomics
**Clinical endpoint:** modified Rodnan Skin Score (mRSS)
**Analysis:** baseline donor-level program scores vs mRSS + adjusted clinical models
**Analysis tools:** Python · Spearman correlation · multivariable regression
**Visualization:** DaVinci clinical association output + Matplotlib clinical summary
"""

from ssc_figures.io import OUTPUT_DIR, data_file

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
from pathlib import Path
from IPython.display import display, HTML


# ============================================================
# LOAD REPRESENTATIVE DAVINCI FIGURE
# ============================================================

activated_img = Image.open(data_file("R3c_activated_PRSS23_THBS1_vs_mRSS.png")).convert("RGB")


# ============================================================
# CROP WHITE MARGINS
# ============================================================


def crop_white_margin(image, threshold=248, padding=8):
    """Crop near-white margins from an RGB image.

    Parameters
    ----------
    image : PIL.Image.Image
        RGB image (a 3-channel array is assumed).
    threshold : int, default 248
        Pixels with any channel below this value count as content.
    padding : int, default 8
        Pixels of margin kept around the detected content.

    Returns
    -------
    PIL.Image.Image
        Cropped image, or the input unchanged if it is entirely near-white.
    """

    arr = np.asarray(image)

    mask = np.any(arr < threshold, axis=2)

    coords = np.argwhere(mask)

    if coords.size == 0:
        return image

    y0, x0 = coords.min(axis=0)

    y1, x1 = coords.max(axis=0)

    x0 = max(0, x0 - padding)

    y0 = max(0, y0 - padding)

    x1 = min(image.width, x1 + padding)

    y1 = min(image.height, y1 + padding)

    return image.crop((x0, y0, x1, y1))


activated_img = crop_white_margin(activated_img)


# ============================================================
# FROZEN R3 CLINICAL RESULTS
#
# These are outputs of the completed DaVinci R3 analysis.
# No scientific statistics are recomputed in Colab.
# ============================================================

clinical = pd.DataFrame(
    [
        {"program": "Activated\nPRSS23 / THBS1", "rho": 0.704484, "adjusted_status": "SUPPORTED"},
        {"program": "Myofibroblast", "rho": 0.691531, "adjusted_status": "SUPPORTED"},
        {"program": "ECM", "rho": 0.551557, "adjusted_status": "SUPPORTED"},
        {"program": "Progenitor", "rho": 0.438975, "adjusted_status": "DIRECTIONAL"},
        {"program": "DPP4", "rho": -0.211494, "adjusted_status": "NOT SUPPORTED"},
    ]
)


# ============================================================
# COMPACT FIGURE
# ============================================================

fig = plt.figure(figsize=(12.8, 4.8), dpi=180)


gs = fig.add_gridspec(
    1, 2, width_ratios=[1.05, 0.95], left=0.045, right=0.98, top=0.77, bottom=0.14, wspace=0.27
)


ax1 = fig.add_subplot(gs[0, 0])

ax2 = fig.add_subplot(gs[0, 1])


# ============================================================
# PANEL A — REPRESENTATIVE PATIENT-LEVEL ASSOCIATION
# ============================================================

ax1.imshow(activated_img, interpolation="lanczos")

ax1.axis("off")

ax1.set_title("A. Activated fibroblast program vs mRSS", fontsize=10.8, fontweight="bold", pad=6)


# ============================================================
# PANEL B — CLINICAL ASSOCIATION SUMMARY
# ============================================================

clinical_plot = clinical.sort_values("rho", ascending=True).reset_index(drop=True)


y = np.arange(len(clinical_plot))


# Stems
for i, row in clinical_plot.iterrows():
    ax2.hlines(y=i, xmin=min(0, row["rho"]), xmax=max(0, row["rho"]), linewidth=1.5, alpha=0.35)


# Plot supported / directional / unsupported separately
for status, marker, alpha in [
    ("SUPPORTED", "o", 1.0),
    ("DIRECTIONAL", "o", 0.55),
    ("NOT SUPPORTED", "X", 1.0),
]:
    sub = clinical_plot[clinical_plot["adjusted_status"] == status]

    ax2.scatter(sub["rho"], sub.index, s=70, marker=marker, alpha=alpha, label=status, zorder=3)


# Zero line
ax2.axvline(0, linestyle="--", linewidth=0.9, alpha=0.6)


# ============================================================
# LABEL VALUES
# ============================================================

for i, row in clinical_plot.iterrows():
    rho = row["rho"]

    offset = 0.035 if rho >= 0 else -0.035

    ax2.text(
        rho + offset,
        i,
        f"{rho:.2f}",
        ha=("left" if rho >= 0 else "right"),
        va="center",
        fontsize=8.8,
        fontweight="bold",
    )


ax2.set_yticks(y)

ax2.set_yticklabels(clinical_plot["program"], fontsize=9.2)


ax2.set_xlabel("Spearman correlation with baseline mRSS", fontsize=9.6, labelpad=6)


ax2.set_xlim(-0.40, 0.82)


ax2.set_title(
    "B. Clinical relevance across fibroblast programs", fontsize=10.8, fontweight="bold", pad=6
)


ax2.grid(axis="x", alpha=0.15)


ax2.set_axisbelow(True)


ax2.spines["top"].set_visible(False)

ax2.spines["right"].set_visible(False)


ax2.legend(frameon=False, fontsize=8.0, loc="lower right")


# ============================================================
# GLOBAL TITLE
# ============================================================

fig.suptitle(
    "Fibrotic fibroblast programs track clinical skin severity",
    fontsize=13.8,
    fontweight="bold",
    y=0.965,
)


fig.text(
    0.5,
    0.895,
    (
        "Downstream activated, myofibroblast and ECM programs "
        "track mRSS more strongly than DPP4 expression itself"
    ),
    ha="center",
    fontsize=9.3,
)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_12_fibroblast_programs_mRSS.png")


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

        Molecular fibroblast programs identified in human SSc skin
        show clear relationships with the clinical severity of
        cutaneous fibrosis.

        <br><br>

        The strongest baseline associations with mRSS are:

        <ul style="
            margin-top:7px;
            margin-bottom:7px;
        ">

          <li>
            Activated PRSS23/THBS1:
            <b>ρ ≈ 0.70</b>
          </li>

          <li>
            Myofibroblast:
            <b>ρ ≈ 0.69</b>
          </li>

          <li>
            ECM:
            <b>ρ ≈ 0.55</b>
          </li>

        </ul>

        These downstream fibrotic programs also remain supported in
        adjusted clinical models.

        <br><br>

        <b>DPP4 behaves differently:</b>
        baseline DPP4 expression shows a weak negative association
        with mRSS (<b>ρ ≈ −0.21</b>) and is not supported as an
        independent positive severity biomarker.

        <br><br>

        <b>Interpretation:</b><br>

        DPP4 appears more useful as a
        <b>marker/participant of a disease-relevant fibroblast context</b>
        than as a direct quantitative biomarker of fibrosis severity.

        The clinically relevant endpoint lies downstream:
        <b>activated fibroblast → myofibroblast → ECM output</b>.

        <br><br>

        <b>Verdict:</b><br>

        FIBROTIC FIBROBLAST PROGRAMS ↔ mRSS —
        <b>SUPPORTED</b><br>

        DPP4 AS A POSITIVE SSc SEVERITY BIOMARKER —
        <b>NOT SUPPORTED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
