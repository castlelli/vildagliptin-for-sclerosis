"""Render figures from the command line.

    python -m ssc_figures            # every figure
    python -m ssc_figures 03 15 16   # selected figures
    python -m ssc_figures --list

Needs SSC_BUNDLE (or SSC_DATA) for every figure except 03, 15 and 16.
Output goes to SSC_OUTPUT (default ./figures_out).
"""

import argparse
import os
import sys


def save_interactive(key, namespace, out_dir):
    """Write a Plotly figure that the cell only displayed (e.g. 03) to HTML."""
    fig = namespace.get("fig")
    if type(fig).__module__.startswith("plotly") and not list(out_dir.glob(f"Figure_{key}_*")):
        from ssc_figures import FIGURES

        path = out_dir / f"Figure_{key}_{FIGURES[key].split('_', 1)[1]}.html"
        fig.write_html(path, include_plotlyjs="cdn")
        print(f"Saved interactive figure to: {path}")


def main(argv=None):
    os.environ.setdefault("MPLBACKEND", "Agg")
    from ssc_figures import FIGURES, NO_DATA, prepare_export, run
    from ssc_figures.io import OUTPUT_DIR

    parser = argparse.ArgumentParser(prog="ssc-figures", description=__doc__.split("\n")[0])
    parser.add_argument("figures", nargs="*", help="figure numbers, e.g. 04 09 (default: all)")
    parser.add_argument("--list", action="store_true", help="list figures and exit")
    args = parser.parse_args(argv)

    if args.list:
        for key, name in FIGURES.items():
            print(f"{key}  {name}{'' if key not in NO_DATA else '  (no data needed)'}")
        return 0

    prepare_export()
    # Outside a notebook, fig.show() would start a browser and wait for it.
    import plotly.io as pio

    pio.renderers.default = ""
    failed = []
    for key in args.figures or list(FIGURES):
        print(f"\n### Figure {key}")
        try:
            namespace = run(key)
            save_interactive(key, namespace, OUTPUT_DIR)
        except Exception as exc:  # keep going; report at the end
            failed.append(key)
            print(f"Figure {key} failed: {type(exc).__name__}: {exc}", file=sys.stderr)
    print(f"\nOutput directory: {OUTPUT_DIR.resolve()}")
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
