"""CRM: relationship managers' meetings, client holdings across the bank's systems and client interactions."""

from __future__ import annotations

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "crm"
TITLE = "Client meetings (CRM)"
LINE = "Relationship managers' meetings with clients, what each client holds across the bank, and what was said to them before."


class Brief(BaseModel):
    summary: str = Field(..., min_length=1, description="Two or three plain sentences: who the client is and what the meeting is for.")
    client_position: str = Field("", description="What the client holds and owes, with the totals, in plain sentences.")
    talking_points: list[str] = Field(default_factory=list, description="What to cover in the meeting, in order.")
    points_to_raise_with_care: list[str] = Field(default_factory=list, description="Anything the manager should know before the meeting, such as press coverage, a loan in progress or a complaint.")
    questions_to_ask: list[str] = Field(default_factory=list, description="Questions to ask the client.")
    sources: list[str] = Field(default_factory=list, description="The records the brief used, each as system and id, for example news ART-6001.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the meetings of relationship managers with clients. It also gathers what a client holds across the core, "
                                  "lending and pension systems, so the totals agree with those systems.")
    st = ctx.store
    d = lambda: st.data
    mtg_p = Path(..., description="Meeting id, for example MTG-1001.")
    cus_p = Path(..., description="Customer id, for example CUS-1007.")

    def mtg_or_404(i):
        m = d()["crm_meetings"].get(i)
        if not m:
            raise not_found("meeting", i, "Use list_client_meetings to find ids.")
        return m

    def cust_or_404(i):
        c = d()["customers"].get(i)
        if not c:
            raise not_found("customer", i, "Customer ids look like CUS-1001.")
        return c

    def row(m):
        c = d()["customers"][m["customer_id"]]
        return {"meeting_id": m["meeting_id"], "date": m["date"], "time": m["time"], "customer_id": m["customer_id"], "client_name": c["name"],
                "client_type": c["type"], "relationship_manager": m["relationship_manager"], "purpose": m["purpose"], "status": m["status"]}

    @reg(app, "get", "/meetings", "list_client_meetings", "List client meetings",
         "List client meetings: meeting_id, date, time, the client, the relationship manager, the purpose and the status (scheduled or held). Filter by "
         "date (YYYY-MM-DD) and by relationship manager. To prepare for tomorrow, use tomorrow's date and the manager's name. Read one with get_client_meeting.")
    def list_client_meetings(date: str = Query("", description="Only meetings on this date, YYYY-MM-DD. Leave empty for all dates."),
                             relationship_manager: str = Query("", description="Only meetings of this relationship manager, for example Sunniva Haldane-Rook. Leave empty for all.")):
        rows = [row(m) for m in d()["crm_meetings"].values()
                if (not date or m["date"] == date) and (not relationship_manager or m["relationship_manager"].lower() == relationship_manager.lower())]
        rows.sort(key=lambda r: (r["date"], r["time"], r["meeting_id"]))
        return listing(rows)

    @reg(app, "get", "/meetings/{meeting_id}", "get_client_meeting", "Get one client meeting",
         "Read one meeting: the date and time, the place, who attends, the purpose, the client's name, type and segment, the relationship manager, the "
         "notes from the meeting if it was held, and any saved briefs. To prepare a brief, read what the client holds with get_client_holdings and "
         "the earlier contact with list_client_interactions, and look for news, loan applications and complaints in the other systems.")
    def get_client_meeting(meeting_id: str = mtg_p):
        m = mtg_or_404(meeting_id)
        c = d()["customers"][m["customer_id"]]
        return {**m, "client": {k: c[k] for k in ("customer_id", "type", "name", "segment", "risk_rating", "address", "customer_since")}}

    @reg(app, "get", "/clients/{customer_id}/holdings", "get_client_holdings", "Get what a client holds",
         "Read what one client holds across the bank: deposits (each account and its balance), investments (pension holdings by fund, if the client is a "
         "member of the scheme), lending (each loan outstanding and any loan applications in progress) and the totals. The numbers are read from the core, "
         "lending and pension systems, so they agree with them. Totals are in USD and accounts in another currency are listed separately.")
    def get_client_holdings(customer_id: str = cus_p):
        c = cust_or_404(customer_id)
        dd = d()
        accounts = [{k: a[k] for k in ("account_id", "product", "currency", "status", "balance")} for a in dd["accounts"].values() if a["customer_id"] == customer_id]
        usd = round(sum(a["balance"] for a in accounts if a["currency"] == "USD"), 2)
        other = [a for a in accounts if a["currency"] != "USD"]
        member = next((m for m in dd["pension_members"].values() if m["customer_id"] == customer_id), None)
        inv, inv_total = [], 0.0
        if member:
            for fid, units in dd["pension_holdings"].get(member["member_id"], {}).items():
                f = dd["pension_funds"][fid]
                val = round(units * f["unit_price"], 2)
                inv_total += val
                inv.append({"fund_id": fid, "fund_name": f["name"], "units": units, "value": val, "currency": "USD", "member_id": member["member_id"]})
        loans = [{k: ln[k] for k in ("loan_id", "product", "principal", "outstanding", "currency", "status", "maturity_date")}
                 for ln in dd["loans"].values() if ln["customer_id"] == customer_id]
        apps = [{k: a.get(k, "") for k in ("application_id", "status", "product", "amount", "currency", "term_months", "received")}
                for a in dd["applications"].values() if a["customer_id"] == customer_id and a["status"] in ("received", "in_review")]
        return {"customer_id": customer_id, "client_name": c["name"], "as_of": ctx.settings.bank_today.isoformat(), "currency": "USD",
                "deposits": {"accounts": accounts, "total_usd": usd, "accounts_in_other_currencies": [a["account_id"] for a in other]},
                "investments": {"pension_member_id": member["member_id"] if member else "", "holdings": inv, "total_usd": round(inv_total, 2)},
                "lending": {"loans": loans, "total_outstanding_usd": round(sum(x["outstanding"] for x in loans if x["currency"] == "USD"), 2),
                            "applications_in_progress": apps},
                "totals": {"deposits_usd": usd, "investments_usd": round(inv_total, 2),
                           "lending_outstanding_usd": round(sum(x["outstanding"] for x in loans if x["currency"] == "USD"), 2)}}

    @reg(app, "get", "/clients/{customer_id}/interactions", "list_client_interactions", "List client interactions",
         "List what the bank has recorded of its contact with one client, newest first: contact notes from the core system (calls, emails, branch notes), "
         "meetings that were held with their notes, and complaints. Each row has the date, the kind, the subject and a summary.")
    def list_client_interactions(customer_id: str = cus_p):
        cust_or_404(customer_id)
        dd = d()
        rows = [{"date": c["date"], "kind": c["channel"], "source": "core", "id": c["contact_id"], "subject": c["subject"], "summary": c["summary"]}
                for c in dd["contacts"].values() if c["customer_id"] == customer_id]
        rows += [{"date": m["date"], "kind": "meeting", "source": "crm", "id": m["meeting_id"], "subject": m["purpose"], "summary": " ".join(m["notes"])}
                 for m in dd["crm_meetings"].values() if m["customer_id"] == customer_id and m["status"] == "held"]
        rows += [{"date": c["received"], "kind": "complaint", "source": "complaints", "id": c["complaint_id"], "subject": c["subject"], "summary": c["customer_words"]}
                 for c in dd["complaints"].values() if c["customer_id"] == customer_id]
        rows.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
        return listing(rows)

    @reg(app, "post", "/meetings/{meeting_id}/brief", "save_meeting_brief", "Save a meeting brief (draft)",
         "Save your brief for a client meeting: a summary, the client's position, the talking points, the points to raise with care, the questions to ask "
         "and the sources. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Nothing is sent to the client.")
    def save_meeting_brief(body: Brief, meeting_id: str = mtg_p):
        m = mtg_or_404(meeting_id)
        v = st.add_draft(m, "briefs", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "meeting_status": m["status"], "draft": v}

    return app
