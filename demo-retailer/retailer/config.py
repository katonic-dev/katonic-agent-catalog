"""Settings read from the environment. Nothing here touches the disk."""

from __future__ import annotations

import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

log = logging.getLogger("demo-retailer")

RETAILER_NAME = "Rowanmere Group"
INVENTED_NOTICE = (
    "Rowanmere Group is invented, and so is every person, company, store, restaurant, supplier "
    "and record in this service. Nothing here describes a real retailer or a real customer."
)
SEED = 20261124


@dataclass
class Settings:
    retailer_today: date
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
        return Path(dataset) / "demo-retailer-state"
    return None


def load_settings(env: dict | None = None) -> Settings:
    env = dict(os.environ if env is None else env)
    raw_date = env.get("RETAILER_TODAY", "").strip()
    if raw_date:
        today = date.fromisoformat(raw_date)
    else:
        today = date.today()
    key = env.get("RETAILER_API_KEY", "").strip()
    generated = False
    if not key:
        key = secrets.token_urlsafe(24)
        generated = True
    auth_off = env.get("RETAILER_AUTH", "on").strip().lower() == "off"
    hooks: list[dict] = []
    raw_hooks = env.get("RETAILER_WEBHOOKS", "").strip()
    if raw_hooks:
        try:
            parsed = json.loads(raw_hooks)
            if isinstance(parsed, list):
                hooks = [h for h in parsed if isinstance(h, dict)]
        except ValueError:
            log.warning("RETAILER_WEBHOOKS is not valid JSON and was ignored")
    return Settings(
        retailer_today=today,
        api_key=key,
        key_was_generated=generated,
        auth_enabled=not auth_off,
        data_dir=_resolve_data_dir(env),
        webhooks=hooks,
    )
