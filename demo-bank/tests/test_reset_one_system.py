"""POST /admin/reset/{system} puts back what one system has changed and leaves the rest of the bank alone.

Several people can then test different agents against one bank without wiping each other's records.
"""
from datetime import date

from fastapi.testclient import TestClient

from bank.app import create_app
from bank.seed import build_all
from bank.store import sharing_groups
from conftest import ALL_SYSTEMS, H, TODAY, make_env

TODAY_D = date.fromisoformat(TODAY)
ASSESSMENT = {"what_is_happening": "Card payments fail.", "likely_cause": "An expired certificate."}
SUMMARY = {"subject_name": "Valdis Orrenmoor", "customer_id": "CUS-1007", "conclusion": "Adverse.",
           "findings": [{"article_id": "ART-6001", "relevance": "about_subject", "adverse": True,
                         "reason": "Born 1971, lives in Port Ilvane."}]}
PROPOSAL = {"corrections": [{"field": "beneficiary_bic", "old_value": "QNMKXQQ1", "new_value": "TESLXTT1",
                             "rule_relied_on": "MTB-PAY-RULE-102"}], "explanation": "BIC taken from the bank directory."}


def post(client, path, body=None, status=200):
    r = client.post(path, json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def get(client, path):
    r = client.get(path, headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def test_one_system_goes_back_and_the_others_keep_their_records(client, store):
    post(client, "/itops/incidents/INC-7001/assessment", ASSESSMENT)
    post(client, "/news/screenings", SUMMARY)
    post(client, "/cards/cards/CRD-2001/block", {"reason": "lost"})
    assert get(client, "/admin/state")["changed_by"] == {"cards": ["cards"], "itops": ["itops_incidents"],
                                                         "news": ["media_screenings"]}

    r = post(client, "/admin/reset/itops")
    assert r["applied"] is True and r["system"] == "itops" and r["put_back"] == ["itops_incidents"]
    assert "itops" in r["message"] and r["counts"]["open_incidents"] == 3

    assert get(client, "/itops/incidents/INC-7001")["assessments"] == []
    assert len(store.data["media_screenings"]) == 1
    assert get(client, "/cards/cards/CRD-2001")["status"] == "blocked"
    assert get(client, "/admin/state")["changed_by"] == {"cards": ["cards"], "news": ["media_screenings"]}


def test_every_system_put_back_in_turn_gives_the_starting_bank(client, store):
    post(client, "/itops/incidents/INC-7001/assessment", ASSESSMENT)
    post(client, "/news/screenings", SUMMARY)
    post(client, "/cards/cards/CRD-2001/block", {"reason": "lost"})
    post(client, "/payments/repairs/REP-7002/proposal", PROPOSAL)
    post(client, "/core/customers/CUS-1001/contacts", {"channel": "call", "subject": "A question", "summary": "Asked about fees."})
    for kind in ("incident", "contribution-batch", "complaint", "monitoring-alert", "regulator-publication"):
        post(client, f"/admin/simulate/{kind}")
    assert store.data != build_all(TODAY_D)
    for system in ALL_SYSTEMS + ["regulator"]:
        assert post(client, f"/admin/reset/{system}")["applied"] is True
    assert store.data == build_all(TODAY_D)
    assert store.changed == {} and store.simulated == {}
    assert {k: v for k, v in store.counters.items() if k != "event"} == {}


def test_a_system_that_changed_nothing_puts_nothing_back(client, store):
    post(client, "/news/screenings", SUMMARY)
    r = post(client, "/admin/reset/funds")
    assert r["applied"] is True and r["put_back"] == [] and "nothing" in r["message"]
    assert len(store.data["media_screenings"]) == 1


def test_an_unknown_system_is_refused_and_the_names_are_given(client, store):
    post(client, "/news/screenings", SUMMARY)
    r = client.post("/admin/reset/everything", headers=H)
    assert r.status_code == 404 and r.json()["applied"] is False
    assert "itops" in r.json()["detail"] and "funds" in r.json()["detail"]
    assert len(store.data["media_screenings"]) == 1


def test_it_needs_the_key(client, store):
    post(client, "/news/screenings", SUMMARY)
    assert client.post("/admin/reset/news").status_code == 401
    assert len(store.data["media_screenings"]) == 1


def test_numbers_start_again_for_that_system_only(client):
    first = post(client, "/news/screenings", SUMMARY)["screening_id"]
    one = post(client, "/cards/cards/CRD-2001/disputes", {"transaction_ids": ["CTX-2001-U01"], "reason": "not_recognised"})
    post(client, "/admin/reset/news")
    assert post(client, "/news/screenings", SUMMARY)["screening_id"] == first
    two = post(client, "/cards/cards/CRD-2001/disputes", {"transaction_ids": ["CTX-2001-U02"], "reason": "not_recognised"})
    assert two["dispute"]["dispute_id"] != one["dispute"]["dispute_id"]


def test_an_item_made_to_arrive_goes_back_with_its_system(client, store):
    first = post(client, "/admin/simulate/incident")
    assert first["system"] == "itops" and first["item_id"] in store.data["itops_incidents"]
    post(client, "/admin/simulate/contribution-batch")
    batches = len(store.data["pension_batches"])
    post(client, "/admin/reset/itops")
    assert first["item_id"] not in store.data["itops_incidents"] and len(store.data["itops_incidents"]) == 4
    assert len(store.data["pension_batches"]) == batches
    assert post(client, "/admin/simulate/incident")["item_id"] == first["item_id"]


def test_a_search_sent_as_a_post_is_not_a_change(client):
    post(client, "/screening/search", {"name": "Valdis Orrenmoor"})
    post(client, "/finance/query", {"sql": "select 1"})
    assert get(client, "/admin/state")["changed_by"] == {}


def test_a_change_made_through_the_mcp_door_is_put_down_to_its_system(client, store):
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "save_incident_assessment", "arguments": {"incident_id": "INC-7002", **ASSESSMENT}}}
    r = client.post("/itops/mcp", json=call, headers={**H, "Accept": "application/json, text/event-stream"})
    assert r.status_code == 200
    assert len(store.data["itops_incidents"]["INC-7002"]["assessments"]) == 1
    assert get(client, "/admin/state")["changed_by"] == {"itops": ["itops_incidents"]}
    post(client, "/admin/reset/itops")
    assert store.data["itops_incidents"]["INC-7002"]["assessments"] == []


def test_record_sets_that_share_records_go_back_together(client, store):
    groups = sharing_groups(build_all(TODAY_D))
    assert {"payments", "repairs"} in groups
    post(client, "/payments/repairs/REP-7002/proposal", PROPOSAL)
    put_back = post(client, "/admin/reset/payments")["put_back"]
    assert "payments" in put_back and "repairs" in put_back
    assert {"payments", "repairs"} in sharing_groups(store.data)
    assert store.data == build_all(TODAY_D)


def test_who_changed_what_outlives_a_restart(tmp_path):
    env = make_env(DATA_DIR=str(tmp_path / "state"))
    first = TestClient(create_app(env))
    post(first, "/itops/incidents/INC-7001/assessment", ASSESSMENT)
    post(first, "/news/screenings", SUMMARY)

    app = create_app(env)
    second = TestClient(app)
    assert len(get(second, "/itops/incidents/INC-7001")["assessments"]) == 1
    assert post(second, "/admin/reset/itops")["put_back"] == ["itops_incidents"]
    assert get(second, "/itops/incidents/INC-7001")["assessments"] == []
    assert len(app.state.ctx.store.data["media_screenings"]) == 1

    third = create_app(env).state.ctx.store
    assert third.data["itops_incidents"]["INC-7001"]["assessments"] == [] and len(third.data["media_screenings"]) == 1
    assert third.changed == {"news": {"sets": ["media_screenings"], "counters": ["media_screening"]}}


def test_the_full_reset_still_puts_everything_back(client, store):
    post(client, "/itops/incidents/INC-7001/assessment", ASSESSMENT)
    post(client, "/news/screenings", SUMMARY)
    assert post(client, "/admin/reset")["applied"] is True
    assert store.data == build_all(TODAY_D) and store.changed == {}
    assert get(client, "/admin/state")["changed_by"] == {}
