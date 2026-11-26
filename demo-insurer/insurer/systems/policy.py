"""Policy administration: policies with their schedules and endorsements, and the policy wordings with numbered clauses."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, Path, Query

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..seed_policy import cover_on

KEY = "policy"
TITLE = "Policy administration"
LINE = "Policies with their schedules and endorsements, and the policy wordings with numbered clauses."


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the insurer's policies (holder, period, status, schedule, endorsements) and the "
                                  "policy wordings, each as a list of numbered clauses. It changes nothing.")
    st = ctx.store
    d = lambda: st.data
    pol_p = Path(..., description="Policy id, for example POL-2001.")

    def policy_or_404(i):
        p = d()["policies"].get(i)
        if not p:
            raise not_found("policy", i, "Use search_policies with the holder's name to find the id.")
        return p

    def summary(p):
        return {k: p[k] for k in ("policy_id", "product", "holder", "address", "status", "period_start", "period_end", "wording_id")}

    @reg(app, "get", "/policies", "search_policies", "Search policies by holder or address",
         "Find policies by the holder's name or the insured address. Any word of the text may match, in any order, so a name with one "
         "word misspelt is still found. With no text, every policy is listed. Each row gives the policy id, product (private_motor or "
         "home), holder, address, status (in_force, lapsed or cancelled), the policy period and the wording id. Check a row's holder and "
         "address against what you were told before you rely on it.")
    def search_policies(text: str | None = Query(None, description="Words from the holder's name or the address, for example Stannaway "
                                                                   "or Otterburn Gardens. Leave empty to list every policy.")):
        words = [w.lower() for w in (text or "").replace(",", " ").split() if len(w) > 2]
        rows = []
        for p in d()["policies"].values():
            hay = f"{p['holder']} {p['address']} {p['policy_id']}".lower()
            if not words or any(w in hay for w in words):
                rows.append(summary(p))
        return listing(rows, searched_for=text or "")

    @reg(app, "get", "/policies/{policy_id}", "get_policy", "Get one policy",
         "Read one policy in full: holder, address, product, status with a note on why it is lapsed or cancelled, the policy period, the "
         "wording id and version, the schedule (the insured vehicle or home, sums insured, the deductible, named drivers, listed items, "
         "limits worked out from the sums insured) and every endorsement with its id, title, effective date and text. An endorsement "
         "changes the wording for this policy.")
    def get_policy(policy_id: str = pol_p):
        return {**policy_or_404(policy_id), "read_on": ctx.settings.insurer_today.isoformat()}

    @reg(app, "get", "/policies/{policy_id}/cover", "check_policy_cover_on_date", "Check whether a policy was in force on a date",
         "Say whether the policy was in force on one date, usually the date of a loss. The answer gives in_force (true or false) and "
         "the reason in a sentence, with the dates and the number of days worked out by the system. Use this answer and do not work "
         "out the days yourself.")
    def check_policy_cover_on_date(policy_id: str = pol_p,
                                   on: str = Query(..., description="The date to check, as YYYY-MM-DD, for example 2026-11-17.")):
        p = policy_or_404(policy_id)
        try:
            date.fromisoformat(on)
        except ValueError:
            raise HTTPException(422, f"The date {on} is not valid. Send it as YYYY-MM-DD, for example 2026-11-17. Nothing was checked.")
        return cover_on(p, on)

    @reg(app, "get", "/wordings/{wording_id}", "get_policy_wording", "Get a policy wording with its numbered clauses",
         "Read one policy wording in full: its title, version, a note on how to read it, and every clause with its number, section, "
         "heading and text. Section 1 is what is covered, section 2 what is not covered, section 3 the most that is paid, section 4 "
         "the deductible, section 5 the conditions. The wording covers nothing it does not name. A policy's wording id is on the policy.")
    def get_policy_wording(wording_id: str = Path(..., description="Wording id, for example TMI-MOT-01.")):
        w = d()["wordings"].get(wording_id)
        if not w:
            raise not_found("policy wording", wording_id, "The wording id is on the policy: read the policy first.")
        return {**w, "clause_count": len(w["clauses"])}

    return app
