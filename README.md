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
├── vildagliptin_ssc_figures.py   the original Colab notebook (figures and verdicts)
└── requirements.txt              libraries the notebook imports
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

- **Exact, from the notebook code:** network proximity z/q, mRSS ρ, the Kpu threshold table, evidence-landscape and experiment text. The fibroblast-state β/q values are transcribed from labels printed on the original figure.
- **Read from the original figures (approximate, labelled on the page):** bulk expression differences and Reactome NES, DPP4⁺ fractions by cell type, PROGENy/CollecTRI estimates, PAGA layout.
- **Re-implemented:** the PK explorer is a one-compartment model calibrated to the original figure. It reproduces the study's Kpu threshold table exactly on the study's Kpu grid.

Each original figure is one click away under its chart.

### The notebook

`vildagliptin_ssc_figures.py` is a Colab export that loads frozen results from a private bundle (`colab_upload.zip`), checks each file against its SHA-256 hash and renders the figures. The upstream analyses ran on an HPC cluster (Slurm); that pipeline is not public, so **the notebook cannot be re-run from this repository.** Known issues, kept so the code matches what was presented and marked with `NOTE:` comments:

- Several verdicts and some values are written into the code rather than computed (cells 9, 11–16).
- Cell 6 references two tables (`d`, `a`) whose loader is missing from the export.
- It is Colab-only (`google.colab`, `/content` paths, `!pip`).

## Context and credit

Cortellis Drug Repositioning Hackathon, organised by Clarivate and Hospital Israelita Albert Einstein with InovaUSP. Team project with five members; I co-led the computational analysis and presented the proposal and business case. Third-party figures (Distler et al. 2026; Soare et al. 2020) are reproduced with credit for educational, non-commercial use. Not affiliated with or endorsed by Clarivate, Hospital Israelita Albert Einstein or InovaUSP; "Cortellis" is a trademark of Clarivate.

**Data.** No data are redistributed. Public sources: NCBI GEO (GSE58095, GSE138669, GSE249279, GSE181549), Reactome, STRING v12, PROGENy, CollecTRI, LINCS/L1000, GWAS Catalog, GTEx, Open Targets, PubMed, ClinicalTrials.gov. Cortellis was used only for a manual review; no Cortellis content is included beyond the cited potency values.

**Disclaimer.** Nothing here shows that vildagliptin is safe or effective for systemic sclerosis. Do not start, stop or change any medication on the basis of this work.

## References

1. Tabib, T. et al. Myofibroblast transcriptome indicates SFRP2hi fibroblast progenitors in systemic sclerosis skin. *Nat. Commun.* **12**, 4384 (2021). [doi:10.1038/s41467-021-24607-6](https://doi.org/10.1038/s41467-021-24607-6)
2. Soare, A. et al. Dipeptidylpeptidase 4 as a marker of activated fibroblasts and a potential target for the treatment of fibrosis in systemic sclerosis. *Arthritis Rheumatol.* **72**, 137–149 (2020). [doi:10.1002/art.41058](https://doi.org/10.1002/art.41058)

The full list of 54 references is on the [project page](https://castlelli.github.io/vildagliptin-for-sclerosis/#references).
