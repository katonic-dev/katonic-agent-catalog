"""Events: simulate new items and tell subscribers with a plain-language message."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

from .seed_food import sim_records
from .seed_purch import sim_invoice
from .store import Store, now_iso

KINDS = ["supplier-invoice", "food-safety-records"]
SYSTEM_OF = {"supplier-invoice": "purchasing", "food-safety-records": "foodsafety"}
TIMEOUT = 10

# ----------------------------------------------------------------- sending

def _post(store: Store, sub: dict, payload: dict, event_id: str) -> None:
    started = now_iso()
    outcome = {"event_id": event_id, "subscription_id": sub["subscription_id"], "url": sub["url"],
               "sent_at": started, "status": "failed", "http_status": None, "error": ""}
    try:
        headers = {"Content-Type": "application/json"}
        if sub.get("header_name"):
            headers[sub["header_name"]] = sub.get("secret_value", "")
        req = urllib.request.Request(sub["url"], data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            outcome["http_status"] = resp.status
            outcome["status"] = "delivered" if 200 <= resp.status < 300 else "failed"
    except urllib.error.HTTPError as exc:
        outcome["http_status"] = exc.code
        outcome["error"] = f"HTTP {exc.code}"
    except Exception as exc:  # never fails the caller
        outcome["error"] = f"{type(exc).__name__}: {exc}"
    with store.lock:
        store.events.append(outcome)


def dispatch(store: Store, kind: str, item_id: str, message: str, wait: bool = False) -> list[dict]:
    """Send to every matching subscription in the background. Returns what was queued."""
    event_id = f"EVT-{store.next_number('event', 1):04d}"
    payload = {"message": message, "event_type": kind, "item_id": item_id, "system": SYSTEM_OF[kind], "demo_data": True}
    queued, threads = [], []
    with store.lock:
        subs = [s for s in store.subscriptions if s["event_kind"] in ("*", kind)]
        store.events.append({"event_id": event_id, "subscription_id": None, "url": None, "sent_at": now_iso(),
                             "status": "created", "http_status": None, "error": "", "event_type": kind,
                             "item_id": item_id, "subscribers": len(subs)})
    for s in subs:
        t = threading.Thread(target=_post, args=(store, s, payload, event_id), daemon=True)
        t.start()
        threads.append(t)
        queued.append({"subscription_id": s["subscription_id"], "status": "queued"})
    if wait:
        for t in threads:
            t.join(TIMEOUT + 2)
    return queued


# ----------------------------------------------------------------- simulate

def _invoice(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.retailer_today
    po = store.next_free("sim_po", 1, d["purchase_orders"], lambda k: f"PO-{450200 + k}")
    receipt = store.next_free("sim_gr", 1, d["goods_receipts"], lambda k: f"GR-{60200 + k}")
    number = store.next_free("sim_inv", 1, d["supplier_invoices"], lambda k: f"INV-{4400 + k}")
    return sim_invoice(d, today, n % 4, po, receipt, number)


def _records(store: Store, n: int) -> tuple[str, str]:
    return sim_records(store.data, store.settings.retailer_today, n % 4, store.next_number("sim_fsr", 1))


MAKERS = {"supplier-invoice": _invoice, "food-safety-records": _records}


def simulate(store: Store, kind: str, wait: bool = False) -> dict:
    with store.lock:
        n = store.simulated.get(kind, 0)
        store.simulated[kind] = n + 1
        item_id, message = MAKERS[kind](store, n)
        store.save()
    queued = dispatch(store, kind, item_id, message, wait=wait)
    return {"event_type": kind, "item_id": item_id, "system": SYSTEM_OF[kind], "message": message, "deliveries": queued}
