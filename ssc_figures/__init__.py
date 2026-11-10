"""Figures for the vildagliptin / systemic sclerosis repositioning study.

Each figure is one module in ``ssc_figures.figures``; running it renders the
figure from the frozen results bundle (see ``ssc_figures.io``). Use
``run("04")`` in a notebook or ``python -m ssc_figures 04`` in a shell.
"""

import runpy

FIGURES = {
    "03": "fig03_evidence_architecture",
    "04": "fig04_bulk_fibrotic_program",
    "05": "fig05_dpp4_localization",
    "06": "fig06_scrna_replication",
    "07": "fig07_paga_branches",
    "08": "fig08_regulatory_state",
    "09": "fig09_network_proximity",
    "10": "fig10_pk_dermal_exposure",
    "11": "fig11_functional_bridge",
    "12": "fig12_programs_mrss",
    "13": "fig13_translational_gap",
    "14": "fig14_stress_tests",
    "15": "fig15_proof_of_mechanism",
    "16": "fig16_evidence_landscape",
}

# Figures that draw only from values written into the code; they run without the bundle.
NO_DATA = ("03", "15", "16")


def prepare_export():
    """Fetch the headless Chrome Kaleido uses for Plotly PNG export (best effort, as before)."""
    try:
        import kaleido

        kaleido.get_chrome_sync()
    except Exception:
        pass


def run(number):
    """Render one figure by number ("04") and return the module's namespace."""
    key = f"{int(number):02d}"
    if key not in FIGURES:
        raise KeyError(f"No figure {number}; choose from {', '.join(FIGURES)}")
    return runpy.run_module(f"ssc_figures.figures.{FIGURES[key]}", run_name="__main__")
