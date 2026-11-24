"""Stores and restaurants of the invented group."""

from __future__ import annotations

AREAS = {
    "Ilvane Area": "Odalys Fenwright-Mourne",
    "Marlow Area": "Brannock Teague-Lowell",
    "Tallowby Area": "Isaura Vennick-Dray",
}

# site_id, kind, name, town, street, area, franchisee
_STORES = [
    ("S-101", "Rowanmere Market Port Ilvane Central", "Port Ilvane", "Market Street", "Ilvane Area", "supermarket"),
    ("S-102", "Rowanmere Market Dockside", "Port Ilvane", "Dockside Parade", "Ilvane Area", "supermarket"),
    ("S-103", "Rowanmere Market Ferry Road", "Port Ilvane", "Ferry Road", "Ilvane Area", "convenience"),
    ("S-104", "Rowanmere Market Marlow High Street", "Marlow Reach", "High Street", "Marlow Area", "supermarket"),
    ("S-105", "Rowanmere Market Reach Road", "Marlow Reach", "Reach Road", "Marlow Area", "convenience"),
    ("S-106", "Rowanmere Market Causeway Park", "Marlow Reach", "Causeway Park", "Marlow Area", "convenience"),
    ("S-107", "Rowanmere Market Tallowby Brewery Lane", "Tallowby", "Brewery Lane", "Tallowby Area", "supermarket"),
    ("S-108", "Rowanmere Market Tallowby Mill Road", "Tallowby", "Mill Road", "Tallowby Area", "convenience"),
]

# site_id, town, street, area, franchisee
_RESTAURANTS = [
    ("R-014", "Port Ilvane", "Harbour Street", "Ilvane Area", ""),
    ("R-022", "Port Ilvane", "Malting Lane", "Ilvane Area", ""),
    ("R-031", "Marlow Reach", "Quayside", "Marlow Area", ""),
    ("R-047", "Tallowby", "Kiln Road", "Tallowby Area", ""),
    ("R-058", "Port Ilvane", "Lantern Square", "Ilvane Area", ""),
    ("R-063", "Marlow Reach", "Station Parade", "Marlow Area", ""),
    ("R-071", "Port Ilvane", "Netmakers Row", "Ilvane Area", ""),
    ("R-076", "Marlow Reach", "Chandlers Walk", "Marlow Area", ""),
    ("R-082", "Tallowby", "Tanners Hill", "Tallowby Area", ""),
    ("R-090", "Tallowby", "Saddlers Close", "Tallowby Area", "Brindle-Crake Foods Ltd"),
    ("R-104", "Marlow Reach", "Bellfounders Road", "Marlow Area", "Wickersham-Ode Pizza Partners Ltd"),
    ("R-117", "Port Ilvane", "Rope Walk", "Ilvane Area", "Ostrand-Pell Quick Meals Ltd"),
]

RESTAURANT_IDS = [r[0] for r in _RESTAURANTS]
EXTRA_RESTAURANT_IDS = RESTAURANT_IDS[6:]  # the six that have no records at the start


def build_sites() -> dict:
    sites = {}
    for sid, name, town, street, area, fmt in _STORES:
        sites[sid] = {"site_id": sid, "name": name, "kind": "store", "format": fmt, "town": town, "street": street,
                      "area": area, "area_manager": AREAS[area], "franchised": False, "franchisee": ""}
    for sid, town, street, area, franchisee in _RESTAURANTS:
        sites[sid] = {"site_id": sid, "name": f"Rowanmere Kitchen {street}", "kind": "restaurant", "format": "quick-service",
                      "town": town, "street": street, "area": area, "area_manager": AREAS[area],
                      "franchised": bool(franchisee), "franchisee": franchisee}
    return sites
