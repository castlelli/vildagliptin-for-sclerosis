# Vildagliptin for skin fibrosis in systemic sclerosis

**[Read the project page →](https://castlelli.github.io/vildagliptin-for-sclerosis/)** · [Versão em português](https://castlelli.github.io/vildagliptin-for-sclerosis/pt/)

[![Project page: "Can a diabetes drug quiet the cells that harden skin?"](public/og.png)](https://castlelli.github.io/vildagliptin-for-sclerosis/)

Vildagliptin is an approved type 2 diabetes drug that blocks the enzyme DPP-4. In systemic sclerosis (SSc), DPP-4 marks the progenitor fibroblasts that turn into collagen-producing myofibroblasts.<sup>1,2</sup> Over a seven-day drug-repositioning hackathon (pitched 31 August 2026), a five-person team tested whether that overlap is worth a laboratory experiment, across seven independent evidence layers and four public human skin cohorts.

> **Verdict: advance to a disease-relevant proof-of-mechanism experiment.** This is a research hypothesis, not a clinical efficacy claim and not medical advice.

## Results at a glance

| Layer | Finding | Role |
| --- | --- | --- |
| Bulk skin (GSE58095) | Strong collagen/ECM program in SSc; *DPP4* itself not increased | supports |
| Single cell (GSE138669) | DPP4⁺ cells concentrate in fibroblasts (≈15% SSc vs ≈10% control) | supports |
| Replication (GSE249279) | DPP4⁺ fibroblasts track progenitor (β = 0.82) and ECM (β = 0.59) states | supports |
| Fibroblast graph (PAGA) | DPP4-high/activated/ECM share a branch; myofibroblasts also reachable by another route | refines |
| Signalling (PROGENy, CollecTRI) | DPP4⁺ cells have *lower* TGFβ/MAPK/NF-κB/JAK–STAT activity | refines |
| Network (STRING v12) | Close to the ECM module (z = −4.52, q = 0.002), not to SSc genes overall (z = −0.99) | supports |
| Clinical (GSE181549) | Activated, myofibroblast and ECM programs track mRSS (ρ 0.55–0.70); DPP4 does not (ρ = −0.21) | supports |
| Pharmacology | Plasma exposure is ample; skin needs Kpu ≥ 0.10 for ≥ 80% inhibition over half the interval. Skin exposure is unmeasured | supports, with a gate |
| Stress tests | No LINCS reversal, no human-genetic support | no added support |

The page shows each result as an interactive chart, with every claim cited (54 references, Nature style, verified against PubMed).

## Repository

```
.
├── src/                          project page (Astro + D3)
│   ├── i18n/en.ts, pt.ts         all copy; citations as [@key], numbered by first use
│   ├── data/references.json      bibliography (PubMed-verified)
│   ├── data/figures/*.json       chart data, each with its provenance (exact or read from figure)
│   ├── components/, layouts/     page structure
│   └── scripts/                  charts, hero simulation, citation popovers
├── public/img/                   deck figures (originals of the re-plotted charts) and credited third-party figures
├── scripts/check-refs.mjs        checks every citation resolves and EN/PT numbering match
├── ssc_figures/                  the study's figures as a Python package
│   ├── figures/figNN_*.py        one module per figure (03–16), the original notebook cells
│   ├── values.py                 every result written into the code rather than loaded
│   ├── io.py                     finds the results bundle, verifies SHA-256, output paths
│   └── style.py                  shared image helpers
├── notebook/vildagliptin_ssc.ipynb   narrative plus one call per figure (Colab or local)
└── tests/test_values.py          the page's exact values match values.py
```

### Run the page locally

Requires Node ≥ 22.

```bash
npm ci
npm run dev          # http://localhost:4321/vildagliptin-for-sclerosis/
npm run build && npm run check:refs
```

Pushing to `main` deploys to GitHub Pages through `.github/workflows/deploy.yml`.

### Where the chart numbers come from

- **Exact, from the figure code:** network proximity z/q, mRSS ρ and the evidence landscape (all in `ssc_figures/values.py`), the Kpu threshold table and the experiment text. The fibroblast-state β/q values are transcribed from labels printed on the original figure.
- **Read from the original figures (approximate, labelled on the page):** bulk expression differences and Reactome NES, DPP4⁺ fractions by cell type, PROGENy/CollecTRI estimates, PAGA layout.
- **Re-implemented:** the PK explorer is a one-compartment model calibrated to the original figure. It reproduces the study's Kpu threshold table exactly on the study's Kpu grid.

Each original figure is one click away under its chart.

### The figures

The figures render from frozen results in a private bundle (`colab_upload.zip`); every file is checked against its SHA-256 hash first. The upstream analyses ran on an HPC cluster (Slurm) and that pipeline is not public, so **only figures 03, 15 and 16 run without the bundle.**

```bash
pip install -e ".[test]"
python -m ssc_figures --list
python -m ssc_figures 03 15 16                              # no data needed
SSC_BUNDLE=/path/to/colab_upload.zip python -m ssc_figures  # everything
pytest
```

Output goes to `figures_out/` (`SSC_OUTPUT` to change it). In Colab, open `notebook/vildagliptin_ssc.ipynb`; it installs the package and finds the bundle in your Google Drive.

The code is the notebook that was presented, split one cell per module and formatted; the split was checked to leave every cell's syntax tree unchanged, and figures 03, 15 and 16 render identically to the original. Known limits, marked with `NOTE:` in the code:

- Several verdicts are written into the figure code rather than computed (figures 09, 11–16); the numbers among them are collected in `values.py`.
- Figure 06 draws two tables (`d`, `a`) whose loader is missing from the original export. It stops with an explanation unless you pass them: `run("06", d=..., a=...)`.
- Library versions used in Colab were not recorded; only plotly and kaleido are bounded.

The single-file Colab export is in the history at commit `c23ef3b` (`vildagliptin_ssc_figures.py`).

## Context and credit

Cortellis Drug Repositioning Hackathon, organised by Clarivate and Hospital Israelita Albert Einstein with InovaUSP. Team project with five members; I co-led the computational analysis and presented the proposal and business case. Third-party figures (Distler et al. 2026; Soare et al. 2020) are reproduced with credit for educational, non-commercial use. Not affiliated with or endorsed by Clarivate, Hospital Israelita Albert Einstein or InovaUSP; "Cortellis" is a trademark of Clarivate.

**Data.** No data are redistributed. Public sources: NCBI GEO (GSE58095, GSE138669, GSE249279, GSE181549), Reactome, STRING v12, PROGENy, CollecTRI, LINCS/L1000, GWAS Catalog, GTEx, Open Targets, PubMed, ClinicalTrials.gov. Cortellis was used only for a manual review; no Cortellis content is included beyond the cited potency values.

**Disclaimer.** Nothing here shows that vildagliptin is safe or effective for systemic sclerosis. Do not start, stop or change any medication on the basis of this work.

## References

1. Tabib, T. et al. Myofibroblast transcriptome indicates SFRP2hi fibroblast progenitors in systemic sclerosis skin. *Nat. Commun.* **12**, 4384 (2021). [doi:10.1038/s41467-021-24607-6](https://doi.org/10.1038/s41467-021-24607-6)
2. Soare, A. et al. Dipeptidylpeptidase 4 as a marker of activated fibroblasts and a potential target for the treatment of fibrosis in systemic sclerosis. *Arthritis Rheumatol.* **72**, 137–149 (2020). [doi:10.1002/art.41058](https://doi.org/10.1002/art.41058)

The full list of 54 references is on the [project page](https://castlelli.github.io/vildagliptin-for-sclerosis/#references).
