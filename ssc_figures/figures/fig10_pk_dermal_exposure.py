"""Figure 10. Human PK supports systemic target engagement and defines the dermal exposure requirement

**Question:** Does clinically achievable human vildagliptin exposure provide a pharmacological basis for sustained DPP4 inhibition in skin?

**Data:** published human vildagliptin PK/PD + biochemical DPP4 potency + R8 plasma/skin sensitivity model
**Analysis:** human exposure-to-potency comparison + repeated-dose plasma PK simulation + skin-partition sensitivity analysis
**Analysis tools:** Python · one-compartment oral PK model · repeated dosing · tissue equilibration model · PK/PD sensitivity analysis
**Dose scenario:** 50 mg twice daily
**Important:** the plasma model is anchored to published human PK; the skin component is a sensitivity analysis, not measured human dermal PK
**Visualization:** DaVinci R5/R8 outputs + Matplotlib
"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from PIL import Image

from ssc_figures.io import OUTPUT_DIR, data_file, load_tsv
from ssc_figures.style import crop_white_margin

# ============================================================
# LOAD FROZEN DAVINCI RESULTS
# ============================================================

thresholds = load_tsv("R8_decision_threshold_summary.tsv")

plasma_diagnostic = load_tsv("R8_plasma_model_diagnostic.tsv")


# ============================================================
# LOAD PRE-RENDERED DAVINCI FIGURES
# ============================================================

systemic_img = Image.open(data_file("R5a_vildagliptin_exposure_vs_DPP4_IC50.png")).convert("RGB")


plasma_skin_img = Image.open(data_file("R8_plasma_skin_concentration_profiles.png")).convert("RGB")


dermal_img = Image.open(data_file("R8_dermal_DPP4_inhibition_profiles.png")).convert("RGB")


# ============================================================
# CROP WHITE MARGINS
# ============================================================


systemic_img = crop_white_margin(systemic_img)

plasma_skin_img = crop_white_margin(plasma_skin_img)

dermal_img = crop_white_margin(dermal_img)


# ============================================================
# R8 THRESHOLD TABLE
# ============================================================

t = thresholds.copy()

t["IC50_nM"] = pd.to_numeric(t["IC50_nM"], errors="coerce")


for column in ["min_tested_Kpu_for_50pct_interval", "min_tested_Kpu_for_80pct_interval"]:
    t[column] = pd.to_numeric(t[column], errors="coerce")


def parse_target_percent(value):
    """Parse an inhibition target (e.g. 80% or 92%) from a table cell.

    A standalone ``80`` or ``92`` in the text is used first; otherwise the
    value is parsed as a number (``%`` removed) and fractions <= 1 are
    converted to percent.

    Parameters
    ----------
    value : object
        Cell value from the R8 ``target`` column.

    Returns
    -------
    float
        Target in percent, or NaN if it cannot be parsed.
    """

    text = str(value)

    match = re.search(r"(?<!\d)(80|92)(?!\d)", text)

    if match:
        return float(match.group(1))

    try:
        value = float(text.replace("%", ""))

        if value <= 1:
            value *= 100

        return value

    except Exception:
        return np.nan


t["target_percent"] = t["target"].map(parse_target_percent)


# ============================================================
# EXTRACT CENTRAL R8 THRESHOLDS
# ============================================================


def threshold_value(ic50, target, column):
    """Look up one R8 skin-partition (Kpu) threshold.

    Reads the module-level table ``t`` built in this cell.

    Parameters
    ----------
    ic50 : float
        DPP4 IC50 scenario in nM.
    target : float
        Target inhibition in percent (80 or 92).
    column : str
        Threshold column to return.

    Returns
    -------
    float
        The threshold value.

    Raises
    ------
    RuntimeError
        If not exactly one row matches ``ic50`` and ``target``.
    """

    x = t[np.isclose(t["IC50_nM"], ic50) & np.isclose(t["target_percent"], target)]

    if len(x) != 1:
        raise RuntimeError(
            f"Expected one threshold row for IC50={ic50}, target={target}; found {len(x)}."
        )

    return float(x.iloc[0][column])


IC50_REFERENCE = 4.5


kpu_80_half = threshold_value(IC50_REFERENCE, 80, "min_tested_Kpu_for_50pct_interval")

kpu_80_most = threshold_value(IC50_REFERENCE, 80, "min_tested_Kpu_for_80pct_interval")

kpu_92_half = threshold_value(IC50_REFERENCE, 92, "min_tested_Kpu_for_50pct_interval")

kpu_92_most = threshold_value(IC50_REFERENCE, 92, "min_tested_Kpu_for_80pct_interval")


# ============================================================
# SANITY CHECK AGAINST FROZEN R8 RESULT
# ============================================================

expected = [(kpu_80_half, 0.10), (kpu_80_most, 0.20), (kpu_92_half, 0.20), (kpu_92_most, 0.50)]


for observed, reference in expected:
    if not np.isclose(observed, reference):
        raise RuntimeError(f"R8 threshold mismatch: observed={observed}, expected={reference}")


# ============================================================
# THREE-PANEL PHARMACOLOGY FIGURE
# ============================================================

fig = plt.figure(figsize=(15.0, 4.8), dpi=180)


gs = fig.add_gridspec(
    1,
    3,
    width_ratios=[0.85, 1.08, 1.07],
    left=0.025,
    right=0.985,
    top=0.76,
    bottom=0.08,
    wspace=0.10,
)


ax1 = fig.add_subplot(gs[0, 0])

ax2 = fig.add_subplot(gs[0, 1])

ax3 = fig.add_subplot(gs[0, 2])


# ============================================================
# PANEL A — HUMAN EXPOSURE VS POTENCY
# ============================================================

ax1.imshow(systemic_img, interpolation="lanczos")

ax1.axis("off")

ax1.set_title("A. Human exposure vs DPP4 potency", fontsize=10.4, fontweight="bold", pad=6)


# ============================================================
# PANEL B — HUMAN-ANCHORED PLASMA SIMULATION
# ============================================================

ax2.imshow(plasma_skin_img, interpolation="lanczos")

ax2.axis("off")

ax2.set_title("B. Repeated-dose plasma → skin simulation", fontsize=10.4, fontweight="bold", pad=6)


# ============================================================
# PANEL C — DERMAL PD
# ============================================================

ax3.imshow(dermal_img, interpolation="lanczos")

ax3.axis("off")

ax3.set_title("C. Predicted dermal DPP4 inhibition", fontsize=10.4, fontweight="bold", pad=6)


# ============================================================
# GLOBAL TITLE
# ============================================================

fig.suptitle(
    "Human pharmacology supports systemic engagement; skin exposure remains the translational gate",
    fontsize=13.7,
    fontweight="bold",
    y=0.965,
)


fig.text(
    0.5,
    0.895,
    (
        "Published human PK anchors the plasma model, which is then "
        "propagated through hypothetical skin partition scenarios"
    ),
    ha="center",
    fontsize=9.3,
)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_10_human_PK_dermal_translation.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight")


plt.show()


# ============================================================
# MODEL LOGIC — VISUAL SUMMARY
# ============================================================

display(
    HTML(
        """
        <div style="
            display:grid;
            grid-template-columns:1fr auto 1fr auto 1fr;
            align-items:center;
            gap:10px;
            margin:10px 0 12px 0;
        ">

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:10px 12px;
              text-align:center;
          ">
            <b>Published human PK</b><br>
            plasma Cmax / Tmax / exposure
          </div>

          <div style="
              font-size:22px;
              text-align:center;
          ">
            →
          </div>

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:10px 12px;
              text-align:center;
          ">
            <b>Repeated-dose plasma model</b><br>
            50 mg every 12 h
          </div>

          <div style="
              font-size:22px;
              text-align:center;
          ">
            →
          </div>

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:10px 12px;
              text-align:center;
          ">
            <b>Skin sensitivity model</b><br>
            Kpu → local concentration → DPP4 inhibition
          </div>

        </div>
        """
    )
)


# ============================================================
# COMPACT THRESHOLD TABLE
# ============================================================

decision_display = pd.DataFrame(
    {
        "Target inhibition": ["≥80%", "≥92%"],
        "≥50% of dosing interval": [f"Kpu ≥ {kpu_80_half:.2f}", f"Kpu ≥ {kpu_92_half:.2f}"],
        "≥80% of dosing interval": [f"Kpu ≥ {kpu_80_most:.2f}", f"Kpu ≥ {kpu_92_most:.2f}"],
    }
)


display(
    HTML(
        """
        <div style="
            font-size:12px;
            font-weight:600;
            margin-top:5px;
            margin-bottom:5px;
        ">
        Central dermal sensitivity scenario — IC50 = 4.5 nM
        </div>
        """
    )
)


display(decision_display.style.hide(axis="index"))


# ============================================================
# OPTIONAL MODEL DIAGNOSTIC
#
# This is the frozen DaVinci diagnostic table.
# Keep collapsed/secondary in the notebook rather than
# rebuilding scientific calculations here.
# ============================================================

display(
    HTML(
        """
        <details style="
            margin-top:10px;
            margin-bottom:10px;
        ">
          <summary style="
              cursor:pointer;
              font-weight:600;
          ">
            Show R8 plasma-model diagnostic
          </summary>

          <div id="r8-diagnostic-placeholder"
               style="margin-top:8px;">
          </div>
        </details>
        """
    )
)

display(plasma_diagnostic)


# ============================================================
# RESULT
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

        The R8 pharmacological model starts from
        <b>published human vildagliptin plasma pharmacokinetics</b>
        rather than from an arbitrary drug concentration.

        <br><br>

        A repeated-dose oral PK model was calibrated to the human
        plasma exposure scenario and used to generate the
        concentration-time profile that drives the subsequent
        skin-partition analysis.

        <br><br>

        This creates an explicit translational chain:

        <br><br>

        <b>
        clinical dose → human plasma exposure → hypothetical skin
        exposure → local DPP4 inhibition
        </b>

        <br><br>

        Under the central sensitivity scenario
        (<b>IC50 = {IC50_REFERENCE:.1f} nM</b>):

        <ul style="
            margin-top:7px;
            margin-bottom:7px;
        ">

          <li>
            ≥80% dermal inhibition for at least half of the dosing
            interval requires approximately
            <b>Kpu ≥ {kpu_80_half:.2f}</b>.
          </li>

          <li>
            ≥80% inhibition for most of the interval requires
            <b>Kpu ≥ {kpu_80_most:.2f}</b>.
          </li>

          <li>
            A stringent ≥92% inhibition target requires
            <b>Kpu ≥ {kpu_92_half:.2f}</b>
            for at least half of the interval and approximately
            <b>Kpu ≥ {kpu_92_most:.2f}</b>
            for most of the interval.
          </li>

        </ul>

        <b>Interpretation:</b><br>

        The plasma side of the model is anchored to
        <b>clinically achievable human exposure</b>.
        Therefore, systemic pharmacology is not the main uncertainty.

        The major translational unknown is the
        <b>free skin/plasma partition and actual dermal target
        engagement in patients with SSc</b>.

        <br><br>

        <b>Important:</b><br>

        This is <b>not a clinical skin PK study</b>.
        The plasma component is a simplified human-PK-anchored
        simulation, and the dermal component is a sensitivity model,
        not a validated skin PBPK model.

        <br><br>

        <b>Verdict:</b><br>

        HUMAN PLASMA PHARMACOLOGICAL ANCHOR —
        <b>SUPPORTED</b><br>

        SYSTEMIC DPP4 TARGET ENGAGEMENT —
        <b>SUPPORTED</b><br>

        DERMAL PHARMACOLOGICAL PLAUSIBILITY —
        <b>QUANTIFIED</b><br>

        HUMAN SSc SKIN TARGET ENGAGEMENT —
        <b>UNRESOLVED</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
