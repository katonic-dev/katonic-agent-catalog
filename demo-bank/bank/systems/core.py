"""Core banking: customer and account records."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "core"
TITLE = "Core banking"
LINE = "Customer and account records, transactions, contacts and credit exposure."


class ContactNote(BaseModel):
    channel: Literal["call", "email", "branch_note"] = Field("branch_note", description="Kind of contact.")
    subject: str = Field(..., min_length=1, description="Short subject line.")
    summary: str = Field(..., min_length=1, description="What was said or noted, in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the note. Free text. Default is agent.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds customer records, accounts, transactions, contact history and credit exposure.")
    st = ctx.store

    def d():
        return st.data

    cust_id = Path(..., description="Customer id, for example CUS-1001.")
    acc_id = Path(..., description="Account id, for example ACC-1001-01.")

    @reg(app, "get", "/customers", "search_customers", "Search customers by name or id",
         "Find customers. Give a part of the name, or a customer id, or both. Use this first when you only have a name. "
         "Returns a list (count, items) with customer_id, type (individual or business), name, segment, risk_rating and status. "
         "With no filter it returns the first customers up to the limit.")
    def search_customers(name: str | None = Query(None, description="Part of the customer name. Not case sensitive."),
                         customer_id: str | None = Query(None, description="Exact customer id, for example CUS-1001."),
                         limit: int = Query(20, ge=1, le=200, description="Most rows to return.")):
        rows = []
        for c in d()["customers"].values():
            if customer_id and c["customer_id"].lower() != customer_id.strip().lower():
                continue
            if name and name.strip().lower() not in c["name"].lower():
                continue
            rows.append({k: c[k] for k in ("customer_id", "type", "name", "segment", "risk_rating", "status")})
        return listing(rows[:limit], total_matches=len(rows))

    @reg(app, "get", "/customers/{customer_id}", "get_customer", "Get one customer record",
         "Read the full record of one customer: name, type, date of birth and place of birth (individuals) or registration details, nationality, address, "
         "identity number, risk rating, status and when the customer started and when the next KYC review is due. "
         "Use list_customer_accounts for the accounts.")
    def get_customer(customer_id: str = cust_id):
        c = d()["customers"].get(customer_id)
        if not c:
            raise not_found("customer", customer_id, "Use search_customers to find the id.")
        return c

    @reg(app, "get", "/customers/{customer_id}/accounts", "list_customer_accounts", "List a customer's accounts",
         "List every account of one customer with account_id, IBAN, product, currency, status, opened date and current balance. "
         "Use the account_id with get_account or list_account_transactions.")
    def list_customer_accounts(customer_id: str = cust_id):
        if customer_id not in d()["customers"]:
            raise not_found("customer", customer_id, "Use search_customers to find the id.")
        rows = [a for a in d()["accounts"].values() if a["customer_id"] == customer_id]
        return listing(rows, customer_id=customer_id)

    @reg(app, "get", "/accounts/{account_id}", "get_account", "Get one account",
         "Read one account: IBAN, product, currency, status, opened date, balance and the owning customer's id and name.")
    def get_account(account_id: str = acc_id):
        a = d()["accounts"].get(account_id)
        if not a:
            raise not_found("account", account_id, "Use list_customer_accounts to find account ids.")
        return {**a, "customer_name": d()["customers"][a["customer_id"]]["name"]}

    @reg(app, "get", "/accounts/{account_id}/transactions", "list_account_transactions",
         "List transactions on an account",
         "List transactions of one account for the last 90 days, newest first. Each row has transaction_id, date, amount, "
         "direction (credit or debit), type (for example cash_deposit, transfer_in, transfer_out, payroll, card_purchase), "
         "counterparty, counterparty_id, counterparty_country and narrative. Filter by date range, minimum amount or counterparty name.")
    def list_account_transactions(
            account_id: str = acc_id,
            date_from: str | None = Query(None, description="First date to include, YYYY-MM-DD."),
            date_to: str | None = Query(None, description="Last date to include, YYYY-MM-DD."),
            min_amount: float | None = Query(None, description="Only transactions of at least this amount."),
            counterparty: str | None = Query(None, description="Part of the counterparty name. Not case sensitive."),
            limit: int = Query(50, ge=1, le=500, description="Most rows to return.")):
        if account_id not in d()["accounts"]:
            raise not_found("account", account_id, "Use list_customer_accounts to find account ids.")
        rows = [t for t in d()["transactions"].values() if t["account_id"] == account_id]
        if date_from:
            rows = [t for t in rows if t["date"] >= date_from]
        if date_to:
            rows = [t for t in rows if t["date"] <= date_to]
        if min_amount is not None:
            rows = [t for t in rows if t["amount"] >= min_amount]
        if counterparty:
            rows = [t for t in rows if counterparty.lower() in t["counterparty"].lower()]
        rows.sort(key=lambda t: (t["date"], t["transaction_id"]), reverse=True)
        return listing(rows[:limit], total_matches=len(rows), account_id=account_id)

    @reg(app, "get", "/customers/{customer_id}/contacts", "list_customer_contacts", "List contact history",
         "List calls, emails and branch notes recorded for one customer, newest first. Each row has contact_id, channel, date, "
         "subject, summary and who recorded it. Read these for context before judging a case.")
    def list_customer_contacts(customer_id: str = cust_id):
        if customer_id not in d()["customers"]:
            raise not_found("customer", customer_id, "Use search_customers to find the id.")
        rows = [c for c in d()["contacts"].values() if c["customer_id"] == customer_id]
        rows.sort(key=lambda c: (c["date"], c["contact_id"]), reverse=True)
        return listing(rows, customer_id=customer_id)

    @reg(app, "get", "/customers/{customer_id}/exposure", "get_customer_exposure", "Get a customer's credit exposure",
         "Read the bank's credit exposure to one customer: loans with outstanding amount and monthly_instalment (the amount due "
         "each month, the same as on the customer's statements and in the collections data), limits with drawn amount and "
         "utilisation percent, collateral with value, and totals.")
    def get_customer_exposure(customer_id: str = cust_id):
        e = d()["exposure"].get(customer_id)
        if not e:
            raise not_found("customer", customer_id, "Use search_customers to find the id.")
        return e

    @reg(app, "post", "/customers/{customer_id}/contacts", "add_contact_note", "Add a contact note (draft)",
         "Write a note to the customer's contact history. This is a draft record: it carries who wrote it, a timestamp and a "
         "version number, and nothing else changes. Returns applied true and the stored note.")
    def add_contact_note(body: ContactNote, customer_id: str = cust_id):
        if customer_id not in d()["customers"]:
            raise not_found("customer", customer_id, "Use search_customers to find the id.")
        with st.lock:
            n = st.next_number("contact", 5100)
            cid = f"CNT-{n}"
            version = 1 + sum(1 for c in d()["contacts"].values()
                              if c["customer_id"] == customer_id and c.get("drafted_at"))
            rec = {"contact_id": cid, "customer_id": customer_id, "channel": body.channel,
                   "date": ctx.settings.bank_today.isoformat(), "direction": "internal", "subject": body.subject,
                   "summary": body.summary, "recorded_by": body.drafted_by, "drafted_by": body.drafted_by,
                   "drafted_at": now_iso(), "version": version}
            d()["contacts"][cid] = rec
            st.save()
        return {"applied": True, "kind": "draft", "contact": rec}

    return app
