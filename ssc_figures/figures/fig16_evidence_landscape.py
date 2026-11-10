"""Figure 16. Integrated evidence and final translational decision

**Decision question:** Does the complete evidence package justify advancing vildagliptin for cutaneous systemic sclerosis?

**Evidence integration:** human transcriptomics · independent single-cell replication · fibroblast-state biology · network medicine · human PK/PD · functional perturbation · clinical relevance · translational precedent
**Stress tests:** LINCS perturbational transcriptomics · human genetics
**Decision level:** disease-relevant proof-of-mechanism — **not clinical efficacy**
**Visualization:** interactive evidence landscape · Plotly
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display

from ssc_figures import values
from ssc_figures.io import OUTPUT_DIR

# ============================================================
# FINAL EVIDENCE LANDSCAPE
#
# x-position indicates the ROLE of each result in the decision.
# It is NOT a quantitative score or ranking.
# ============================================================

evidence = values.EVIDENCE_LANDSCAPE


df = pd.DataFrame(evidence)


# ============================================================
# DECISION AXIS
#
# Categorical only — NOT an evidence-strength scale.
# ============================================================

ROLE_ORDER = [
    "Supports hypothesis",
    "Refines model",
    "No additional support",
    "Requires experiment",
]

ROLE_X = {role: i for i, role in enumerate(ROLE_ORDER)}


df["x"] = df["decision_role"].map(ROLE_X)


# ============================================================
# ROW ORDER
# ============================================================

DOMAIN_ORDER = [
    "Human disease",
    "Target & mechanism",
    "Drug & pharmacology",
    "Translation",
    "Model refinement",
    "Stress test",
    "Experimental gate",
]


df["domain"] = pd.Categorical(df["domain"], categories=DOMAIN_ORDER, ordered=True)


df = df.sort_values(["domain", "evidence"], ascending=[True, True]).reset_index(drop=True)


# Reverse so first item appears at top
df["y"] = len(df) - 1 - df.index


# ============================================================
# DOMAIN COLORS
#
# Color = independent evidence domain
# Position = decision role
# ============================================================

DOMAIN_COLORS = {
    "Human disease": "#3572B8",
    "Target & mechanism": "#2E8B57",
    "Drug & pharmacology": "#E69F00",
    "Translation": "#8064A2",
    "Model refinement": "#D28A2D",
    "Stress test": "#B85450",
    "Experimental gate": "#9B684A",
}


# ============================================================
# FIGURE
# ============================================================

fig = go.Figure()


for domain in DOMAIN_ORDER:
    sub = df[df["domain"] == domain]

    if len(sub) == 0:
        continue

    fig.add_trace(
        go.Scatter(
            x=sub["x"],
            y=sub["y"],
            mode="markers",
            name=domain,
            marker=dict(size=15, color=DOMAIN_COLORS[domain], line=dict(color="white", width=1.2)),
            customdata=sub[["evidence", "status", "finding", "basis", "decision_role"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br><br>"
                "<b>Role:</b> %{customdata[4]}"
                "<br>"
                "<b>Status:</b> %{customdata[1]}"
                "<br><br>"
                "<b>Finding:</b><br>%{customdata[2]}"
                "<br><br>"
                "<b>Evidence / tool:</b><br>%{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )


# ============================================================
# Y LABELS
# ============================================================

tickvals = df["y"].tolist()

ticktext = df["evidence"].tolist()


# ============================================================
# DOMAIN SEPARATORS
# ============================================================

shapes = []


for i in range(len(df) - 1):
    current_domain = str(df.loc[i, "domain"])

    next_domain = str(df.loc[i + 1, "domain"])

    if current_domain != next_domain:
        separator_y = df.loc[i, "y"] - 0.5

        shapes.append(
            dict(
                type="line",
                x0=-0.45,
                x1=3.45,
                y0=separator_y,
                y1=separator_y,
                line=dict(color="#D9DEE3", width=1),
            )
        )


# ============================================================
# DECISION REGION BACKGROUNDS
# ============================================================

ROLE_BACKGROUNDS = ["#F0F8F3", "#FFF7E8", "#FCF0EF", "#F8F1EB"]


for i, color in enumerate(ROLE_BACKGROUNDS):
    shapes.append(
        dict(
            type="rect",
            x0=i - 0.42,
            x1=i + 0.42,
            y0=-0.8,
            y1=len(df) - 0.2,
            fillcolor=color,
            opacity=0.50,
            line=dict(width=0),
            layer="below",
        )
    )


# ============================================================
# LAYOUT
# ============================================================

fig.update_layout(
    title=dict(
        text=(
            "<b>Integrated evidence landscape</b>"
            "<br>"
            "<sup>"
            "Position indicates the role of each result in the decision — "
            "not quantitative evidence strength"
            "</sup>"
        ),
        x=0.5,
        xanchor="center",
    ),
    height=680,
    margin=dict(l=260, r=35, t=90, b=85),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(size=12, color="#18212B"),
    xaxis=dict(
        tickmode="array",
        tickvals=[0, 1, 2, 3],
        ticktext=[
            "<b>SUPPORTS<br>HYPOTHESIS</b>",
            "<b>REFINES<br>MODEL</b>",
            "<b>NO ADDITIONAL<br>SUPPORT</b>",
            "<b>REQUIRES<br>EXPERIMENT</b>",
        ],
        range=[-0.48, 3.48],
        side="top",
        tickfont=dict(size=11),
        showgrid=False,
        zeroline=False,
        fixedrange=True,
    ),
    yaxis=dict(
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        tickfont=dict(size=10),
        showgrid=False,
        zeroline=False,
        fixedrange=True,
    ),
    legend=dict(orientation="h", y=-0.10, x=0.5, xanchor="center", title=None, font=dict(size=10)),
    shapes=shapes,
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
)


fig.show()


# ============================================================
# SAVE INTERACTIVE FIGURE
# ============================================================

OUTPUT_HTML = Path(OUTPUT_DIR / "Figure_16_integrated_evidence_landscape.html")


fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn")


# ============================================================
# FINAL DECISION CARD
# ============================================================

display(
    HTML(
        """
        <div style="
            border:2px solid #2E8B57;
            background:#F1F8F4;
            border-radius:12px;
            padding:17px 22px;
            margin-top:10px;
            text-align:center;
        ">

        <div style="
            font-size:12px;
            font-weight:700;
            color:#2E8B57;
            letter-spacing:0.7px;
        ">
        FINAL TRANSLATIONAL DECISION
        </div>

        <div style="
            font-size:22px;
            font-weight:800;
            margin-top:5px;
            color:#18212B;
        ">
        ADVANCE TO DISEASE-RELEVANT PROOF-OF-MECHANISM
        </div>

        <div style="
            max-width:1000px;
            margin:9px auto 0 auto;
            font-size:14px;
            line-height:1.5;
            color:#4F5B66;
        ">

        Independent human disease biology, fibroblast-state replication,
        network medicine, functional DPP4 perturbation and human
        pharmacology converge on a testable repurposing opportunity.

        <br><br>

        The critical remaining gate is
        <b>human dermal DPP4 target engagement and suppression of
        disease-relevant fibroblast fibrotic activity</b>.

        </div>

        <div style="
            margin-top:10px;
            color:#A34D47;
            font-size:13px;
            font-weight:700;
        ">
        This is not a clinical efficacy claim.
        </div>

        </div>
        """
    )
)


# ============================================================
# CONCISE FINAL CONCLUSION
# ============================================================

display(
    HTML(
        """
        <div style="
            border-left:4px solid #666;
            padding:14px 18px;
            margin-top:14px;
            line-height:1.55;
        ">

        <b>Integrated conclusion</b><br>

        The evidence supports a
        <b>mechanistically grounded and pharmacologically plausible
        opportunity to test vildagliptin for cutaneous fibrosis in
        systemic sclerosis</b>.

        <br><br>

        Human SSc datasets define a reproducible fibroblast/ECM context
        for DPP4, downstream fibrotic programs track mRSS, experimental
        perturbation provides causal antifibrotic support, and human
        pharmacology supports systemic target engagement.

        <br><br>

        The analyses also refine the original model:
        DPP4 is not globally increased, is not a positive severity
        biomarker, and does not define a simple linear fibroblast
        trajectory or the state with maximal canonical TGFβ signaling.

        <br><br>

        LINCS reversal and human genetics did not add independent
        positive support and are retained as explicit limitations.

        <br><br>

        Human dermal pharmacology has been
        <b>partially de-risked</b>:
        the required skin exposure has been quantified, but actual
        dermal exposure and DPP4 target engagement remain to be measured.

        <br><br>

        <b>
        The project therefore advances from computational/mechanistic
        validation to disease-relevant experimental proof-of-mechanism.
        </b>

        </div>
        """
    )
)


print("\nInteractive evidence landscape saved to:")

print(OUTPUT_HTML)
