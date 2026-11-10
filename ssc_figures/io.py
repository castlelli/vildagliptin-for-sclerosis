"""Locate, extract and verify the curated results bundle; export paths.

Replaces cells 1-2 of the original Colab notebook. All scientific analyses
ran earlier on DaVinci (Slurm); this module only finds the frozen results
(``colab_upload.zip``), checks every file against its SHA-256 hash and hands
figure modules a path to it.

Where the bundle is looked for, in order:

1. ``SSC_DATA``: a directory that already holds ``colab_inventory.tsv``.
2. ``SSC_BUNDLE``: a path to ``colab_upload.zip``; it is extracted into
   ``SSC_WORKDIR`` (default ``/content/vildagliptin_ssc`` in Colab,
   ``.ssc_data`` elsewhere).
3. In Colab only: Google Drive is mounted and searched for exactly one
   ``colab_upload.zip``, as the original notebook did.

The bundle is resolved on first use, so figures that need no data
(03, 15, 16) run without it.

Figures are written to ``SSC_OUTPUT`` (default ``/content`` in Colab,
``figures_out`` elsewhere).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import zipfile
from functools import lru_cache
from pathlib import Path

import pandas as pd

BUNDLE_NAME = "colab_upload.zip"
INVENTORY_NAME = "colab_inventory.tsv"


def in_colab() -> bool:
    try:
        import google.colab  # noqa: F401
    except ImportError:
        return False
    return True


def _output_dir() -> Path:
    default = "/content" if in_colab() else "figures_out"
    path = Path(os.environ.get("SSC_OUTPUT", default))
    path.mkdir(parents=True, exist_ok=True)
    return path


OUTPUT_DIR = _output_dir()


# ------------------------------------------------------------
# Finding the bundle
# ------------------------------------------------------------


def _find_on_drive() -> Path:
    from google.colab import drive

    drive.mount("/content/drive")
    root = Path("/content/drive/MyDrive")
    print(f"\nSearching Google Drive for {BUNDLE_NAME}...")
    hits = list(root.rglob(BUNDLE_NAME))
    if not hits:
        others = list(root.rglob("*.zip"))
        print(f"\nCould not find '{BUNDLE_NAME}'.")
        if others:
            print("\nZIP files found in MyDrive:")
            for path in others:
                print(f"  - {path}")
        else:
            print("\nNo ZIP files were found anywhere in MyDrive.")
        raise FileNotFoundError(f"Could not find '{BUNDLE_NAME}' anywhere inside Google Drive/MyDrive.")
    if len(hits) > 1:
        print(f"\nMultiple copies of {BUNDLE_NAME} were found:")
        for path in hits:
            print(f"  - {path}")
        raise RuntimeError(
            f"Multiple copies of '{BUNDLE_NAME}' were found. "
            "Keep only one copy or set SSC_BUNDLE to its path."
        )
    return hits[0]


def _extract(zip_path: Path) -> Path:
    default = "/content/vildagliptin_ssc" if in_colab() else ".ssc_data"
    workdir = Path(os.environ.get("SSC_WORKDIR", default))
    target = workdir / "data"
    # Start from a clean workspace, as the original notebook did.
    if workdir.exists():
        shutil.rmtree(workdir)
    target.mkdir(parents=True, exist_ok=True)
    print(f"\nUsing curated evidence bundle: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(target)
    return target


def _locate_inventory(root: Path) -> Path:
    hits = list(root.rglob(INVENTORY_NAME))
    if len(hits) != 1:
        raise RuntimeError(f"Could not uniquely locate {INVENTORY_NAME} under {root}.")
    return hits[0]


# ------------------------------------------------------------
# Integrity
# ------------------------------------------------------------


def sha256_file(path: Path) -> str:
    """SHA-256 hex digest of a file, read in 1 MiB blocks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(data: Path, inventory_path: Path) -> pd.DataFrame:
    """Check every file listed in the inventory; raise if any is missing or altered."""
    inventory = pd.read_csv(inventory_path, sep="\t")
    checks = []
    for _, row in inventory.iterrows():
        path = data / row["File"]
        exists = path.exists()
        observed = sha256_file(path) if exists else None
        checks.append(
            {
                "file": row["File"],
                "exists": exists,
                "sha256_match": exists and observed == str(row["SHA256"]).lower(),
            }
        )
    integrity = pd.DataFrame(checks)
    n_expected = len(integrity)
    n_present = int(integrity["exists"].sum())
    n_valid = int(integrity["sha256_match"].sum())

    print("\n" + "=" * 64)
    print("REPRODUCIBLE DATA IMPORT")
    print("=" * 64)
    print(f"Dataset directory   : {data}")
    print(f"Expected files      : {n_expected}")
    print(f"Files found         : {n_present}")
    print(f"Valid SHA256 hashes : {n_valid}")

    if n_present == n_expected and n_valid == n_expected:
        print("\n✓ DATASET INTEGRITY: PASS")
        return integrity

    print("\n✗ DATASET INTEGRITY: FAIL")
    print(integrity[~integrity["exists"] | ~integrity["sha256_match"]].to_string(index=False))
    raise RuntimeError("Dataset integrity validation failed.")


@lru_cache(maxsize=1)
def data_dir() -> Path:
    """Directory of the verified results bundle (resolved and checked once)."""
    if os.environ.get("SSC_DATA"):
        root = Path(os.environ["SSC_DATA"])
    elif os.environ.get("SSC_BUNDLE"):
        root = _extract(Path(os.environ["SSC_BUNDLE"]))
    elif in_colab():
        root = _extract(_find_on_drive())
    else:
        raise FileNotFoundError(
            f"This figure needs the results bundle ({BUNDLE_NAME}), which is not public. "
            "Set SSC_BUNDLE=/path/to/colab_upload.zip or SSC_DATA=/path/to/extracted/dir."
        )
    inventory = _locate_inventory(root)
    # All curated files live next to the inventory.
    data = inventory.parent
    verify(data, inventory)
    return data


# ------------------------------------------------------------
# Access helpers used by the figure modules
# ------------------------------------------------------------


def data_file(name: str) -> Path:
    """Path of a file in the verified bundle; raises if it is absent."""
    path = data_dir() / name
    if not path.exists():
        raise FileNotFoundError(f"File not found: {name}")
    return path


def load_tsv(name: str) -> pd.DataFrame:
    """Load a tab-separated result table from the bundle."""
    return pd.read_csv(data_file(name), sep="\t")


def require(*names: str) -> None:
    """Fail fast if bundle files a figure documents but does not draw from are missing.

    The original cells loaded these tables and never used them; checking that
    they exist keeps the same failure behaviour without the dead loads.
    """
    for name in names:
        data_file(name)
