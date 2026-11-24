"""Builds the whole starting data set. Same retailer date and seed give the same data."""

from __future__ import annotations

from datetime import date

from .seed_care import build_care
from .seed_food import build_food
from .seed_perf import build_performance
from .seed_property import build_property
from .seed_purch import build_purchasing
from .seed_stores import build_sites
from .seed_tills import build_tills
from .seed_visits import build_visits


def build_all(today: date) -> dict:
    return {"sites": build_sites(), **build_visits(today), **build_food(today), **build_care(today),
            **build_purchasing(today), **build_property(today), **build_performance(today), **build_tills(today)}
