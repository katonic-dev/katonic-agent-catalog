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

log = logging.getLogger("demo-insurer")
STATE_FILE = "demo-insurer-state.json"
SHARED_COUNTERS = {"event"}  # numbers the whole insurer shares: they go back only with a full reset


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
            if saved.get("insurer_today") == self.settings.insurer_today.isoformat() and saved.get("seed") == SEED:
                self.data, self.counters = saved["data"], saved["counters"]
                self.simulated = saved.get("simulated", {})
                self.changed = saved.get("changed", {})
                for key, value in build_all(self.settings.insurer_today).items():  # a file from an older version
                    self.data.setdefault(key, value)
        except Exception as exc:  # a damaged file never stops the service
            log.warning("State file ignored: %s", exc)

    def save(self) -> None:
        path = self._path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"insurer_today": self.settings.insurer_today.isoformat(), "seed": SEED, "data": self.data,
                       "counters": self.counters, "simulated": self.simulated, "changed": self.changed}
            fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, path)
        except Exception as exc:
            log.warning("Could not write state file: %s", exc)

    def reset(self, clear_files: bool = True) -> None:
        with self.lock:
            self.data = build_all(self.settings.insurer_today)
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
                fresh = build_all(self.settings.insurer_today)
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
        return {
            "policies": len(d["policies"]),
            "policies_in_force": sum(1 for p in d["policies"].values() if p["status"] == "in_force"),
            "wordings": len(d["wordings"]),
            "new_loss_reports": sum(1 for r in d["loss_reports"].values() if r["status"] == "new"),
            "claims": len(d["claims"]),
            "new_claims": sum(1 for c in d["claims"].values() if c["status"] == "new"),
            "claims_in_assessment": sum(1 for c in d["claims"].values() if c["status"] == "in_assessment"),
            "claims_decided": sum(1 for c in d["claims"].values() if c["status"] == "decided"),
            "health_members": len(d["health_members"]),
            "pre_authorisation_requests_received": sum(1 for r in d["pre_authorisations"].values() if r["status"] == "received"),
            "medical_claims_held": sum(1 for c in d["medical_claims"].values() if c["status"] == "held"),
            "provider_invoices_received": sum(1 for i in d["provider_invoices"].values() if i["status"] == "received"),
            "underwriting_submissions_received": sum(1 for s in d["uw_submissions"].values() if s["status"] == "received"),
            "underwriting_referrals_to_draft": len(d["uw_referrals"]),
            "renewals_due_for_review": len(d["uw_renewals"]),
            "closed_claims_in_the_leakage_review": len(d["leakage_claims"]),
            "claims_waiting_for_the_fraud_check": sum(1 for c in d["investigation_claims"].values() if c["status"] == "new"),
            "claims_referred_to_investigations": sum(1 for c in d["investigation_claims"].values() if c["status"] == "flagged"),
            "change_requests_received": sum(1 for c in d["sv_change_requests"].values() if c["status"] == "received"),
            "certificate_requests_received": sum(1 for c in d["sv_certificate_requests"].values() if c["status"] == "received"),
            "broker_call_back_requests_saved": sum(len(b["call_back_requests"]) for b in d["sv_brokers"].values()),
            "complaints_new": sum(1 for c in d["cd_complaints"].values() if c["status"] == "new"),
            "regulatory_publications_new": sum(1 for p in d["cd_publications"].values() if p["status"] == "new"),
            "disputed_claims_to_be_sorted": len(d["cd_disputes"]),
        }
