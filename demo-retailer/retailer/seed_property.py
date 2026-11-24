"""Property, version 1.1: the leases of some of the group's stores and restaurants.

Every lease is written in numbered clauses. The dates are relative to the retailer date: each lease starts
on the first day of a month, a fixed number of months before the month of the retailer date.

The answers a careful reader should reach are kept in their own record set (lease_answers) and no operation
serves it.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_stores import build_sites

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
WORDS = {3: "three", 6: "six", 9: "nine", 12: "twelve"}
DEFAULT_ORDER = ["parties", "term", "rent", "review", "break", "repairs", "service", "assignment", "notices"]
HEADINGS = {"parties": "Parties and premises", "term": "Term", "rent": "Rent", "review": "Rent review",
            "break": "Break option", "repairs": "Repairs", "service": "Service charge",
            "assignment": "Assignment and subletting", "notices": "Notices"}
TENANTS = {"store": "Rowanmere Market Ltd", "restaurant": "Rowanmere Kitchen Ltd"}

# start: months from the first day of the retailer date's month to the first day of the term (negative: in the past).
# reviews: the anniversaries of the start on which the rent is reviewed. brk: who may break, on which anniversary,
# and the months of notice.
_LEASES = [
    dict(id="LS-2001", site="S-101", landlord="Harbourfield Estates Ltd", start=-52, years=10, rent=412000,
         reviews=[5], basis="upward_or_downward", brk=dict(who="tenant", year=5, notice=6), repairs="tenant_all",
         service=None, assignment="group", renewal=9, order=DEFAULT_ORDER),
    dict(id="LS-2002", site="S-102", landlord="Dockside Wharf Properties Ltd", start=-92, years=15, rent=365000,
         reviews=[5, 10], basis="upward_or_downward", brk=dict(who="tenant", year=10, notice=9), repairs="structure_landlord",
         service=dict(pct=18, cap=None, estate="Dockside Wharf"), assignment="consent", renewal=12, order=DEFAULT_ORDER),
    dict(id="LS-2003", site="S-104", landlord="Marlow Reach Town Holdings Ltd", start=-70, years=10, rent=298000,
         reviews=[5], basis="upward_only", brk=dict(who="tenant", year=7, notice=6), repairs="tenant_all",
         service=None, assignment="consent", renewal=9, order=DEFAULT_ORDER),
    dict(id="LS-2004", site="S-107", landlord="Brewery Lane Developments Ltd", start=-37, years=12, rent=254000,
         reviews=[3, 6, 9], basis="fixed_increase", brk=dict(who="tenant", year=6, notice=12), repairs="tenant_all",
         service=dict(pct=12, cap=30000, estate="Brewery Lane retail park"), assignment="group", renewal=12,
         order=DEFAULT_ORDER),
    dict(id="LS-2005", site="S-108", landlord="Millrace Property Company Ltd", start=-30, years=5, rent=68500,
         reviews=[3], basis="index_linked", brk=None, repairs="structure_landlord",
         service=None, assignment="none", renewal=6,
         order=["parties", "term", "rent", "review", "repairs", "service", "assignment", "notices"]),
    dict(id="LS-2006", site="R-014", landlord="Ilvane Quay Investments Ltd", start=-74, years=10, rent=96000,
         reviews=[5], basis="upward_or_downward", brk=dict(who="tenant", year=8, notice=6), repairs="tenant_all",
         service=None, assignment="franchise", renewal=9, order=DEFAULT_ORDER),
    dict(id="LS-2007", site="R-031", landlord="Quayside Arcade Ltd", start=-57, years=15, rent=118000,
         reviews=[5, 10], basis="upward_or_downward", brk=dict(who="either", year=10, notice=12), repairs="roof_landlord",
         service=dict(pct=9, cap=14000, estate="Quayside Arcade"), assignment="franchise", renewal=12,
         order=["parties", "term", "rent", "review", "repairs", "service", "break", "assignment", "notices"]),
    dict(id="LS-2008", site="R-047", landlord="Kilnyard Estates Ltd", start=-17, years=10, rent=74000,
         reviews=[5], basis="upward_or_downward", brk=dict(who="tenant", year=5, notice=6), repairs="tenant_all",
         service=dict(pct=7, cap=6500, estate="Kiln Road parade"), assignment="franchise", renewal=9, order=DEFAULT_ORDER),
    dict(id="LS-2009", site="R-058", landlord="Lantern Square Trustees Ltd", start=-95, years=15, rent=132000,
         reviews=[5, 10], basis="upward_or_downward", brk=dict(who="landlord", year=11, notice=12), repairs="structure_landlord",
         service=dict(pct=11, cap=None, estate="Lantern Square"), assignment="consent", renewal=12, order=DEFAULT_ORDER),
]

BASIS_TEXT = {
    "upward_only": "On each review date the rent is reviewed to the open market rent of the premises. The reviewed rent is the "
                   "higher of the open market rent and the rent payable immediately before the review date. The rent cannot "
                   "go down on a review.",
    "upward_or_downward": "On each review date the rent is reviewed to the open market rent of the premises, whether that is "
                          "higher or lower than the rent payable immediately before the review date.",
    "fixed_increase": "On each review date the rent rises by 3 percent of the rent payable immediately before the review date. "
                      "There is no open market review.",
    "index_linked": "On each review date the rent changes, up or down, in line with the change in the Meridia Consumer Price "
                    "Index since the first day of the term. There is no open market review.",
}


def add_months(d: date, n: int) -> date:
    """The same day of the month, n months on. Only used for the first day of a month."""
    months = d.year * 12 + (d.month - 1) + n
    return date(months // 12, months % 12 + 1, d.day)


def long_date(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def _join(dates: list[date]) -> str:
    words = [long_date(d) for d in dates]
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def _sections(spec: dict, site: dict, start: date, end: date, reviews: list[date], break_date: date | None) -> dict:
    """The text of each section as a list of sub-clauses, and which sub-clause holds each answer."""
    tenant = TENANTS[site["kind"]]
    premises = f"the {site['kind']} premises known as {site['name']}, {site['street']}, {site['town']}, Meridia"
    out, where = {}, {}
    out["parties"] = [f"The landlord is {spec['landlord']}. The tenant is {tenant}, a company of Rowanmere Group plc.",
                      f"The premises are {premises}. Notices to the landlord go to {spec['landlord']}, Estate Office, "
                      f"{site['town']}. Notices to the tenant go to Rowanmere Group plc, Property Team, Port Ilvane."]
    out["term"] = [f"The term is {spec['years']} years. It begins on {long_date(start)} and ends on {long_date(end)}."]
    where["term"] = 1
    out["rent"] = [f"The rent is USD {spec['rent']:,} a year, before value added tax.",
                   "The rent is paid in four equal parts, in advance, on the first day of January, April, July and October."]
    where["rent"] = 1
    out["review"] = [f"The rent is reviewed on {_join(reviews)}. " + ("Each of these is a review date." if len(reviews) > 1
                                                                      else "This is the review date."),
                     BASIS_TEXT[spec["basis"]]]
    where["review_dates"], where["review_basis"] = 1, 2
    brk = spec["brk"]
    if brk:
        notice = f"not less than {WORDS[brk['notice']]} months' written notice before the break date"
        if brk["who"] == "tenant":
            first = f"The tenant may end this lease on {long_date(break_date)} (the break date)."
            second = f"To do so the tenant gives the landlord {notice}."
        elif brk["who"] == "landlord":
            first = (f"The landlord may end this lease on {long_date(break_date)} (the break date) if it intends to redevelop "
                     "the building. The tenant has no right to end this lease before the end of the term.")
            second = f"To do so the landlord gives the tenant {notice}."
        else:
            first = f"Either the landlord or the tenant may end this lease on {long_date(break_date)} (the break date)."
            second = f"To do so the party that wishes to end the lease gives the other {notice}."
        third = ("If the landlord ends this lease under this clause, it pays the tenant a sum equal to six months' rent."
                 if brk["who"] == "landlord" else
                 "A break by the tenant takes effect only if, on the break date, the rent is paid up to date and the "
                 "tenant gives the premises back empty.")
        out["break"] = [first, second, third]
        where["break"], where["break_notice"] = 1, 2
    decorate = "The tenant redecorates the inside of the premises in every fifth year of the term and in its last six months."
    if spec["repairs"] == "tenant_all":
        out["repairs"] = ["The tenant keeps the whole of the premises in good repair and condition, including the roof, the "
                          "structure, the outside walls, the shopfront, the drains and everything inside.",
                          "The landlord has no duty to repair any part of the premises.", decorate]
        where["repairs_tenant"], where["repairs_landlord"] = 1, 2
    elif spec["repairs"] == "roof_landlord":
        out["repairs"] = ["The landlord keeps the roof of the premises in good repair.",
                          "The tenant keeps every other part of the premises in good repair and condition, including the "
                          "structure, the outside walls, the shopfront, the drains and everything inside.", decorate]
        where["repairs_landlord"], where["repairs_tenant"] = 1, 2
    else:
        out["repairs"] = ["The landlord keeps the roof, the structure and the outside walls of the premises in good repair.",
                          "The tenant keeps the inside of the premises, the shopfront and the tenant's fixtures in good repair "
                          "and condition.", decorate]
        where["repairs_landlord"], where["repairs_tenant"] = 1, 2
    svc = spec["service"]
    if svc is None:
        out["service"] = ["No service charge is payable under this lease."]
    else:
        cap = (f"The service charge is not more than USD {svc['cap']:,} in any year of the term." if svc["cap"]
               else "There is no upper limit on the service charge.")
        out["service"] = [f"The tenant pays {svc['pct']} percent of the landlord's costs of running {svc['estate']}: cleaning and "
                          "lighting the shared areas, security, and insuring the building.", cap]
    where["service"] = 1
    if spec["assignment"] == "none":
        out["assignment"] = ["The tenant may not assign this lease, and may not sublet the premises or any part of them."]
    else:
        first = ("The tenant may assign the whole of this lease with the landlord's written consent, which the landlord may not "
                 "unreasonably withhold. The tenant may not assign part of the premises.")
        second = {"consent": "The tenant may not sublet the premises or any part of them.",
                  "group": "The tenant may assign the whole of this lease to another company of Rowanmere Group plc without "
                           "consent, by giving the landlord 20 working days' written notice. The tenant may not sublet.",
                  "franchise": "The tenant may allow a franchisee of the Rowanmere Kitchen brand to occupy the premises, by "
                               "giving the landlord 30 days' written notice. That does not release the tenant from this lease."
                  }[spec["assignment"]]
        out["assignment"] = [first, second]
    where["assignment"] = 1
    out["notices"] = ["A notice under this lease is in writing. It is delivered by hand or sent by recorded post to the address "
                      "of the other party in clause 1. A notice sent by post is treated as received on the second working day "
                      "after posting. An email is not a notice.",
                      f"If the tenant wishes to renew this lease, it tells the landlord in writing not less than "
                      f"{WORDS[spec['renewal']]} months before the end of the term."]
    where["notices"] = 1
    return {"text": out, "where": where}


def build_lease(spec: dict, site: dict, today: date) -> tuple[dict, dict]:
    anchor = date(today.year, today.month, 1)
    start = add_months(anchor, spec["start"])
    end = add_months(start, 12 * spec["years"]) - timedelta(days=1)
    reviews = [add_months(start, 12 * y) for y in spec["reviews"]]
    brk = spec["brk"]
    break_date = add_months(start, 12 * brk["year"]) if brk else None
    notice_by = add_months(break_date, -brk["notice"]) if brk else None
    made = _sections(spec, site, start, end, reviews, break_date)
    clauses, number_of, lines = [], {}, []
    for n, key in enumerate(spec["order"], start=1):
        lines.append(f"\n{n}. {HEADINGS[key]}")
        number_of[key] = n
        for m, text in enumerate(made["text"][key], start=1):
            clauses.append({"number": f"{n}.{m}", "heading": HEADINGS[key], "text": text})
            lines.append(f"{n}.{m} {text}")
    tenant = TENANTS[site["kind"]]
    head = (f"INVENTED SAMPLE. Every party, place and amount here is made up. It is not a real lease.\n"
            f"LEASE {spec['id']}\nbetween {spec['landlord']} (the landlord) and {tenant} (the tenant)\n"
            f"of {site['name']}, {site['street']}, {site['town']}, Meridia")
    lease = {"lease_id": spec["id"], "site_id": site["site_id"], "site_name": site["name"], "town": site["town"],
             "landlord": spec["landlord"], "tenant": tenant, "term_start": start.isoformat(), "term_end": end.isoformat(),
             "annual_rent": float(spec["rent"]), "currency": "USD", "clauses": clauses, "text": head + "\n" + "\n".join(lines) + "\n",
             "summaries": []}
    w = made["where"]

    def ref(section: str, part: str) -> str:
        return f"{number_of[section]}.{w[part]}"

    answers = {
        "lease_id": spec["id"], "site_id": site["site_id"],
        "term": {"start_date": start.isoformat(), "end_date": end.isoformat(), "clause": ref("term", "term")},
        "rent": {"annual_rent": float(spec["rent"]), "clause": ref("rent", "rent")},
        "rent_reviews": [{"review_date": d.isoformat(), "basis": spec["basis"]} for d in reviews],
        "review_dates_clause": ref("review", "review_dates"), "review_basis_clause": ref("review", "review_basis"),
        "break_options": ([{"break_date": break_date.isoformat(), "who_may_break": brk["who"], "notice_months": brk["notice"],
                            "notice_by": notice_by.isoformat(), "clause": ref("break", "break"),
                            "notice_clause": ref("break", "break_notice")}] if brk else []),
        "repairs": spec["repairs"], "repairs_tenant_clause": ref("repairs", "repairs_tenant"),
        "repairs_landlord_clause": ref("repairs", "repairs_landlord"),
        "service_charge_clause": ref("service", "service"), "assignment_clause": ref("assignment", "assignment"),
        "notices_clause": ref("notices", "notices"),
    }
    return lease, answers


def build_property(today: date) -> dict:
    sites = build_sites()
    leases, answers = {}, {}
    for spec in _LEASES:
        lease, answer = build_lease(spec, sites[spec["site"]], today)
        leases[spec["id"]] = lease
        answers[spec["id"]] = answer
    return {"leases": leases, "lease_answers": answers}
