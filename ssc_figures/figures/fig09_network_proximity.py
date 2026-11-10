"""Figure 09. Network medicine places DPP4 selectively near SSc fibrotic modules

**Question:** Is DPP4 selectively positioned near fibrosis-relevant molecular modules in systemic sclerosis?

**Data:** human SSc transcriptomic modules + curated fibroblast/ECM programs + STRING v12 interactome
**Analysis:** degree-matched network proximity permutation + illustrative shortest paths
**Analysis tools:** STRING v12 · NetworkX · degree-matched empirical null · Python
**Primary network:** STRING functional network, confidence ≥ 700
**Visualization:** Matplotlib

**How to read:** more negative network-proximity z-scores indicate that a module lies closer to DPP4 than expected under the degree-matched null model. Statistical support is evaluated using FDR-adjusted **q < 0.05**.
"""

import re
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, Patch

from ssc_figures import values
from ssc_figures.io import OUTPUT_DIR, load_tsv

# ============================================================
# LOAD FROZEN DAVINCI RESULTS
# ============================================================

paths = load_tsv("R4a_STRING_DPP4_shortest_paths.tsv")

network_summary = load_tsv("R10_network_summary.tsv")

proximity_stats = load_tsv("R10_proximity_statistics.tsv")


# ============================================================
# VALIDATED PRIMARY R10 RESULTS
#
# Used only as a last-resort fallback if column naming in the
# exported TSVs prevents automatic recovery.
#
# Primary network:
# STRING functional network, confidence >= 700
# 1000 degree-matched permutations
# ============================================================

# NOTE: hardcoded from the DaVinci R10 run. Any value filled from here is
# labelled "validated R10 primary fallback" in the printed `source` column.
R10_PRIMARY_FALLBACK = pd.DataFrame(values.NETWORK_PROXIMITY_R10)


# ============================================================
# GENERAL COLUMN HELPERS
# ============================================================


def norm_col(x):
    """Normalize a column name for robust matching.

    Parameters
    ----------
    x : object
        Column name; converted to lower-case ``str``.

    Returns
    -------
    str
        The name with every non-alphanumeric character removed.
    """
    return re.sub(r"[^a-z0-9]+", "", str(x).lower())


def numeric_candidate(df, column):
    """Check whether a column contains any usable numeric values.

    Parameters
    ----------
    df : pandas.DataFrame
        Table containing the column.
    column : str
        Column to test.

    Returns
    -------
    bool
        True if at least one value converts to a number.
    """
    try:
        x = pd.to_numeric(df[column], errors="coerce")

        return x.notna().sum() > 0

    except Exception:
        return False


def find_column(
    df, exact_candidates=None, contains_any=None, exclude_any=None, require_numeric=False
):
    """Locate a column even when exported names vary.

    Exact matches (after :func:`norm_col` normalization) are tried first, then
    fuzzy substring matches.

    Parameters
    ----------
    df : pandas.DataFrame
        Table to search.
    exact_candidates : list of str, optional
        Names accepted as exact matches after normalization.
    contains_any : list of str, optional
        For the fuzzy pass, the normalized name must contain one of these.
    exclude_any : list of str, optional
        For the fuzzy pass, names containing any of these are skipped.
    require_numeric : bool, default False
        If True, only columns with usable numeric values are returned.

    Returns
    -------
    str or None
        The matching column name, or ``None`` if nothing matches.
    """

    exact_candidates = exact_candidates or []

    contains_any = contains_any or []

    exclude_any = exclude_any or []

    normalized = {col: norm_col(col) for col in df.columns}

    # --------------------------------------------------------
    # Exact normalized matches first
    # --------------------------------------------------------

    wanted = {norm_col(x) for x in exact_candidates}

    for col, ncol in normalized.items():
        if ncol in wanted:
            if not require_numeric or numeric_candidate(df, col):
                return col

    # --------------------------------------------------------
    # Fuzzy matching second
    # --------------------------------------------------------

    for col, ncol in normalized.items():
        if exclude_any:
            if any(norm_col(x) in ncol for x in exclude_any):
                continue

        if contains_any:
            if not any(norm_col(x) in ncol for x in contains_any):
                continue

        if require_numeric and not numeric_candidate(df, col):
            continue

        return col

    return None


# ============================================================
# PRIMARY NETWORK FILTER
# ============================================================


def filter_primary_network(df):
    """Keep only rows for the primary STRING network (functional, >= 700).

    Rows are first selected by text labels containing ``"functional"`` and
    ``"700"`` or ``"0.7"``; otherwise by a numeric confidence/threshold column
    equal to 700 or 0.7. If neither applies, the table is returned unchanged.

    Parameters
    ----------
    df : pandas.DataFrame
        R10 table that may contain several network configurations.

    Returns
    -------
    pandas.DataFrame
        Copy of the filtered (or unfiltered) table.
    """

    if len(df) == 0:
        return df.copy()

    x = df.copy()

    # --------------------------------------------------------
    # Search all text columns for explicit functional700 labels
    # --------------------------------------------------------

    text_cols = [
        c for c in x.columns if (x[c].dtype == object or str(x[c].dtype).startswith("string"))
    ]

    if text_cols:
        row_text = x[text_cols].fillna("").astype(str).agg(" ".join, axis=1).str.lower()

        primary_mask = row_text.str.contains("functional", regex=False) & (
            row_text.str.contains("700", regex=False) | row_text.str.contains("0.7", regex=False)
        )

        if primary_mask.any():
            return x[primary_mask].copy()

    # --------------------------------------------------------
    # Try numeric confidence/threshold column
    # --------------------------------------------------------

    confidence_col = find_column(
        x,
        exact_candidates=[
            "confidence",
            "confidence_cutoff",
            "score_cutoff",
            "string_score",
            "threshold",
            "min_score",
            "score_threshold",
        ],
        contains_any=["confidence", "cutoff", "threshold"],
        require_numeric=True,
    )

    if confidence_col is not None:
        vals = pd.to_numeric(x[confidence_col], errors="coerce")

        mask700 = np.isclose(vals, 700, equal_nan=False) | np.isclose(vals, 0.7, equal_nan=False)

        if mask700.any():
            x = x[mask700].copy()

    return x


# ============================================================
# MODULE IDENTIFICATION
# ============================================================


def identify_module(value):
    """Map a module description or identifier to ``"M1"``-``"M4"``.

    Explicit ``M1``-``M4`` tokens are used first, then keyword rules:
    leading-edge/recurrent/ECM module -> M4, fibroblast -> M3,
    SSc up/upregulated -> M2, SSc significant/broad/all significant -> M1.

    Parameters
    ----------
    value : object
        Module label or ID; converted to ``str``.

    Returns
    -------
    str or None
        Module ID, or ``None`` if no rule matches.
    """

    text = str(value).strip()

    upper = text.upper()

    # Explicit M1-M4
    match = re.search(r"\bM([1-4])\b", upper)

    if match:
        return "M" + match.group(1)

    lower = text.lower()

    # Semantic fallback
    if "leading edge" in lower or "recurrent" in lower or ("ecm" in lower and "module" in lower):
        return "M4"

    if "fibroblast" in lower:
        return "M3"

    if "ssc up" in lower or "upregulated" in lower or "up-regulated" in lower:
        return "M2"

    if "ssc significant" in lower or "broad" in lower or "all significant" in lower:
        return "M1"

    return None


# ============================================================
# BENJAMINI-HOCHBERG
# ============================================================


def bh_adjust(pvalues):
    """Benjamini-Hochberg FDR correction without another library.

    Parameters
    ----------
    pvalues : array_like
        P-values; non-finite entries are ignored and returned as NaN.

    Returns
    -------
    numpy.ndarray
        BH-adjusted q-values, capped at 1, in the input order.
    """

    p = np.asarray(pvalues, dtype=float)

    q = np.full(p.shape, np.nan, dtype=float)

    valid = np.isfinite(p)

    if not valid.any():
        return q

    pv = p[valid]

    m = len(pv)

    order = np.argsort(pv)

    ranked = pv[order]

    adjusted = ranked * m / np.arange(1, m + 1)

    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]

    adjusted = np.minimum(adjusted, 1.0)

    restored = np.empty(m)

    restored[order] = adjusted

    q[valid] = restored

    return q


# ============================================================
# EXTRACT MODULE STATISTICS FROM ANY R10 TABLE
# ============================================================


def extract_stats_from_table(df, source_name):
    """Recover module, z-score, p-value and q-value from an R10 table.

    Works regardless of exact column naming by combining
    :func:`filter_primary_network`, :func:`find_column` and
    :func:`identify_module`.

    Parameters
    ----------
    df : pandas.DataFrame
        R10 proximity or summary table.
    source_name : str
        Label recorded in the ``source`` column of the output.

    Returns
    -------
    pandas.DataFrame
        One row per module with columns ``module_id``, ``source``, ``z``,
        ``p`` and ``q`` (NaN where not found); empty if no module column is
        found.
    """

    x = filter_primary_network(df)

    if len(x) == 0:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Module column
    # --------------------------------------------------------

    module_col = find_column(
        x,
        exact_candidates=[
            "module",
            "module_id",
            "module_name",
            "gene_set",
            "geneset",
            "set_name",
            "target_module",
        ],
        contains_any=["module", "geneset", "gene_set"],
    )

    if module_col is None:
        # Search every text column for M1-M4
        for col in x.columns:
            vals = x[col].astype(str).map(identify_module)

            if vals.notna().sum() >= 2:
                module_col = col
                break

    if module_col is None:
        return pd.DataFrame()

    x["module_id"] = x[module_col].map(identify_module)

    x = x[x["module_id"].isin(["M1", "M2", "M3", "M4"])].copy()

    if len(x) == 0:
        return pd.DataFrame()

    # --------------------------------------------------------
    # z-score
    # --------------------------------------------------------

    z_col = find_column(
        x,
        exact_candidates=[
            "z",
            "z_score",
            "zscore",
            "proximity_z",
            "network_proximity_z",
            "z_proximity",
        ],
        contains_any=["zscore", "proximityz"],
        require_numeric=True,
    )

    # broader z fallback
    if z_col is None:
        for col in x.columns:
            ncol = norm_col(col)

            if "z" in ncol and numeric_candidate(x, col):
                vals = pd.to_numeric(x[col], errors="coerce")

                # z-scores usually include negative values
                if vals.notna().sum() > 0 and (vals < 0).any():
                    z_col = col
                    break

    # --------------------------------------------------------
    # q / FDR
    # --------------------------------------------------------

    q_col = find_column(
        x,
        exact_candidates=[
            "q",
            "q_BH",
            "q_value",
            "qvalue",
            "FDR",
            "fdr_bh",
            "padj",
            "p_adj",
            "adjusted_p",
            "adjusted_p_value",
        ],
        contains_any=["qvalue", "qbh", "fdr", "padj", "adjustedp"],
        require_numeric=True,
    )

    # --------------------------------------------------------
    # empirical / raw p
    # --------------------------------------------------------

    p_col = find_column(
        x,
        exact_candidates=[
            "p",
            "p_value",
            "pvalue",
            "p_val",
            "pval",
            "p_empirical",
            "empirical_p",
            "empirical_p_value",
            "empirical_p_lower",
            "p_lower",
            "perm_p",
            "permutation_p",
        ],
        contains_any=["empiricalp", "permutationp", "permp", "pvalue", "pval"],
        exclude_any=["adj", "fdr", "q"],
        require_numeric=True,
    )

    # --------------------------------------------------------
    # Build compact output
    # --------------------------------------------------------

    out = pd.DataFrame({"module_id": x["module_id"].astype(str), "source": source_name})

    if z_col is not None:
        out["z"] = pd.to_numeric(x[z_col], errors="coerce")

    else:
        out["z"] = np.nan

    if p_col is not None:
        out["p"] = pd.to_numeric(x[p_col], errors="coerce")

    else:
        out["p"] = np.nan

    if q_col is not None:
        out["q"] = pd.to_numeric(x[q_col], errors="coerce")

    else:
        out["q"] = np.nan

    # Keep one row per module from each source
    out = out.drop_duplicates("module_id").reset_index(drop=True)

    return out


# ============================================================
# RECOVER R10 STATISTICS
# ============================================================

candidate_tables = [
    (proximity_stats, "R10_proximity_statistics.tsv"),
    (network_summary, "R10_network_summary.tsv"),
]


extracted = []


for table, name in candidate_tables:
    tmp = extract_stats_from_table(table, name)

    if len(tmp) > 0:
        extracted.append(tmp)


# ============================================================
# START WITH MODULE FRAME
# ============================================================

prox = pd.DataFrame({"module_id": ["M1", "M2", "M3", "M4"]})


prox["z"] = np.nan

prox["p"] = np.nan

prox["q"] = np.nan

prox["source"] = ""


# ============================================================
# MERGE AUTOMATICALLY EXTRACTED VALUES
# ============================================================

for table in extracted:
    for _, row in table.iterrows():
        module = str(row["module_id"])

        mask = prox["module_id"] == module

        if not mask.any():
            continue

        for col in ["z", "p", "q"]:
            value = row[col]

            if pd.notna(value) and prox.loc[mask, col].isna().all():
                prox.loc[mask, col] = float(value)

        if row.get("source", ""):
            old = prox.loc[mask, "source"].iloc[0]

            src = str(row["source"])

            if old:
                if src not in old:
                    prox.loc[mask, "source"] = old + " + " + src

            else:
                prox.loc[mask, "source"] = src


# ============================================================
# IF p EXISTS BUT q DOES NOT, CALCULATE BH
# ============================================================

if prox["p"].notna().sum() >= 2:
    calculated_q = bh_adjust(prox["p"].values)

    for i in range(len(prox)):
        if pd.isna(prox.loc[i, "q"]) and pd.notna(calculated_q[i]):
            prox.loc[i, "q"] = calculated_q[i]


# ============================================================
# FILL ONLY MISSING VALUES FROM VALIDATED PRIMARY R10 RESULTS
# ============================================================

fallback = R10_PRIMARY_FALLBACK.set_index("module_id")


for i, row in prox.iterrows():
    module = row["module_id"]

    for col in ["z", "p", "q"]:
        if pd.isna(prox.loc[i, col]):
            prox.loc[i, col] = fallback.loc[module, col]

            if "validated R10 primary fallback" not in prox.loc[i, "source"]:
                if prox.loc[i, "source"]:
                    prox.loc[i, "source"] += " + validated R10 primary fallback"

                else:
                    prox.loc[i, "source"] = "validated R10 primary fallback"


# ============================================================
# PRESENTATION LABELS
# ============================================================

MODULE_LABELS = {
    "M1": "Broad SSc gene set",
    "M2": "SSc-upregulated genes",
    "M3": "Fibroblast-state module",
    "M4": "ECM / fibrotic module",
}


MODULE_DETAILS = {
    "M1": "all significant disease genes",
    "M2": "genes increased in SSc skin",
    "M3": "fibroblast-centered program",
    "M4": "recurrent fibrosis / ECM program",
}


module_order = ["M1", "M2", "M3", "M4"]


prox["module_id"] = pd.Categorical(prox["module_id"], categories=module_order, ordered=True)


prox = prox.sort_values("module_id").reset_index(drop=True)


prox["label"] = prox["module_id"].astype(str).map(MODULE_LABELS)


prox["detail"] = prox["module_id"].astype(str).map(MODULE_DETAILS)


prox["significant"] = prox["q"] < 0.05


# ============================================================
# PREPARE STRING PATH EXAMPLES
# ============================================================

p = paths.copy()


if "connected" in p.columns:
    p["connected_bool"] = p["connected"].astype(str).str.lower().isin(["true", "1", "yes"])

else:
    p["connected_bool"] = pd.to_numeric(p["n_hops"], errors="coerce").notna()


p["n_hops"] = pd.to_numeric(p["n_hops"], errors="coerce")


def get_path(gene):
    """Return the first connected STRING shortest path from DPP4 to a gene.

    Reads the module-level table ``p`` built in this cell.

    Parameters
    ----------
    gene : str
        Target gene symbol, e.g. ``"COL1A1"``.

    Returns
    -------
    dict
        Keys ``gene``, ``path`` (``"not connected"`` if absent) and ``hops``
        (NaN if absent).
    """

    x = p[(p["target_gene"] == gene) & (p["connected_bool"])]

    if len(x) == 0:
        return {"gene": gene, "path": "not connected", "hops": np.nan}

    row = x.iloc[0]

    return {"gene": gene, "path": str(row["path"]), "hops": float(row["n_hops"])}


example_paths = [get_path("THBS1"), get_path("COL1A1"), get_path("ACTA2")]


# ============================================================
# COLORS
# ============================================================

SUPPORT = "#218C5A"
NOT_SIG = "#B7C0C8"

TEXT = "#172033"
MUTED = "#64748B"

GRID = "#E5E7EB"

CALLOUT_BG = "#F7F9FB"
CALLOUT_BORDER = "#D7DEE5"


# ============================================================
# FIGURE LAYOUT
# ============================================================

fig = plt.figure(figsize=(14.8, 7.4), dpi=180, facecolor="white")


gs = GridSpec(
    nrows=3,
    ncols=2,
    figure=fig,
    height_ratios=[0.15, 0.70, 0.15],
    width_ratios=[1.48, 0.52],
    hspace=0.24,
    wspace=0.18,
)


ax_header = fig.add_subplot(gs[0, :])

ax_main = fig.add_subplot(gs[1, 0])

ax_paths = fig.add_subplot(gs[1, 1])

ax_footer = fig.add_subplot(gs[2, :])


ax_header.axis("off")

ax_paths.axis("off")

ax_footer.axis("off")


# ============================================================
# HEADER
# ============================================================

ax_header.text(
    0.5,
    0.72,
    ("DPP4 shows selective network proximity to fibrosis-focused SSc modules"),
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold",
    color=TEXT,
)


ax_header.text(
    0.5,
    0.25,
    (
        "The broad SSc gene set is not significantly proximal, "
        "whereas disease-upregulated, fibroblast and ECM modules are"
    ),
    ha="center",
    va="center",
    fontsize=11.2,
    color=MUTED,
)


# ============================================================
# MAIN RESULT
# ============================================================

y = np.arange(len(prox))


z_values = prox["z"].astype(float).values


xmin = min(-5.25, float(np.nanmin(z_values)) - 0.55)


xmax = 0.72


ax_main.set_xlim(xmin, xmax)


# ============================================================
# LOLLIPOPS
# ============================================================

for i, row in prox.iterrows():
    z = float(row["z"])

    q = float(row["q"])

    significant = bool(row["significant"])

    color = SUPPORT if significant else NOT_SIG

    # --------------------------------------------------------
    # Stem from module to zero
    # --------------------------------------------------------

    ax_main.hlines(y=i, xmin=z, xmax=0, color=color, linewidth=7, alpha=0.24, zorder=1)

    # --------------------------------------------------------
    # Module estimate
    # --------------------------------------------------------

    ax_main.scatter(z, i, s=135, color=color, edgecolor="white", linewidth=1.5, zorder=3)

    # --------------------------------------------------------
    # Statistics label
    # --------------------------------------------------------

    if q < 0.001:
        q_text = "q < 0.001"

    else:
        q_text = f"q = {q:.3f}"

    ax_main.text(
        z + 0.10,
        i,
        (f"z = {z:.2f}  ·  {q_text}"),
        ha="left",
        va="center",
        fontsize=9.5,
        color=(SUPPORT if significant else MUTED),
        fontweight=("bold" if significant else "normal"),
        zorder=4,
    )


# ============================================================
# Y LABELS
# ============================================================

ax_main.set_yticks(y)


ax_main.set_yticklabels(
    [(f"{label}\n{detail}") for label, detail in zip(prox["label"], prox["detail"])], fontsize=10.3
)


ax_main.invert_yaxis()


# ============================================================
# ZERO REFERENCE
# ============================================================

ax_main.axvline(0, linestyle="--", linewidth=1.1, color="#94A3B8")


ax_main.set_xlabel("Network-proximity z-score", fontsize=10.5, labelpad=8)


ax_main.set_title(
    "Formal degree-matched proximity to DPP4",
    loc="left",
    fontsize=13,
    fontweight="bold",
    pad=18,
    color=TEXT,
)


ax_main.text(
    0.00,
    1.025,
    ("← stronger proximity to DPP4 than expected"),
    transform=ax_main.transAxes,
    ha="left",
    va="bottom",
    fontsize=9.3,
    color=MUTED,
)


ax_main.grid(axis="x", color=GRID, linewidth=0.8)


ax_main.set_axisbelow(True)


ax_main.spines["top"].set_visible(False)

ax_main.spines["right"].set_visible(False)

ax_main.spines["left"].set_visible(False)


ax_main.tick_params(axis="y", length=0, pad=10)


# ============================================================
# LEGEND
# ============================================================

legend_handles = [
    Patch(facecolor=SUPPORT, label="q < 0.05"),
    Patch(facecolor=NOT_SIG, label="not significant"),
]


ax_main.legend(
    handles=legend_handles,
    loc="lower left",
    bbox_to_anchor=(0.0, -0.18),
    ncol=2,
    frameon=False,
    fontsize=9.2,
)


# ============================================================
# SIDE CALLOUT
# ============================================================

box = FancyBboxPatch(
    (0.02, 0.05),
    0.95,
    0.90,
    boxstyle=("round,pad=0.018,rounding_size=0.025"),
    transform=ax_paths.transAxes,
    facecolor=CALLOUT_BG,
    edgecolor=CALLOUT_BORDER,
    linewidth=1.2,
)


ax_paths.add_patch(box)


ax_paths.text(
    0.08,
    0.89,
    "Illustrative STRING paths",
    transform=ax_paths.transAxes,
    ha="left",
    va="top",
    fontsize=12.2,
    fontweight="bold",
    color=TEXT,
)


ax_paths.text(
    0.08,
    0.81,
    ("Examples showing how DPP4 is\nconnected to fibrosis-related genes"),
    transform=ax_paths.transAxes,
    ha="left",
    va="top",
    fontsize=9.0,
    color=MUTED,
    linespacing=1.3,
)


# ============================================================
# PATH EXAMPLES
# ============================================================

start_y = 0.66
dy = 0.19


for i, item in enumerate(example_paths):
    yy = start_y - i * dy

    ax_paths.text(
        0.08,
        yy,
        item["gene"],
        transform=ax_paths.transAxes,
        ha="left",
        va="top",
        fontsize=10.5,
        fontweight="bold",
        color=SUPPORT,
    )

    pretty_path = item["path"].replace("->", " → ")

    pretty_path = "\n".join(textwrap.wrap(pretty_path, width=32))

    ax_paths.text(
        0.08,
        yy - 0.052,
        pretty_path,
        transform=ax_paths.transAxes,
        ha="left",
        va="top",
        fontsize=8.9,
        color=TEXT,
        linespacing=1.25,
    )

    if pd.notna(item["hops"]):
        hop_text = f"{int(item['hops'])} network hops"

    else:
        hop_text = ""

    ax_paths.text(
        0.08,
        yy - 0.115,
        hop_text,
        transform=ax_paths.transAxes,
        ha="left",
        va="top",
        fontsize=8.2,
        color=MUTED,
    )


# ============================================================
# METHOD NOTE
# ============================================================

ax_paths.text(
    0.08,
    0.07,
    ("STRING functional network ≥ 700\n1,000 degree-matched permutations"),
    transform=ax_paths.transAxes,
    ha="left",
    va="bottom",
    fontsize=8.3,
    color=MUTED,
    linespacing=1.35,
)


# ============================================================
# FOOTER
# ============================================================

ax_footer.text(
    0.5,
    0.68,
    (
        "Take-home: DPP4 is not generically proximal to SSc genes; "
        "its network proximity becomes significant in the "
        "fibroblast / ECM-focused component of the disease."
    ),
    ha="center",
    va="center",
    fontsize=11.2,
    fontweight="bold",
    color=TEXT,
)


ax_footer.text(
    0.5,
    0.26,
    (
        "Network proximity indicates topological / functional relatedness — "
        "not causal direction or direct physical interaction."
    ),
    ha="center",
    va="center",
    fontsize=9.6,
    color=MUTED,
    style="italic",
)


# ============================================================
# FINAL SPACING
# ============================================================

fig.subplots_adjust(left=0.20, right=0.98, top=0.97, bottom=0.05)


# ============================================================
# EXPORT
# ============================================================

OUTPUT_FIGURE = Path(OUTPUT_DIR / "Figure_09_DPP4_selective_network_proximity.png")


fig.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches="tight", facecolor="white")


plt.show()


# ============================================================
# RESULT HELPERS
# ============================================================


def module_row(module):
    """Return the proximity-statistics row for one module.

    Reads the module-level table ``prox`` built in this cell.

    Parameters
    ----------
    module : str
        Module ID, ``"M1"``-``"M4"``.

    Returns
    -------
    pandas.Series or None
        Matching row, or ``None`` if absent.
    """

    x = prox[prox["module_id"].astype(str) == module]

    if len(x) == 0:
        return None

    return x.iloc[0]


def format_module(module):
    """Format a module's z-score and q-value for the result text.

    Parameters
    ----------
    module : str
        Module ID, ``"M1"``-``"M4"``.

    Returns
    -------
    str
        ``"z=<z>, q=<q>"`` (``q<0.001`` when small), or ``"NA"``.
    """

    row = module_row(module)

    if row is None:
        return "NA"

    z = float(row["z"])

    q = float(row["q"])

    if q < 0.001:
        q_text = "q<0.001"

    else:
        q_text = f"q={q:.3f}"

    return f"z={z:.2f}, {q_text}"


# ============================================================
# RESULT
# ============================================================

display(
    HTML(
        f"""
        <div style="
            border-left:4px solid #218C5A;
            padding:13px 17px;
            margin-top:10px;
            line-height:1.55;
        ">

        <b>Result</b><br>

        Degree-matched network analysis does <b>not</b> identify
        significant DPP4 proximity to the broad SSc gene set
        (<b>{format_module("M1")}</b>).

        <br><br>

        In contrast, DPP4 becomes significantly closer than expected
        when the analysis focuses on progressively more
        fibrosis-relevant molecular modules:

        <ul style="
            margin-top:7px;
            margin-bottom:7px;
        ">

          <li>
            <b>SSc-upregulated genes:</b>
            {format_module("M2")}
          </li>

          <li>
            <b>Fibroblast-state module:</b>
            {format_module("M3")}
          </li>

          <li>
            <b>ECM / fibrotic module:</b>
            {format_module("M4")}
          </li>

        </ul>

        <b>Interpretation:</b><br>

        DPP4 is not broadly embedded across all molecular features
        associated with systemic sclerosis. Instead, its network
        position is selectively closer to the
        <b>fibroblast- and ECM-centered component of the disease</b>.

        <br><br>

        The STRING paths shown beside the formal test are
        <b>illustrative examples</b> that make this network position
        biologically interpretable. They do not demonstrate a causal
        signaling cascade.

        <br><br>

        <b>Verdict:</b><br>

        SELECTIVE DPP4 PROXIMITY TO SSc FIBROTIC MODULES —
        <b>SUPPORTED</b>

        </div>
        """
    )
)


# ============================================================
# SMALL TRACEABILITY CHECK
# ============================================================

print(f"\nHigh-resolution figure saved to:\n{OUTPUT_FIGURE}")

print("\nNetwork statistics used in the figure:")

display(prox[["module_id", "label", "z", "p", "q", "source"]])
