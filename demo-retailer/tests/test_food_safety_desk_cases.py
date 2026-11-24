"""The food safety desk's demo cases are this retailer's own records.

../retail/desks/food-safety/cases.json is written by make_cases.py in the same folder, from the
seed of this service for the period 2026-10 at retailer date 2026-11-24. These tests fail when
the file differs from what the script would write, and when a case differs from what the service
returns for that restaurant.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from conftest import H

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "food-safety"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the food safety desk folder is not next to this copy of the retailer", allow_module_level=True)

SITES = ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063"]
PERIOD = "2026-10"


def _script():
    spec = importlib.util.spec_from_file_location("food_safety_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_six_restaurants_in_order():
    checks = json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["checks"]
    assert [c["title"].split(" ")[0] for c in checks] == SITES
    assert all(c["period"] == "October 2026" for c in checks)


def test_each_case_holds_what_the_service_returns(client):
    """The town, street, area manager and every line of the records, read back through the API."""
    script = _script()
    checks = {c["title"].split(" ")[0]: c for c in json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["checks"]}
    for site_id in SITES:
        site = client.get(f"/stores/sites/{site_id}", headers=H).json()
        records = client.get(f"/foodsafety/records/{site_id}/{PERIOD}", headers=H)
        assert records.status_code == 200, records.text
        records = records.json()
        case = checks[site_id]
        assert case["title"] == f"{site_id} {site['name']}"
        assert (case["town"], case["street"]) == (site["town"], site["street"])
        assert case["area_manager"] == f"{site['area_manager']}, {site['area']}"
        assert case["text"] == script.records_text(site, records, "October", "2026")
        assert len(records["temperature_log"]) == 31 and len(records["delivery_log"]) == 9
