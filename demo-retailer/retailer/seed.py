"""Builds the whole starting data set. Same retailer date and seed give the same data."""

from __future__ import annotations

from datetime import date

from .seed_care import build_care
from .seed_care_desk import build_care_desk
from .seed_catalogue import build_catalogue
from .seed_food import build_food
from .seed_loyalty import build_loyalty
from .seed_orders import build_orders
from .seed_perf import build_performance
from .seed_pricing import build_pricing
from .seed_property import build_property
from .seed_purch import build_purchasing
from .seed_purch_more import build_more
from .seed_range import SKUS
from .seed_stock import build_stock, line_position
from .seed_stores import build_sites
from .seed_tills import build_tills
from .seed_visits import build_visits


def build_all(today: date) -> dict:
    purchasing = build_purchasing(today)
    purchasing.update(build_more(today, purchasing))
    tills = build_tills(today)
    orders = build_orders(today, tills)
    # version 1.3: Rowanmere Market's side of the business
    catalogue = build_catalogue(today)
    stock = build_stock(today, orders["orders"])
    cover = {sku: line_position(stock["stock_levels"][sku], stock["supply_terms"][sku], today)["days_of_cover"] for sku in SKUS}
    pricing = build_pricing(today, stock["stock_levels"], cover)
    loyalty = build_loyalty(today, catalogue["catalogue_products"])
    return {"sites": build_sites(), **build_visits(today), **build_food(today), **build_care(today),
            **build_care_desk(today), **purchasing, **build_property(today), **build_performance(today), **tills,
            **orders, **catalogue, **stock, **pricing, **loyalty}
