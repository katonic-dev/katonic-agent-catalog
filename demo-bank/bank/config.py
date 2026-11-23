"""Settings read from the environment. Nothing here touches the disk."""

from __future__ import annotations

import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

log = logging.getLogger("demo-bank")

BANK_NAME = "Meridian Trust Bank"
INVENTED_NOTICE = (
    "Meridian Trust Bank is invented, and so is every person, company, account "
    "and record in this service. Nothing here describes a real bank or a real customer."
)
SEED = 20260101


@dataclass
class Settings:
    bank_today: date
    api_key: str
    key_was_generated: bool
    auth_enabled: bool
    data_dir: Path | None
    webhooks: list[dict] = field(default_factory=list)


def _resolve_data_dir(env: dict) -> Path | None:
    explicit = env.get("DATA_DIR", "").strip()
    if explicit:
        return Path(explicit)
    dataset = env.get("KATONIC_DATASET_PATH", "").strip()
    if dataset:
        return Path(dataset) / "demo-bank-state"
    return None


def load_settings(env: dict | None = None) -> Settings:
    env = dict(os.environ if env is None else env)
    raw_date = env.get("BANK_TODAY", "").strip()
    if raw_date:
        today = date.fromisoformat(raw_date)
    else:
        today = date.today()
    key = env.get("BANK_API_KEY", "").strip()
    generated = False
    if not key:
        key = secrets.token_urlsafe(24)
        generated = True
    auth_off = env.get("BANK_AUTH", "on").strip().lower() == "off"
    hooks: list[dict] = []
    raw_hooks = env.get("BANK_WEBHOOKS", "").strip()
    if raw_hooks:
        try:
            parsed = json.loads(raw_hooks)
            if isinstance(parsed, list):
                hooks = [h for h in parsed if isinstance(h, dict)]
        except ValueError:
            log.warning("BANK_WEBHOOKS is not valid JSON and was ignored")
    return Settings(
        bank_today=today,
        api_key=key,
        key_was_generated=generated,
        auth_enabled=not auth_off,
        data_dir=_resolve_data_dir(env),
        webhooks=hooks,
    )
