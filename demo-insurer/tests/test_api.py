"""The service as a whole: sign-in, the invented-data marks, the OpenAPI documents, reset and arrivals."""
import re
from datetime import date

import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate

from insurer.app import create_app
from insurer.seed import build_all
from conftest import ALL_SYSTEMS, H, TODAY, make_env

TODAY_D = date.fromisoformat(TODAY)


def test_health_needs_no_key_and_gives_the_insurer_date(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["insurer_date"] == TODAY and r.headers["x-demo-data"] == "invented"


def test_a_data_operation_needs_the_key_in_either_header(client):
    assert client.get("/policy/policies/POL-2001").status_code == 401
    assert client.get("/policy/policies/POL-2001", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/policy/policies/POL-2001", headers=H).status_code == 200
    assert client.get("/policy/policies/POL-2001", headers={"Authorization": f"Bearer {H['X-API-Key']}"}).status_code == 200
    assert client.post("/admin/reset").status_code == 401


def test_with_sign_in_off_no_key_is_needed():
    c = TestClient(create_app(make_env(INSURER_AUTH="off")))
    assert c.get("/claims/claims").status_code == 200
    assert "sign-in is OFF" in c.get("/").text


def test_every_json_answer_says_the_data_is_invented(client):
    for path in ("/policy/policies", "/claims/claims", "/claims/handling-guide", "/claims/claims/NOPE"):
        r = client.get(path, headers=H)
        assert r.json()["demo_data"] is True and r.headers["x-demo-data"] == "invented"


@pytest.mark.parametrize("system", ALL_SYSTEMS)
def test_each_system_has_a_valid_openapi_303_document_made_for_a_model(client, system):
    doc = client.get(f"/{system}/openapi.json").json()
    assert doc["openapi"] == "3.0.3"
    validate(doc)
    for item in doc["paths"].values():
        for method, op in item.items():
            assert re.fullmatch(r"[a-z]+(_[a-z]+)+", op["operationId"])
            assert op["summary"] and len(op["description"]) > 60
            if method != "get" and op["operationId"] != "calculate_settlement":
                assert "(draft)" in op["summary"] or "(change)" in op["summary"], op["operationId"]


def test_operation_ids_are_unique_across_the_service(client):
    seen = []
    for system in ALL_SYSTEMS:
        doc = client.get(f"/{system}/openapi.json").json()
        seen += [op["operationId"] for item in doc["paths"].values() for op in item.values()]
    assert len(seen) == len(set(seen))


def test_the_same_date_gives_the_same_data():
    assert build_all(TODAY_D) == build_all(TODAY_D)


def test_no_text_in_the_data_counts_days_or_names_a_weekday():
    """An agent quotes what it reads: a note that says 'yesterday' would be quoted and be untrue the next day."""
    import json
    blob = json.dumps(build_all(TODAY_D)).lower()
    for word in ("yesterday", "last week", "days ago", "this morning", "tomorrow", "monday", "tuesday", "wednesday", "thursday",
                 "friday", "saturday", "sunday", "over the weekend"):
        assert word not in blob, word


def test_no_field_of_a_record_is_a_bare_iso_date_inside_a_document_text():
    for claim in build_all(TODAY_D)["claims"].values():
        for doc in claim["documents"].values():
            assert not re.search(r"\b20\d\d-\d\d-\d\d\b", doc["text"]), doc["document_id"]


def test_the_landing_page_lists_both_systems_and_shows_no_key(client):
    page = client.get("/").text
    assert "policy/openapi.json" in page and "claims/openapi.json" in page and H["X-API-Key"] not in page


def test_reset_puts_everything_back(client, store):
    client.post("/claims/claims/CLM-4001/triage", headers=H, json={"rule_id": "HG-3", "track": "fast track", "team": "fast-track team",
                                                                  "severity": "low", "reason": "Estimate under 2,500."})
    client.post("/admin/simulate/loss-report", headers=H)
    assert store.data != build_all(TODAY_D)
    assert client.post("/admin/reset", headers=H).json()["applied"] is True
    assert store.data == build_all(TODAY_D)


def test_one_system_goes_back_and_an_unknown_one_is_refused(client, store):
    client.post("/claims/claims/CLM-4001/triage", headers=H, json={"rule_id": "HG-3", "track": "fast track", "team": "fast-track team",
                                                                  "severity": "low", "reason": "Estimate under 2,500."})
    assert client.get("/admin/state", headers=H).json()["changed_by"] == {"claims": ["claims"]}
    assert client.post("/admin/reset/policy", headers=H).json()["put_back"] == []
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert store.data == build_all(TODAY_D)
    assert client.post("/admin/reset/everything", headers=H).status_code == 404


def test_a_simulated_loss_report_arrives_and_goes_back_with_the_claims_system(client, store):
    first = client.post("/admin/simulate/loss-report", headers=H).json()
    second = client.post("/admin/simulate/loss-report", headers=H).json()
    assert first["item_id"] == "LR-3101" and second["item_id"] == "LR-3102" and first["system"] == "claims"
    assert client.get("/claims/loss-reports/LR-3102", headers=H).json()["reporter"] == "Henrietta Quillby"
    client.post("/admin/reset/claims", headers=H)
    assert store.data == build_all(TODAY_D) and store.simulated == {}
    assert client.post("/admin/simulate/loss-report", headers=H).json()["item_id"] == "LR-3101"
