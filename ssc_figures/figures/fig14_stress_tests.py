"""Figure 14. Independent stress tests define the limits of the hypothesis

**Question:** Do perturbational transcriptomics or human genetics independently strengthen the DPP4–SSc repurposing hypothesis?

**R16:** vildagliptin + DPP4 genetic perturbation signatures from LINCS/L1000
**R17:** GWAS Catalog · GTEx · Open Targets · Ensembl
**Analysis:** human-disease signature reversal + GWAS/locus/eQTL audit
**Analysis tools:** SigCom LINCS · Spearman reversal · Wilcoxon · BH-FDR · GWAS Catalog · GTEx · Open Targets
**Primary R16 analysis:** top 500 up + 500 down disease genes · 24 h · 1.11 µM
**Interpretation:** absence of additional support is treated as a stress test, not automatic falsification
**Visualization:** Matplotlib
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from matplotlib.patches import FancyBboxPatch

from ssc_figures.io import OUTPUT_DIR, load_tsv, require

# ============================================================
# LOAD FROZEN DAVINCI RESULTS
# ============================================================

r16_all = load_tsv("R16_primary_vildagliptin_summary.tsv")

# Documented but not drawn (the original cell loaded them without using them).
require(
    "R16_primary_vildagliptin_verdict.tsv",
    "R16_target_validation_verdict.tsv",
    "R16_drug_target_concordance.tsv",
)

r17 = load_tsv("R17_human_genetics_summary.tsv")

# NOTE: only `r16_all` feeds the figure; `r17` is only checked for one row,
# and the genetics cards and verdict text below are hardcoded.


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_cols = [
    "top_n_each_direction",
    "n_cell_lines",
    "median_rho",
    "CI95_median_low",
    "CI95_median_high",
    "fraction_reversal",
    "p_Wilcoxon_less_zero",
    "q_BH",
]

for col in numeric_cols:
    if col in r16_all.columns:
        r16_all[col] = pd.to_numeric(r16_all[col], errors="coerce")


# ============================================================
# IMPORTANT — PRIMARY R16 ANALYSIS ONLY
#
# Frozen primary design:
# top 500 disease-up + top 500 disease-down genes.
#
# The table also contains top250/top1000 sensitivity analyses.
# Those must NOT be mixed into the primary visualization.
# ============================================================

if "top_n_each_direction" in r16_all.columns:
    r16 = r16_all[r16_all["top_n_each_direction"] == 500].copy()

else:
    # Fallback only if the summary table is already primary-only.
    r16 = r16_all.copy()


# Integrity: exactly one row for R1, R11 and R2.
expected_datasets = {"R1", "R11", "R2"}

observed_datasets = set(r16["dataset"].astype(str))


if len(r16) != 3 or observed_datasets != expected_datasets:
    raise RuntimeError(
        "Primary R16 filtering did not return exactly "
        "one result for R1, R11 and R2.\n"
        f"Rows found: {len(r16)}\n"
        f"Datasets: {sorted(observed_datasets)}\n"
        f"Available columns: {list(r16_all.columns)}"
    )


# ============================================================
# R16 ORDER / LABELS
# ============================================================

dataset_order = ["R1", "R11", "R2"]

dataset_labels = {
    "R1": "GSE58095\nwhole skin",
    "R11": "GSE249279\nfibroblasts",
    "R2": "GSE138669\nfibroblasts",
}


r16["dataset"] = pd.Categorical(r16["dataset"], categories=dataset_order, ordered=True)

r16 = r16.sort_values("dataset").reset_index(drop=True)

r16["display"] = r16["dataset"].astype(str).map(dataset_labels)


# ============================================================
# R17 SUMMARY
# ============================================================

if len(r17) != 1:
    raise RuntimeError(f"Expected one R17 summary row; found {len(r17)}.")

g = r17.iloc[0]


genetics = [
    {
        "title": "Direct SSc GWAS",
        "subtitle": "association mapped to DPP4",
        "status": "NOT IDENTIFIED",
    },
    {
        "title": "DPP4 locus",
        "subtitle": "SSc association within ±500 kb",
        "status": "NOT IDENTIFIED",
    },
    {
        "title": "Relevant-tissue cis-eQTL",
        "subtitle": "skin / transformed fibroblasts",
        "status": "NOT IDENTIFIED",
    },
    {
        "title": "Colocalization",
        "subtitle": "pre-specified prerequisites met",
        "status": "NO CANDIDATE",
    },
]


# ============================================================
# COLORS
# ============================================================

C = {
    "R1": "#3572B8",
    "R11": "#7851A9",
    "R2": "#D97732",
    "zero": "#89939D",
    "negative": "#B85450",
    "negative_soft": "#FCF5F4",
    "text": "#18212B",
    "muted": "#66727D",
    "border": "#CDD3D9",
    "soft": "#F6F8FA",
}


# ============================================================
# FIGURE
# ============================================================

fig = plt.figure(figsize=(12.8, 4.7), dpi=180)


gs = fig.add_gridspec(
    1, 2, width_ratios=[1.05, 0.95], left=0.075, right=0.975, top=0.74, bottom=0.18, wspace=0.30
)


ax1 = fig.add_subplot(gs[0, 0])

ax2 = fig.add_subplot(gs[0, 1])


# ============================================================
# PANEL A — PRIMARY VILDAGLIPTIN REVERSAL
# ============================================================

y = np.arange(len(r16))[::-1]


for i, row in r16.iterrows():
    yi = y[i]

    dataset = str(row["dataset"])

    median = float(row["median_rho"])

    ci_low = float(row["CI95_median_low"])

    ci_high = float(row["CI95_median_high"])

    ax1.errorbar(
        median,
        yi,
        xerr=np.array([[median - ci_low], [ci_high - median]]),
        fmt="o",
        markersize=7.2,
        linewidth=1.7,
        capsize=0,
        color=C[dataset],
        zorder=3,
    )

    # q-value positioned consistently
    ax1.text(
        0.050, yi, f"q = {row['q_BH']:.2f}", ha="right", va="center", fontsize=8.3, color=C["muted"]
    )


# No reversal / mimicry boundary
ax1.axvline(0, linestyle="--", linewidth=1.0, color=C["zero"], alpha=0.8)


ax1.set_xlim(-0.052, 0.052)

ax1.set_ylim(-0.60, 2.60)


ax1.set_yticks(y)

ax1.set_yticklabels(r16["display"], fontsize=9.0)


ax1.set_xlabel("Median Spearman ρ: SSc disease effect vs perturbation", fontsize=9.2, labelpad=7)


ax1.tick_params(axis="x", labelsize=8.3)


ax1.grid(axis="x", alpha=0.15)

ax1.set_axisbelow(True)

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)


ax1.set_title("A. Vildagliptin transcriptomic reversal", fontsize=10.8, fontweight="bold", pad=7)


# Direction labels inside the panel
ax1.text(
    0.02,
    0.97,
    "← reversal",
    transform=ax1.transAxes,
    ha="left",
    va="top",
    fontsize=8.3,
    color=C["muted"],
)


ax1.text(
    0.98,
    0.97,
    "mimicry →",
    transform=ax1.transAxes,
    ha="right",
    va="top",
    fontsize=8.3,
    color=C["muted"],
)


# ============================================================
# PANEL B — HUMAN GENETICS
# ============================================================

ax2.set_xlim(0, 1)

ax2.set_ylim(0, 1)

ax2.axis("off")


ax2.set_title("B. Direct human genetic support", fontsize=10.8, fontweight="bold", pad=7)


card_positions = [0.80, 0.60, 0.40, 0.20]


for item, cy in zip(genetics, card_positions):
    card = FancyBboxPatch(
        (0.04, cy - 0.067),
        0.92,
        0.134,
        boxstyle=("round,pad=0.010,rounding_size=0.015"),
        facecolor=C["soft"],
        edgecolor=C["border"],
        linewidth=1.0,
    )

    ax2.add_patch(card)

    # Negative/not-identified icon
    ax2.scatter(0.105, cy, s=62, marker="X", color=C["negative"], zorder=3)

    ax2.text(
        0.165,
        cy + 0.022,
        item["title"],
        ha="left",
        va="center",
        fontsize=9.2,
        fontweight="bold",
        color=C["text"],
    )

    ax2.text(
        0.165, cy - 0.025, item["subtitle"], ha="left", va="center", fontsize=8.1, color=C["muted"]
    )

    ax2.text(
        0.92,
        cy,
        item["status"],
        ha="right",
        va="center",
        fontsize=8.3,
        fontweight="bold",
        color=C["negative"],
    )


# ============================================================
# GLOBAL TITLE
# ============================================================

fig.suptitle(
    "Independent stress tests define the limits of the hypothesis",
    fontsize=13.8,
    fontweight="bold",
    y=0.965,
)


fig.text(
    0.5,
    0.895,
    ("Neither global LINCS reversal nor direct human genetics adds independent positive support"),
    ha="center",
    fontsize=9.3,
    color=C["muted"],
)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_14_stress_tests_R16_R17.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight")


plt.show()


# ============================================================
# PRIMARY R16 VALUES
# ============================================================

r16_display = r16[
    ["dataset", "n_cell_lines", "median_rho", "CI95_median_low", "CI95_median_high", "q_BH"]
].copy()


r16_display.columns = ["Dataset", "LINCS cell lines", "Median rho", "CI low", "CI high", "FDR q"]


display(HTML("<b>Primary R16 result — top 500 up + 500 down</b>"))

display(
    r16_display.style.format(
        {"Median rho": "{:.4f}", "CI low": "{:.4f}", "CI high": "{:.4f}", "FDR q": "{:.3f}"}
    ).hide(axis="index")
)


# ============================================================
# COMPACT STATUS STRIP
# ============================================================

display(
    HTML(
        """
        <div style="
            display:grid;
            grid-template-columns:repeat(3,1fr);
            gap:10px;
            margin:12px 0;
        ">

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:9px 12px;
          ">
            <b>Vildagliptin / LINCS</b><br>
            <span style="
                color:#a34d47;
                font-weight:700;
            ">
            NOT REPLICATED
            </span>
          </div>

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:9px 12px;
          ">
            <b>DPP4 KO / KD</b><br>
            <span style="
                color:#a34d47;
                font-weight:700;
            ">
            NOT REPLICATED
            </span>
          </div>

          <div style="
              border:1px solid #ddd;
              border-radius:8px;
              padding:9px 12px;
          ">
            <b>Human genetics</b><br>
            <span style="
                color:#a34d47;
                font-weight:700;
            ">
            NOT IDENTIFIED
            </span>
          </div>

        </div>
        """
    )
)


# ============================================================
# INTERPRETATION
# ============================================================

display(
    HTML(
        """
        <div style="
            border-left:4px solid #666;
            padding:13px 17px;
            margin-top:8px;
            line-height:1.52;
        ">

        <b>Result</b><br>

        The pre-specified primary LINCS analysis does
        <b>not demonstrate reproducible vildagliptin reversal</b>
        of human SSc disease signatures.

        The three independent human signatures show median
        correlations close to zero, with confidence intervals
        spanning zero and non-significant FDR values.

        <br><br>

        DPP4 CRISPR knockout and shRNA perturbations also fail to
        reproducibly reverse the same disease signatures.

        <br><br>

        Human genetics independently provides
        <b>no direct positive support</b>:
        no reviewed SSc GWAS association maps directly to DPP4,
        no association lies within the pre-specified ±500 kb locus,
        and no significant DPP4 cis-eQTL was identified in the
        reviewed skin/fibroblast GTEx contexts.

        <br><br>

        <b>Interpretation:</b><br>

        These results weaken claims of
        <b>global transcriptomic rescue</b> or
        <b>germline genetically driven DPP4 causality</b>.

        They do not directly falsify the pharmacological hypothesis.

        LINCS predominantly represents transformed cell-line
        perturbations rather than primary SSc dermal fibroblasts,
        while pharmacological modification of an acquired fibrotic
        state does not require DPP4 to be a germline disease-risk locus.

        <br><br>

        <b>Verdict:</b><br>

        VILDAGLIPTIN GLOBAL TRANSCRIPTOMIC REVERSAL —
        <b>NOT REPLICATED</b><br>

        DPP4 GENETIC-PERTURBATION REVERSAL —
        <b>NOT REPLICATED</b><br>

        DIRECT HUMAN GENETIC SUPPORT —
        <b>NOT IDENTIFIED</b><br>

        HYPOTHESIS FALSIFIED —
        <b>NO</b>

        </div>
        """
    )
)


print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")
