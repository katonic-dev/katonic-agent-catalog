"""POST /admin/reset/{system} puts back what one system has changed and leaves the rest of the retailer alone.

Several people can then test different agents against one retailer without wiping each other's records.
"""
from datetime import date

from retailer.seed import build_all
from conftest import ALL_SYSTEMS, H, TODAY

TODAY_D = date.fromisoformat(TODAY)
FS = "/foodsafety/reviews/R-014/2026-10"
ANALYSIS = {"period": "2026-10", "themes": [{"name": "late delivery", "count": 78}], "harm_comments": []}


def post(client, path, body=None, status=200):
    r = client.post(path, json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def get(client, path):
    r = client.get(path, headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def test_one_system_goes_back_and_the_others_keep_their_records(client, store):
    post(client, "/care/analysis", ANALYSIS)
    post(client, f"{FS}/sign", {"signed_by": "B. Teague"})
    post(client, "/purchasing/invoices/INV-5120/query", {"raised_by": "C. Payer", "message": "Please explain."})
    assert get(client, "/admin/state")["changed_by"] == {
        "care": ["feedback_analyses"], "foodsafety": ["fs_reviews"], "purchasing": ["supplier_invoices"]}

    r = post(client, "/admin/reset/purchasing")
    assert r["applied"] is True and r["system"] == "purchasing" and r["put_back"] == ["supplier_invoices"]
    assert "purchasing" in r["message"] and r["counts"]["supplier_invoices_queried"] == 0

    assert get(client, "/purchasing/invoices/INV-5120")["status"] == "received"
    assert get(client, FS)["status"] == "signed"
    assert get(client, "/care/analysis/2026-10")["count"] == 1
    assert get(client, "/admin/state")["changed_by"] == {"care": ["feedback_analyses"], "foodsafety": ["fs_reviews"]}


def test_an_event_belongs_to_the_system_that_holds_what_arrived(client, store):
    post(client, "/admin/simulate/supplier-invoice")
    post(client, "/admin/simulate/food-safety-records")
    changed = get(client, "/admin/state")["changed_by"]
    assert changed["purchasing"] == ["goods_receipts", "purchase_orders", "supplier_invoices"]
    assert changed["foodsafety"] == ["fs_records", "fs_reviews"]

    r = post(client, "/admin/reset/foodsafety")
    assert r["put_back"] == ["fs_records", "fs_reviews"]
    assert len(store.data["fs_records"]) == 6 and len(store.data["supplier_invoices"]) == 7
    # the same arrival comes again, because the count of foodsafety arrivals went back
    assert post(client, "/admin/simulate/food-safety-records")["item_id"] == "R-071:2026-10"

    r = post(client, "/admin/reset/purchasing")
    assert r["put_back"] == ["goods_receipts", "purchase_orders", "supplier_invoices"]
    assert len(store.data["supplier_invoices"]) == 6 and post(client, "/admin/simulate/supplier-invoice")["item_id"] == "INV-4401"


def test_numbers_of_one_system_go_back_with_it(client):
    base = f"{FS}"
    post(client, f"{base}/corrective-actions/request", {"requested_by": "A", "note": "n"})
    first = post(client, f"{base}/corrective-actions", {"unit_or_check": "u", "what_was_done": "w", "done_by": "b",
                                                        "done_on": "2026-10-09"})
    assert first["corrective_action"]["action_id"] == "CA-0001"
    post(client, "/admin/reset/foodsafety")
    post(client, f"{base}/corrective-actions/request", {"requested_by": "A", "note": "n"})
    again = post(client, f"{base}/corrective-actions", {"unit_or_check": "u", "what_was_done": "w", "done_by": "b",
                                                        "done_on": "2026-10-09"})
    assert again["corrective_action"]["action_id"] == "CA-0001"


def test_every_system_put_back_in_turn_gives_the_starting_retailer(client, store):
    post(client, "/care/analysis", ANALYSIS)
    post(client, f"{FS}/sign", {"signed_by": "B. Teague"})
    post(client, "/purchasing/invoices/INV-5120/query", {"raised_by": "C. Payer", "message": "Please explain."})
    post(client, "/admin/simulate/supplier-invoice")
    post(client, "/admin/simulate/food-safety-records")
    assert store.data != build_all(TODAY_D)
    for system in ALL_SYSTEMS:
        assert post(client, f"/admin/reset/{system}")["applied"] is True
    assert store.data == build_all(TODAY_D)
    assert store.changed == {} and store.simulated == {}
    assert {k: v for k, v in store.counters.items() if k != "event"} == {}


def test_a_system_that_changed_nothing_puts_nothing_back(client, store):
    post(client, "/care/analysis", ANALYSIS)
    r = post(client, "/admin/reset/stores")
    assert r["applied"] is True and r["put_back"] == [] and "nothing" in r["message"]
    assert get(client, "/care/analysis/2026-10")["count"] == 1


def test_an_unknown_system_is_refused_and_the_names_are_given(client, store):
    post(client, "/care/analysis", ANALYSIS)
    r = client.post("/admin/reset/everything", headers=H)
    assert r.status_code == 404 and r.json()["applied"] is False
    for name in ("stores", "foodsafety", "care", "purchasing"):
        assert name in r.json()["detail"]
    assert get(client, "/care/analysis/2026-10")["count"] == 1


def test_reset_of_one_system_needs_a_key(client):
    assert client.post("/admin/reset/care").status_code == 401
