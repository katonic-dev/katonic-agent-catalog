"""SCENARIOS.md says what the service holds. These tests read the file and compare it with what the API serves."""
import re
from pathlib import Path

from conftest import H

TEXT = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")


def rows(prefix, text=TEXT):
    return [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith(f"| {prefix}")]


COMPANY = TEXT.split("## The company")[1].split("## Food safety records")[0]


def num(text):
    return float(text.replace(",", ""))


def test_the_harm_rows_match_the_service(client):
    harm = rows("GF-")
    assert len(harm) == 7
    for ref, day, site, channel, _ in harm:
        x = client.get(f"/care/feedback/{ref}", headers=H).json()
        assert (x["date"], x["site_id"], x["channel"], x["rating"]) == (day, site, channel, 1), ref


def test_the_invoice_rows_match_the_service(client):
    inv = rows("INV-")
    assert [r[0] for r in inv] == ["INV-88214", "INV-3391", "INV-77102", "INV-5120", "INV-6417", "INV-9034"]
    for number, dated, po, net, tax, total, _ in inv:
        x = client.get(f"/purchasing/invoices/{number}", headers=H).json()
        assert (x["invoice_date"], x["po_number"], x["net"], x["tax"], x["total"]) == (dated, po, num(net), num(tax), num(total)), number


def test_the_order_and_receipt_rows_match_the_service(client):
    for row in rows("PO-"):
        po, supplier, ordered = row[0], row[1], row[2]
        x = client.get(f"/purchasing/purchase-orders/{po}", headers=H).json()
        assert (x["supplier_id"], x["order_date"]) == (supplier, ordered), po
        receipt = re.match(r"(GR-\d+) on (\d{4}-\d\d-\d\d)", row[4])
        r = client.get("/purchasing/goods-receipts", headers=H, params={"po_number": po}).json()["items"][0]
        assert (r["receipt_id"], r["received_on"]) == receipt.groups(), po


def test_the_site_rows_match_the_service(client):
    sites = {s["site_id"]: s for s in client.get("/stores/sites", headers=H).json()["items"]}
    named = rows("S-", COMPANY) + rows("R-", COMPANY)
    assert len(named) == 20
    for row in named:
        s = sites[row[0]]
        town, street = (row[2], row[3]) if row[0].startswith("S-") else (row[1], row[2])
        assert (s["town"], s["street"]) == (town, street), row[0]


def test_the_feedback_numbers_in_the_file_match_the_service(client):
    assert "`GF-2610-0001` to `GF-2610-0260`" in TEXT
    x = client.get("/care/feedback", headers=H, params={"limit": 500}).json()["items"]
    for channel in ("call centre", "app review", "survey", "web form"):
        n = sum(1 for c in x if c["channel"] == channel)
        assert f"{channel} {n}" in TEXT, channel
    by_site = {}
    for c in x:
        by_site[c["site_id"]] = by_site.get(c["site_id"], 0) + 1
    ranked = ", ".join(f"{s} {n}" for s, n in sorted(by_site.items(), key=lambda kv: (-kv[1], kv[0])))
    assert ranked in TEXT
