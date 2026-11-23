"""In-memory state. Written to one JSON file only when a data directory is given."""

from __future__ import annotations

import copy
import json
import logging
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone

from .config import SEED, Settings
from .seed import build_all

log = logging.getLogger("demo-bank")
STATE_FILE = "demo-bank-state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lock = threading.RLock()
        self.data: dict = {}
        self.counters: dict = {}
        self.simulated: dict = {}
        self.subscriptions: list[dict] = []
        self.events: list[dict] = []
        self.reset(clear_files=False)
        self._load_file()
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
            if saved.get("bank_today") == self.settings.bank_today.isoformat() and saved.get("seed") == SEED:
                self.data, self.counters = saved["data"], saved["counters"]
                self.simulated = saved.get("simulated", {})
                for key, value in build_all(self.settings.bank_today).items():  # a file from an older version
                    self.data.setdefault(key, value)
        except Exception as exc:  # a damaged file never stops the service
            log.warning("State file ignored: %s", exc)

    def save(self) -> None:
        path = self._path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"bank_today": self.settings.bank_today.isoformat(), "seed": SEED, "data": self.data,
                       "counters": self.counters, "simulated": self.simulated}
            fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, path)
        except Exception as exc:
            log.warning("Could not write state file: %s", exc)

    def reset(self, clear_files: bool = True) -> None:
        with self.lock:
            self.data = build_all(self.settings.bank_today)
            self.counters = {}
            self.simulated = {}
            if clear_files:
                self.events = []
                path = self._path()
                if path is not None and path.exists():
                    try:
                        path.unlink()
                    except OSError:
                        pass

    # ----- helpers used by the systems
    def next_number(self, key: str, start: int) -> int:
        with self.lock:
            n = self.counters.get(key, start)
            self.counters[key] = n + 1
            return n

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
        openc = lambda coll, field="status", val="open": sum(1 for x in d[coll].values() if x.get(field) == val)
        return {
            "customers": len(d["customers"]), "accounts": len(d["accounts"]), "transactions": len(d["transactions"]),
            "cards": len(d["cards"]),
            "open_card_disputes": openc("disputes"),
            "open_screening_alerts": openc("screening_alerts"),
            "open_monitoring_alerts": openc("monitoring_alerts"),
            "open_cases": openc("cases"),
            "open_payment_investigations": openc("investigations"),
            "held_payment_repairs": sum(1 for r in d["repairs"].values() if r["status"] in ("held", "proposed")),
            "loan_applications_received": sum(1 for a in d["applications"].values() if a["status"] == "received"),
            "approved_loans": len(d["approved_terms"]),
            "open_fraud_cases": openc("fraud_cases"),
            "open_reconciliation_breaks": openc("recon_breaks"),
            "news_articles": len(d["news_articles"]),
            "regulator_publications": len(d["regulator_publications"]),
        }
