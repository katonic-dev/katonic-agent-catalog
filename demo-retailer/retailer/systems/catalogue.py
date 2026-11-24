"""Catalogue, version 1.3: product listings, suppliers' specifications, the style guide, new products and the search log."""

from __future__ import annotations

import re
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_base import period_of
from ..seed_catalogue import (ADULT_SENTENCE, ATTRIBUTES, BANNED_WORDS, IMAGES_NOTE, MAX_TAGS, MAX_WORDS, MIN_TAGS, MIN_WORDS,
                              STYLE_GUIDE)
from ..seed_range import CATEGORIES
from ..store import now_iso

KEY = "catalogue"
TITLE = "Catalogue"
LINE = ("The online shop's product listings, the suppliers' specifications, the style guide for descriptions, new products "
        "with their image descriptions, and the shop's search log.")

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
Category = Literal["ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household",
                   "personal_care"]
Attribute = Literal["net_quantity", "pack_size", "allergen_statement", "country_of_origin"]
LISTING_FIELDS = ("sku, name, brand, category, status (live or awaiting_description), new_product, listed_on, age_restricted, "
                  "attributes (net_quantity, pack_size, allergen_statement and country_of_origin, each as the listing shows "
                  "it: an empty text means the listing has nothing there), description and image_tags")
SPEC_FIELDS = ("sku, specification_ref, version, issued_on, supplier_id, supplier_name, product_name, brand, net_quantity, "
               "pack_size, allergen_statement, country_of_origin, storage, shelf_life_days, age_restricted and claims (the "
               "only claims the supplier makes, for example free-range; an empty list means none)")


class DescriptionDraft(BaseModel):
    description: str = Field(..., min_length=1, description="The description, 40 to 80 words, in plain sentences. None of "
                             "the words the style guide rules out. An age-restricted line ends with the sentence the style "
                             "guide gives.")
    image_tags: list[str] = Field(..., description="Three to six tags, in lower case. Each names something the image "
                                                   "descriptions say is in the picture.")
    net_quantity: str = Field(..., description="The net quantity, exactly as the supplier's specification gives it.")
    pack_size: str = Field(..., description="The pack size, exactly as the supplier's specification gives it.")
    allergen_statement: str = Field(..., description="The allergen statement, copied word for word from the supplier's "
                                                     "specification. Never worked out.")
    country_of_origin: str = Field(..., description="The country of origin, exactly as the supplier's specification gives it.")
    differences_for_the_content_lead: list[str] = Field(default_factory=list, description="Each place where an image "
                                                        "description and the specification disagree, in one plain "
                                                        "sentence. Empty when there is none.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PublishBody(BaseModel):
    published_by: str = Field(..., min_length=1, description="The content lead who publishes it. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


class DataFinding(BaseModel):
    sku: str = Field(..., min_length=1, description="The line, for example AG-4407.")
    attribute: Attribute = Field(..., description="The attribute: net_quantity, pack_size, allergen_statement or "
                                                  "country_of_origin.")
    kind: Literal["missing", "does_not_match"] = Field(
        ..., description="missing: the listing has nothing for the attribute and the specification has a value. "
                         "does_not_match: both have a value and they differ.")
    listing_value: str = Field("", description="What the listing shows. Empty when kind is missing.")
    specification_value: str = Field(..., min_length=1, description="What the supplier's specification gives.")


class DataCheck(BaseModel):
    findings: list[DataFinding] = Field(default_factory=list, description="One entry for each attribute that is missing or "
                                        "does not match. An empty list means nothing was found.")
    category: str = Field("", description="Leave empty for a check of every listing. Give a category when the check covers one.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class TermGroup(BaseModel):
    name: str = Field(..., min_length=1, description="A short name for the group, in plain words.")
    what_shoppers_seemed_to_want: str = Field(..., min_length=1, description="One plain sentence on what the shoppers "
                                              "who typed these terms seem to have wanted.")
    terms: list[str] = Field(..., min_length=1, description="The search terms in the group, each written exactly as the "
                                                            "search log gives it.")


class TermsAnalysis(BaseModel):
    groups: list[TermGroup] = Field(..., min_length=1, description="The groups. Every term is in one group only.")
    summary: str = Field("", description="A short summary in plain sentences. It proposes no change to the shop. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9'°-]+", text)


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the listings of Rowanmere Market's online shop: sixty lines in eight "
                                  "categories, the supplier's specification for each, the style guide, a dozen new products "
                                  "and a month of the shop's search log. It holds no images: an image appears as a "
                                  "description in words. Saving a description, a data check or an analysis is a draft. A "
                                  "content lead publishes every description.")
    st = ctx.store
    d = lambda: st.data

    def product_or_404(sku: str) -> dict:
        x = d()["catalogue_products"].get(sku)
        if not x:
            raise not_found("product listing", sku, "Use list_product_listings to find line ids. They look like AG-4407.")
        return x

    def shown(x: dict) -> dict:
        return {k: v for k, v in x.items() if k not in ("image_descriptions", "description_drafts", "published")}

    def log_or_error(period: str) -> dict:
        log = d()["search_log"].get(period)
        if log:
            return log
        held = ", ".join(sorted(d()["search_log"]))
        if period > period_of(st.settings.retailer_today):
            raise conflict(f"The period {period} has not ended, so its search log is not complete. Nothing was changed. "
                           f"The search log holds {held}.")
        raise not_found("search log for the period", period, f"The search log holds {held}.")

    sku_p = Path(..., description="Line id, for example AG-4407.")
    period_p = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")

    # ------------------------------------------------------------ listings and specifications
    @reg(app, "get", "/listings", "list_product_listings", "List product listings",
         f"List the listings of the online shop, in order of line id. Each row has {LISTING_FIELDS}. Filters are optional and "
         "add up: category, status and new_product. The answer has count. Read the supplier's specification of a line with "
         "get_supplier_specification. This system holds no images.")
    def list_product_listings(category: Category | None = Query(None, description="Only listings of this category."),
                              status: Literal["live", "awaiting_description"] | None = Query(None, description="Only listings with this status."),
                              new_product: bool | None = Query(None, description="true: only the new products. false: only the others.")):
        rows = [shown(x) for x in d()["catalogue_products"].values()
                if (not category or x["category"] == category) and (not status or x["status"] == status)
                and (new_product is None or x["new_product"] == new_product)]
        return listing(sorted(rows, key=lambda x: x["sku"]))

    @reg(app, "get", "/listings/{sku}", "get_product_listing", "Get one product listing",
         f"Read one listing: {LISTING_FIELDS}; description_drafts (every saved description draft, each a version with "
         "drafted_by, drafted_at, description, image_tags, the four attributes and differences_for_the_content_lead) and "
         "published (who published the description and when, empty until it is published). Find line ids with "
         "list_product_listings.")
    def get_product_listing(sku: str = sku_p):
        return {k: v for k, v in product_or_404(sku).items() if k != "image_descriptions"}

    @reg(app, "get", "/specifications/{sku}", "get_supplier_specification", "Get the supplier's specification of a line",
         f"Read the supplier's specification of one line: {SPEC_FIELDS}. The specification is what the supplier has signed. "
         "Where a listing and the specification differ, the specification is the one to go by, and a person corrects the "
         "listing. Find line ids with list_product_listings.")
    def get_supplier_specification(sku: str = sku_p):
        product_or_404(sku)
        return d()["supplier_specs"][sku]

    @reg(app, "get", "/style-guide", "get_product_style_guide", "Get the product style guide",
         "Read the style guide for product descriptions: document, version, owner, minimum_words and maximum_words (a "
         "description is 40 to 80 words), minimum_image_tags and maximum_image_tags (three to six), words_not_used, "
         "closing_sentence_for_age_restricted_lines, rules (each with rule_id PS-1 to PS-10, title and text), "
         "what_the_guide_does_not_decide and text (the whole guide as one document).")
    def get_product_style_guide():
        return STYLE_GUIDE

    @reg(app, "get", "/new-products", "list_new_products", "List new products with their image descriptions",
         "List the new products, newest first. Each row has sku, name, brand, category, status (awaiting_description when it "
         "has no description yet, live when it has), listed_on, age_restricted, image_descriptions (each image as a "
         "description in words, written by the photo studio) and description_drafts (how many are saved). The answer has "
         "images_note: this system holds no images, so nobody reading an image description has seen the picture. The filter "
         "status is optional. Read the facts of a product with get_supplier_specification.")
    def list_new_products(status: Literal["live", "awaiting_description"] | None = Query(None, description="Only new products with this status.")):
        rows = [{"sku": x["sku"], "name": x["name"], "brand": x["brand"], "category": x["category"], "status": x["status"],
                 "listed_on": x["listed_on"], "age_restricted": x["age_restricted"],
                 "image_descriptions": x["image_descriptions"], "description_drafts": len(x["description_drafts"])}
                for x in d()["catalogue_products"].values() if x["new_product"] and (not status or x["status"] == status)]
        return listing(sorted(rows, key=lambda x: (x["listed_on"], x["sku"]), reverse=True), images_note=IMAGES_NOTE)

    @reg(app, "post", "/listings/{sku}/description", "save_product_description", "Save a product description (draft)",
         "Save a description and image tags for one new product that has no description yet, as a draft. It publishes "
         "nothing and changes no status. Each call is kept as a new version with who wrote it and when. Send description, "
         "image_tags, net_quantity, pack_size, allergen_statement, country_of_origin, differences_for_the_content_lead and "
         "drafted_by. Refused with 422, with the reason: a description shorter than 40 words or longer than 80; a word the "
         "style guide rules out; fewer than three or more than six image tags, or a tag that is not in lower case; a net "
         "quantity, pack size, allergen statement or country of origin that is not exactly what the supplier's "
         "specification gives; and an age-restricted line whose description does not end with the sentence the style guide "
         "gives. Refused with 409 when the product already has a published description. A content lead publishes every "
         "description. Returns the saved version.")
    def save_product_description(body: DescriptionDraft, sku: str = sku_p):
        x = product_or_404(sku)
        if x["status"] != "awaiting_description":
            raise conflict(f"{sku} already has a published description. Nothing was saved. list_new_products with the status "
                           "awaiting_description gives the products that have none.")
        spec = d()["supplier_specs"][sku]
        count = len(words(body.description))
        if not MIN_WORDS <= count <= MAX_WORDS:
            raise HTTPException(422, f"The description has {count} words. The style guide asks for {MIN_WORDS} to {MAX_WORDS}. "
                                     "Nothing was saved.")
        used = [w for w in BANNED_WORDS if re.search(rf"\b{re.escape(w)}\b", body.description, re.I)]
        if used:
            raise HTTPException(422, f"The description uses a word the style guide rules out: {', '.join(used)}. Nothing was saved.")
        tags = [t for t in body.image_tags if t.strip()]
        if not MIN_TAGS <= len(tags) <= MAX_TAGS or any(t != t.lower() for t in tags):
            raise HTTPException(422, f"Send {MIN_TAGS} to {MAX_TAGS} image tags, each in lower case. Nothing was saved.")
        for attribute in ATTRIBUTES:
            if getattr(body, attribute).strip() != spec[attribute]:
                raise HTTPException(422, f"{attribute} is not what the supplier's specification gives. Nothing was saved. Read "
                                         "the specification with get_supplier_specification and copy the value exactly.")
        if x["age_restricted"] and not body.description.strip().endswith(ADULT_SENTENCE):
            raise HTTPException(422, f"{sku} is an age-restricted line. Its description ends with the sentence: "
                                     f"{ADULT_SENTENCE} Nothing was saved.")
        payload = {"description": body.description.strip(), "image_tags": tags, "net_quantity": spec["net_quantity"],
                   "pack_size": spec["pack_size"], "allergen_statement": spec["allergen_statement"],
                   "country_of_origin": spec["country_of_origin"], "words": count,
                   "differences_for_the_content_lead": list(body.differences_for_the_content_lead)}
        v = st.add_draft(x, "description_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "listing_status": x["status"]}

    @reg(app, "post", "/listings/{sku}/description/publish", "publish_product_description", "Publish a product description (change)",
         "Publish the latest saved description of one new product. This is a change: the listing takes the description, the "
         "image tags and the four attributes of the draft, and its status becomes live. Needs published_by. Refused with "
         "409 until a description has been saved with save_product_description, and when the product already has a "
         "published description.")
    def publish_product_description(body: PublishBody, sku: str = sku_p):
        x = product_or_404(sku)
        with st.lock:
            if x["status"] != "awaiting_description":
                who = f" by {x['published']['published_by']}" if x["published"] else ""
                raise conflict(f"The description of {sku} was already published{who}. Nothing was changed.")
            if not x["description_drafts"]:
                raise conflict(f"No description is saved for {sku}. Nothing was changed. Use save_product_description first.")
            draft = x["description_drafts"][-1]
            x["description"], x["image_tags"] = draft["description"], list(draft["image_tags"])
            for attribute in ATTRIBUTES:
                x["attributes"][attribute] = draft[attribute]
            x["status"] = "live"
            x["published"] = {"published_by": body.published_by, "published_at": now_iso(), "version": draft["version"],
                              "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "live", "listing": shown(x)}

    # ------------------------------------------------------------ the data check
    @reg(app, "get", "/data-checks", "get_product_data_checks", "Get the saved product data checks",
         "Read every product data check saved, oldest first. Fields: count and checks, a list of versions, each with "
         "version, drafted_by, drafted_at, category (empty for every listing), findings (sku, attribute, kind, "
         "listing_value, specification_value) and summary. The list is empty when nothing was saved.")
    def get_product_data_checks():
        checks = d()["product_data_checks"]["checks"]
        return {"count": len(checks), "checks": checks}

    @reg(app, "post", "/data-checks", "save_product_data_check", "Save a product data check (draft)",
         "Save the result of setting listings against their suppliers' specifications, as a draft. It changes no listing. "
         "Each call is kept as a new version with who wrote it and when. Send findings (each with sku, attribute, kind, "
         "listing_value and specification_value; an empty list when nothing was found), an optional category, an optional "
         "summary and drafted_by. attribute is net_quantity, pack_size, allergen_statement or country_of_origin. kind is "
         "missing or does_not_match. An unknown sku or category is refused with 404. Refused with 422: the same sku and "
         "attribute listed twice; missing with a listing_value; does_not_match with no listing_value; and a sku outside the "
         "category when a category is given. A content lead corrects every listing. Returns the saved version.")
    def save_product_data_check(body: DataCheck):
        if body.category and body.category not in CATEGORIES:
            raise not_found("category", body.category, f"Nothing was saved. The categories are: {', '.join(CATEGORIES)}.")
        seen = set()
        for f in body.findings:
            x = d()["catalogue_products"].get(f.sku)
            if not x:
                raise not_found("product listing", f.sku, "Nothing was saved. Use list_product_listings to find line ids.")
            if body.category and x["category"] != body.category:
                raise HTTPException(422, f"{f.sku} is in the category {x['category']}, not {body.category}. Nothing was saved.")
            if (f.sku, f.attribute) in seen:
                raise HTTPException(422, f"{f.sku} is listed twice for {f.attribute}. Nothing was saved. List each attribute "
                                         "of a line once.")
            seen.add((f.sku, f.attribute))
            if f.kind == "missing" and f.listing_value.strip():
                raise HTTPException(422, f"{f.sku} {f.attribute}: missing goes with an empty listing_value. Use does_not_match "
                                         "when the listing has a value that differs. Nothing was saved.")
            if f.kind == "does_not_match" and not f.listing_value.strip():
                raise HTTPException(422, f"{f.sku} {f.attribute}: does_not_match needs the listing_value. Use missing when the "
                                         "listing has nothing there. Nothing was saved.")
        payload = {"category": body.category, "findings": [f.model_dump() for f in body.findings], "summary": body.summary}
        v = st.add_draft(d()["product_data_checks"], "checks", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    # ------------------------------------------------------------ the search log
    @reg(app, "get", "/search-log/{period}", "get_search_log", "Get the shop's search log for a month",
         "Read what shoppers typed into the online shop's search box in one month. Fields: period, count, total_searches "
         "and rows, most searched first, each with term (as typed, in lower case), searches (how many times) and "
         "results_found (how many listings the search returned; 0 means the shopper found nothing). Set no_results to true "
         "for only the terms that found nothing. A month that has not ended is refused with 409, and a month with no log "
         "with 404.")
    def get_search_log(period: str = period_p,
                       no_results: bool = Query(False, description="true: only the terms that found nothing.")):
        rows = [r for r in log_or_error(period)["rows"] if not no_results or r["results_found"] == 0]
        return {"period": period, "count": len(rows), "total_searches": sum(r["searches"] for r in rows), "rows": rows}

    @reg(app, "get", "/search-log/{period}/analysis", "get_search_terms_analysis", "Get the saved search terms analyses for a month",
         "Read every search terms analysis saved for one month, oldest first. Fields: period, count and analyses, a list of "
         "versions, each with version, drafted_by, drafted_at, groups (name, what_shoppers_seemed_to_want, terms with "
         "their searches, and total_searches), total_searches and summary. The list is empty when nothing was saved.")
    def get_search_terms_analysis(period: str = period_p):
        item = d()["search_analyses"].get(period, {"analyses": []})
        return {"period": period, "count": len(item["analyses"]), "analyses": item["analyses"]}

    @reg(app, "post", "/search-log/{period}/analysis", "save_search_terms_analysis", "Save a search terms analysis for a month (draft)",
         "Save a grouping of the search terms that found nothing in one month, as a draft. It changes nothing in the shop. "
         "Each call is kept as a new version with who wrote it and when. Send groups (each with name, "
         "what_shoppers_seemed_to_want and terms), an optional summary and drafted_by. Write each term exactly as the "
         "search log gives it. The answer adds the searches of each term and the total of each group, taken from the log. "
         "A term that is not in the month's log is refused with 404. Refused with 422: a term that found results, and a "
         "term in two groups. A month that has not ended is refused with 409. The e-commerce team decides what to change. "
         "Returns the saved version.")
    def save_search_terms_analysis(body: TermsAnalysis, period: str = period_p):
        by_term = {r["term"]: r for r in log_or_error(period)["rows"]}
        seen, groups = set(), []
        for g in body.groups:
            rows = []
            for term in g.terms:
                key = term.strip().lower()
                if key not in by_term:
                    raise not_found(f"search term in the log for {period}", term, "Nothing was saved. Write each term as "
                                    "get_search_log gives it.")
                if by_term[key]["results_found"] > 0:
                    raise HTTPException(422, f"'{key}' found {by_term[key]['results_found']} results, so it is not a term that "
                                             "found nothing. Nothing was saved.")
                if key in seen:
                    raise HTTPException(422, f"'{key}' is in two groups. Nothing was saved. Put each term in one group.")
                seen.add(key)
                rows.append({"term": key, "searches": by_term[key]["searches"]})
            groups.append({"name": g.name, "what_shoppers_seemed_to_want": g.what_shoppers_seemed_to_want, "terms": rows,
                           "total_searches": sum(r["searches"] for r in rows)})
        payload = {"groups": groups, "total_searches": sum(g["total_searches"] for g in groups), "summary": body.summary}
        with st.lock:
            item = d()["search_analyses"].setdefault(period, {"period": period, "analyses": []})
            v = st.add_draft(item, "analyses", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "period": period}

    return app
