"""Version 1.3: the catalogue, stock, pricing and loyalty systems of Rowanmere Market.

Every planted case is read back through the API and compared with the tables in SCENARIOS.md. The tests work the
right answers out from what the API serves, the way an agent has to, and never read them from the seed.
"""
import copy
import json
from datetime import date
from pathlib import Path

import pytest

from bodies_1_3 import (BRIEF, DATA_CHECK, DEMAND_NOTE, DESCRIPTION, PACK, PLAN, PRICES, RANGE_PACK, REVIEW, SHRINK,
                        SUGGESTIONS, TERMS)
from conftest import H, KEY, TODAY
from retailer.seed import build_all
from retailer.seed_catalogue import style_guide_markdown
from retailer.seed_loyalty import brief_template_markdown
from test_operations import get, post

TEXT = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
LIBRARY = Path(__file__).resolve().parents[2] / "retail" / "policy-library"
TODAY_D = date.fromisoformat(TODAY)
PERIOD = "2026-10"
NEW_SYSTEMS = ["catalogue", "stock", "pricing", "loyalty"]
STORES = [f"S-10{n}" for n in range(1, 9)]


def section(title):
    return TEXT.split(f"## {title}")[1].split("\n## ")[0]


def rows(prefix, text):
    return [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith(f"| {prefix}")]


def num(text):
    return float(text.replace(",", ""))


def simulate(client, kind):
    return post(client, f"/admin/simulate/{kind}")


RANGE = section("The range")
DATA = section("Product data check")
NEW = section("New products and descriptions")
SEARCH = section("Search terms")
REPLENISH = section("Replenishment")
LOSS = section("Stock loss")
RECALL = section("A recalled batch")
PRICING = section("Prices")
PROMOS = section("Promotions")
RANGE_REVIEW = section("Range review")
DEMAND = section("Demand planning")
MEMBERS = section("Loyalty members and suggestions")
CAMPAIGNS = section("Campaigns")
ARRIVALS = section("Simulated arrivals")
ATTRIBUTES = ["net_quantity", "pack_size", "allergen_statement", "country_of_origin"]


# ================================================================ the range

def test_sixty_lines_in_eight_categories_shared_by_the_four_systems(client, store):
    listings = get(client, "/catalogue/listings")
    assert listings["count"] == 60
    by_category = {}
    for x in listings["items"]:
        by_category[x["category"]] = by_category.get(x["category"], 0) + 1
    for category, n in by_category.items():
        assert f"`{category}` ({n}" in RANGE or f"`{category}` ({n})" in RANGE, category
    assert len(by_category) == 8 and sum(by_category.values()) == 60
    skus = [x["sku"] for x in listings["items"]]
    assert skus == sorted(skus)
    assert [x["sku"] for x in get(client, "/stock/levels")["items"]] == skus
    assert [x["sku"] for x in get(client, "/pricing/prices")["items"]] == skus
    assert [x["sku"] for x in get(client, "/stock/supply-terms")["items"]] == skus
    assert sorted(x["sku"] for x in listings["items"] if x["age_restricted"]) == ["DR-5905", "DR-5906", "DR-5907"]
    # the seven lines the online orders already name keep their ids and prices
    prices = {x["sku"]: x["price"] for x in get(client, "/pricing/prices")["items"]}
    named = {}
    for o in store.data["orders"].values():
        for line in o["lines"]:
            if line["sku"] in prices:
                named[line["sku"]] = line["unit_price"]
    assert sorted(named) == ["AG-4401", "AG-4402", "AG-4403", "CH-5501", "FZ-5601", "PC-6601", "PC-6602"]
    assert all(prices[s] == p for s, p in named.items()) and all(f"`{s}`" in RANGE for s in named)


def test_the_ten_suppliers_and_their_lead_times(client):
    terms = get(client, "/stock/supply-terms")["items"]
    suppliers = {(t["supplier_id"], t["supplier_name"], t["lead_time_days"], t["supplier_in_purchasing"]) for t in terms}
    assert len(suppliers) == 10
    in_purchasing = {x["supplier_id"] for x in get(client, "/purchasing/suppliers")["items"]}
    for sid, name, lead, held in suppliers:
        assert f"{sid} {name}" in RANGE and (sid in in_purchasing) == held, sid
        assert f"{sid} {name} (lead time {lead} days)" in RANGE or f"{sid} {name} ({lead} days)" in RANGE or f"{sid} {name} ({lead})" in RANGE, sid
    assert {sid for sid, _, _, held in suppliers if held} == {"SUP-301", "SUP-303", "SUP-304"}
    one = get(client, "/stock/supply-terms", supplier_id="SUP-301")
    assert one["count"] == 4 and {t["payment_terms_days"] for t in one["items"]} == {45}
    assert get(client, "/stock/supply-terms", sku="HH-6105")["items"][0]["payment_terms_days"] is None
    get(client, "/stock/supply-terms", 404, sku="ZZ-0000")


# ================================================================ catalogue: the data check

def differences(client):
    """Every attribute of every listing that is missing or does not match the specification, worked out from the API."""
    found = []
    for x in get(client, "/catalogue/listings")["items"]:
        spec = get(client, f"/catalogue/specifications/{x['sku']}")
        for a in ATTRIBUTES:
            if x["attributes"][a] != spec[a]:
                found.append((x["sku"], a, "missing" if not x["attributes"][a] else "does_not_match", x["attributes"][a], spec[a]))
    return sorted(found)


def test_exactly_ten_listings_differ_from_their_specification(client):
    table = rows("", DATA)
    table = [r for r in table if r[0][:2].isalpha() and "-" in r[0] and r[0] != "Line"]
    want = sorted((r[0], r[2], r[3], "" if r[4] == "(nothing)" else r[4], r[5]) for r in table)
    assert len(want) == 10 and differences(client) == want
    for r in table:
        assert get(client, f"/catalogue/listings/{r[0]}")["name"] == r[1]
    by_attribute = {}
    for _, a, kind, _, _ in want:
        by_attribute[a] = by_attribute.get(a, 0) + 1
    assert by_attribute == {"net_quantity": 3, "allergen_statement": 3, "pack_size": 2, "country_of_origin": 2}
    assert sum(1 for w in want if w[2] == "missing") == 4
    assert "net quantity three, allergen statement three, pack size two, country of origin two" in DATA
    assert "Four are missing and six do not match" in DATA


def test_a_data_check_is_saved_as_versions_and_changes_no_listing(client, store):
    before = get(client, "/catalogue/listings/AG-4407")
    full = {"findings": [{"sku": s, "attribute": a, "kind": k, "listing_value": lv, "specification_value": sv}
                         for s, a, k, lv, sv in differences(client)], "drafted_by": "a test"}
    v1 = post(client, "/catalogue/data-checks", full)
    assert v1["applied"] is True and v1["kind"] == "draft" and v1["draft"]["version"] == 1 and len(v1["draft"]["findings"]) == 10
    v2 = post(client, "/catalogue/data-checks", {**DATA_CHECK, "summary": "Two found."})
    assert v2["draft"]["version"] == 2 and v2["draft"]["drafted_by"] == "a test"
    empty = post(client, "/catalogue/data-checks", {"findings": [], "category": "fresh_produce"})
    assert empty["draft"]["version"] == 3 and empty["draft"]["drafted_by"] == "agent"
    got = get(client, "/catalogue/data-checks")
    assert got["count"] == 3 and got["checks"][1]["summary"] == "Two found." and got["checks"][2]["category"] == "fresh_produce"
    assert get(client, "/catalogue/listings/AG-4407") == before
    assert get(client, "/admin/state")["counts"]["product_data_checks"] == 3


def test_a_data_check_that_does_not_fit_is_refused(client):
    f = DATA_CHECK["findings"][0]
    assert "ZZ-0000" in post(client, "/catalogue/data-checks", {"findings": [{**f, "sku": "ZZ-0000"}]}, 404)["detail"]
    assert "listed twice" in post(client, "/catalogue/data-checks", {"findings": [f, f]}, 422)["detail"]
    r = post(client, "/catalogue/data-checks", {"findings": [{**f, "kind": "missing"}]}, 422)
    assert "empty listing_value" in r["detail"] and r["applied"] is False
    assert "needs the listing_value" in post(client, "/catalogue/data-checks", {"findings": [{**f, "listing_value": ""}]}, 422)["detail"]
    assert "attribute" in post(client, "/catalogue/data-checks", {"findings": [{**f, "attribute": "weight"}]}, 422)["detail"]
    assert "not bakery" in post(client, "/catalogue/data-checks", {"findings": [f], "category": "bakery"}, 422)["detail"]
    assert "categories are" in post(client, "/catalogue/data-checks", {"findings": [], "category": "toys"}, 404)["detail"]
    assert get(client, "/catalogue/data-checks")["count"] == 0
    get(client, "/catalogue/listings/ZZ-0000", 404)
    get(client, "/catalogue/specifications/ZZ-0000", 404)


def test_listing_filters(client):
    assert get(client, "/catalogue/listings", category="bakery")["count"] == 6
    assert get(client, "/catalogue/listings", status="awaiting_description")["count"] == 6
    assert get(client, "/catalogue/listings", new_product="true")["count"] == 12
    assert get(client, "/catalogue/listings", new_product="false", category="drinks")["count"] == 6
    get(client, "/catalogue/listings", 422, category="toys")
    one = get(client, "/catalogue/listings/CH-5507")
    assert "image_descriptions" not in one and one["description_drafts"] == [] and one["published"] is None
    assert get(client, "/catalogue/specifications/CH-5507")["claims"] == ["free-range"]


# ================================================================ catalogue: new products and descriptions

def test_twelve_new_products_six_without_a_description(client):
    new = get(client, "/catalogue/new-products")
    assert new["count"] == 12 and "holds no images" in new["images_note"]
    assert all(len(x["image_descriptions"]) == 2 for x in new["items"])
    assert [x["listed_on"] for x in new["items"]] == sorted((x["listed_on"] for x in new["items"]), reverse=True)
    awaiting = get(client, "/catalogue/new-products", status="awaiting_description")
    table = [r for r in rows("", NEW) if r[0] in {x["sku"] for x in awaiting["items"]}]
    assert len(table) == 6 == awaiting["count"]
    for sku, name, net, pack, allergens, origin, _ in table:
        spec = get(client, f"/catalogue/specifications/{sku}")
        assert (spec["product_name"], spec["net_quantity"], spec["pack_size"], spec["allergen_statement"],
                spec["country_of_origin"]) == (name, net, pack, allergens, origin), sku
        assert get(client, f"/catalogue/listings/{sku}")["description"] == ""
    live = sorted(x["sku"] for x in get(client, "/catalogue/new-products", status="live")["items"])
    assert "The six live new products are " + ", ".join(f"`{s}`" for s in live[:-1]) + f" and `{live[-1]}`." in NEW
    # the planted disagreement between a picture and the specification, and the one age-restricted line
    berries = next(x for x in awaiting["items"] if x["sku"] == "FZ-5606")
    assert "'450 g'" in berries["image_descriptions"][0] and get(client, "/catalogue/specifications/FZ-5606")["net_quantity"] == "500 g"
    assert [x["sku"] for x in awaiting["items"] if x["age_restricted"]] == ["DR-5906"]
    for x in awaiting["items"]:
        if x["sku"] != "FZ-5606":
            spec = get(client, f"/catalogue/specifications/{x['sku']}")
            assert f"'{spec['net_quantity']}'" in x["image_descriptions"][0] or x["sku"] in ("BK-5706", "HH-6107"), x["sku"]


def test_the_style_guide_is_served_and_is_the_library_document(client):
    guide = get(client, "/catalogue/style-guide")
    assert (guide["document"], guide["version"]) == ("Product Style Guide", "1.3")
    assert [r["rule_id"] for r in guide["rules"]] == [f"PS-{n}" for n in range(1, 11)]
    assert (guide["minimum_words"], guide["maximum_words"], guide["minimum_image_tags"], guide["maximum_image_tags"]) == (40, 80, 3, 6)
    assert ", ".join(guide["words_not_used"]) in NEW and guide["closing_sentence_for_age_restricted_lines"] in NEW
    text = (LIBRARY / "product-style-guide.md").read_text(encoding="utf-8")
    assert text == style_guide_markdown() == guide["text"]
    assert "invented" in text.splitlines()[0] and "Version: 1.3" in text


def test_a_description_is_saved_and_a_person_publishes_it(client, store):
    assert "Use save_product_description first" in post(client, "/catalogue/listings/AG-4411/description/publish",
                                                        {"published_by": "I. Editor"}, 409)["detail"]
    v = post(client, "/catalogue/listings/AG-4411/description", DESCRIPTION)
    assert v["draft"]["version"] == 1 and 40 <= v["draft"]["words"] <= 80 and v["listing_status"] == "awaiting_description"
    v2 = post(client, "/catalogue/listings/AG-4411/description", {**DESCRIPTION, "image_tags": ["granola", "bowl", "milk"]})
    assert v2["draft"]["version"] == 2
    x = get(client, "/catalogue/listings/AG-4411")
    assert x["status"] == "awaiting_description" and x["description"] == "" and len(x["description_drafts"]) == 2
    post(client, "/catalogue/listings/AG-4411/description/publish", {}, 422)
    done = post(client, "/catalogue/listings/AG-4411/description/publish", {"published_by": "I. Editor"})
    assert done["kind"] == "change" and done["status"] == "live" and done["listing"]["image_tags"] == ["granola", "bowl", "milk"]
    x = get(client, "/catalogue/listings/AG-4411")
    assert x["description"].startswith("Oat granola") and x["published"]["published_by"] == "I. Editor" and x["published"]["version"] == 2
    assert "already published by I. Editor" in post(client, "/catalogue/listings/AG-4411/description/publish",
                                                    {"published_by": "X"}, 409)["detail"]
    assert "already has a published description" in post(client, "/catalogue/listings/AG-4411/description", DESCRIPTION, 409)["detail"]
    assert get(client, "/admin/state")["counts"]["products_awaiting_description"] == 5
    assert get(client, "/catalogue/new-products", status="awaiting_description")["count"] == 5


def test_a_description_outside_the_style_guide_is_refused(client):
    path = "/catalogue/listings/AG-4411/description"
    assert "has 4 words" in post(client, path, {**DESCRIPTION, "description": "Oat granola, 500 g."}, 422)["detail"]
    long = " ".join(["oats"] * 81)
    assert "has 81 words" in post(client, path, {**DESCRIPTION, "description": long}, 422)["detail"]
    bad = DESCRIPTION["description"].replace("baked oats", "delicious and healthy oats")
    assert "delicious, healthy" in post(client, path, {**DESCRIPTION, "description": bad}, 422)["detail"]
    assert "3 to 6 image tags" in post(client, path, {**DESCRIPTION, "image_tags": ["granola"]}, 422)["detail"]
    assert "lower case" in post(client, path, {**DESCRIPTION, "image_tags": ["Granola", "bowl", "milk"]}, 422)["detail"]
    for attribute, wrong in (("allergen_statement", "Contains: oats"), ("net_quantity", "450 g"), ("pack_size", "2"),
                             ("country_of_origin", "Tessaly")):
        r = post(client, path, {**DESCRIPTION, attribute: wrong}, 422)
        assert attribute in r["detail"] and "copy the value exactly" in r["detail"]
        assert "almonds" not in r["detail"]  # the refusal does not hand the answer over
    get(client, "/catalogue/listings/ZZ-0000", 404)
    post(client, "/catalogue/listings/ZZ-0000/description", DESCRIPTION, 404)
    assert get(client, "/catalogue/listings/AG-4411")["description_drafts"] == []


def test_an_age_restricted_line_ends_with_the_sentence_of_the_guide(client):
    wine = {**DESCRIPTION, "net_quantity": "75 cl", "pack_size": "1", "allergen_statement": "Contains: sulphites",
            "country_of_origin": "Tessaly", "image_tags": ["bottle", "white wine", "glasses"],
            "description": "White wine from Windlebury in a 75 cl bottle with a screw cap. The wine is pale in the glass. "
                           "Chill it before serving and keep an opened bottle in the fridge. It is shown here with a plate "
                           "of olives, as the photo studio describes the picture."}
    assert "ends with the sentence" in post(client, "/catalogue/listings/DR-5906/description", wine, 422)["detail"]
    wine["description"] += " For adults aged 18 or over."
    assert post(client, "/catalogue/listings/DR-5906/description", wine)["draft"]["version"] == 1
    berries = {**DESCRIPTION, "allergen_statement": "No allergens", "country_of_origin": "Rovaland",
               "differences_for_the_content_lead": ["The pack in the first image reads 450 g. The specification gives 500 g."]}
    saved = post(client, "/catalogue/listings/FZ-5606/description", berries)["draft"]
    assert saved["net_quantity"] == "500 g" and len(saved["differences_for_the_content_lead"]) == 1


# ================================================================ catalogue: the search log

def test_twenty_terms_found_nothing_and_they_are_the_five_groups(client):
    log = get(client, f"/catalogue/search-log/{PERIOD}")
    assert (log["count"], log["total_searches"]) == (60, 11857) and "60 terms and 11,857 searches" in SEARCH
    assert [r["searches"] for r in log["rows"]] == sorted((r["searches"] for r in log["rows"]), reverse=True)
    none = get(client, f"/catalogue/search-log/{PERIOD}", no_results="true")
    assert (none["count"], none["total_searches"]) == (20, 2429) and "2,429 searches in all" in SEARCH
    served = {r["term"]: r["searches"] for r in none["rows"]}
    table = [r for r in rows("", SEARCH) if r[0] not in ("Group", "---")]
    assert len(table) == 5
    listed = {}
    for name, terms, total in table:
        group = {t.rsplit(" (", 1)[0]: int(t.rsplit(" (", 1)[1].rstrip(")")) for t in terms.split(", ")}
        assert len(group) == 4 and sum(group.values()) == int(total), name
        listed.update(group)
    assert listed == served
    assert none["rows"][0]["term"] == "oat milk" and "`oat milk`" in SEARCH
    by = {r["term"]: r for r in log["rows"]}
    assert by["almond"]["results_found"] == 2 and by["yoghurt"]["results_found"] == 1 and by["yogurt"]["results_found"] == 0
    assert "theme" not in json.dumps(log) and "group" not in json.dumps(log)


def test_a_search_terms_analysis_is_saved_with_the_counts_of_the_log(client):
    table = [r for r in rows("", SEARCH) if r[0] not in ("Group", "---")]
    body = {"groups": [{"name": name, "what_shoppers_seemed_to_want": "x", "terms": [t.rsplit(" (", 1)[0] for t in terms.split(", ")]}
                       for name, terms, _ in table]}
    v = post(client, f"/catalogue/search-log/{PERIOD}/analysis", body)
    assert v["draft"]["version"] == 1 and v["draft"]["total_searches"] == 2429 and v["period"] == PERIOD
    assert [g["total_searches"] for g in v["draft"]["groups"]] == [int(r[2]) for r in table]
    assert v["draft"]["groups"][1]["terms"][0] == {"term": "oat milk", "searches": 301}
    v2 = post(client, f"/catalogue/search-log/{PERIOD}/analysis", {**TERMS, "groups": [{**TERMS["groups"][0], "terms": ["Oat Milk "]}]})
    assert v2["draft"]["version"] == 2 and v2["draft"]["total_searches"] == 301
    got = get(client, f"/catalogue/search-log/{PERIOD}/analysis")
    assert got["count"] == 2 and got["analyses"][0]["drafted_by"] == "agent"
    assert get(client, "/catalogue/search-log/2026-09/analysis")["count"] == 0


def test_a_search_terms_analysis_that_does_not_fit_is_refused(client):
    path = f"/catalogue/search-log/{PERIOD}/analysis"
    g = TERMS["groups"][0]
    assert "found 2 results" in post(client, path, {"groups": [{**g, "terms": ["almond"]}]}, 422)["detail"]
    assert "in two groups" in post(client, path, {"groups": [g, {**g, "name": "Again", "terms": ["oat milk"]}]}, 422)["detail"]
    assert "oat mlik" in post(client, path, {"groups": [{**g, "terms": ["oat mlik"]}]}, 404)["detail"]
    post(client, path, {"groups": []}, 422)
    r = post(client, "/catalogue/search-log/2026-11/analysis", TERMS, 409)
    assert "has not ended" in r["detail"] and "2026-10" in r["detail"]
    assert "holds 2026-10" in post(client, "/catalogue/search-log/2026-08/analysis", TERMS, 404)["detail"]
    assert "has not ended" in get(client, "/catalogue/search-log/2026-11", 409)["detail"]
    get(client, "/catalogue/search-log/2026-08", 404)
    get(client, "/catalogue/search-log/october", 422)
    assert get(client, path)["count"] == 0


# ================================================================ stock: replenishment

def positions(client):
    """Where every line stands under the replenishment rules, worked out from what the API serves."""
    rules = get(client, "/stock/replenishment-rules")
    levels = {x["sku"]: x for x in get(client, "/stock/levels")["items"]}
    out = {}
    for t in get(client, "/stock/supply-terms")["items"]:
        x = levels[t["sku"]]
        daily = x["units_sold_last_four_weeks"] / 28
        cover = x["on_hand"] / daily
        dues = sorted(o["due_on"] for o in t["open_orders"])
        days = (date.fromisoformat(dues[0]) - TODAY_D).days if dues else t["lead_time_days"]
        cases = 0
        if cover < days:
            units = round(daily * (t["lead_time_days"] + rules["target_cover_days"]) - x["on_hand"] - t["units_on_order"])
            cases = max(-(-units // t["case_size"]), t["minimum_order_cases"])
        out[t["sku"]] = {"name": t["name"], "supplier": t["supplier_id"], "on_hand": x["on_hand"],
                         "weekly": x["units_sold_last_four_weeks"] / 4, "daily": daily, "cover": round(cover, 1),
                         "lead": t["lead_time_days"], "on_order": t["units_on_order"], "days": days, "case": t["case_size"],
                         "runs_out": cover < days, "overstocked": cover > rules["overstock_days"], "cases": cases,
                         "units": cases * t["case_size"]}
    return out


def test_the_five_lines_that_run_out_match_the_scenario_table(client):
    pos = positions(client)
    table = [r for r in rows("", REPLENISH) if r[0] in pos]
    assert sorted(r[0] for r in table) == sorted(s for s, p in pos.items() if p["runs_out"]) and len(table) == 5
    for sku, name, supplier, on_hand, weekly, daily, cover, lead, on_order, days, case, cases, units in table:
        p = pos[sku]
        assert (p["name"], p["supplier"], p["on_hand"], p["weekly"], p["daily"], p["cover"], p["lead"], p["on_order"], p["days"],
                p["case"], p["cases"], p["units"]) == (name, supplier, int(on_hand), num(weekly), num(daily), num(cover),
                                                       int(lead), int(on_order), int(days), int(case), int(cases), int(units)), sku
    assert {p["supplier"] for p in pos.values() if p["runs_out"]} == {"SUP-301", "SUP-303", "SUP-304"}
    for sid in ("SUP-301", "SUP-303", "SUP-304"):
        assert get(client, f"/purchasing/suppliers/{sid}")["supplier_id"] == sid


def test_the_lines_that_look_low_and_the_lines_that_are_overstocked(client):
    pos = positions(client)
    assert sorted(s for s, p in pos.items() if p["overstocked"]) == ["DR-5904", "FZ-5604", "HH-6105"]
    for sku, days, on_hand in (("DR-5904", "80.0", "1,600"), ("FZ-5604", "70.0", "700"), ("HH-6105", "90.0", "900")):
        assert pos[sku]["cover"] == float(days) and f"({on_hand} on hand, {days} days)" in REPLENISH
    assert pos["PC-6606"]["cover"] == 56.0 and not pos["PC-6606"]["overstocked"]
    butter = pos["CH-5503"]
    assert (butter["on_hand"], butter["cover"], butter["lead"], butter["on_order"], butter["days"], butter["runs_out"]) == (100, 2.5, 3, 480, 2, False)
    flour = pos["AG-4410"]
    assert (flour["on_hand"], flour["cover"], flour["days"], flour["runs_out"]) == (100, 5.0, 5, False)
    peppers = get(client, "/stock/supply-terms", sku="FP-5801")["items"][0]["open_orders"]
    assert peppers == [{"order_ref": "MO-7131", "ordered_on": "2026-11-23", "due_on": "2026-11-28", "units": 360}]
    assert "`MO-7131`, for 360 units due on 2026-11-28" in REPLENISH and "`MO-7128` for 480 units is due on 2026-11-26" in REPLENISH
    others = [p["cover"] for s, p in pos.items() if not p["runs_out"] and not p["overstocked"] and s not in ("CH-5503", "AG-4410", "PC-6606")]
    assert 15 <= min(others) and max(others) <= 39 and "between 15 and 39 days of cover" in REPLENISH


def test_stock_levels_history_and_rules(client):
    all_stores = get(client, "/stock/levels")
    assert all_stores["count"] == 60 and all_stores["retailer_date"] == TODAY and len(all_stores["weeks"]) == 13
    assert all_stores["weeks"][0] == "2026-08-30" and all_stores["weeks"][-1] == "2026-11-22"
    butter = get(client, "/stock/levels/CH-5502")
    assert butter["on_hand"] == 300 and butter["weekly_units"][-4:] == [840] * 4 and len(butter["stores"]) == 8
    assert sum(s["on_hand"] for s in butter["stores"]) == 300 and all(len(s["weekly_sales"]) == 13 for s in butter["stores"])
    by_store = sum(next(x for x in get(client, "/stock/levels", site_id=s)["items"] if x["sku"] == "CH-5502")["on_hand"] for s in STORES)
    assert by_store == 300
    assert get(client, "/stock/levels", category="bakery")["count"] == 6
    assert "R-014" not in json.dumps(all_stores) and "Restaurants hold no stock" in get(client, "/stock/levels", 404, site_id="R-014")["detail"]
    get(client, "/stock/levels/ZZ-0000", 404)
    rules = get(client, "/stock/replenishment-rules")
    assert [r["rule_id"] for r in rules["rules"]] == [f"RP-{n}" for n in range(1, 7)] and rules["version"] == "2.1"
    assert (rules["target_cover_days"], rules["overstock_days"]) == (14, 56) and "version 2.1" in REPLENISH
    for word in ("runs_out", "days_of_cover", "overstocked"):
        assert word not in json.dumps(all_stores) and word not in json.dumps(get(client, "/stock/supply-terms"))


def test_a_replenishment_plan_is_saved_as_draft_orders_and_a_buyer_approves(client, store):
    assert "Use save_replenishment_plan first" in post(client, "/stock/replenishment-plan/approve", {"approved_by": "J. Buyer"}, 409)["detail"]
    nothing = post(client, "/stock/replenishment-plan", {"lines": [], "overstocked": ["HH-6105"]})
    assert nothing["draft"]["version"] == 1 and nothing["draft"]["draft_orders"] == [] and nothing["approved"] is False
    assert "orders nothing" in post(client, "/stock/replenishment-plan/approve", {"approved_by": "J. Buyer"}, 409)["detail"]
    v = post(client, "/stock/replenishment-plan", PLAN)["draft"]
    assert v["version"] == 2 and [o["supplier_id"] for o in v["draft_orders"]] == ["SUP-301", "SUP-303", "SUP-304"]
    assert [(x["sku"], x["cases"], x["units"]) for o in v["draft_orders"] for x in o["lines"]] == [
        ("CH-5502", 87, 1740), ("CH-5505", 73, 876), ("AG-4408", 75, 750), ("FP-5801", 75, 900), ("FP-5802", 145, 1160)]
    assert {o["status"] for o in v["draft_orders"]} == {"draft"} and "three draft purchase orders" in REPLENISH
    before = copy.deepcopy(store.data["stock_levels"])
    post(client, "/stock/replenishment-plan/approve", {}, 422)
    done = post(client, "/stock/replenishment-plan/approve", {"approved_by": "J. Buyer"})
    assert done["kind"] == "change" and done["approval"]["version"] == 2 and {o["status"] for o in done["draft_orders"]} == {"approved"}
    assert "already approved by J. Buyer" in post(client, "/stock/replenishment-plan/approve", {"approved_by": "X"}, 409)["detail"]
    got = get(client, "/stock/replenishment-plan")
    assert got["count"] == 2 and got["approval"]["approved_by"] == "J. Buyer" and store.data["stock_levels"] == before
    assert len(store.data["purchase_orders"]) == 8  # approving a plan places no order in the purchasing system
    assert get(client, "/admin/state")["counts"]["replenishment_plans"] == 2


def test_a_replenishment_plan_that_does_not_fit_is_refused(client):
    line = PLAN["lines"][0]
    path = "/stock/replenishment-plan"
    assert "not supplied by SUP-304" in post(client, path, {"lines": [{**line, "supplier_id": "SUP-304"}]}, 422)["detail"]
    r = post(client, path, {"lines": [{"sku": "AG-4408", "supplier_id": "SUP-303", "cases": 4, "reason": "x"}]}, 422)
    assert "minimum order of 10 cases" in r["detail"]
    assert "listed twice" in post(client, path, {"lines": [line, line]}, 422)["detail"]
    assert "listed twice" in post(client, path, {"lines": [line], "overstocked": ["CH-5502"]}, 422)["detail"]
    post(client, path, {"lines": [{**line, "cases": 0}]}, 422)
    post(client, path, {"lines": [{**line, "sku": "ZZ-0000"}]}, 404)
    post(client, path, {"lines": [], "overstocked": ["ZZ-0000"]}, 404)
    assert get(client, path)["count"] == 0


# ================================================================ stock: counts and loss

def test_the_eight_counts_match_the_scenario_table(client):
    tolerance = get(client, "/stock/shrink-tolerance")
    assert (tolerance["store_tolerance_percent"], tolerance["line_tolerance_percent"], tolerance["version"]) == (1.5, 2.5, "1.4")
    assert [r["rule_id"] for r in tolerance["rules"]] == ["SL-1", "SL-2", "SL-3"]
    counts = get(client, f"/stock/counts/{PERIOD}")
    assert counts["view"] == "by_store" and counts["count"] == 8 == counts["total"]
    table = rows("SC-", LOSS)
    assert [r[0] for r in table] == [c["count_id"] for c in counts["items"]] == [f"SC-2610-10{n}" for n in range(1, 9)]
    for (cid, site, sales, units, value, percent), c in zip(table, counts["items"]):
        assert (c["site_id"], c["sales_value"], c["loss_units"], c["loss_value"], c["loss_percent"], c["lines_counted"]) == (
            site, num(sales), int(units), num(value), num(percent), 60), cid
        assert c["loss_percent"] == round(c["loss_value"] / c["sales_value"] * 100, 2) and "rows" not in c
    beyond = [c["site_id"] for c in counts["items"] if c["loss_percent"] > tolerance["store_tolerance_percent"]]
    assert beyond == ["S-103", "S-106"] and "`S-103` at 2.44 percent and `S-106` at 2.50 percent" in LOSS
    nearest = max(c["loss_percent"] for c in counts["items"] if c["site_id"] not in beyond)
    assert nearest == 1.33 and "`S-102` at 1.33 percent" in LOSS
    assert "beyond" not in json.dumps(counts) and "tolerance" not in json.dumps(counts)


def test_the_three_lines_beyond_tolerance_match_the_scenario_table(client):
    lines = get(client, f"/stock/counts/{PERIOD}", view="by_line")
    assert lines["count"] == 60 and all(x["stores_counted"] == 8 for x in lines["items"])
    beyond = sorted((x for x in lines["items"] if x["loss_percent"] > 2.5), key=lambda x: x["sku"])
    table = [r for r in rows("", LOSS) if r[0] in {x["sku"] for x in beyond}]
    assert [r[0] for r in table] == [x["sku"] for x in beyond] == ["DR-5905", "HH-6105", "PC-6604"]
    for (sku, name, sold, sales, units, value, percent), x in zip(table, beyond):
        assert (x["name"], x["units_sold"], x["sales_value"], x["loss_units"], x["loss_value"], x["loss_percent"]) == (
            name, int(sold), num(sales), int(units), num(value), num(percent)), sku
    rest = max((x for x in lines["items"] if x["loss_percent"] <= 2.5), key=lambda x: x["loss_percent"])
    assert (rest["sku"], rest["loss_percent"]) == ("FP-5806", 1.40) and "`FP-5806` Baby spinach at 1.40 percent" in LOSS
    # the rows add up to both views
    detail = get(client, f"/stock/counts/{PERIOD}", view="rows", limit=500)
    assert detail["total"] == 480 and detail["count"] == 480
    assert get(client, f"/stock/counts/{PERIOD}", view="rows", limit=100, offset=400)["count"] == 80
    wine = get(client, f"/stock/counts/{PERIOD}", view="rows", sku="DR-5905")
    assert wine["count"] == 8 and sum(r["loss_units"] for r in wine["items"]) == 62
    one = get(client, f"/stock/counts/{PERIOD}", view="rows", site_id="S-106")
    assert one["count"] == 60 and round(sum(r["loss_value"] for r in one["items"]), 2) == 481.07
    assert all(r["book_units"] - r["counted_units"] == r["loss_units"] for r in one["items"])
    assert get(client, f"/stock/counts/{PERIOD}", site_id="S-106")["items"][0]["count_id"] == "SC-2610-106"
    for site in ("S-103", "S-106"):
        rows_ = get(client, f"/stock/counts/{PERIOD}", view="rows", site_id=site)["items"]
        top = sorted(rows_, key=lambda r: (-r["loss_value"], r["sku"]))[:3]
        said = [f"`{r['sku']}` ({r['loss_value']:.2f})" for r in top]
        assert top[2]["loss_value"] > sorted(rows_, key=lambda r: -r["loss_value"])[3]["loss_value"]  # no tie for third
        assert f"`{site}`, {said[0]}, {said[1]} and {said[2]}" in LOSS, site


def test_what_the_tills_hold_for_the_two_stores(client):
    for site in ("S-103", "S-106"):
        till = get(client, "/tills/entries", period=PERIOD, site_id=site, limit=500)["items"]
        said = []
        for kind, word in (("refund", "refunds"), ("void", "voids"), ("discount", "discounts")):
            these = [x for x in till if x["kind"] == kind]
            said.append(f"{len(these)} {word} ({sum(x['amount'] for x in these):,.2f})")
        assert f"`{site}` has {said[0]}, {said[1]} and {said[2]}." in LOSS, site


def test_a_shrink_analysis_is_saved_and_one_that_does_not_fit_is_refused(client, store):
    path = f"/stock/counts/{PERIOD}/analysis"
    before = copy.deepcopy(store.data["stock_counts"])
    v = post(client, path, {**SHRINK, "summary": "Two stores and three lines."})
    assert v["draft"]["version"] == 1 and v["period"] == PERIOD and len(v["draft"]["lines_beyond_tolerance"]) == 3
    assert post(client, path, {})["draft"]["version"] == 2
    got = get(client, path)
    assert got["count"] == 2 and got["analyses"][0]["summary"] == "Two stores and three lines." and store.data["stock_counts"] == before
    wrong = {"stores_beyond_tolerance": [{"site_id": "S-106", "loss_percent": 2.4}]}
    assert "not the loss percent the count gives" in post(client, path, wrong, 422)["detail"]
    assert "not the loss percent the counts give" in post(client, path, {"lines_beyond_tolerance": [{"sku": "DR-5905", "loss_percent": 7}]}, 422)["detail"]
    twice = {"stores_beyond_tolerance": [SHRINK["stores_beyond_tolerance"][0]] * 2}
    assert "listed twice" in post(client, path, twice, 422)["detail"]
    post(client, path, {"stores_beyond_tolerance": [{"site_id": "R-014", "loss_percent": 1}]}, 404)
    post(client, path, {"lines_beyond_tolerance": [{"sku": "ZZ-0000", "loss_percent": 1}]}, 404)
    assert "2026-10" in post(client, "/stock/counts/2026-09/analysis", SHRINK, 404)["detail"]
    get(client, "/stock/counts/2026-09", 404)
    get(client, f"/stock/counts/{PERIOD}", 404, site_id="R-014")
    get(client, f"/stock/counts/{PERIOD}", 422, view="by_colleague")
    assert get(client, path)["count"] == 2 and get(client, "/admin/state")["counts"]["shrink_analyses"] == 2


def test_the_stock_system_names_no_person(client):
    for path, params in ((f"/stock/counts/{PERIOD}", {"view": "rows", "limit": 500}), ("/stock/shrink-tolerance", {}),
                         ("/stock/levels", {})):
        body = json.dumps(get(client, path, **params)).lower()
        for word in ("cashier", "counted_by", "manager", "colleague_id", "theft\""):
            assert word not in body, (path, word)
    assert "does not say that any colleague or any customer did anything wrong" in get(client, "/stock/shrink-tolerance")["what_the_tolerance_does_not_decide"]


# ================================================================ stock: the recalled batch

def test_the_recalled_batch_matches_the_scenario_tables(client):
    listed = get(client, "/stock/batches")
    assert listed["count"] == 4 and [b["batch_id"] for b in listed["items"] if b["status"] == "recalled"] == ["BT-44031"]
    assert get(client, "/stock/batches", status="recalled")["count"] == 1 and get(client, "/stock/batches", sku="AG-4403")["count"] == 2
    b = get(client, "/stock/batches/BT-44031")
    assert (b["sku"], b["name"], b["supplier_name"], b["received_on"], b["units_received"], b["best_before"], b["status"]) == (
        "AG-4403", "Pasta sauce, six jars", "Marrowby Provisions Ltd", "2026-10-21", 960, "2027-09-20", "recalled")
    for text in ("received on 2026-10-21, 960 units, best before 2027-09-20", f'"{b["recall"]["reason"]}"'):
        assert text in RECALL
    assert b["recall"]["raised_on"] == TODAY and "full refund without a receipt" in b["recall"]["customer_remedy"]
    assert [s["step"] for s in b["recall_procedure"]["steps"]] == [f"RC-{n}" for n in range(1, 6)] and b["recall_procedure"]["version"] == "1.2"
    stores = rows("S-", RECALL)
    assert [(s["site_id"], s["delivered_on"], str(s["units_delivered"]), str(s["units_sold"]), str(s["units_on_hand"]))
            for s in b["stores"]] == [tuple(r) for r in stores] and len(stores) == 4
    assert (sum(s["units_delivered"] for s in b["stores"]), sum(s["units_sold"] for s in b["stores"]),
            sum(s["units_on_hand"] for s in b["stores"])) == (680, 556, 124) and "680 units delivered to stores, 556 sold and 124 on hand" in RECALL
    assert b["fulfilment_centre"] == {"units_received": 280, "units_picked_for_orders": 8, "units_on_hand": 272}
    orders = rows("RM-", RECALL)
    assert len(orders) == 7 and [o["order_number"] for o in b["online_orders"]] == [r[0] for r in orders]
    customers = set()
    for (number, customer, picked, units, as_line), o in zip(orders, b["online_orders"]):
        order = get(client, f"/orders/orders/{number}")
        assert (o["picked_on"], str(o["units"]), o["went_out_as"]) == (picked, units, as_line), number
        assert order["customer_name"] == customer and order["status"] == "delivered" and order["customer_email"].endswith("@mail.invalid")
        assert {x["sku"] for x in order["lines"]} & set(as_line.replace(" and ", " ").split()), number
        customers.add(customer)
    assert len(customers) == 5 and "Seven orders and five customers" in RECALL
    for site in (r[0] for r in stores):
        assert get(client, f"/stores/sites/{site}")["kind"] == "store"


def test_what_is_not_in_the_recall(client):
    b = get(client, "/stock/batches/BT-44031")
    on_list = {o["order_number"] for o in b["online_orders"]}
    with_the_line = {o["order_number"] for o in get(client, "/orders/orders", limit=200)["items"]
                     if {"AG-4403", "AG-4404"} & {x["sku"] for x in get(client, f"/orders/orders/{o['order_number']}")["lines"]}}
    assert with_the_line - on_list == {"RM-58188", "RM-58198"}
    assert get(client, "/orders/orders/RM-58188")["status"] == "placed" and get(client, "/orders/orders/RM-58198")["status"] == "awaiting_fraud_review"
    later = get(client, "/stock/batches/BT-44032")
    assert (later["sku"], later["status"], later["recall"], [s["site_id"] for s in later["stores"]], later["online_orders"]) == (
        "AG-4403", "on_sale", None, ["S-102", "S-106"], [])
    assert "Batch BT-44032 is not recalled" in post(client, "/stock/batches/BT-44032/recall-pack", PACK, 409)["detail"]
    assert "is not recalled" in post(client, "/stock/batches/BT-44012/recall-notice/issue", {"issued_by": "K. Quality"}, 409)["detail"]
    get(client, "/stock/batches/BT-00000", 404)
    post(client, "/stock/batches/BT-00000/recall-pack", PACK, 404)


def test_a_recall_pack_is_saved_and_the_head_of_quality_issues_the_notice(client, store):
    path = "/stock/batches/BT-44031"
    assert "Use save_recall_pack first" in post(client, f"{path}/recall-notice/issue", {"issued_by": "K. Quality"}, 409)["detail"]
    v = post(client, f"{path}/recall-pack", PACK)
    assert v["draft"]["version"] == 1 and v["batch_status"] == "recalled" and len(v["draft"]["orders"]) == 7
    assert post(client, f"{path}/recall-pack", {**PACK, "summary": "Four stores, seven orders."})["draft"]["version"] == 2
    b = get(client, path)
    assert b["status"] == "recalled" and b["notice"] is None and len(b["recall_packs"]) == 2
    post(client, f"{path}/recall-notice/issue", {}, 422)
    done = post(client, f"{path}/recall-notice/issue", {"issued_by": "K. Quality"})
    assert done["kind"] == "change" and done["status"] == "notice_issued" and done["batch"]["notice"]["version"] == 2
    assert (done["batch"]["notice"]["stores"], done["batch"]["notice"]["orders"]) == (4, 7)
    assert "already issued by K. Quality" in post(client, f"{path}/recall-notice/issue", {"issued_by": "X"}, 409)["detail"]
    counts = get(client, "/admin/state")["counts"]
    assert (counts["batches_recalled"], counts["recall_notices_issued"]) == (0, 1)
    assert get(client, "/stock/batches", status="notice_issued")["items"][0]["recall_packs"] == 2
    assert store.data["orders"]["RM-58147"]["status"] == "delivered"  # a notice changes no order


def test_a_recall_pack_that_does_not_fit_is_refused(client):
    path = "/stock/batches/BT-44031/recall-pack"
    r = post(client, path, {**PACK, "stores": PACK["stores"][:3], "orders": PACK["orders"][:5]}, 422)
    assert "leaves out 1 of the stores and 2 of the orders" in r["detail"] and "S-107" not in r["detail"]
    extra = PACK["stores"] + [{"site_id": "S-102", "units_delivered": 160}]
    assert "S-102 is not a store batch BT-44031 was delivered to" in post(client, path, {**PACK, "stores": extra}, 422)["detail"]
    assert "RM-58188 was not picked from batch BT-44031" in post(client, path, {**PACK, "orders": PACK["orders"] + ["RM-58188"]}, 422)["detail"]
    post(client, path, {**PACK, "orders": PACK["orders"] + ["RM-00000"]}, 404)
    wrong_units = [{"site_id": "S-101", "units_delivered": 42}] + PACK["stores"][1:]
    assert "not the units of the batch delivered" in post(client, path, {**PACK, "stores": wrong_units}, 422)["detail"]
    assert "listed twice" in post(client, path, {**PACK, "orders": PACK["orders"] + ["RM-58115"]}, 422)["detail"]
    assert "store instruction does not give the batch number" in post(client, path, {**PACK, "store_instruction": "Take it off sale."}, 422)["detail"]
    assert "customer notice does not give the batch number" in post(client, path, {**PACK, "customer_notice": "Do not use it."}, 422)["detail"]
    post(client, path, {"stores": PACK["stores"], "orders": PACK["orders"]}, 422)
    assert get(client, "/stock/batches/BT-44031")["recall_packs"] == []


# ================================================================ pricing: prices

def price_answers(client):
    """What the method of the pricing rules gives for every line with a competitor price, worked out from the API."""
    rules = get(client, "/pricing/rules")
    prices = {x["sku"]: x for x in get(client, "/pricing/prices")["items"]}
    cover = {s: p["cover"] for s, p in positions(client).items()}
    out = {}
    for x in get(client, "/pricing/competitor-prices")["items"]:
        row = prices[x["sku"]]
        reference = min(p["price"] for p in x["prices"])
        gap = round((row["price"] - reference) / reference * 100 + (1e-9 if row["price"] >= reference else -1e-9), 1)
        move = round((reference - row["price"]) / row["price"] * 100 + (1e-9 if reference >= row["price"] else -1e-9), 1)
        margin = round((reference / 1.15 - row["cost"]) / (reference / 1.15) * 100 + 1e-9, 1)
        answer = "hold"
        if abs(gap) > rules["band_percent"]:
            broken = []
            if margin < rules["floor_margin_percent"]:
                broken.append("PR-1")
            if int(round(reference * 100)) % 10 not in rules["allowed_last_digits"]:
                broken.append("PR-2")
            if abs(move) > rules["maximum_weekly_move_percent"]:
                broken.append("PR-3")
            if reference < row["price"] and cover[x["sku"]] < rules["minimum_days_of_cover_for_a_reduction"]:
                broken.append("PR-4")
            direction = "decrease" if reference < row["price"] else "increase"
            answer = f"hold, {', '.join(broken)}" if broken else f"{direction} to {reference:.2f}"
        out[x["sku"]] = {"name": row["name"], "price": row["price"], "cost": row["cost"], "reference": reference, "gap": gap,
                         "move": move, "margin": margin, "cover": cover[x["sku"]], "answer": answer}
    return out


def test_the_price_file_and_the_rules(client):
    prices = get(client, "/pricing/prices")
    assert prices["count"] == 60 and prices["retailer_date"] == TODAY
    for x in prices["items"]:
        assert x["price_excluding_tax"] == round(x["price"] / 1.15 + 1e-9, 2) and x["currency"] == "USD"
        assert x["margin_percent"] == round((x["price"] / 1.15 - x["cost"]) / (x["price"] / 1.15) * 100 + 1e-9, 1) >= 18.0
    assert get(client, "/pricing/prices", category="drinks")["count"] == 8 and get(client, "/pricing/prices", sku="DR-5901")["count"] == 1
    get(client, "/pricing/prices", 404, sku="ZZ-0000")
    rules = get(client, "/pricing/rules")
    assert [r["rule_id"] for r in rules["rules"]] == ["PR-1", "PR-2", "PR-3", "PR-4"] and rules["version"] == "2.0"
    assert [s["step"] for s in rules["how_a_recommendation_is_worked_out"]] == ["M-1", "M-2", "M-3", "M-4"]
    assert (rules["floor_margin_percent"], rules["maximum_weekly_move_percent"], rules["band_percent"],
            rules["minimum_days_of_cover_for_a_reduction"], rules["allowed_last_digits"]) == (18.0, 10.0, 5.0, 14, [5, 9])
    comps = get(client, "/pricing/competitor-prices")
    assert comps["count"] == 30 and {p["competitor"] for x in comps["items"] for p in x["prices"]} == {"Quarrowdale Stores", "Oxenwick Fresh"}
    assert "Quarrowdale Stores and Oxenwick Fresh, publish prices for thirty of them" in PRICING
    assert [p["competitor"] for p in get(client, "/pricing/competitor-prices", sku="HH-6102")["items"][0]["prices"]] == ["Quarrowdale Stores"]
    assert get(client, "/pricing/competitor-prices", sku="AG-4403")["count"] == 0
    for word in ("reference", "gap", "recommend"):
        assert word not in json.dumps(comps)


def test_the_seven_price_answers_match_the_scenario_table(client):
    answers = price_answers(client)
    moved = {s: a for s, a in answers.items() if a["answer"] != "hold"}
    table = [r for r in rows("", PRICING) if r[0] in answers]
    assert sorted(r[0] for r in table) == sorted(moved) and len(table) == 7
    for sku, name, price, cost, reference, gap, move, margin, cover, answer in table:
        a = answers[sku]
        assert (a["name"], a["price"], a["cost"], a["reference"], a["gap"], a["move"], a["margin"], a["cover"], a["answer"]) == (
            name, num(price), num(cost), num(reference), num(gap), num(move), num(margin), num(cover), answer), sku
    assert sum(1 for a in moved.values() if not a["answer"].startswith("hold")) == 3
    assert len(answers) - len(moved) == 23 and "other twenty-three lines" in PRICING
    assert (answers["FZ-5602"]["gap"], answers["DR-5905"]["gap"], answers["FP-5802"]["gap"]) == (5.0, 4.8, 4.7)
    assert max(abs(a["gap"]) for s, a in answers.items() if s not in moved) == 5.0
    # the line that needs the stock system: the price rules alone would allow it
    butter = answers["CH-5502"]
    assert butter["answer"] == "hold, PR-4" and butter["margin"] >= 18.0 and abs(butter["move"]) <= 10.0 and butter["cover"] == 2.5


def test_price_recommendations_are_saved_and_a_merchant_approves(client, store):
    assert "Use save_price_recommendations first" in post(client, "/pricing/recommendations/approve", {"approved_by": "L. Merchant"}, 409)["detail"]
    holds = {"recommendations": [r for r in PRICES["recommendations"] if r["action"] == "hold"]}
    assert post(client, "/pricing/recommendations", holds)["draft"]["changes"] == 0
    assert "hold no price change" in post(client, "/pricing/recommendations/approve", {"approved_by": "L. Merchant"}, 409)["detail"]
    v = post(client, "/pricing/recommendations", PRICES)
    assert v["draft"]["version"] == 2 and v["draft"]["changes"] == 3 and v["approved"] is False
    assert get(client, "/pricing/prices", sku="DR-5901")["items"][0]["price"] == 2.69  # a draft changes no price
    post(client, "/pricing/recommendations/approve", {}, 422)
    done = post(client, "/pricing/recommendations/approve", {"approved_by": "L. Merchant"})
    assert done["kind"] == "change" and done["approval"]["changes"] == [
        {"sku": "DR-5901", "from": 2.69, "to": 2.49}, {"sku": "HH-6102", "from": 8.99, "to": 8.49}, {"sku": "FP-5804", "from": 1.15, "to": 1.25}]
    juice = get(client, "/pricing/prices", sku="DR-5901")["items"][0]
    assert (juice["price"], juice["margin_percent"], juice["last_changed_on"]) == (2.49, 35.3, TODAY)
    assert get(client, "/pricing/prices", sku="BK-5701")["items"][0]["price"] == 1.59
    assert get(client, "/pricing/competitor-prices", sku="DR-5901")["items"][0]["our_price"] == 2.49
    assert "already approved by L. Merchant" in post(client, "/pricing/recommendations/approve", {"approved_by": "X"}, 409)["detail"]
    got = get(client, "/pricing/recommendations")
    assert got["count"] == 2 and got["approval"]["version"] == 2 and got["drafts"][1]["recommendations"][3]["rule"] == "PR-1"


def test_a_price_the_rules_forbid_is_refused(client):
    path = "/pricing/recommendations"
    one = lambda **kw: {"recommendations": [{"sku": "BK-5701", "action": "decrease", "current_price": 1.59, "proposed_price": 1.49,
                                             "reason": "x", **kw}]}
    assert "breaks PR-1" in post(client, path, one(), 422)["detail"]
    assert "breaks PR-3" in post(client, path, one(sku="PC-6604", current_price=9.99, proposed_price=8.49), 422)["detail"]
    assert "breaks PR-2" in post(client, path, one(sku="DR-5901", current_price=2.69, proposed_price=2.50), 422)["detail"]
    assert "breaks PR-2 and PR-3" in post(client, path, one(sku="HH-6103", action="increase", current_price=2.19, proposed_price=2.50), 422)["detail"]
    # PR-4 rests on stock, which this system does not hold: the price rules alone let the butter through
    assert post(client, path, one(sku="CH-5502", current_price=2.49, proposed_price=2.29))["draft"]["changes"] == 1
    assert "not the price in the price file" in post(client, path, one(current_price=1.65), 422)["detail"]
    assert "is not a decrease" in post(client, path, one(sku="DR-5901", current_price=2.69, proposed_price=2.79), 422)["detail"]
    assert "needs a proposed_price" in post(client, path, one(proposed_price=None), 422)["detail"]
    assert "a hold proposes no price" in post(client, path, one(action="hold"), 422)["detail"]
    assert "rule goes with a hold only" in post(client, path, one(sku="DR-5901", current_price=2.69, proposed_price=2.49, rule="PR-1"), 422)["detail"]
    assert "no published competitor price" in post(client, path, one(sku="AG-4403", current_price=13.20, proposed_price=12.95), 422)["detail"]
    r = PRICES["recommendations"][0]
    assert "listed twice" in post(client, path, {"recommendations": [r, r]}, 422)["detail"]
    post(client, path, one(sku="ZZ-0000"), 404)
    post(client, path, {"recommendations": []}, 422)
    post(client, path, one(action="cut"), 422)
    assert get(client, path)["count"] == 1


# ================================================================ pricing: promotions

def review_of(p):
    """What a review of a finished promotion adds up to, worked out from what get_promotion serves."""
    lost = [(n["sku"], n["units_in_the_14_days_before"] - n["units_in_the_promotion"], n["profit_a_unit"])
            for n in p["neighbouring_lines"] if n["units_in_the_promotion"] < n["units_in_the_14_days_before"]]
    neighbours = round(sum(units * profit for _, units, profit in lost), 2)
    net = round(p["result"]["profit"] - p["the_14_days_before"]["profit"] - neighbours - p["display_and_leaflet_cost"]
                + p["supplier_funding"], 2)
    return {"against_plan": round(p["result"]["units"] / p["plan"]["units"] * 100, 1), "lost": lost, "neighbours": neighbours, "net": net}


def test_the_six_finished_promotions_match_the_scenario_table(client):
    listed = get(client, "/pricing/promotions")
    assert listed["count"] == 7 and get(client, "/pricing/promotions", status="finished")["count"] == 6
    table = rows("PM-", PROMOS)
    assert [r[0] for r in table] == [f"PM-310{n}" for n in range(1, 7)]
    for pid, sku, mechanic, dates, planned, sold, against, before, profit, profit_before, neighbours, display, funding, net in table:
        p = get(client, f"/pricing/promotions/{pid}")
        r = review_of(p)
        assert (p["sku"], p["mechanic"], f"{p['start_date']} to {p['end_date']}", p["plan"]["units"], p["result"]["units"],
                r["against_plan"], p["the_14_days_before"]["units"], p["result"]["profit"], p["the_14_days_before"]["profit"],
                r["neighbours"], p["display_and_leaflet_cost"], p["supplier_funding"], r["net"]) == (
            sku, mechanic, dates, int(planned), int(sold), num(against), int(before), num(profit), num(profit_before),
            num(neighbours), num(display), num(funding), num(net)), pid
        assert p["status"] == "finished" and p["days"] == 14 and p["start_date"].startswith(PERIOD) and p["end_date"].startswith(PERIOD)
        assert p["result"]["profit"] == round(p["result"]["units"] * p["profit_a_unit_at_the_promotion_price"], 2)
        assert p["profit_a_unit_at_the_normal_price"] == round(p["normal_price"] / 1.15 - p["cost"] + 1e-9, 2)
        assert p["normal_price"] == get(client, "/pricing/prices", sku=sku)["items"][0]["price"]
        for word in ("net_effect", "verdict", "displaced"):
            assert word not in json.dumps(p)
    fish = get(client, "/pricing/promotions/PM-3101")
    assert (fish["profit_a_unit_at_the_promotion_price"], fish["profit_a_unit_at_the_normal_price"]) == (0.10, 3.36)
    assert "0.10 a unit against 3.36" in PROMOS and review_of(fish)["net"] == -1167.20
    croissants = review_of(get(client, "/pricing/promotions/PM-3102"))
    assert croissants["lost"] == [("BK-5705", 160, 0.71), ("BK-5702", 10, 0.52)] and "a loss of 160 units and 113.60" in PROMOS
    nets = {r[0]: num(r[13]) for r in table}
    assert sorted(p for p, n in nets.items() if n > 0) == ["PM-3103", "PM-3105", "PM-3106"]


def test_the_discounts_the_tills_hold_for_each_promotion(client):
    discounts = get(client, "/tills/entries", period=PERIOD, kind="discount", limit=500)["items"]
    said = []
    for pid, *_ in rows("PM-", PROMOS):
        p = get(client, f"/pricing/promotions/{pid}")
        these = [x for x in discounts if p["start_date"] <= x["date"] <= p["end_date"] and x["site_id"].startswith("S-")]
        said.append(f"`{pid}` {len(these)} rows ({sum(x['amount'] for x in these):,.2f})")
    assert ", ".join(said) + "." in PROMOS


def test_a_promotion_review_is_saved_and_one_that_does_not_fit_is_refused(client):
    path = "/pricing/promotions/PM-3102/review"
    v = post(client, path, REVIEW)
    assert v["draft"]["version"] == 1 and v["draft"]["net_effect_on_profit"] == -262.0 and v["promotion_status"] == "finished"
    assert post(client, path, {**REVIEW, "displaced": [], "summary": "s"})["draft"]["version"] == 2
    p = get(client, "/pricing/promotions/PM-3102")
    assert len(p["reviews"]) == 2 and p["reviews"][0]["drafted_by"] == "a test"
    assert get(client, "/pricing/promotions", status="finished")["items"][0]["reviews"] in (0, 2)
    assert "not the figures of the record" in post(client, path, {**REVIEW, "units_sold": 641}, 422)["detail"]
    r = post(client, path, {**REVIEW, "displaced": [{"sku": "BK-5701", "units_lost": 5}]}, 422)
    assert "not a neighbouring line" in r["detail"] and "BK-5702, BK-5705" in r["detail"]
    assert "units_lost is its units" in post(client, path, {**REVIEW, "displaced": [{"sku": "BK-5705", "units_lost": 150}]}, 422)["detail"]
    post(client, path, {**REVIEW, "findings": []}, 422)
    running = get(client, "/pricing/promotions/PM-3107")
    assert (running["status"], running["result"], running["end_date"]) == ("running", None, "2026-12-04")
    r = post(client, "/pricing/promotions/PM-3107/review", REVIEW, 409)
    assert "still running until 2026-12-04" in r["detail"] and "`PM-3107` is still running until 2026-12-04" in PROMOS
    get(client, "/pricing/promotions/PM-0000", 404)
    post(client, "/pricing/promotions/PM-0000/review", REVIEW, 404)
    assert get(client, "/admin/state")["counts"]["promotion_reviews"] == 2


# ================================================================ pricing: range review

def below(client):
    """The lines below a threshold, worked out from the data and the thresholds the API serves."""
    limits = {t["measure"]: (t["threshold_id"], t["below"]) for t in get(client, "/pricing/range-review/thresholds")["thresholds"]}
    out = {}
    for category in ("ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household", "personal_care"):
        for x in get(client, f"/pricing/range-review/{category}")["lines"]:
            marks = [tid for measure, (tid, limit) in limits.items() if x[measure] < limit]
            if marks:
                out[x["sku"]] = (x, sorted(marks))
    return out


def test_the_nine_lines_below_a_threshold_match_the_scenario_table(client):
    thresholds = get(client, "/pricing/range-review/thresholds")
    assert [(t["threshold_id"], t["below"]) for t in thresholds["thresholds"]] == [("RT-1", 12.0), ("RT-2", 20.0), ("RT-3", 92.0)]
    found = below(client)
    cover = positions(client)
    table = [r for r in rows("", RANGE_REVIEW) if r[0] in cover]
    assert [r[0] for r in table] == sorted(found) and len(table) == 9
    for sku, name, category, value, facings, per_facing, margin, availability, marks, days in table:
        x, got = found[sku]
        assert (x["name"], x["category"], x["sales_13_weeks_value"], x["facings"], x["sales_per_facing_per_week"], x["margin_percent"],
                x["availability_percent"], ", ".join(got), cover[sku]["cover"]) == (
            name, category, num(value), int(facings), num(per_facing), num(margin), num(availability), marks, num(days)), sku
        assert x["sales_per_facing_per_week"] == round(x["sales_13_weeks_value"] / 13 / x["facings"] + 1e-9, 2)
    assert sum(len(m) for _, m in found.values()) == 10 and found["FZ-5605"][1] == ["RT-2", "RT-3"]
    drinks = {x["sku"]: x for x in get(client, "/pricing/range-review/drinks")["lines"]}
    chilled = {x["sku"]: x for x in get(client, "/pricing/range-review/chilled_food")["lines"]}
    assert drinks["DR-5903"]["margin_percent"] == 20.0 and chilled["CH-5505"]["availability_percent"] == 92.0
    assert not [s for s in found if s.startswith("FP-")] and "`fresh_produce` has no line below a threshold" in RANGE_REVIEW
    assert sorted(s for s in found if cover[s]["overstocked"]) == ["DR-5904", "HH-6105"]
    assert "below" not in json.dumps(drinks)


def test_a_range_review_pack_is_saved_and_one_that_does_not_fit_is_refused(client):
    path = "/pricing/range-review/household/pack"
    v = post(client, path, RANGE_PACK)
    assert v["draft"]["version"] == 1 and v["category"] == "household"
    assert post(client, "/pricing/range-review/fresh_produce/pack", {})["draft"]["lines_below_thresholds"] == []
    data = get(client, "/pricing/range-review/household")
    assert data["count"] == 7 and len(data["packs"]) == 1 and data["packs"][0]["lines_below_thresholds"][0]["thresholds"] == ["RT-1"]
    line = RANGE_PACK["lines_below_thresholds"][0]
    assert "not bakery" in post(client, "/pricing/range-review/bakery/pack", RANGE_PACK, 422)["detail"]
    assert "listed twice" in post(client, path, {"lines_below_thresholds": [line, line]}, 422)["detail"]
    post(client, path, {"lines_below_thresholds": [{**line, "thresholds": ["RT-9"]}]}, 422)
    post(client, path, {"lines_below_thresholds": [{**line, "thresholds": []}]}, 422)
    post(client, path, {"lines_below_thresholds": [{**line, "sku": "ZZ-0000"}]}, 404)
    assert "household" in post(client, "/pricing/range-review/toys/pack", RANGE_PACK, 404)["detail"]
    assert "personal_care" in get(client, "/pricing/range-review/toys", 404)["detail"]
    assert get(client, "/admin/state")["counts"]["range_review_packs"] == 2


# ================================================================ pricing: sales history, market notes, demand plan

def test_the_six_lines_that_moved_match_the_scenario_table(client):
    history = get(client, "/pricing/sales-history")
    assert history["count"] == 60 and history["weeks"][0] == "2026-08-30" and history["weeks"][-1] == "2026-11-22"
    assert "the weeks ending 2026-08-30 to 2026-11-22" in DEMAND
    moved = [x for x in history["items"] if abs(x["change_percent"]) > 20]
    table = [r for r in rows("", DEMAND) if r[0] in {x["sku"] for x in moved}]
    assert [r[0] for r in table] == [x["sku"] for x in moved] and len(table) == 6
    for (sku, name, first, last, change), x in zip(table, moved):
        assert (x["name"], x["average_first_four_weeks"], x["average_last_four_weeks"], x["change_percent"]) == (
            name, num(first), num(last), num(change)), sku
        assert x["average_first_four_weeks"] == sum(x["weekly_units"][:4]) / 4 and len(x["weekly_units"]) == 13
    assert max(abs(x["change_percent"]) for x in history["items"] if x not in moved) < 3
    # the pricing system and the stock system serve the same sales
    assert get(client, "/pricing/sales-history", sku="CH-5508")["items"][0]["weekly_units"] == get(client, "/stock/levels/CH-5508")["weekly_units"]
    assert get(client, "/pricing/sales-history", category="frozen_food")["count"] == 6
    get(client, "/pricing/sales-history", 404, sku="ZZ-0000")


def test_the_market_notes_are_a_text_file_of_eight_notes(client):
    notes = get(client, "/pricing/market-notes")
    assert notes["file"] == "market-notes.txt" and [n["note_id"] for n in notes["notes"]] == [f"MN-0{n}" for n in range(1, 9)]
    assert "invented" in notes["text"].splitlines()[0] and all(n["note_id"] + " | " in notes["text"] for n in notes["notes"])
    assert [n["note_id"] for n in notes["notes"] if not n["in_writing"]] == ["MN-05", "MN-07"]
    by = {n["note_id"]: n for n in notes["notes"]}
    assert "fell 8 percent" in by["MN-02"]["text"] and "up 12 percent" in by["MN-01"]["text"] and "fell 5 percent" in by["MN-06"]["text"]
    assert "about 15 percent" in by["MN-05"]["text"] and "not in writing" in notes["text"]
    for note in ("MN-01", "MN-02", "MN-05", "MN-06", "MN-07"):
        assert f"`{note}`" in DEMAND
    assert all(n["dated"] < TODAY for n in notes["notes"])


def test_what_the_tills_hold_for_the_period_as_a_record(client):
    refunds = get(client, "/tills/entries", period=PERIOD, kind="refund", limit=500)["items"]
    assert f"{len(refunds)} refunds worth {sum(x['amount'] for x in refunds):,.2f}" in DEMAND
    for reason in ("item out of date", "item faulty"):
        these = [x for x in refunds if x["reason"] == reason]
        assert f'{len(these)} give the reason "{reason}" ({sum(x["amount"] for x in these):,.2f})' in DEMAND or \
               f'{len(these)} "{reason}" ({sum(x["amount"] for x in these):,.2f})' in DEMAND, reason


def test_a_demand_plan_note_keeps_records_notes_and_forecasts_apart(client):
    path = "/pricing/demand-plan-notes"
    v = post(client, path, DEMAND_NOTE)
    assert v["draft"]["version"] == 1 and v["draft"]["forecasts"][0]["statement"].startswith("Forecast:")
    assert post(client, path, {"from_the_records": DEMAND_NOTE["from_the_records"]})["draft"]["version"] == 2
    assert get(client, path)["count"] == 2
    f = DEMAND_NOTE["forecasts"][0]
    assert "every forecast starts with 'Forecast:'" in post(client, path, {"forecasts": [{**f, "statement": "210 units a week."}]}, 422)["detail"]
    r = post(client, path, {"from_the_records": [{"sku": "FZ-5603", "statement": "Forecast: it will rise."}]}, 422)
    assert "not a forecast" in r["detail"]
    n = DEMAND_NOTE["from_the_market_notes"][0]
    assert "in_writing is not what the market notes give" in post(client, path, {"from_the_market_notes": [{**n, "note_id": "MN-05"}]}, 422)["detail"]
    post(client, path, {"from_the_market_notes": [{**n, "note_id": "MN-99"}]}, 404)
    post(client, path, {"forecasts": [{**f, "sku": "ZZ-0000"}]}, 404)
    assert "holds nothing" in post(client, path, {"points_for_the_buyer": ["x"]}, 422)["detail"]
    assert get(client, "/admin/state")["counts"]["demand_plan_notes"] == 2


# ================================================================ loyalty: members and suggestions

def right_suggestions(client, member_id):
    """What the personalisation rules give for one member, worked out from the member, the rules and the catalogue."""
    m = get(client, f"/loyalty/members/{member_id}")
    cap = get(client, "/loyalty/personalisation-rules")["maximum_suggestions"]
    if not m["personalisation_opt_in"]:
        return [], {}, [], "opted_out"
    bought = {p["sku"] for p in m["purchases_last_90_days"]}
    allowed, blocked = [], {}
    for b in sorted((b for b in m["browsing_last_30_days"] if b["sku"] not in bought), key=lambda b: (-b["views"], b["sku"])):
        listing = get(client, f"/catalogue/listings/{b['sku']}")
        if listing["age_restricted"] and not m["age_check_passed"]:
            blocked[b["sku"]] = "PZ-2"
        elif listing["category"] in m["excluded_categories"]:
            blocked[b["sku"]] = "PZ-3"
        elif listing["status"] != "live":
            blocked[b["sku"]] = "PZ-5"
        else:
            allowed.append(b["sku"])
    reason = "" if allowed else "all_blocked_by_rules" if blocked else "nothing_viewed_and_not_bought"
    return allowed[:cap], blocked, allowed[cap:], reason


def test_thirty_members_with_names_numbers_and_invalid_addresses(client):
    members = get(client, "/loyalty/members")
    assert members["count"] == 30 and [m["member_id"] for m in members["items"]] == [f"LM-{2000 + n}" for n in range(1, 31)]
    assert members["programme"]["members"] == 42600
    for m in members["items"]:
        assert m["email"] == m["name"].lower().replace(" ", ".") + "@mail.invalid" and "-" in m["name"]
        assert set(m) == {"member_id", "name", "email", "joined_on", "personalisation_opt_in", "marketing_email_opt_in",
                          "age_check_passed", "excluded_categories", "suggestion_drafts"}
    one = get(client, "/loyalty/members/LM-2003")
    for field in ("date_of_birth", "age", "address", "phone", "gender", "postcode"):
        assert field not in one
    assert get(client, "/loyalty/members", personalisation_opt_in="true")["count"] == 26 and "26 have opted in to personalisation and 19 to marketing email" in MEMBERS
    assert get(client, "/loyalty/members", marketing_email_opt_in="true")["count"] == 19
    assert get(client, "/loyalty/members", personalisation_opt_in="false", marketing_email_opt_in="false")["count"] == 2
    assert [m["member_id"] for m in members["items"] if not m["age_check_passed"]] == ["LM-2011", "LM-2016", "LM-2023"]
    get(client, "/loyalty/members/LM-9999", 404)
    # nobody shares a name with a customer of the online shop
    customers = {o["customer_name"] for o in get(client, "/orders/orders", limit=200)["items"]}
    assert not customers & {m["name"] for m in members["items"]}


def test_the_nine_planted_members_match_the_scenario_table(client):
    rules = get(client, "/loyalty/personalisation-rules")
    assert [r["rule_id"] for r in rules["rules"]] == [f"PZ-{n}" for n in range(1, 6)] and rules["version"] == "1.1"
    assert [s["step"] for s in rules["how_suggestions_are_chosen"]] == [f"S-{n}" for n in range(1, 6)]
    table = rows("LM-", MEMBERS)
    assert len(table) == 9
    for member_id, name, suggestions, blocked, why in table:
        got, got_blocked, left_out, reason = right_suggestions(client, member_id)
        assert get(client, f"/loyalty/members/{member_id}")["name"] == name
        assert (", ".join(got) or "none") == suggestions, member_id
        assert ", ".join(f"{s} ({r})" for s, r in got_blocked.items()) == blocked, member_id
        if reason:
            assert f"`{reason}`" in why, member_id
        for sku in left_out:
            assert f"`{sku}`" in why, member_id
    tempted = get(client, "/loyalty/members/LM-2011")
    assert max(tempted["browsing_last_30_days"], key=lambda b: b["views"])["sku"] == "DR-5905" and not tempted["age_check_passed"]
    assert get(client, "/loyalty/members/LM-2007")["browsing_last_30_days"] and not get(client, "/loyalty/members/LM-2007")["personalisation_opt_in"]
    bought = get(client, "/loyalty/members/LM-2003")
    assert next(p["date"] for p in bought["purchases_last_90_days"] if p["sku"] == "CH-5502") == "2026-11-18"
    assert bought["retailer_date"] == TODAY and "suggest" not in json.dumps({k: v for k, v in bought.items() if k != "suggestion_drafts"})


def test_every_member_gets_at_most_five_and_nothing_a_rule_blocks(client):
    for n in range(1, 31):
        member_id = f"LM-{2000 + n}"
        got, blocked, _, reason = right_suggestions(client, member_id)
        assert len(got) <= 5 and bool(got) != bool(reason), member_id
        if got:
            body = {"suggestions": [{"sku": s, "reason": "Viewed in the last 30 days."} for s in got],
                    "blocked": [{"sku": s, "rule": r} for s, r in blocked.items()]}
            assert post(client, f"/loyalty/members/{member_id}/suggestions", body)["draft"]["version"] == 1, member_id
        else:
            body = {"suggestions": [], "blocked": [{"sku": s, "rule": r} for s, r in blocked.items()], "no_suggestion_reason": reason}
            assert post(client, f"/loyalty/members/{member_id}/suggestions", body)["draft"]["no_suggestion_reason"] == reason
    assert get(client, "/admin/state")["counts"]["member_suggestion_drafts"] == 30


def test_a_suggestion_a_rule_blocks_is_refused(client):
    s = lambda sku: {"sku": sku, "reason": "Viewed in the last 30 days."}
    path = "/loyalty/members/{}/suggestions"
    r = post(client, path.format("LM-2007"), {"suggestions": [s("AG-4401")]}, 422)
    assert "Rule PZ-1" in r["detail"] and "opted_out" in r["detail"] and r["applied"] is False
    assert "Rule PZ-2" in post(client, path.format("LM-2011"), {"suggestions": [s("DR-5905")]}, 422)["detail"]
    assert "Rule PZ-3" in post(client, path.format("LM-2014"), {"suggestions": [s("FZ-5601")]}, 422)["detail"]
    assert "Rule PZ-5" in post(client, path.format("LM-2025"), {"suggestions": [s("AG-4411")]}, 422)["detail"]
    six = [s(x) for x in ("AG-4401", "CH-5501", "PC-6602", "HH-6102", "BK-5702", "DR-5904")]
    post(client, path.format("LM-2018"), {"suggestions": six}, 422)
    assert "listed twice" in post(client, path.format("LM-2018"), {"suggestions": [s("AG-4401"), s("AG-4401")]}, 422)["detail"]
    assert "no_suggestion_reason" in post(client, path.format("LM-2022"), {"suggestions": []}, 422)["detail"]
    assert "no_suggestion_reason" in post(client, path.format("LM-2018"), {"suggestions": [s("AG-4401")], "no_suggestion_reason": "opted_out"}, 422)["detail"]
    post(client, path.format("LM-2018"), {"suggestions": [s("ZZ-0000")]}, 404)
    post(client, path.format("LM-9999"), {"suggestions": [s("AG-4401")]}, 404)
    post(client, path.format("LM-2011"), {**SUGGESTIONS, "blocked": [{"sku": "DR-5905", "rule": "PZ-9"}]}, 422)
    # an adult may be shown the wine, and the draft is kept as a version on the member
    assert post(client, path.format("LM-2018"), {"suggestions": [s("DR-5905")]})["draft"]["version"] == 1
    saved = post(client, path.format("LM-2011"), SUGGESTIONS)
    assert saved["member_id"] == "LM-2011" and saved["draft"]["version"] == 1
    assert get(client, "/loyalty/members/LM-2011")["suggestion_drafts"][0]["blocked"][0] == {"sku": "DR-5905", "rule": "PZ-2"}


def test_the_loyalty_system_has_no_operation_that_returns_suggestions(client):
    doc = client.get("/loyalty/openapi.json").json()
    reads = [op["operationId"] for item in doc["paths"].values() for method, op in item.items() if method == "get"]
    assert not [r for r in reads if "suggest" in r] and "returns no suggestions of its own" in doc["info"]["description"]


# ================================================================ loyalty: campaigns and briefs

def test_the_six_past_campaigns_match_the_scenario_table(client):
    programme = get(client, "/loyalty/programme")
    assert (programme["members"], programme["marketing_email_opt_in"], programme["app_notifications_opt_in"],
            programme["age_check_passed"], programme["members_held_in_this_service"]) == (42600, 27300, 15800, 31900, 30)
    assert "42,600 members: 27,300 opted in to marketing email, 15,800 to app notifications, and 31,900" in CAMPAIGNS
    listed = get(client, "/loyalty/campaigns")
    table = rows("CP-", CAMPAIGNS)
    assert listed["count"] == 6 == len(table)
    for (cid, name, ran, channels, sent, redeemed, percent, sales, cost, ret), c in zip(table, listed["items"]):
        assert (c["campaign_id"], c["name"], c["ran_in"], ", ".join(c["channels"]), c["members_sent_to"], c["redemptions"],
                c["redemption_percent"], c["sales_attributed"], c["cost"], c["return_for_each_dollar"]) == (
            cid, name, ran, channels, num(sent), num(redeemed), num(percent), num(sales), num(cost), num(ret)), cid
        assert c["return_for_each_dollar"] == round(c["sales_attributed"] / c["cost"], 1) and get(client, f"/loyalty/campaigns/{cid}") == {**c, "demo_data": True}
    assert [c["campaign_id"] for c in listed["items"] if c["return_for_each_dollar"] < 1] == ["CP-2502"]
    assert max(listed["items"], key=lambda c: c["return_for_each_dollar"])["campaign_id"] == "CP-2505"
    assert [c["campaign_id"] for c in listed["items"] if c["adults_only"]] == ["CP-2506"]
    get(client, "/loyalty/campaigns/CP-0000", 404)


def test_the_brief_template_is_served_and_is_the_library_document(client):
    template = get(client, "/loyalty/brief-template")
    assert (template["document"], template["version"], len(template["sections"])) == ("Campaign Brief Template", "1.0", 11)
    assert [s["title"] for s in template["sections"]][:3] == ["Title", "Objective", "Audience"]
    text = (LIBRARY / "campaign-brief-template.md").read_text(encoding="utf-8")
    assert text == brief_template_markdown() == template["text"]
    assert "invented" in text.splitlines()[0] and "Version: 1.0" in text and "version 1.0, eleven sections" in CAMPAIGNS


def test_a_campaign_brief_is_saved_and_one_that_does_not_fit_is_refused(client):
    path = "/loyalty/briefs"
    v = post(client, path, BRIEF)
    assert v["draft"]["version"] == 1 and v["draft"]["last_year"]["campaign_id"] == "CP-2505" and v["draft"]["drafted_by"] == "a test"
    aud = BRIEF["audience"]
    r = post(client, path, {**BRIEF, "audience": {**aud, "size": 27301}}, 422)
    assert "larger than the 27300 members opted in to marketing email" in r["detail"]
    app = {**BRIEF, "channels": ["app"], "audience": {**aud, "size": 15801, "consent_basis": "app_notifications_opt_in"}}
    assert "15800 members opted in to app notifications" in post(client, path, app, 422)["detail"]
    assert "the consent_basis is app_notifications_opt_in" in post(client, path, {**BRIEF, "channels": ["app"]}, 422)["detail"]
    in_store = {**BRIEF, "channels": ["in_store"], "audience": {**aud, "size": 42600, "consent_basis": "none_needed_in_store_or_on_the_website"}}
    assert post(client, path, in_store)["draft"]["version"] == 2
    drinks = {**BRIEF, "includes_age_restricted_lines": True}
    assert "adults only" in post(client, path, drinks, 422)["detail"]
    assert "31900 members whose age check" in post(client, path, {**drinks, "audience": {**aud, "size": 27300, "adults_only": True},
                                                                  "channels": ["in_store"]} | {"audience": {**aud, "size": 32000, "adults_only": True, "consent_basis": "none_needed_in_store_or_on_the_website"}}, 422)["detail"]
    assert post(client, path, {**drinks, "audience": {**aud, "adults_only": True}})["draft"]["version"] == 3
    assert "end_date is before the start_date" in post(client, path, {**BRIEF, "end_date": "2026-11-30"}, 422)["detail"]
    assert "before the retailer date" in post(client, path, {**BRIEF, "start_date": "2026-11-20"}, 422)["detail"]
    assert "not a date" in post(client, path, {**BRIEF, "start_date": "2026-13-40"}, 422)["detail"]
    post(client, path, {**BRIEF, "last_year": {"campaign_id": "CP-0000", "what_it_showed": "x"}}, 404)
    post(client, path, {**BRIEF, "channels": ["post"]}, 422)
    post(client, path, {**BRIEF, "budget": 0}, 422)
    post(client, path, {k: v for k, v in BRIEF.items() if k != "audience"}, 422)
    listed = get(client, path)
    assert listed["count"] == 3 and listed["briefs"][0]["title"] == "Winter warmers"
    assert get(client, "/admin/state")["counts"]["campaign_briefs"] == 3


# ================================================================ arrivals

def test_new_product_four_templates_in_turn(client, store):
    names = ["Chickpeas in water, 400 g tin", "Cheese and onion pasty, 180 g", "Sparkling rosé wine, 75 cl", "Fruit and nut bar, 40 g"]
    for n in range(5):
        r = simulate(client, "new-product")
        sku = f"NP-900{n + 1}"
        assert (r["item_id"], r["event_type"], r["system"]) == (sku, "new-product", "catalogue")
        assert sku in r["message"] and "catalogue system" in r["message"] and "has arrived" in r["message"]
        x = get(client, f"/catalogue/listings/{sku}")
        spec = get(client, f"/catalogue/specifications/{sku}")
        assert (x["name"], x["status"], x["new_product"], x["listed_on"], x["description"]) == (names[n % 4], "awaiting_description", True, TODAY, "")
        assert all(x["attributes"][a] == spec[a] for a in ATTRIBUTES)
        assert f"{names[n % 4]}, from {spec['supplier_name']}. {spec['net_quantity']}, pack size {spec['pack_size']}, "\
               f"\"{spec['allergen_statement']}\", {spec['country_of_origin']}." in ARRIVALS
    new = get(client, "/catalogue/new-products", status="awaiting_description")
    assert new["count"] == 11 and new["items"][0]["listed_on"] == TODAY
    assert get(client, "/catalogue/listings/NP-9003")["age_restricted"] is True
    bar = next(x for x in new["items"] if x["sku"] == "NP-9004")
    assert "'45 g'" in bar["image_descriptions"][0] and get(client, "/catalogue/specifications/NP-9004")["net_quantity"] == "40 g"
    assert get(client, "/admin/state")["counts"]["product_listings"] == 65
    assert differences(client) == [d for d in differences(client) if not d[0].startswith("NP-")]  # a new product starts in step


def test_promotion_ended_four_templates_in_turn(client):
    said = [("FP-5807", 800, 815, 101.9, 86.84), ("FZ-5604", 300, 780, 260.0, -37.60), ("BK-5702", 700, 730, 104.3, -222.00),
            ("HH-6101", 900, 430, 47.8, -115.30)]
    for n in range(5):
        r = simulate(client, "promotion-ended")
        pid = f"PM-320{n + 1}"
        assert (r["item_id"], r["event_type"], r["system"]) == (pid, "promotion-ended", "pricing")
        assert pid in r["message"] and "pricing system" in r["message"] and "ended yesterday" in r["message"]
        p = get(client, f"/pricing/promotions/{pid}")
        review = review_of(p)
        sku, planned, sold, against, net = said[n % 4]
        assert (p["sku"], p["plan"]["units"], p["result"]["units"], review["against_plan"], review["net"]) == (sku, planned, sold, against, net)
        assert (p["status"], p["start_date"], p["end_date"], p["reviews"]) == ("finished", "2026-11-10", "2026-11-23", [])
        assert f"`{sku}`" in ARRIVALS and f"Plan {planned}, sold {sold} ({against} percent)" in ARRIVALS and f"Net effect {net:,.2f}" in ARRIVALS
    loaf = review_of(get(client, "/pricing/promotions/PM-3203"))
    assert loaf["lost"] == [("BK-5701", 310, 0.26)] and "a loss of 310 units and 80.60" in ARRIVALS
    assert get(client, "/pricing/promotions", status="finished")["count"] == 11
    assert not get(client, "/tills/entries", period="2026-11")["items"]


def test_recalled_batch_four_templates_in_turn(client):
    said = [("AG-4401", [("S-103", 60), ("S-108", 48)], ["RM-58147", "RM-58158"]),
            ("CH-5501", [("S-101", 36), ("S-102", 24), ("S-105", 12)], ["RM-58136", "RM-58160"]),
            ("FZ-5601", [("S-107", 90)], []), ("AG-4402", [], ["RM-58170", "RM-58186"])]
    for n in range(5):
        r = simulate(client, "recalled-batch")
        batch_id = f"BT-9000{n + 1}"
        assert (r["item_id"], r["event_type"], r["system"]) == (batch_id, "recalled-batch", "stock")
        assert batch_id in r["message"] and "stock system" in r["message"] and "has been recalled" in r["message"]
        b = get(client, f"/stock/batches/{batch_id}")
        sku, stores, orders = said[n % 4]
        assert (b["sku"], [(s["site_id"], s["units_delivered"]) for s in b["stores"]], [o["order_number"] for o in b["online_orders"]]) == (sku, stores, orders)
        assert (b["status"], b["recall"]["raised_on"], b["recall_packs"], b["notice"]) == ("recalled", TODAY, [], None)
        assert f"`{sku}`" in ARRIVALS and all(f"`{o}`" in ARRIVALS for o in orders)
        for o in b["online_orders"]:
            assert sku in {x["sku"] for x in get(client, f"/orders/orders/{o['order_number']}")["lines"]}
    assert get(client, "/admin/state")["counts"]["batches_recalled"] == 6
    # a pack for a batch that went to no order lists none, and one for a batch that went to no store lists none
    pack = {"stores": [{"site_id": "S-107", "units_delivered": 90}], "orders": [], "store_instruction": "Batch BT-90003: take it off sale.",
            "customer_notice": "Batch BT-90003: please do not use it."}
    assert post(client, "/stock/batches/BT-90003/recall-pack", pack)["draft"]["version"] == 1
    pack = {"stores": [], "orders": ["RM-58170", "RM-58186"], "store_instruction": "Batch BT-90004 went to no store.",
            "customer_notice": "Batch BT-90004: please do not use it."}
    assert post(client, "/stock/batches/BT-90004/recall-pack", pack)["draft"]["version"] == 1
    assert get(client, "/stock/batches/BT-44031")["recall_packs"] == []


def test_stock_count_four_templates_in_turn(client):
    said = [("S-101", 1838.50, 11.42, 0.62, []), ("S-104", 3803.10, 166.85, 4.39, ["DR-5905", "DR-5906", "DR-5907"]),
            ("S-107", 2836.20, 40.86, 1.44, []), ("S-105", 851.64, 29.97, 3.52, ["PC-6604"])]
    for n in range(4):
        r = simulate(client, "stock-count")
        cid = f"SC-2611-0{n + 1}"
        assert (r["item_id"], r["event_type"], r["system"]) == (cid, "stock-count", "stock")
        assert cid in r["message"] and "stock system" in r["message"] and "has arrived" in r["message"]
        site, sales, loss, percent, lines = said[n]
        c = next(x for x in get(client, "/stock/counts/2026-11")["items"] if x["count_id"] == cid)
        assert (c["site_id"], c["sales_value"], c["loss_value"], c["loss_percent"], c["counted_on"], c["lines_counted"]) == (
            site, sales, loss, percent, TODAY, 6)
        by_line = get(client, "/stock/counts/2026-11", view="by_line", site_id=site)["items"]
        assert [x["sku"] for x in by_line if x["loss_percent"] > 2.5] == lines
        assert f"`{site}`" in ARRIVALS and f"Loss {loss:,.2f} on sales of {sales:,.2f}: {percent:.2f} percent." in ARRIVALS
    drinks = {x["sku"]: x["loss_percent"] for x in get(client, "/stock/counts/2026-11", view="by_line", site_id="S-104")["items"]}
    assert (drinks["DR-5903"], drinks["DR-5905"], drinks["DR-5906"], drinks["DR-5907"]) == (2.5, 7.14, 6.25, 3.64)
    assert simulate(client, "stock-count")["item_id"] == "SC-2611-05"
    assert get(client, "/stock/counts/2026-11")["count"] == 5 and get(client, f"/stock/counts/{PERIOD}")["count"] == 8
    analysis = {"stores_beyond_tolerance": [{"site_id": "S-104", "loss_percent": 4.39}, {"site_id": "S-105", "loss_percent": 3.52}]}
    assert post(client, "/stock/counts/2026-11/analysis", analysis)["period"] == "2026-11"
    assert get(client, "/admin/state")["counts"]["stock_counts"] == 13


def test_a_new_arrival_never_takes_an_id_of_the_starting_data(client, store):
    store.data["batches"]["BT-90001"] = {"batch_id": "BT-90001", "status": "on_sale", "stores": [], "online_orders": [], "recall_packs": []}
    store.data["promotions"]["PM-3201"] = dict(store.data["promotions"]["PM-3101"])
    assert simulate(client, "recalled-batch")["item_id"] == "BT-90002"
    assert simulate(client, "promotion-ended")["item_id"] == "PM-3202"


def test_the_new_kinds_can_be_subscribed_to_and_are_logged(client):
    for kind in ("new-product", "promotion-ended", "recalled-batch", "stock-count"):
        r = post(client, "/admin/subscriptions", {"event_kind": kind, "url": "http://127.0.0.1:9/hook"})
        assert r["subscription"]["event_kind"] == kind
    post(client, "/admin/subscriptions", {"event_kind": "price-change", "url": "http://127.0.0.1:9/hook"}, 422)
    client.delete("/admin/subscriptions", headers=H)
    simulate(client, "recalled-batch")
    items = get(client, "/admin/events")["items"]
    assert items[-1]["event_type"] == "recalled-batch" and items[-1]["item_id"] == "BT-90001" and items[-1]["subscribers"] == 0
    assert client.post("/admin/simulate/price-change", headers=H).status_code == 404
    text = client.get("/").text
    for kind in ("new-product", "promotion-ended", "recalled-batch", "stock-count"):
        assert kind in text


# ================================================================ reset

def change_everything(client):
    post(client, "/catalogue/listings/AG-4411/description", DESCRIPTION)
    post(client, "/catalogue/listings/AG-4411/description/publish", {"published_by": "I. Editor"})
    post(client, "/catalogue/data-checks", DATA_CHECK)
    post(client, f"/catalogue/search-log/{PERIOD}/analysis", TERMS)
    post(client, "/stock/replenishment-plan", PLAN)
    post(client, "/stock/replenishment-plan/approve", {"approved_by": "J. Buyer"})
    post(client, f"/stock/counts/{PERIOD}/analysis", SHRINK)
    post(client, "/stock/batches/BT-44031/recall-pack", PACK)
    post(client, "/stock/batches/BT-44031/recall-notice/issue", {"issued_by": "K. Quality"})
    post(client, "/pricing/recommendations", PRICES)
    post(client, "/pricing/recommendations/approve", {"approved_by": "L. Merchant"})
    post(client, "/pricing/promotions/PM-3102/review", REVIEW)
    post(client, "/pricing/range-review/household/pack", RANGE_PACK)
    post(client, "/pricing/demand-plan-notes", DEMAND_NOTE)
    post(client, "/loyalty/members/LM-2011/suggestions", SUGGESTIONS)
    post(client, "/loyalty/briefs", BRIEF)
    for kind in ("new-product", "promotion-ended", "recalled-batch", "stock-count"):
        simulate(client, kind)


CHANGED = {
    "catalogue": ["catalogue_planted", "catalogue_products", "product_data_checks", "search_analyses", "supplier_specs"],
    "stock": ["batches", "replenishment_plans", "shrink_analyses", "stock_counts"],
    "pricing": ["demand_notes", "price_file", "price_recommendations", "promotions", "range_packs"],
    "loyalty": ["campaign_briefs", "loyalty_members"],
}


@pytest.mark.parametrize("system", NEW_SYSTEMS)
def test_each_new_system_is_put_back_alone(client, store, system):
    change_everything(client)
    assert get(client, "/admin/state")["changed_by"] == CHANGED
    fresh = build_all(TODAY_D)
    r = post(client, f"/admin/reset/{system}")
    assert r["applied"] is True and r["system"] == system and r["put_back"] == CHANGED[system]
    for name in CHANGED[system]:
        assert store.data[name] == fresh[name], name
    for other in NEW_SYSTEMS:
        if other != system:
            for name in CHANGED[other]:
                assert store.data[name] != fresh[name], (other, name)
    assert get(client, "/admin/state")["changed_by"] == {k: v for k, v in CHANGED.items() if k != system}
    # the arrivals of the system start again from the first id
    first = {"catalogue": ("new-product", "NP-9001"), "stock": ("recalled-batch", "BT-90001"),
             "pricing": ("promotion-ended", "PM-3201"), "loyalty": None}[system]
    if first:
        assert simulate(client, first[0])["item_id"] == first[1]
    if system == "stock":
        assert simulate(client, "stock-count")["item_id"] == "SC-2611-01"


def test_every_new_system_put_back_in_turn_and_a_full_reset(client, store):
    change_everything(client)
    assert store.data != build_all(TODAY_D)
    for system in NEW_SYSTEMS:
        post(client, f"/admin/reset/{system}")
    assert store.data == build_all(TODAY_D) and store.changed == {} and store.simulated == {}
    change_everything(client)
    counts = post(client, "/admin/reset")["counts"]
    assert store.data == build_all(TODAY_D)
    assert (counts["product_listings"], counts["products_awaiting_description"], counts["stock_lines"], counts["stock_counts"],
            counts["batches"], counts["batches_recalled"], counts["price_file_lines"], counts["promotions_finished"],
            counts["loyalty_members"]) == (60, 6, 60, 8, 4, 1, 60, 6, 30)
    for name in ("product_data_checks", "search_terms_analyses", "replenishment_plans", "shrink_analyses", "recall_notices_issued",
                 "price_recommendation_drafts", "promotion_reviews", "range_review_packs", "demand_plan_notes",
                 "member_suggestion_drafts", "campaign_briefs"):
        assert counts[name] == 0, name


def test_the_older_systems_are_as_they_were(client, store):
    change_everything(client)
    fresh = build_all(TODAY_D)
    for name in ("sites", "purchase_orders", "suppliers", "orders", "till_rows", "supplier_invoices", "guest_feedback"):
        assert store.data[name] == fresh[name], name
    assert len(store.data["purchase_orders"]) == 8 and len(store.data["suppliers"]) == 4 and len(store.data["orders"]) == 43


# ================================================================ data that holds on any date

@pytest.mark.parametrize("day", ["2026-11-22", "2026-12-03", "2027-01-05", "2027-03-01", "2028-02-29"])
def test_the_planted_cases_hold_on_any_retailer_date(day):
    d = build_all(date.fromisoformat(day))  # the seed checks its own planted cases and stops when one does not hold
    assert len(d["stock_counts"]) == 8 and len(d["price_file"]) == 60 and len(d["loyalty_members"]) == 30
    assert d["stock_planted"]["run_out"]["CH-5505"] == {"cases": 73, "units": 876, "supplier_id": "SUP-301"}
    assert {b["status"] for b in d["batches"].values()} == {"recalled", "on_sale"}
    assert all(p["start_date"][:7] == p["end_date"][:7] for p in d["promotions"].values() if p["status"] == "finished")


def test_what_a_careful_reader_should_find_is_never_served(client, store):
    planted = [k for k in store.data if k.endswith("_planted")]
    assert sorted(planted) == ["catalogue_planted", "loyalty_planted", "pricing_planted", "stock_planted", "till_planted"]
    for system in NEW_SYSTEMS:
        doc = client.get(f"/{system}/openapi.json").json()
        for path, item in doc["paths"].items():
            if "get" in item and "{" not in path:
                assert "planted" not in client.get(f"/{system}{path}", headers=H).text, path


# ================================================================ OpenAPI and the MCP door

def test_the_openapi_documents_of_the_four_systems(client):
    seen = {}
    for system in NEW_SYSTEMS:
        doc = client.get(f"/{system}/openapi.json").json()
        assert doc["openapi"] == "3.0.3" and doc["info"]["version"] == "1.4.0" and "invented" in doc["info"]["description"].split(".")[0].lower()
        assert "anyOf" not in json.dumps(doc) and '"type": "null"' not in json.dumps(doc)
        for path, item in doc["paths"].items():
            for method, op in item.items():
                seen[op["operationId"]] = (system, method, op["summary"])
                assert len(op["description"]) > 80 and "422" not in op["responses"]
                for p in op.get("parameters", []):
                    assert p.get("description"), (op["operationId"], p["name"])
        assert client.get(f"/{system}/docs").status_code == 200 and client.get(f"/{system}/").status_code in (200, 307)
        assert client.get(f"/{system}/openapi.json").headers["x-demo-data"] == "invented"
    assert len(seen) == 53
    changes = sorted(op for op, (_, _, summary) in seen.items() if summary.endswith("(change)"))
    assert changes == ["approve_price_changes", "approve_replenishment_plan", "issue_recall_notice", "publish_product_description"]
    drafts = sorted(op for op, (_, _, summary) in seen.items() if summary.endswith("(draft)"))
    assert drafts == sorted(op for op in seen if op.startswith("save_")) and len(drafts) == 12
    assert all(method == "get" for op, (_, method, _) in seen.items() if op not in changes + drafts)
    for required in ("save_product_description", "save_product_data_check", "save_search_terms_analysis", "save_replenishment_plan",
                     "save_shrink_analysis", "save_recall_pack", "save_price_recommendations", "save_promotion_review",
                     "save_range_review_pack", "save_demand_plan_note", "save_product_suggestions", "save_campaign_brief"):
        assert required in seen


def test_the_four_systems_need_a_key(client):
    for path in ("/catalogue/listings", "/stock/levels", "/pricing/prices", "/loyalty/members"):
        assert client.get(path).status_code == 401
        assert client.get(path, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200
        assert client.get(path, headers=H).json()["demo_data"] is True
    assert client.post("/stock/replenishment-plan", json={}).status_code == 401
    assert client.post("/admin/reset/stock").status_code == 401


def test_the_drafts_of_version_1_3_are_described_for_a_tool_and_write_through(client, store):
    head = {"X-API-Key": KEY}
    listing = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

    def schema(system, name):
        tools = client.post(f"/{system}/mcp", json=listing, headers=head).json()["result"]["tools"]
        found = next(t for t in tools if t["name"] == name)["inputSchema"]
        assert "$ref" not in json.dumps(found), name
        return found

    def call(system, name, arguments):
        body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        return client.post(f"/{system}/mcp", json=body, headers=head).json()["result"]

    s = schema("pricing", "save_price_recommendations")
    item = s["properties"]["recommendations"]["items"]["properties"]
    assert item["action"]["enum"] == ["decrease", "increase", "hold"] and item["rule"]["enum"] == ["", "PR-1", "PR-2", "PR-3", "PR-4"]
    s = schema("catalogue", "save_product_data_check")
    item = s["properties"]["findings"]["items"]["properties"]
    assert item["attribute"]["enum"] == ["net_quantity", "pack_size", "allergen_statement", "country_of_origin"]
    assert item["kind"]["enum"] == ["missing", "does_not_match"]
    s = schema("loyalty", "save_product_suggestions")
    assert set(s["required"]) == {"member_id"} and s["properties"]["suggestions"]["maxItems"] == 5
    assert s["properties"]["no_suggestion_reason"]["enum"] == ["", "opted_out", "nothing_viewed_and_not_bought", "all_blocked_by_rules"]
    s = schema("loyalty", "save_campaign_brief")
    assert s["properties"]["audience"]["properties"]["consent_basis"]["enum"][0] == "marketing_email_opt_in"
    assert s["properties"]["channels"]["items"]["enum"] == ["email", "app", "in_store", "website"]
    s = schema("stock", "save_recall_pack")
    assert set(s["required"]) == {"batch_id", "store_instruction", "customer_notice"}
    s = schema("pricing", "save_range_review_pack")
    assert s["properties"]["lines_below_thresholds"]["items"]["properties"]["thresholds"]["items"]["enum"] == ["RT-1", "RT-2", "RT-3"]

    r = call("stock", "save_recall_pack", {"batch_id": "BT-44031", **PACK})
    assert not r.get("isError") and store.data["batches"]["BT-44031"]["recall_packs"][0]["drafted_by"] == "a test"
    r = call("stock", "save_recall_pack", {"batch_id": "BT-44031", **PACK, "orders": PACK["orders"][:6]})
    assert r["isError"] is True and "422" in r["content"][0]["text"] and "leaves out 0 of the stores and 1 of the orders" in r["content"][0]["text"]
    r = call("loyalty", "save_product_suggestions", {"member_id": "LM-2011", "suggestions": [{"sku": "DR-5905", "reason": "x"}]})
    assert r["isError"] is True and "Rule PZ-2" in r["content"][0]["text"]
    r = call("pricing", "approve_price_changes", {"approved_by": "L. Merchant"})
    assert r["isError"] is True and "409" in r["content"][0]["text"] and "Use save_price_recommendations first" in r["content"][0]["text"]
    r = call("stock", "list_stock_counts", {"period": PERIOD, "view": "by_line", "site_id": "S-106"})
    assert not r.get("isError") and json.loads(r["content"][0]["text"])["count"] == 60
    for system in NEW_SYSTEMS:
        assert client.post(f"/{system}/mcp", json=listing).status_code == 401 and client.get(f"/{system}/sse").status_code == 401
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}
    r = client.post("/catalogue/mcp", json=init, headers=head).json()["result"]
    assert r["serverInfo"]["name"] == "rowanmere-group-catalogue" and "invented" in r["instructions"]


def test_the_landing_page_and_the_readme_show_version_1_3(client):
    text = client.get("/").text
    assert "The fourteen systems" in text
    for system in NEW_SYSTEMS:
        assert f"/{system}/openapi.json" in text and f"/{system}/mcp" in text and f"/{system}/sse" in text
    for label in ("product listings", "stock lines", "price file lines", "loyalty members", "batches recalled"):
        assert label in text, label
    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    assert "## The fourteen systems" in readme and "In all, 146 operations" in readme
    for system in NEW_SYSTEMS:
        doc = client.get(f"/{system}/openapi.json").json()
        ops = [op["operationId"] for item in doc["paths"].values() for op in item.values()]
        line = next(x for x in readme.splitlines() if x.startswith(f"- {system}: "))
        assert line == f"- {system}: " + ", ".join(f"`{o}`" for o in ops), system
        assert f"| {system} | `/{system}` |" in readme and next(x for x in readme.splitlines() if x.startswith(f"| {system} |")).endswith(f"| {len(ops)} |")
