"""The project page and the figure code must state the same exact results."""

import json
from pathlib import Path

import pytest

from ssc_figures import values

SITE = Path(__file__).resolve().parents[1] / "src" / "data" / "figures"


def site(name):
    return json.loads((SITE / f"{name}.json").read_text())


def test_network_proximity_matches_site():
    page = {m["id"]: m for m in site("network")["data"]}
    code = values.NETWORK_PROXIMITY_R10
    assert list(page) == code["module_id"]
    for i, module in enumerate(code["module_id"]):
        for key in ("z", "p", "q"):
            assert page[module][key] == code[key][i], (module, key)


def test_mrss_matches_site():
    page = site("mrss")["data"]
    code = values.MRSS_R3
    assert [p["rho"] for p in page] == [c["rho"] for c in code]
    status = {"SUPPORTED": "supported", "DIRECTIONAL": "directional", "NOT SUPPORTED": "not"}
    assert [p["status"] for p in page] == [status[c["adjusted_status"]] for c in code]


ROLES = {
    "Supports hypothesis": "supports",
    "Refines model": "refines",
    "No additional support": "nosupport",
    "Requires experiment": "experiment",
}


def test_evidence_landscape_matches_site():
    page = site("landscape")["items"]
    code = values.EVIDENCE_LANDSCAPE
    assert len(page) == len(code)
    for p, c in zip(page, code):
        assert p["title"] == c["evidence"]
        assert p["finding"] == c["finding"]
        assert p["evidence"] == c["basis"]
        assert p["role"] == ROLES[c["decision_role"]]


@pytest.mark.parametrize("name", ["network", "mrss", "landscape"])
def test_site_marks_these_as_exact(name):
    assert site(name)["exact"] is True
