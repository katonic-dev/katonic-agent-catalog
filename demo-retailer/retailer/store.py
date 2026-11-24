"""In-memory state. Written to one JSON file only when a data directory is given."""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone

from .config import SEED, Settings
from .seed import build_all

log = logging.getLogger("demo-retailer")
STATE_FILE = "demo-retailer-state.json"
SHARED_COUNTERS = {"event"}  # numbers the whole retailer shares: they go back only with a full reset


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def digest(value) -> str:
    return hashlib.sha1(json.dumps(value, default=str).encode("utf-8")).hexdigest()


def sharing_groups(data: dict) -> list[set]:
    """Sets of record sets that hold some of the same objects, and so must be put back together."""
    owner: dict = {}
    parent = {name: name for name in data}

    def root(name):
        while parent[name] != name:
            name = parent[name]
        return name

    def walk(obj, name):
        if not isinstance(obj, (dict, list)):
            return
        first = owner.setdefault(id(obj), name)
        if first != name:
            parent[root(name)] = root(first)
            return
        for child in (obj.values() if isinstance(obj, dict) else obj):
            walk(child, name)

    for name, value in data.items():
        walk(value, name)
    groups: dict = {}
    for name in data:
        groups.setdefault(root(name), set()).add(name)
    return [g for g in groups.values() if len(g) > 1]


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lock = threading.RLock()
        self.data: dict = {}
        self.counters: dict = {}
        self.simulated: dict = {}
        self.changed: dict = {}  # system -> the record sets and counters its requests have changed
        self._marks: dict = {}
        self._counter_marks: dict = {}
        self.subscriptions: list[dict] = []
        self.events: list[dict] = []
        self.reset(clear_files=False)
        self._load_file()
        self._mark()
        for hook in settings.webhooks:
            self.add_subscription(hook.get("event_kind", "*"), hook.get("url", ""),
                                  hook.get("header_name", ""), hook.get("secret_value", ""))

    # ----- state file (only when a writable directory is given)
    def _path(self):
        if self.settings.data_dir is None:
            return None
        return self.settings.data_dir / STATE_FILE

    def _load_file(self) -> None:
        path = self._path()
        if path is None or not path.exists():
            return
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            if saved.get("retailer_today") == self.settings.retailer_today.isoformat() and saved.get("seed") == SEED:
                self.data, self.counters = saved["data"], saved["counters"]
                self.simulated = saved.get("simulated", {})
                self.changed = saved.get("changed", {})
                for key, value in build_all(self.settings.retailer_today).items():  # a file from an older version
                    self.data.setdefault(key, value)
        except Exception as exc:  # a damaged file never stops the service
            log.warning("State file ignored: %s", exc)

    def save(self) -> None:
        path = self._path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"retailer_today": self.settings.retailer_today.isoformat(), "seed": SEED, "data": self.data,
                       "counters": self.counters, "simulated": self.simulated, "changed": self.changed}
            fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, path)
        except Exception as exc:
            log.warning("Could not write state file: %s", exc)

    def reset(self, clear_files: bool = True) -> None:
        with self.lock:
            self.data = build_all(self.settings.retailer_today)
            self.counters = {}
            self.simulated = {}
            self.changed = {}
            self._mark()
            if clear_files:
                self.events = []
                path = self._path()
                if path is not None and path.exists():
                    try:
                        path.unlink()
                    except OSError:
                        pass

    # ----- who changed what, so one system can be put back without the others
    def _mark(self) -> None:
        self._marks = {name: digest(value) for name, value in self.data.items()}
        self._counter_marks = dict(self.counters)

    def note_writes(self, system: str) -> None:
        """After a request that may have written: put the record sets and counters that changed down to this system."""
        with self.lock:
            now = {name: digest(value) for name, value in self.data.items()}
            sets = [name for name in now if now[name] != self._marks.get(name)]
            counters = [key for key in self.counters
                        if key not in SHARED_COUNTERS and self.counters[key] != self._counter_marks.get(key)]
            self._marks, self._counter_marks = now, dict(self.counters)
            if not sets and not counters:
                return
            mine = self.changed.setdefault(system, {"sets": [], "counters": []})
            mine["sets"] = sorted(set(mine["sets"]) | set(sets))
            mine["counters"] = sorted(set(mine["counters"]) | set(counters))
            self.save()

    def reset_system(self, system: str, kinds: tuple = ()) -> list[str]:
        """Put back what this one system has changed since the start or the last full reset. Returns the record sets put back."""
        with self.lock:
            mine = self.changed.pop(system, {"sets": [], "counters": []})
            sets = set(mine["sets"])
            if sets:
                fresh = build_all(self.settings.retailer_today)
                for group in sharing_groups(fresh):
                    if sets & group:
                        sets |= group
                for name in sets:
                    self.data[name] = fresh[name]
                    self._marks[name] = digest(fresh[name])
            for key in mine["counters"]:
                self.counters.pop(key, None)
                self._counter_marks.pop(key, None)
            for kind in kinds:
                self.simulated.pop(kind, None)
            for other in self.changed.values():  # what another system changed in the same record sets is gone as well
                other["sets"] = [name for name in other["sets"] if name not in sets]
                other["counters"] = [key for key in other["counters"] if key not in mine["counters"]]
            self.changed = {name: rec for name, rec in self.changed.items() if rec["sets"] or rec["counters"]}
            self.save()
            return sorted(sets)

    # ----- helpers used by the systems
    def next_number(self, key: str, start: int) -> int:
        with self.lock:
            n = self.counters.get(key, start)
            self.counters[key] = n + 1
            return n

    def next_free(self, key: str, start: int, taken, make) -> str:
        """The next id that is not in use: a number the starting data already holds is skipped, never overwritten."""
        with self.lock:
            while True:
                ident = make(self.next_number(key, start))
                if ident not in taken:
                    return ident

    def add_draft(self, item: dict, field: str, payload: dict, drafted_by: str) -> dict:
        with self.lock:
            versions = item.setdefault(field, [])
            version = {"version": len(versions) + 1, "drafted_by": drafted_by or "agent",
                       "drafted_at": now_iso(), **copy.deepcopy(payload)}
            versions.append(version)
            self.save()
            return version

    # ----- subscriptions (memory only, never saved)
    def add_subscription(self, kind: str, url: str, header: str, secret: str) -> dict:
        with self.lock:
            sub = {"subscription_id": f"SUB-{uuid.uuid4().hex[:8]}", "event_kind": kind or "*", "url": url,
                   "header_name": header, "secret_value": secret}
            self.subscriptions.append(sub)
            return sub

    def counts(self) -> dict:
        d = self.data
        sites = d["sites"].values()
        return {
            "stores": sum(1 for s in sites if s["kind"] == "store"),
            "restaurants": sum(1 for s in sites if s["kind"] == "restaurant"),
            "site_visits": len(d["site_visits"]),
            "site_visits_without_a_report": sum(1 for v in d["site_visits"].values() if not v["reports"]),
            "record_periods": len(d["fs_records"]),
            "record_periods_not_reviewed": sum(1 for r in d["fs_reviews"].values() if r["status"] == "not_reviewed"),
            "guest_feedback_comments": len(d["guest_feedback"]),
            "suppliers": len(d["suppliers"]),
            "purchase_orders": len(d["purchase_orders"]),
            "goods_receipts": len(d["goods_receipts"]),
            "supplier_invoices_received": sum(1 for i in d["supplier_invoices"].values() if i["status"] == "received"),
            "supplier_invoices_queried": sum(1 for i in d["supplier_invoices"].values() if i["status"] == "queried"),
            "supplier_invoices_approved": sum(1 for i in d["supplier_invoices"].values() if i["status"] == "approved"),
            "leases": len(d["leases"]),
            "lease_summaries": sum(len(x["summaries"]) for x in d["leases"].values()),
            "performance_periods": len({x["period"] for x in d["performance"].values()}),
            "performance_reviews": sum(len(x["reviews"]) for x in d["performance_reviews"].values()),
            "till_refunds": sum(1 for x in d["till_rows"].values() if x["kind"] == "refund"),
            "till_voids": sum(1 for x in d["till_rows"].values() if x["kind"] == "void"),
            "till_discounts": sum(1 for x in d["till_rows"].values() if x["kind"] == "discount"),
            "till_audits": sum(len(x["audits"]) for x in d["till_audits"].values()),
            "online_orders": len(d["orders"]),
            "orders_awaiting_fraud_review": sum(1 for o in d["orders"].values() if o["flag"] and o["flag"]["status"] == "awaiting_review"),
            "return_requests": len(d["return_requests"]),
            "return_requests_not_decided": sum(1 for r in d["return_requests"].values() if r["status"] == "requested"),
            "customer_tickets_open": sum(1 for t in d["tickets"].values() if t["status"] == "open"),
            "complaints_open": sum(1 for c in d["complaints"].values() if c["status"] == "open"),
            "public_reviews_unanswered": sum(1 for r in d["public_reviews"].values() if r["status"] == "unanswered"),
            "delivery_notes": len(d["delivery_notes"]),
            "delivery_note_claims_sent": sum(1 for n in d["delivery_notes"].values() if n["status"] == "claim_sent"),
            "supplier_payments": len(d["supplier_payments"]),
            "supplier_questions_open": sum(1 for q in d["supplier_questions"].values() if q["status"] == "open"),
            # version 1.3
            "product_listings": len(d["catalogue_products"]),
            "products_awaiting_description": sum(1 for x in d["catalogue_products"].values() if x["status"] == "awaiting_description"),
            "product_data_checks": len(d["product_data_checks"]["checks"]),
            "search_terms_analyses": sum(len(x["analyses"]) for x in d["search_analyses"].values()),
            "stock_lines": len(d["stock_levels"]),
            "replenishment_plans": len(d["replenishment_plans"]["plans"]),
            "stock_counts": len(d["stock_counts"]),
            "shrink_analyses": sum(len(x["analyses"]) for x in d["shrink_analyses"].values()),
            "batches": len(d["batches"]),
            "batches_recalled": sum(1 for b in d["batches"].values() if b["status"] == "recalled"),
            "recall_notices_issued": sum(1 for b in d["batches"].values() if b["status"] == "notice_issued"),
            "price_file_lines": len(d["price_file"]),
            "price_recommendation_drafts": len(d["price_recommendations"]["drafts"]),
            "promotions_finished": sum(1 for p in d["promotions"].values() if p["status"] == "finished"),
            "promotion_reviews": sum(len(p["reviews"]) for p in d["promotions"].values()),
            "range_review_packs": sum(len(x["packs"]) for x in d["range_packs"].values()),
            "demand_plan_notes": len(d["demand_notes"]["notes"]),
            "loyalty_members": len(d["loyalty_members"]),
            "member_suggestion_drafts": sum(len(m["suggestion_drafts"]) for m in d["loyalty_members"].values()),
            "campaign_briefs": len(d["campaign_briefs"]["briefs"]),
        }
