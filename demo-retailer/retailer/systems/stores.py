"""Stores: the group's stores and restaurants, their areas, area managers and franchisees."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "stores"
TITLE = "Stores"
LINE = "The group's stores and restaurants: town, street, area, area manager and franchisee."

SITE_FIELDS = "site_id, name, kind (store or restaurant), format, town, street, area, area_manager, franchised and franchisee"


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the group's sites: eight stores of Rowanmere Market and twelve restaurants "
                                  "of Rowanmere Kitchen. It only reads.")
    st = ctx.store
    d = lambda: st.data

    @reg(app, "get", "/sites", "list_sites", "List stores and restaurants",
         f"List the group's sites, sorted by site id. Each row has {SITE_FIELDS}. Store ids start with S- and restaurant ids "
         "start with R-. franchised is true for a restaurant run by a franchisee, and then franchisee names the company. "
         "Every filter is optional and the filters add up. Use the site_id from here in the other systems.")
    def list_sites(kind: Literal["store", "restaurant"] | None = Query(None, description="Only this kind of site: store or restaurant."),
                   town: str | None = Query(None, description="Only sites in this town, for example Port Ilvane. Not case sensitive."),
                   franchised: bool | None = Query(None, description="true for franchised restaurants only, false for all the others.")):
        rows = [s for s in d()["sites"].values()
                if (kind is None or s["kind"] == kind)
                and (not town or s["town"].lower() == town.strip().lower())
                and (franchised is None or s["franchised"] == franchised)]
        return listing(sorted(rows, key=lambda s: s["site_id"]))

    @reg(app, "get", "/sites/{site_id}", "get_site", "Get one store or restaurant",
         f"Read one site: {SITE_FIELDS}. Find the id with list_sites, for example R-014 or S-101.")
    def get_site(site_id: str = Path(..., description="Site id, for example R-014 or S-101.")):
        site = d()["sites"].get(site_id)
        if not site:
            raise not_found("site", site_id, "Use list_sites to find site ids.")
        return site

    return app
