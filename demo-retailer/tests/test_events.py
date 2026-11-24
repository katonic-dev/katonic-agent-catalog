"""Both event kinds: what each of the four templates makes, and who is told."""


from conftest import H
from test_operations import PERIOD, deviations, differences, get


def simulate(client, kind):
    r = client.post(f"/admin/simulate/{kind}", headers=H)
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------- supplier-invoice

def test_supplier_invoice_four_templates_in_turn(client, store):
    expected = [
        [],
        [("price_differs", "Butter, unsalted", 120.00)],
        [("quantity_differs", "Onions, white", 140.00)],
        [("not_on_order", "Pallet charge", 95.00)],
    ]
    made = []
    for n in range(8):
        r = simulate(client, "supplier-invoice")
        made.append(r["item_id"])
        assert r["event_type"] == "supplier-invoice" and r["system"] == "purchasing"
        inv = get(client, f"/purchasing/invoices/{r['item_id']}")
        assert inv["status"] == "received" and inv["invoice_date"] == "2026-11-24" and inv["currency"] == "USD"
        assert differences(client, r["item_id"]) == expected[n % 4], n
        assert r["item_id"] in r["message"] and inv["po_number"] in r["message"] and "purchasing system" in r["message"]
        assert "has arrived" in r["message"] and "get_supplier_invoice" in r["message"]
        po = get(client, f"/purchasing/purchase-orders/{inv['po_number']}")
        assert po["status"] == "received" and po["goods_receipt_ids"] == [get(
            client, "/purchasing/goods-receipts", po_number=inv["po_number"])["items"][0]["receipt_id"]]
        assert po["invoice_numbers"] == [r["item_id"]]
    assert len(set(made)) == 8 and not set(made) & {"INV-88214", "INV-3391", "INV-77102", "INV-5120", "INV-6417", "INV-9034"}
    assert len(store.data["supplier_invoices"]) == 14 and len(store.data["purchase_orders"]) == 14
    assert len(store.data["goods_receipts"]) == 14
    assert get(client, "/admin/state")["counts"]["supplier_invoices_received"] == 14


def test_a_new_invoice_never_takes_an_id_of_the_starting_data(client, store):
    for n in (1, 2, 3):
        store.data["supplier_invoices"][f"INV-440{n}"] = {"invoice_number": f"INV-440{n}", "status": "received"}
    ids = [simulate(client, "supplier-invoice")["item_id"] for _ in range(4)]
    assert ids == ["INV-4404", "INV-4405", "INV-4406", "INV-4407"]


# ---------------------------------------------------------------- food-safety-records

D = lambda day, period=PERIOD: f"{period}-{day:02d}"
CLEAN = "daily_cleaning_signed_by"
TEMPLATE_FAULTS = [
    [],
    [("walk_in_chiller_afternoon_c", D(4), 6.4), ("walk_in_chiller_opening_c", D(5), 6.9), ("walk_in_chiller_afternoon_c", D(18), 7.2)],
    [("chilled_item_c", D(9), 7.1), (CLEAN, D(12), "")],
    [("hot_holding_14h_c", D(10), 60.8), ("hot_holding_16h_c", D(22), 61.5), ("chicken_core_first_batch_am_c", D(15), 73.5)],
]


def test_food_safety_records_four_templates_for_four_new_restaurants(client, store):
    assert get(client, "/foodsafety/records")["count"] == 6
    for n, site in enumerate(["R-071", "R-076", "R-082", "R-090"]):
        r = simulate(client, "food-safety-records")
        assert r["event_type"] == "food-safety-records" and r["system"] == "foodsafety"
        assert r["item_id"] == f"{site}:{PERIOD}"
        assert site in r["message"] and PERIOD in r["message"] and "foodsafety system" in r["message"]
        assert "have arrived" in r["message"] and "get_food_safety_records" in r["message"]
        assert deviations(client, site) == sorted(TEMPLATE_FAULTS[n]), site
        rev = get(client, f"/foodsafety/reviews/{site}/{PERIOD}")
        assert rev["status"] == "not_reviewed" and rev["checks"] == []
    listed = get(client, "/foodsafety/records")
    assert listed["count"] == 10 and {x["review_status"] for x in listed["items"]} == {"not_reviewed"}
    assert get(client, "/admin/state")["counts"]["record_periods_not_reviewed"] == 10


def test_after_six_restaurants_the_records_are_for_the_month_before(client):
    for _ in range(6):
        simulate(client, "food-safety-records")
    r = simulate(client, "food-safety-records")
    assert r["item_id"] == "R-071:2026-09"
    assert deviations(client, "R-071", "2026-09") == sorted([
        ("chilled_item_c", D(9, "2026-09"), 7.1), (CLEAN, D(12, "2026-09"), "")])
    assert get(client, "/foodsafety/records", site_id="R-071")["count"] == 2


def test_the_starting_records_are_not_touched_by_arrivals(client):
    before = get(client, "/foodsafety/records/R-014/2026-10")
    for _ in range(4):
        simulate(client, "food-safety-records")
    assert get(client, "/foodsafety/records/R-014/2026-10") == before


def test_an_event_is_logged_with_how_many_subscribers_it_had(client):
    simulate(client, "food-safety-records")
    items = get(client, "/admin/events")["items"]
    assert len(items) == 1 and items[0]["status"] == "created" and items[0]["event_type"] == "food-safety-records"
    assert items[0]["subscribers"] == 0 and items[0]["event_id"] == "EVT-0001"
