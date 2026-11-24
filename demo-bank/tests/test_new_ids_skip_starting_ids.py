"""A new record never takes an id the starting data already holds.

Contact notes are numbered from CNT-5100 and the starting data holds CNT-5201 to CNT-5206.
Payments made to arrive are numbered from PAY-6301 and the starting data holds PAY-6390, PAY-6401 and PAY-6402.
"""
import copy
from datetime import date

from bank import events
from bank.seed import build_all
from conftest import H, TODAY

START = build_all(date.fromisoformat(TODAY))
NOTE = {"channel": "call", "subject": "A question", "summary": "Asked about fees."}


def test_the_starting_data_holds_ids_above_the_first_new_number():
    assert all(f"CNT-{n}" in START["contacts"] for n in range(5201, 5207))
    assert all(p in START["payments"] for p in ("PAY-6390", "PAY-6401", "PAY-6402"))


def test_a_new_contact_note_never_overwrites_a_note_of_the_starting_data(client, store):
    made = []
    for _ in range(110):
        r = client.post("/core/customers/CUS-1001/contacts", json=NOTE, headers=H)
        assert r.status_code == 200
        made.append(r.json()["contact"]["contact_id"])
    assert len(set(made)) == 110 and not set(made) & set(START["contacts"])
    assert len(store.data["contacts"]) == len(START["contacts"]) + 110
    for n in range(5201, 5207):
        assert store.data["contacts"][f"CNT-{n}"] == START["contacts"][f"CNT-{n}"]
    assert made[100] == "CNT-5200" and made[101] == "CNT-5207"


def test_a_payment_made_to_arrive_never_overwrites_a_payment_of_the_starting_data(store):
    before = copy.deepcopy({p: store.data["payments"][p] for p in ("PAY-6390", "PAY-6401", "PAY-6402")})
    made = [events.simulate(store, "payment-repair")["item_id"] for _ in range(104)]
    assert len(set(made)) == 104
    for p, record in before.items():
        assert store.data["payments"][p] == record
    new_payments = set(store.data["payments"]) - set(START["payments"])
    assert len(new_payments) == 104 and "PAY-6389" in new_payments and "PAY-6391" in new_payments and "PAY-6403" in new_payments
