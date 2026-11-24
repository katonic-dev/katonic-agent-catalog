"""Loyalty, version 1.3: members with their history, the personalisation rules, past campaigns and campaign briefs."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..seed_loyalty import BRIEF_TEMPLATE, MAX_SUGGESTIONS, PERSONALISATION_RULES, PROGRAMME

KEY = "loyalty"
TITLE = "Loyalty"
LINE = ("Members of the Rowanmere Market loyalty programme with their consent flags, purchases and browsing, the "
        "personalisation rules, past campaigns with results, and the campaign brief template.")

MEMBER_ROW = ("member_id, name, email, joined_on, personalisation_opt_in, marketing_email_opt_in, age_check_passed and "
              "excluded_categories")
CAMPAIGN_FIELDS = ("campaign_id, name, ran_in (YYYY-MM), audience, adults_only, channels, members_sent_to, redemptions, "
                   "redemption_percent, sales_attributed, cost, return_for_each_dollar (sales divided by cost) and note")
DATE_RE = r"^\d{4}-\d{2}-\d{2}$"


class Suggestion(BaseModel):
    sku: str = Field(..., min_length=1, description="The line suggested, for example AG-4402.")
    reason: str = Field(..., min_length=1, description="What the member's own history shows, for example 'viewed 5 times "
                                                       "in the last 30 days'. Nothing about the member as a person.")


class Blocked(BaseModel):
    sku: str = Field(..., min_length=1, description="A line the member viewed that a rule blocks.")
    rule: Literal["PZ-2", "PZ-3", "PZ-5"] = Field(..., description="The rule that blocks it: PZ-2, PZ-3 or PZ-5.")


class ProductSuggestions(BaseModel):
    suggestions: list[Suggestion] = Field(default_factory=list, max_length=MAX_SUGGESTIONS, description="At most five "
                                          "suggestions, in order. Empty when the member gets none.")
    blocked: list[Blocked] = Field(default_factory=list, description="Each line a rule took off, with the rule.")
    no_suggestion_reason: Literal["", "opted_out", "nothing_viewed_and_not_bought", "all_blocked_by_rules"] = Field(
        "", description="Needed when suggestions is empty, and empty otherwise. opted_out: the member has not opted in to "
                        "personalisation. nothing_viewed_and_not_bought: there is no candidate. all_blocked_by_rules: every "
                        "candidate was blocked.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Audience(BaseModel):
    segment: str = Field(..., min_length=1, description="Who the campaign is for, in plain words.")
    size: int = Field(..., gt=0, description="How many members that is. Never more than the programme's total of members "
                                             "opted in to the channel.")
    consent_basis: Literal["marketing_email_opt_in", "app_notifications_opt_in", "none_needed_in_store_or_on_the_website"] = Field(
        ..., description="The consent the audience rests on.")
    adults_only: bool = Field(False, description="true when the campaign goes only to members whose age check has been passed.")


class LastYear(BaseModel):
    campaign_id: str = Field(..., min_length=1, description="The past campaign most like this one, for example CP-2505.")
    what_it_showed: str = Field(..., min_length=1, description="Its figures as the records give them: members sent to, "
                                                               "redemptions, sales, cost and return for each dollar.")


class CampaignBrief(BaseModel):
    title: str = Field(..., min_length=1, description="The name of the campaign, in six words or fewer.")
    objective: str = Field(..., min_length=1, description="One sentence, with a number and a date.")
    audience: Audience
    offer: str = Field(..., min_length=1, description="What the member gets, on which lines, and for how long.")
    includes_age_restricted_lines: bool = Field(False, description="true when the offer includes an age-restricted line.")
    channels: list[Literal["email", "app", "in_store", "website"]] = Field(
        ..., min_length=1, description="The channels: email, app, in_store or website.")
    start_date: str = Field(..., pattern=DATE_RE, description="The first day, as YYYY-MM-DD.")
    end_date: str = Field(..., pattern=DATE_RE, description="The last day, as YYYY-MM-DD.")
    budget: float = Field(..., gt=0, description="The whole cost in US dollars.")
    measures_of_success: list[str] = Field(..., min_length=1, description="What will be counted afterwards, each with its target.")
    last_year: LastYear
    rules_and_risks: list[str] = Field(..., min_length=1, description="Consent, age-restricted lines and anything else the "
                                                                      "marketing lead should weigh.")
    open_points: list[str] = Field(default_factory=list, description="What the brief could not settle from the records.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds thirty members of the Rowanmere Market loyalty programme, as a sample "
                                  "of the whole programme, with what each one bought and viewed, the rules the marketing "
                                  "team sets for suggestions, six past campaigns and the campaign brief template. A member "
                                  "is a name, a member number and an email address. The system returns no suggestions of "
                                  "its own. Saving suggestions or a brief is a draft: the marketing team approves each "
                                  "release and the marketing lead owns each brief.")
    st = ctx.store
    d = lambda: st.data

    def member_or_404(member_id: str) -> dict:
        x = d()["loyalty_members"].get(member_id)
        if not x:
            raise not_found("member", member_id, "Use list_members to find member numbers. They look like LM-2003.")
        return x

    member_p = Path(..., description="Member number, for example LM-2003.")

    # ------------------------------------------------------------ members and rules
    @reg(app, "get", "/members", "list_members", "List loyalty members",
         f"List the members held here, in order of member number. Each row has {MEMBER_ROW}, and suggestion_drafts (how "
         "many are saved). Filters are optional: personalisation_opt_in and marketing_email_opt_in. The answer has count "
         "and programme (the totals of the whole programme, of which these members are a sample). Read a member's "
         "history with get_member.")
    def list_members(personalisation_opt_in: bool | None = Query(None, description="true: only members opted in to personalisation. false: only those who are not."),
                     marketing_email_opt_in: bool | None = Query(None, description="true: only members opted in to marketing email. false: only those who are not.")):
        keys = ("member_id", "name", "email", "joined_on", "personalisation_opt_in", "marketing_email_opt_in",
                "age_check_passed", "excluded_categories")
        rows = [{**{k: m[k] for k in keys}, "suggestion_drafts": len(m["suggestion_drafts"])}
                for m in d()["loyalty_members"].values()
                if (personalisation_opt_in is None or m["personalisation_opt_in"] == personalisation_opt_in)
                and (marketing_email_opt_in is None or m["marketing_email_opt_in"] == marketing_email_opt_in)]
        return listing(sorted(rows, key=lambda m: m["member_id"]), programme=PROGRAMME)

    @reg(app, "get", "/members/{member_id}", "get_member", "Get one member with purchase and browsing history",
         f"Read one member: {MEMBER_ROW}; purchases_last_90_days (each with date, sku, name, category and quantity, newest "
         "first); browsing_last_30_days (each line viewed, with sku, name, category, views and last_viewed_on) and "
         "suggestion_drafts (every saved set of suggestions, each a version). The answer has retailer_date. The system "
         "returns no suggestion: the rules are in get_personalisation_rules, and whether a line is live or age-restricted "
         "is in the catalogue system.")
    def get_member(member_id: str = member_p):
        return {**member_or_404(member_id), "retailer_date": st.settings.retailer_today.isoformat()}

    @reg(app, "get", "/personalisation-rules", "get_personalisation_rules", "Get the personalisation rules",
         "Read the rules the marketing team sets for suggestions: document, version, owner, maximum_suggestions (5), rules "
         "(each with rule_id PZ-1 to PZ-5, title and text), how_suggestions_are_chosen (steps S-1 to S-5) and "
         "what_the_rules_do_not_decide.")
    def get_personalisation_rules():
        return PERSONALISATION_RULES

    @reg(app, "post", "/members/{member_id}/suggestions", "save_product_suggestions", "Save product suggestions for a member (draft)",
         "Save the product suggestions for one member, as a draft. It shows the member nothing. Each call is kept as a new "
         "version with who wrote it and when. Send suggestions (at most five, each with sku and reason, in order), blocked "
         "(each with sku and rule), no_suggestion_reason and drafted_by. rule is PZ-2, PZ-3 or PZ-5. no_suggestion_reason is "
         "opted_out, nothing_viewed_and_not_bought or all_blocked_by_rules when there is no suggestion, and empty "
         "otherwise. An unknown sku is refused with 404. Refused with 422, with the rule: any suggestion for a member who "
         "has not opted in to personalisation; an age-restricted line for a member whose age check has not been passed; a "
         "line from a category the member has excluded; a line whose listing is not live; more than five suggestions; a "
         "line listed twice; and an empty list with no reason, or a reason with a list that is not empty. The marketing "
         "team approves each release. Returns the saved version.")
    def save_product_suggestions(body: ProductSuggestions, member_id: str = member_p):
        m = member_or_404(member_id)
        listings = d()["catalogue_products"]
        skus = [s.sku for s in body.suggestions] + [b.sku for b in body.blocked]
        for sku in skus:
            if sku not in listings:
                raise not_found("product listing", sku, "Nothing was saved. Line ids look like AG-4402.")
        if len(set(skus)) != len(skus):
            raise HTTPException(422, "A line is listed twice. Nothing was saved. A line is either suggested once or blocked once.")
        if body.suggestions and not m["personalisation_opt_in"]:
            raise HTTPException(422, f"Rule PZ-1: {member_id} has not opted in to personalisation and gets no suggestion. "
                                     "Nothing was saved. Save an empty list with the reason opted_out.")
        for s in body.suggestions:
            x = listings[s.sku]
            if x["age_restricted"] and not m["age_check_passed"]:
                raise HTTPException(422, f"Rule PZ-2: {s.sku} is an age-restricted line and the age check of {member_id} has "
                                         "not been passed. Nothing was saved. List the line under blocked.")
            if x["category"] in m["excluded_categories"]:
                raise HTTPException(422, f"Rule PZ-3: {s.sku} is in the category {x['category']}, which {member_id} has "
                                         "excluded. Nothing was saved. List the line under blocked.")
            if x["status"] != "live":
                raise HTTPException(422, f"Rule PZ-5: the listing of {s.sku} is not live. Nothing was saved. List the line "
                                         "under blocked.")
        if bool(body.suggestions) == bool(body.no_suggestion_reason):
            raise HTTPException(422, "Send no_suggestion_reason when there is no suggestion, and leave it empty when there "
                                     "is one. Nothing was saved.")
        payload = {"suggestions": [s.model_dump() for s in body.suggestions], "blocked": [b.model_dump() for b in body.blocked],
                   "no_suggestion_reason": body.no_suggestion_reason}
        v = st.add_draft(m, "suggestion_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "member_id": member_id}

    # ------------------------------------------------------------ campaigns
    @reg(app, "get", "/programme", "get_loyalty_programme_summary", "Get the totals of the loyalty programme",
         "Read the totals of the whole loyalty programme: members, marketing_email_opt_in, app_notifications_opt_in, "
         "age_check_passed, members_held_in_this_service and note. Use these totals for the size of an audience. The "
         "thirty members held here are a sample.")
    def get_loyalty_programme_summary():
        return PROGRAMME

    @reg(app, "get", "/campaigns", "list_past_campaigns", "List past campaigns with results",
         f"List last year's campaigns with their results, in the order they ran. Each row has {CAMPAIGN_FIELDS}. Amounts are "
         "US dollars. A return_for_each_dollar below 1.0 means the campaign brought in less than it cost.")
    def list_past_campaigns():
        return listing(sorted(d()["past_campaigns"].values(), key=lambda c: c["ran_in"]))

    @reg(app, "get", "/campaigns/{campaign_id}", "get_past_campaign", "Get one past campaign",
         f"Read one past campaign: {CAMPAIGN_FIELDS}. Find ids with list_past_campaigns.")
    def get_past_campaign(campaign_id: str = Path(..., description="Campaign id, for example CP-2505.")):
        c = d()["past_campaigns"].get(campaign_id)
        if not c:
            raise not_found("past campaign", campaign_id, "Use list_past_campaigns to find campaign ids.")
        return c

    @reg(app, "get", "/brief-template", "get_campaign_brief_template", "Get the campaign brief template",
         "Read the company's campaign brief template: document, version, owner, sections (eleven, each with number, title "
         "and what_goes_in_it), what_a_brief_does_not_do and text (the template as one document).")
    def get_campaign_brief_template():
        return BRIEF_TEMPLATE

    @reg(app, "get", "/briefs", "list_campaign_briefs", "List the saved campaign briefs",
         "Read every campaign brief saved, oldest first. Fields: count and briefs, a list of versions, each with version, "
         "drafted_by, drafted_at and the eleven sections of the template as saved.")
    def list_campaign_briefs():
        briefs = d()["campaign_briefs"]["briefs"]
        return {"count": len(briefs), "briefs": briefs}

    @reg(app, "post", "/briefs", "save_campaign_brief", "Save a campaign brief (draft)",
         "Save a campaign brief in the company's template, as a draft. It sends nothing to any member. Each call is kept as "
         "a new version with who wrote it and when. Send title, objective, audience (segment, size, consent_basis and "
         "adults_only), offer, includes_age_restricted_lines, channels, start_date, end_date, budget, measures_of_success, "
         "last_year (campaign_id and what_it_showed), rules_and_risks, open_points and drafted_by. channels holds email, "
         "app, in_store or website. consent_basis is marketing_email_opt_in, app_notifications_opt_in or "
         "none_needed_in_store_or_on_the_website. A campaign_id that does not exist is refused with 404. Refused with 422, "
         "with the reason: an end_date before the start_date, or a start_date before the retailer date; an audience larger "
         "than the programme's total of members opted in to the channel (email first, then the app); a consent_basis that "
         "does not fit the channels; and an offer with an age-restricted line whose audience is not adults only, or an "
         "adults-only audience larger than the total of members whose age check has been passed. The marketing lead owns "
         "the brief. Returns the saved version.")
    def save_campaign_brief(body: CampaignBrief):
        if body.last_year.campaign_id not in d()["past_campaigns"]:
            raise not_found("past campaign", body.last_year.campaign_id, "Nothing was saved. Use list_past_campaigns.")
        try:
            start, end = date.fromisoformat(body.start_date), date.fromisoformat(body.end_date)
        except ValueError:
            raise HTTPException(422, "start_date or end_date is not a date. Write them as YYYY-MM-DD. Nothing was saved.")
        if end < start:
            raise HTTPException(422, "The end_date is before the start_date. Nothing was saved.")
        if start < st.settings.retailer_today:
            raise HTTPException(422, f"The start_date is before the retailer date, {st.settings.retailer_today.isoformat()}. "
                                     "Nothing was saved.")
        if "email" in body.channels:
            basis, cap, channel = "marketing_email_opt_in", PROGRAMME["marketing_email_opt_in"], "marketing email"
        elif "app" in body.channels:
            basis, cap, channel = "app_notifications_opt_in", PROGRAMME["app_notifications_opt_in"], "app notifications"
        else:
            basis, cap, channel = "none_needed_in_store_or_on_the_website", PROGRAMME["members"], "the programme"
        if body.audience.consent_basis != basis:
            raise HTTPException(422, f"With the channels {', '.join(body.channels)} the consent_basis is {basis}. Nothing was saved.")
        if body.audience.size > cap:
            raise HTTPException(422, f"The audience of {body.audience.size} is larger than the {cap} members opted in to "
                                     f"{channel}. Nothing was saved. get_loyalty_programme_summary gives the totals.")
        if body.includes_age_restricted_lines and not body.audience.adults_only:
            raise HTTPException(422, "The offer includes an age-restricted line, so the audience is adults only. Set "
                                     "adults_only to true. Nothing was saved.")
        if body.audience.adults_only and body.audience.size > PROGRAMME["age_check_passed"]:
            raise HTTPException(422, f"An adults-only audience of {body.audience.size} is larger than the "
                                     f"{PROGRAMME['age_check_passed']} members whose age check has been passed. Nothing was saved.")
        v = st.add_draft(d()["campaign_briefs"], "briefs", body.model_dump(exclude={"drafted_by"}), body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    return app
