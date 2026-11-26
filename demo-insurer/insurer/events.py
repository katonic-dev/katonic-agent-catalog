"""Events: simulate new items and tell subscribers with a plain-language message."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request


from .seed_policy import d_ago, long_date
from .store import Store, now_iso

KINDS = ["loss-report"]
SYSTEM_OF = {"loss-report": "claims"}
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

def _loss_report(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.insurer_today
    day = long_date(d_ago(today, 1))
    templates = [
        ("web form", "Corwin Ashgrove", "POL-2001",
         f"Policy POL-2001. On {day} a stone thrown up by a lorry on the Marlow Reach bypass cracked my windscreen. Nobody was hurt and "
         "I did not get the lorry's registration."),
        ("email", "Henrietta Quillby", "POL-2006",
         "My policy is POL-2006. There is a damp patch spreading on the bathroom wall at 61 Thistledown Close. I do not know when it started."),
        ("telephone note", "Bram Tollermoor", "POL-2005",
         f"Call taken by the first contact team. Mr Tollermoor, policy POL-2005, reports that on {day} his Vesper Lane (registration "
         "MR-7720-B) was scratched along one side while parked at Marlow Reach station. Nobody was hurt."),
        ("web form", "Teodor Brackwell", "POL-2009",
         f"Policy POL-2009. On {day} I slipped on the wet kitchen floor after the washing machine leaked at 12 Millpond Court and hurt my wrist. "
         "The kitchen floor is damaged."),
    ]
    channel, reporter, number, text = templates[n % 4]
    rid = store.next_free("sim_lr", 3101, d["loss_reports"], lambda k: f"LR-{k}")
    d["loss_reports"][rid] = {"loss_report_id": rid, "status": "new", "channel": channel, "received": today.isoformat(),
                              "reporter": reporter, "policy_number_given": number, "text": text, "claim_file_drafts": [], "claim_id": None}
    return rid, (f"A new loss report {rid} has arrived in the claims system from {reporter}. It is new and needs a claim file prepared. "
                 f"Read it with get_loss_report in the claims system.")


MAKERS = {"loss-report": _loss_report}


def simulate(store: Store, kind: str, wait: bool = False) -> dict:
    with store.lock:
        n = store.simulated.get(kind, 0)
        store.simulated[kind] = n + 1
        item_id, message = MAKERS[kind](store, n)
        store.save()
    queued = dispatch(store, kind, item_id, message, wait=wait)
    return {"event_type": kind, "item_id": item_id, "system": SYSTEM_OF[kind], "message": message, "deliveries": queued}
