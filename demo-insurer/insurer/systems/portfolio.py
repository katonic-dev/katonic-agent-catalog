"""Portfolio: the product catalogue with what depends on each section and rating factor, proposed product changes, the
experience of each pricing segment with the pricing method, and the exposure warehouse with the concentration limits.

Three chat agents read it for the insurer's own product, pricing and risk staff. Nothing here changes a product, a rate or a
record. The one save is a question for a person, kept as a draft."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query, Request
from pydantic import Field

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg
from ..seed_portfolio import (BAND_WORDS, CATALOGUE_HOW_TO_READ, CATALOGUE_NEVER_HOLDS, CHANGE_KINDS, EXPERIENCE_SPLIT, FIELD_NOTES,
                              FIELDS, FULL_CREDIBILITY_CLAIMS, ITEM_KINDS, LIMITS_HOW_TO_READ, MEASURES, NOT_HELD,
                              PRICING_ASSUMPTIONS, PRICING_HOW_TO_READ, PROFIT_MARGIN_PERCENT, RELIABLE_FROM_CLAIMS, Refused,
                              change_impact, exposure_query, experience_years, measure_limit, parse_years, premium_change,
                              rating_year, search_catalogue, segment_experience, warehouse_as_at, what_refers_to)
from ..store import now_iso

KEY = "portfolio"
TITLE = "Portfolio"
LINE = ("The product catalogue with what depends on each section and rating factor, proposed product changes, the experience of "
        "each pricing segment with the pricing method, and the exposure warehouse with the concentration limits.")

QUERY_PARAMS = {"measure", "group_by", "product", "region", "construction_class", "vehicle_class", "sum_insured_band", "other_field"}


class QuestionForAPerson(ForgivingModel):
    topic: Literal["product_change", "pricing", "portfolio_exposure"] = Field(
        ..., description="What the question is about: product_change for a proposed change to a product, pricing for a loss ratio "
                         "or a premium change, portfolio_exposure for the warehouse or a concentration limit.")
    about: str = Field("", description="The id of the record the question is about, where there is one: a proposed change "
                                       "(PCR-8503), a product (PRD-8303), a dependent item (DEP-8426), a pricing segment (SEG-8604) "
                                       "or a concentration limit (LIM-2). Leave empty when the question is about no single record.")
    question: str = Field(..., min_length=1, description="The question, in one or two sentences, as the person who answers it should "
                                                         "read it.")
    why_the_system_does_not_settle_it: str = Field(
        ..., min_length=1, description="What was read and why it does not answer the question: what the catalogue, the experience or "
                                       "the warehouse holds, and what it does not hold. Give the figures the system returned.")
    for_whom: str = Field("", description="The role or the person the question is for, as the system names them, for example the "
                                          "pricing actuary or Marguerite Tolland, reinsurance manager. Leave empty when the system "
                                          "names nobody.")
    drafted_by: str = Field("agent", description="Who wrote the note. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the product catalogue (products, their wordings by section, their rating "
                                  "factors, and the documents and systems that depend on each), proposed product changes, the "
                                  "experience of each pricing segment with the pricing method, and the exposure warehouse with the "
                                  "concentration limits. The system does every sum, ratio and comparison and returns its working. "
                                  "Nothing here changes a product, a rate, a limit or a policy. The one save is a question for a "
                                  "person, stored as a draft.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today
    as_at = lambda: warehouse_as_at(today())
    years = lambda: experience_years(today())
    prd_p = Path(..., description="Product id, for example PRD-8303.")
    pcr_p = Path(..., description="Proposed change id, for example PCR-8501.")
    seg_p = Path(..., description="Pricing segment id, for example SEG-8601.")
    tgt_p = Path(..., description="The id of a clause (SEC-8303-4.1), of a section as a whole (SEC-8303-4) or of a rating factor "
                                  "(FAC-8303-5). get_product lists them.")
    years_q = Query(None, description="The accident years to read, for example 2024,2025 or 2024-2025. Leave empty for every year "
                                      "held.")

    def one(name, kind, ident, hint):
        item = d()[name].get((ident or "").strip().upper())
        if not item:
            raise not_found(kind, ident, hint)
        return item

    def refuse(call):
        try:
            return call()
        except Refused as exc:
            raise conflict(str(exc))

    def segment_or_404(segment_id):
        return one("pf_segments", "pricing segment", segment_id,
                   f"The segments are {', '.join(d()['pf_segments'])}. {EXPERIENCE_SPLIT} Nothing was worked out.")

    def notes_about(ident):
        return sum(1 for q in d()["pf_questions"].values() if q["about"] == ident)

    # ------------------------------------------------------------ the product catalogue
    def items_of(product_id):
        return [i for i in d()["pf_items"].values() if i["product_id"] == product_id]

    def product_brief(p):
        clauses = [s for s in p["sections"] if s["kind"] == "clause"]
        kinds = [i["kind"] for i in items_of(p["product_id"])]
        return {"product_id": p["product_id"], "name": p["name"], "line_of_business": p["line_of_business"], "status": p["status"],
                "wording": p["wording"],
                "sections": [{"section_id": s["section_id"], "heading": s["heading"]} for s in p["sections"] if s["kind"] == "section"],
                "clauses": len(clauses), "rating_factors": [{"factor_id": f["factor_id"], "name": f["name"]} for f in p["rating_factors"]],
                "dependent_items": len(kinds), "dependent_items_by_kind": {k: kinds.count(k) for k in ITEM_KINDS if k in kinds}}

    @reg(app, "get", "/products", "list_catalogue_products", "List the products of the catalogue",
         "List the products the catalogue holds: id, name, line of business, the wording with its id and where it is held, the "
         "sections of the wording by id and heading, the number of clauses, the rating factors by id and name, and how many "
         "dependent items the product has of each kind (schedule template, rating table, claims checklist, broker or member guide, "
         "regulatory filing, reinsurance treaty note, underwriting guideline, system). how_to_read explains the ids and the "
         "relations. the_catalogue_never_holds lists what no read of the catalogue can answer: rates, the text of a filing or a "
         "treaty, policies and customers, decisions. For one product with every clause and every reference, use get_product.")
    def list_catalogue_products():
        return listing([product_brief(p) for p in d()["pf_products"].values()], document="Product catalogue",
                       how_to_read=CATALOGUE_HOW_TO_READ, the_catalogue_never_holds=CATALOGUE_NEVER_HOLDS)

    @reg(app, "get", "/products/{product_id}", "get_product", "Get one product with its wording, rating factors and dependent items",
         "Read one product whole, in one call. sections gives the wording: one row for each section as a whole (SEC-8303-4) and one "
         "for each clause (SEC-8303-4.1) with its heading and exact text; for group medical the rows are the table of benefits. "
         "rating_factors gives each factor with its id, name, levels and the wording clauses that name the same thing. "
         "dependent_items gives every document and system that depends on the product: id (DEP-..), kind, name, reference, owner, "
         "what the catalogue holds about it and what it does not hold, what happens on a change, and refers_to: one reference for "
         "each clause, section or factor it refers to, with the relation (quotes, uses, relies_on, lists or is_filed), what it says, "
         "the figures it quotes and, for a section as a whole, when the reference applies. An underwriting guideline is given as the "
         "underwriting system holds it. The catalogue holds no rates and no text of a filing or a treaty. To ask what refers to one "
         "clause or factor, use get_what_refers_to.")
    def get_product(product_id: str = prd_p):
        p = one("pf_products", "product", product_id, "Use list_catalogue_products to find ids.")
        return {**p, "dependent_items": items_of(p["product_id"]), "how_to_read": CATALOGUE_HOW_TO_READ,
                "the_catalogue_never_holds": CATALOGUE_NEVER_HOLDS,
                "proposed_changes": [c["change_id"] for c in d()["pf_change_requests"].values() if c["product_id"] == p["product_id"]]}

    @reg(app, "get", "/references/{target_id}", "get_what_refers_to", "Get what refers to a clause, a section or a rating factor",
         "The dependency read. For one clause, one section as a whole or one rating factor it says what else refers to it. target "
         "gives the clause or factor with its text. items_that_refer_to_it gives one row for each dependent item that names it: id, "
         "kind, name, reference, owner, what happens on a change, and the references with the relation, what each says and the "
         "figures quoted. For a clause, items_that_refer_to_its_section_as_a_whole gives the items that refer to the section it "
         "sits in, each with applies_when: on any change to a clause of the section, or only when a clause is added or removed. For "
         "a section, items_that_refer_to_a_clause_of_it lists the references to its clauses. For a rating factor, "
         "wording_clauses_that_name_it gives the clauses that use the same figure. items_of_the_product_that_do_not_refer_to_it "
         "lists the rest, counts gives the numbers, and sentence says it in words. When nothing refers to it the answer says so: "
         "then only the wording itself changes. It reads only the catalogue: it does not say what a change would cost or whether it "
         "is allowed.")
    def get_what_refers_to(target_id: str = tgt_p):
        found = what_refers_to(d(), target_id.strip())
        if not found:
            raise not_found("clause, section or rating factor", target_id, "Ids look like SEC-8303-4.1, SEC-8303-4 or FAC-8303-5. "
                            "get_product lists the ids of a product.")
        return found

    @reg(app, "get", "/catalogue/search", "search_product_catalogue", "Search the product catalogue by words",
         "Find the clauses, rating factors and dependent items that name any word of the text, for example flood, deductible or "
         "glass. Any word may match, in any order; common words are left out. Each row gives the kind (clause, rating_factor or the "
         "kind of the dependent item), the id, the product, a heading, the text and the words that matched; rows with the most "
         "matching words come first. With no text everything is listed. When nothing matches the answer says so: the catalogue is "
         "then silent on those words. A word can match for another product: check product_id before you rely on a row.")
    def search_product_catalogue(text: str | None = Query(None, description="Words to look for, for example flood exclusion. Leave "
                                                                            "empty to list everything.")):
        return search_catalogue(d(), text or "")

    def change_brief(c):
        return {**c, "product": d()["pf_products"][c["product_id"]]["name"]}

    @reg(app, "get", "/proposed-changes", "list_proposed_product_changes", "List the proposed product changes",
         "List the proposed product changes, whole: id, status (proposed), the date received, who proposed it with role, the "
         "product, the kind of change (change_a_figure, add_a_clause, remove_a_clause, reword_a_clause or change_a_rating_factor), a "
         "title, the proposal's text, the clauses, sections or rating factors it names (targets), the current and the proposed "
         "figure where it changes one, and the new term where it adds something. What each change touches is not in the list: "
         "get_proposed_product_change works it out. Saved questions are not in the list.")
    def list_proposed_product_changes():
        return listing([change_brief(c) for c in d()["pf_change_requests"].values()], kinds_of_change=CHANGE_KINDS)

    @reg(app, "get", "/proposed-changes/{change_id}", "get_proposed_product_change",
         "Get one proposed product change with what it touches",
         "Read one proposed product change with what it touches, worked out by the system from the references of the catalogue, in "
         "one call. impact.targets gives each clause, section or factor the proposal names, with its text. the_wording_itself names "
         "the wording that changes. items_touched has one row for each dependent item the change reaches: id, kind, name, owner, "
         "what happens on a change, and the references that make it so, each with the relation, what it says, the figures it quotes "
         "and quotes_the_current_figure (true when the item repeats the figure that would change). items_of_the_product_not_touched "
         "lists the items no reference connects to the change. items_that_rely_on_what_is_changed names the items built on the "
         "clause staying as it is: a conflict to raise. wording_clauses_that_name_the_same_thing gives clauses the proposal does not "
         "name but that use the same figure. the_new_term_in_the_catalogue, for an added clause, says whether anything in the "
         "product names the new thing, and whether another product does. what_the_catalogue_cannot_say lists each question the "
         "catalogue cannot answer, with the item it comes from and who owns it: give these as open questions and do not answer them. "
         "counts gives the numbers and sentence says it in words. Use these lists and counts as they are. The system approves "
         "nothing and prices nothing. Saved questions are not part of the change: questions_on_file only counts them, and "
         "list_portfolio_questions_for_a_person reads them.")
    def get_proposed_product_change(change_id: str = pcr_p):
        c = one("pf_change_requests", "proposed change", change_id, "Use list_proposed_product_changes to find ids.")
        return {**change_brief(c), "impact": change_impact(d(), c), "the_catalogue_never_holds": CATALOGUE_NEVER_HOLDS,
                "questions_on_file": notes_about(c["change_id"]), "read_on": today().isoformat()}

    # ------------------------------------------------------------ pricing
    @reg(app, "get", "/pricing-method", "get_pricing_method", "Get the pricing method as numbered rules, with the assumptions",
         "Read the pricing method: the rules PM-1 to PM-8 with their exact text (loss ratio, the experience that is read, claims "
         "trend, target loss ratio, premium change needed, target already met, credibility, who decides), and "
         "default_assumptions_by_product: the claims trend and the expense ratio the method uses for each product when a question "
         "gives none, with the profit margin and the target loss ratio that follows. It also gives the accident years held, the "
         "year the new rates apply, the number of claims for full credibility and the number below which a segment is too thin. It "
         "works out nothing for a segment: calculate_premium_change_for_target_loss_ratio does.")
    def get_pricing_method():
        defaults = {p: {**a, "profit_margin_percent": PROFIT_MARGIN_PERCENT,
                        "target_loss_ratio_percent_when_none_is_given": 100.0 - a["expense_ratio_percent"] - PROFIT_MARGIN_PERCENT}
                    for p, a in PRICING_ASSUMPTIONS.items()}
        return {"document": "Pricing method", "version": "6", "how_to_read": PRICING_HOW_TO_READ,
                "rules": list(d()["pf_pricing_method"].values()), "default_assumptions_by_product": defaults,
                "accident_years_held": years(), "rating_year": rating_year(today()),
                "claims_for_full_credibility": FULL_CREDIBILITY_CLAIMS, "claims_needed_to_rely_on_a_figure": RELIABLE_FROM_CLAIMS,
                "how_the_experience_is_split": EXPERIENCE_SPLIT}

    @reg(app, "get", "/segments", "list_pricing_segments", "List the pricing segments with their experience",
         "List the pricing segments, whole: id, name, product, the unit of exposure (vehicle years or policy years), a note where "
         "there is one, and the experience of every accident year held: earned premium, incurred claims, number of claims and "
         "exposure, with the loss ratio of each year, and the totals with the loss ratio of the years together and the credibility. "
         "how_the_experience_is_split says what the experience can and cannot be split by: a question about a split it does not "
         "hold, or about a year that is not held, cannot be answered from it. Every ratio is worked out by the system.")
    def list_pricing_segments():
        return listing([segment_experience(s, years()) for s in d()["pf_segments"].values()], accident_years_held=years(),
                       how_the_experience_is_split=EXPERIENCE_SPLIT)

    @reg(app, "get", "/segments/{segment_id}/experience", "get_segment_experience",
         "Get the experience and the loss ratios of one pricing segment",
         "Read the experience of one segment and its loss ratios, worked out by the system. by_year has one row for each accident "
         "year read: earned premium, incurred claims, number of claims, exposure, loss_ratio_percent, claims for every 100 units of "
         "exposure, the average cost of a claim, the average premium, and the working as a sentence. totals gives the same for the "
         "years together, with the working. credibility gives the number of claims, the number the method needs, the credibility "
         "figure, whether the figures can be relied on, and a sentence. With years, only those accident years are read. Refused "
         "with 409 and a plain sentence for a year that is not held: no figure is estimated. It saves nothing.")
    def get_segment_experience(segment_id: str = seg_p, years_to_read: str | None = years_q):
        seg = segment_or_404(segment_id)
        return {**segment_experience(seg, refuse(lambda: parse_years(years_to_read, years()))), "accident_years_held": years(),
                "how_the_experience_is_split": EXPERIENCE_SPLIT, "saved": False}

    @reg(app, "get", "/segments/{segment_id}/credibility", "check_segment_credibility",
         "Check whether a pricing segment has enough claims to rely on",
         "Work out the credibility of one segment under rule PM-7: the number of claims in the years read, the number for full "
         "credibility, the number needed to rely on a figure, the credibility (the square root of claims over the full number, "
         "never above 1), the threshold of 0.50, reliable as true or false, how many claims short the segment is, and a sentence. A "
         "segment exactly on the number needed is reliable. A segment that is not reliable is too thin: say so, give the reason, and "
         "do not present its premium change as a finding. Refused with 409 for a year that is not held. It saves nothing.")
    def check_segment_credibility(segment_id: str = seg_p, years_to_read: str | None = years_q):
        seg = segment_or_404(segment_id)
        seen = segment_experience(seg, refuse(lambda: parse_years(years_to_read, years())))
        return {"segment_id": seg["segment_id"], "segment": seg["name"], "years_read": seen["years_read"], **seen["credibility"],
                "saved": False}

    @reg(app, "get", "/segments/{segment_id}/premium-change", "calculate_premium_change_for_target_loss_ratio",
         "Work out the premium change that holds a target loss ratio",
         "Work out, for one segment, the premium change needed to hold a target loss ratio, with every step shown. assumptions "
         "names each assumption with its value and where it came from: the target loss ratio (given, or worked out from the expense "
         "ratio and the profit margin), the expense ratio, the claims trend, the profit margin, the years read, the rating year and "
         "the years of trend. Then: the experience totals, trend_factor, trended_incurred_claims, trended_loss_ratio_percent, "
         "target_already_met with the points below or above the target, premium_change_on_these_figures_percent, "
         "premium_change_to_rely_on_percent (empty when the segment is too thin), premium_needed_for_the_same_exposure, reliable "
         "with the credibility, the combined ratio at the target with a note when claims and expenses would take more than the "
         "premium, working as a list of sentences, sensitivity (the change at a target 5 points either side and a trend 2 points "
         "either side), and a sentence. When the target is already met the change is 0.00: the method works out no decrease. When "
         "reliable is false the figure is not reliable alone: say so with the number of claims and the number needed. Give the "
         "assumptions with every answer. Refused with 409 and a plain sentence for a year that is not held or a value outside what "
         "the method works with. It changes no rate and saves nothing.")
    def calculate_premium_change_for_target_loss_ratio(
            segment_id: str = seg_p,
            target_loss_ratio_percent: float | None = Query(None, description="The loss ratio to hold, as a percentage, for example "
                                                            "70. Leave empty to use 100 less the expense ratio less the profit "
                                                            "margin."),
            expense_ratio_percent: float | None = Query(None, description="Expenses as a percentage of premium. Leave empty to use "
                                                        "the method's default for the product."),
            claims_trend_percent: float | None = Query(None, description="The yearly rise in claims cost, as a percentage. Leave "
                                                       "empty to use the method's default for the product."),
            years_to_read: str | None = years_q):
        seg = segment_or_404(segment_id)
        return {**refuse(lambda: premium_change(seg, today(), parse_years(years_to_read, years()), target_loss_ratio_percent,
                                                expense_ratio_percent, claims_trend_percent)), "saved": False}

    # ------------------------------------------------------------ the exposure warehouse
    def grand_totals():
        return {m: exposure_query(d(), as_at(), m)["total"] for m in ("policies_in_force", "total_sum_insured", "annual_premium")}

    @reg(app, "get", "/warehouse", "get_exposure_warehouse_guide", "Get what the exposure warehouse holds",
         "Read what the exposure warehouse holds, before a query. as_at is the date the policies in force are counted on. fields "
         "gives each field a query can group or filter by, with its values and a note: product, region, construction_class "
         "(property only), vehicle_class (motor only) and sum_insured_band. measures gives the four measures: policies_in_force, "
         "total_sum_insured, annual_premium and average_sum_insured. not_held lists what the warehouse does not hold, for example "
         "the flood zone, a postcode, the occupancy, the policyholder, claims: a question that needs one of these cannot be answered "
         "from it. totals gives the whole portfolio and by_product each product, worked out by the system. It also says how to read "
         "a word such as property or motor that fits more than one product. For any figure by region, class or band, use "
         "run_exposure_query.")
    def get_exposure_warehouse_guide():
        by_product = {}
        for m in ("policies_in_force", "total_sum_insured", "annual_premium"):
            for row in exposure_query(d(), as_at(), m, "product")["rows"]:
                by_product.setdefault(row["product"], {})[m] = row["value"]
        return {"document": "Exposure warehouse", "as_at": as_at(), "rows_held": len(d()["pf_warehouse"]),
                "what_a_row_is": "One row is the policies in force of one product in one region, one construction or vehicle class "
                                 "and one sum insured band, with their number, total sum insured and annual premium.",
                "fields": [{"field": f, "values": v, "note": FIELD_NOTES[f]} for f, v in FIELDS.items()],
                "sum_insured_bands_in_words": BAND_WORDS, "measures": MEASURES,
                "not_held": sorted(set(NOT_HELD.values())),
                "words_with_two_readings": "property can mean home and commercial_property together, or one of them. motor can mean "
                                           "private_motor and motor_fleet together, or one of them. exposure can mean the total sum "
                                           "insured or the number of policies. Where a question does not say, choose one reading, "
                                           "say which one you took, and give the other where it helps.",
                "totals": grand_totals(), "by_product": by_product}

    @reg(app, "get", "/warehouse/query", "run_exposure_query", "Run one structured query on the exposure warehouse",
         "Run one query on the exposure warehouse and get the rows, the total and the query as run. Choose one measure "
         "(policies_in_force, total_sum_insured, annual_premium or average_sum_insured), up to two fields to group by, and filters "
         "from the fixed lists; a filter may hold several values separated by commas. The answer gives query (the measure, the "
         "grouping, the filters and the as-at date as the system read them), query_in_words (one sentence to show the user), rows "
         "(one for each group, with the value and its share of the total as a percentage), total, the number of warehouse rows read "
         "and notes. Show query_in_words with every figure you give. No rows means zero: the warehouse holds no policy of that "
         "kind. Refused with 409 and a plain sentence, and nothing read, when the measure, a field or a value is not one the "
         "warehouse holds: then the warehouse cannot answer, and no figure is estimated. A word that fits two products, such as "
         "property, is refused with the two readings named. It is not free SQL and it saves nothing.")
    def run_exposure_query(
            request: Request,
            measure: str = Query(..., description="One of: policies_in_force, total_sum_insured, annual_premium, average_sum_insured."),
            group_by: str | None = Query(None, description="Up to two fields, separated by a comma, from: product, region, "
                                                           "construction_class, vehicle_class, sum_insured_band. Leave empty for "
                                                           "one figure."),
            product: str | None = Query(None, description="home, commercial_property, private_motor or motor_fleet. Several: "
                                                          "home,commercial_property."),
            region: str | None = Query(None, description="Port Ilvane, Marlow Reach, Tallowby or Saltmarsh Coast."),
            construction_class: str | None = Query(None, description="A, B or C. Property products only."),
            vehicle_class: str | None = Query(None, description="car, van or light_truck. Motor products only."),
            sum_insured_band: str | None = Query(None, description="up_to_250000, 250001_to_1000000, 1000001_to_2500000 or "
                                                                   "over_2500000."),
            other_field: str | None = Query(None, description="Any other field the question needs that is not in this list, by "
                                                              "name, for example flood_zone. The system then says whether the "
                                                              "warehouse holds it. Leave empty otherwise.")):
        def run():
            unknown = [k for k in request.query_params if k not in QUERY_PARAMS]
            for name in unknown + [x.split("=")[0] for x in (other_field or "").replace(";", ",").split(",") if x.strip()]:
                exposure_query(d(), as_at(), "policies_in_force", name.strip())  # says whether the warehouse holds the field
                raise Refused(f"{name.strip()} is a field of the warehouse: send it as its own filter or in group_by, not as "
                              "other_field. Nothing was read.")
            return exposure_query(d(), as_at(), measure, group_by,
                                  {"product": product, "region": region, "construction_class": construction_class,
                                   "vehicle_class": vehicle_class, "sum_insured_band": sum_insured_band})
        return {**refuse(run), "saved": False}

    def limit_view(limit):
        return {k: limit[k] for k in ("limit_id", "heading", "text")} | {
            "unit": "USD" if limit["kind"] == "amount" else "percent", "limit": limit["limit"]}

    @reg(app, "get", "/concentration-limits", "get_concentration_limits", "Get the concentration limits as numbered rules",
         "Read the insurer's concentration limits LIM-1 to LIM-6, each with its id, a heading, its exact text, the unit (percent or "
         "USD) and the limit as a figure. how_to_read says who sets them, that a value exactly on a limit is within it, and who is "
         "told when one is passed. It measures nothing: measure_portfolio_against_concentration_limits does.")
    def get_concentration_limits():
        return listing([limit_view(x) for x in d()["pf_limits"].values()], document="Concentration limits", version="3",
                       how_to_read=LIMITS_HOW_TO_READ)

    @reg(app, "get", "/concentration-limits/measure", "measure_portfolio_against_concentration_limits",
         "Measure the portfolio against the concentration limits",
         "Measure the warehouse against every concentration limit, or against one. For each limit the answer gives its text, the "
         "unit, measured, limit, result (within or over), exactly_on_the_limit, how far over or how much room is left (in points "
         "and as an amount for a share, as an amount for an amount limit), what it was measured for (the region or product with the "
         "largest share, where the limit speaks of any one), every value measured, the queries run in words, and a sentence. A "
         "value exactly on a limit is within it. limits_over and limits_exactly_on name the ids. Use these results and do not "
         "compare figures yourself. Over a limit is a fact for the chief risk officer: nothing here declines or cancels a policy. "
         "It saves nothing.")
    def measure_portfolio_against_concentration_limits(
            limit_id: str | None = Query(None, description="One limit, for example LIM-2. Leave empty for every limit.")):
        wanted = (limit_id or "").strip().upper()
        limits = d()["pf_limits"]
        if wanted and wanted not in limits:
            raise not_found("concentration limit", limit_id, f"The limits are {', '.join(limits)}.")
        rows = [measure_limit(d(), as_at(), x) for x in limits.values() if not wanted or x["limit_id"] == wanted]
        return listing(rows, as_at=as_at(), limits_over=[r["limit_id"] for r in rows if r["result"] == "over"],
                       limits_exactly_on=[r["limit_id"] for r in rows if r["exactly_on_the_limit"]],
                       limits_within=[r["limit_id"] for r in rows if r["result"] == "within"], how_to_read=LIMITS_HOW_TO_READ,
                       saved=False)

    # ------------------------------------------------------------ a question for a person
    @reg(app, "get", "/questions", "list_portfolio_questions_for_a_person", "List the questions saved for a person",
         "Read every question saved for a person in this system, each with its id, the topic, the record it is about, the question, "
         "why the system does not settle it, who it is for, a version number, who wrote it and when. With about, only the questions "
         "on that record. A saved question is somebody's note, not a fact of any record and not an answer.")
    def list_portfolio_questions_for_a_person(about: str | None = Query(None, description="Only questions about this record, for "
                                                                                          "example PCR-8503. Leave empty for all.")):
        wanted = (about or "").strip().upper()
        return listing([q for q in d()["pf_questions"].values() if not wanted or q["about"] == wanted])

    @reg(app, "post", "/questions", "save_portfolio_question_for_a_person", "Save a question for a person (draft)",
         "Save one question that the catalogue, the experience or the warehouse does not settle, for a person to answer: the topic, "
         "the record it is about where there is one, the question, why the system does not settle it, and who it is for. This is a "
         "draft note: stored with an id, who wrote it, a time and version 1. It changes no product, no rate, no limit and no "
         "record, sends nothing and promises no answer by any time. Refused with 409, and nothing saved, when about names an id "
         "this system does not hold.")
    def save_portfolio_question_for_a_person(body: QuestionForAPerson):
        about = body.about.strip().upper()
        if about and about.lower() in ("none", "n/a", "na"):
            about = ""
        if about:
            held = set(d()["pf_products"]) | set(d()["pf_items"]) | set(d()["pf_change_requests"]) | set(d()["pf_segments"]) | set(
                d()["pf_limits"])
            if about not in held and not what_refers_to(d(), body.about.strip()):
                raise conflict(f"{body.about} is not an id this system holds. Use a proposed change (PCR-..), a product (PRD-..), a "
                               "dependent item (DEP-..), a clause or factor (SEC-.., FAC-..), a pricing segment (SEG-..) or a "
                               "concentration limit (LIM-..), or leave about empty. Nothing was saved.")
        with st.lock:
            qid = st.next_free("portfolio_question", 8901, d()["pf_questions"], lambda n: f"QN-{n}")
            note = {"question_id": qid, "kind": "draft", "version": 1, "drafted_by": body.drafted_by or "agent",
                    "drafted_at": now_iso(), **body.model_dump(exclude={"drafted_by", "about"}), "about": about}
            d()["pf_questions"][qid] = note
            st.save()
        return {"applied": True, "kind": "draft", "draft": note,
                "message": f"The question is saved as {qid}, a draft note for a person. Nothing else is changed and nothing is sent."}

    return app
