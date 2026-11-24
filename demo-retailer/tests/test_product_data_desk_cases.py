"""The product data desk's demo cases are this retailer's own records.

../retail/desks/product-data/cases.json is written by make_cases.py in the same folder, from the seed of
this service at retailer date 2026-11-24: the six new products that have no description yet, and a
listing check for each of thirteen listings. These tests fail when the file differs from what the script
would write, and when a case differs from what the service returns for that listing, specification, image
description or style guide. They also hold the cases to what the service's own answer set says: which
listings have an attribute that is missing or does not match, and which image description differs.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

from conftest import H

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "product-data"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the product data desk folder is not next to this copy of the retailer", allow_module_level=True)

NEW = ["AG-4411", "BK-5706", "CH-5508", "DR-5906", "FZ-5606", "HH-6107"]
LISTINGS = ["AG-4401", "AG-4407", "AG-4412", "AG-4413", "BK-5703", "CH-5506", "CH-5507", "DR-5902", "DR-5905", "FP-5804",
            "FZ-5602", "HH-6104", "PC-6603"]
CLEAN = ["AG-4413", "CH-5507", "DR-5905"]
# The label a case gives each attribute of the system.
LABELS = {"net_quantity": "Net quantity", "pack_size": "Pack size", "allergen_statement": "Allergens", "country_of_origin": "Origin"}


def _script():
    spec = importlib.util.spec_from_file_location("product_data_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _held() -> list:
    return json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]


def _cases() -> dict:
    return {c["title"].split(" ")[0]: c for c in _held()}


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API."""

    def __init__(self, client):
        self.client = client

    def _get(self, path, **params):
        answer = self.client.get(path, headers=H, params=params)
        assert answer.status_code == 200, f"{path} {params}: {answer.status_code}"
        return answer.json()

    def awaiting(self):
        rows = self._get("/catalogue/new-products", status="awaiting_description")["items"]
        return sorted(({"sku": x["sku"], "image_descriptions": x["image_descriptions"]} for x in rows), key=lambda x: x["sku"])

    def images_note(self):
        return self._get("/catalogue/new-products")["images_note"]

    def listing(self, sku):
        return self._get(f"/catalogue/listings/{sku}")

    def spec(self, sku):
        return self._get(f"/catalogue/specifications/{sku}")

    def guide(self):
        return self._get("/catalogue/style-guide")


def _block(text: str, heading: str) -> dict:
    """The labelled lines under one heading of a case, as a dict."""
    out = {}
    for line in text.split(heading + "\n", 1)[1].splitlines():
        if re.fullmatch(r"[A-Z][A-Z0-9 ,&/'()-]{2,}", line):
            break
        if ": " in line:
            label, value = line.split(": ", 1)
            out[label] = value
    return out


def _findings(text: str) -> dict:
    """What is missing or does not match, worked out from the case's own lines."""
    listing, spec = _block(text, "THE LISTING"), _block(text, "THE SUPPLIER'S SPECIFICATION")
    out = {}
    for attribute, label in LABELS.items():
        if listing[label] != spec[label]:
            says = "" if listing[label] == "(nothing)" else listing[label]
            out[attribute] = {"kind": "does_not_match" if says else "missing", "listing_value": says,
                              "specification_value": spec[label]}
    return out


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_nineteen_cases_in_order_each_with_its_kind():
    held = _held()
    assert [c["title"].split(" ")[0] for c in held] == NEW + LISTINGS
    assert [c["kind"] for c in held] == ["New product"] * 6 + ["Listing check"] * 13
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert set(c["kind"] for c in held) == set(config["routing"]["kinds"])
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys


def test_every_case_holds_what_the_service_returns(client):
    """The whole file, built again from the API in place of the seed."""
    assert _held() == _script().cases_from(ApiSource(client))


def test_the_new_products_are_the_six_with_no_description_and_each_carries_its_records(client, store):
    planted = store.data["catalogue_planted"]
    assert sorted(planted["awaiting_description"]) == NEW
    cases, source = _cases(), ApiSource(client)
    guide = source.guide()
    for sku in NEW:
        text = cases[sku]["text"]
        spec = source.spec(sku)
        held = _block(text, "THE SUPPLIER'S SPECIFICATION")
        for attribute, label in LABELS.items():
            assert held[label] == spec[attribute], f"{sku}: {attribute}"
        assert held["Storage"] == spec["storage"]
        # The desk holds no images: each image is a description in words, and the case says so.
        assert "The catalogue system holds no images." in text and "Nobody reading it has seen the picture." in text
        for description in store.data["catalogue_products"][sku]["image_descriptions"]:
            assert description in text
        assert not re.search(r"https?:|\.png|\.jpe?g", text, flags=re.I)
        for rule in guide["rules"]:
            assert f"{rule['rule_id']} {rule['title']}: {rule['text']}" in text
        assert ("Age restricted: yes" in text) == spec["age_restricted"]
    # The one image description that gives a quantity the specification does not is in its case, word for word.
    assert list(planted["image_differences"]) == ["FZ-5606"]
    assert "'450 g'" in cases["FZ-5606"]["text"] and "Net quantity: 500 g" in cases["FZ-5606"]["text"]


def test_the_listing_checks_hold_the_ten_planted_faults_and_three_clean_listings(store):
    cases = _cases()
    planted = store.data["catalogue_planted"]["mismatches"]
    assert sorted(planted) == sorted(set(LISTINGS) - set(CLEAN))
    for sku in LISTINGS:
        text = cases[sku]["text"]
        found = _findings(text)
        if sku in CLEAN:
            assert found == {}, sku
            continue
        want = planted[sku]
        assert found == {want["attribute"]: {k: want[k] for k in ("kind", "listing_value", "specification_value")}}, sku
        # The system's field names stay out of the case: each attribute is written in plain words.
        assert not re.search(r"net_quantity|pack_size|allergen_statement|country_of_origin", text)
    # The case does not say which listing was planted, or what is wrong with it.
    for sku in LISTINGS:
        case = cases[sku]
        assert not re.search(r"missing|does not match|differs|planted", json.dumps({k: v for k, v in case.items() if k != "text"}), flags=re.I)


def test_the_desk_records_a_decision_and_calls_no_operation_of_the_retailer():
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert all("act" not in d for d in config["decisions"])
    said = json.dumps({"next": config["next"], "register": config["register"]["heading"]})
    assert "published nothing" in said and "changed no listing" in said
    assert config["rules"]["fourEyes"] is True
