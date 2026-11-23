"""AML: transaction monitoring alerts and cases."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "aml"
TITLE = "Transaction monitoring"
LINE = "Transaction monitoring alerts, rules, counterparties and cases. It cannot file a report."


class OpenCase(BaseModel):
    customer_id: str = Field(..., description="Customer the case is about, for example CUS-1020.")
    alert_ids: list[str] = Field(..., min_length=1, description="Monitoring alert ids that belong in the case.")
    summary: str = Field(..., min_length=1, description="Why the case is opened, in plain sentences.")
    priority: Literal["low", "medium", "high"] = Field("medium", description="Case priority.")
    opened_by: str = Field("agent", description="Who opened the case. Free text.")


class EvidenceItem(BaseModel):
    type: Literal["transaction", "alert", "rule", "contact", "counterparty", "other"] = Field(..., description="Kind of evidence.")
    id: str = Field(..., description="Id of the evidence item, for example TXN-S3001-01.")
    note: str = Field("", description="Why it matters.")


class Narrative(BaseModel):
    narrative: str = Field(..., min_length=1, description="The case narrative, in plain sentences.")
    evidence: list[EvidenceItem] = Field(..., min_length=1, description="The evidence the narrative relies on.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds monitoring alerts and cases. It has no operation that files a report: a person does that.")
    st = ctx.store
    d = lambda: st.data
    alert_id = Path(..., description="Monitoring alert id, for example TMA-3001.")

    def alert_or_404(aid):
        a = d()["monitoring_alerts"].get(aid)
        if not a:
            raise not_found("monitoring alert", aid, "Use list_monitoring_alerts to find ids.")
        return a

    def row(a):
        return {k: a[k] for k in ("alert_id", "status", "customer_id", "account_id", "rule_id", "period_start",
                                  "period_end", "summary", "risk_score", "case_id")}

    @reg(app, "get", "/alerts", "list_monitoring_alerts", "List monitoring alerts",
         "List transaction monitoring alerts: alert_id, status (open, case_opened, closed), customer, account, rule fired, period, "
         "a one-line summary and a risk score.")
    def list_monitoring_alerts(status: Literal["open", "case_opened", "closed"] | None = Query(None, description="Only alerts with this status.")):
        return listing([row(a) for a in d()["monitoring_alerts"].values() if not status or a["status"] == status])

    @reg(app, "get", "/alerts/{alert_id}", "get_monitoring_alert", "Get one monitoring alert in full",
         "Read one alert: the rule that fired (with its text), the period, the customer and account, and the full records of the "
         "transactions involved. Check the transactions and the customer's contacts before deciding.")
    def get_monitoring_alert(alert_id: str = alert_id):
        a = alert_or_404(alert_id)
        txs = [d()["transactions"][t] for t in a["transaction_ids"] if t in d()["transactions"]]
        return {**a, "rule": d()["aml_rules"][a["rule_id"]], "customer_name": d()["customers"][a["customer_id"]]["name"],
                "transactions": txs}

    @reg(app, "get", "/rules/{rule_id}", "get_monitoring_rule", "Get a monitoring rule",
         "Read the text of one monitoring rule (id like MTB-AML-RULE-001), its name, policy code and thresholds, so you can cite it.")
    def get_monitoring_rule(rule_id: str = Path(..., description="Rule id, for example MTB-AML-RULE-001.")):
        r = d()["aml_rules"].get(rule_id)
        if not r:
            raise not_found("monitoring rule", rule_id, "Rule ids appear in monitoring alerts.")
        return r

    @reg(app, "get", "/customers/{customer_id}/alerts", "list_customer_alert_history", "List a customer's alert and case history",
         "List all monitoring alerts, open and closed, and all cases of one customer, with how earlier alerts were closed.")
    def list_customer_alert_history(customer_id: str = Path(..., description="Customer id, for example CUS-1020.")):
        if customer_id not in d()["customers"]:
            raise not_found("customer", customer_id, "Customer ids look like CUS-1001.")
        alerts = [row(a) | {"closure": a["closure"]} for a in d()["monitoring_alerts"].values() if a["customer_id"] == customer_id]
        cases = [c for c in d()["cases"].values() if c["customer_id"] == customer_id]
        return {"customer_id": customer_id, "alerts": alerts, "cases": cases}

    @reg(app, "get", "/counterparties/{counterparty_id}", "get_counterparty", "Get a counterparty",
         "Read one counterparty seen in transactions: name, country, bank, risk rating, first seen date, notes and whether it "
         "is in a higher-risk jurisdiction.")
    def get_counterparty(counterparty_id: str = Path(..., description="Counterparty id, for example CPY-4005.")):
        c = d()["counterparties"].get(counterparty_id)
        if not c:
            raise not_found("counterparty", counterparty_id, "Counterparty ids appear on transactions.")
        return c

    @reg(app, "get", "/cases/{case_id}", "get_case", "Get a case",
         "Read one case: customer, alerts, status, priority, summary and all narrative drafts with versions.")
    def get_case(case_id: str = Path(..., description="Case id, for example CASE-4001.")):
        c = d()["cases"].get(case_id)
        if not c:
            raise not_found("case", case_id, "Case ids look like CASE-4001.")
        return c

    @reg(app, "post", "/cases", "open_case", "Open a case",
         "Open a case for a customer from one or more open alerts. The alerts move to status case_opened. Refused with 409 if an "
         "alert already belongs to a case. Returns the new case id.")
    def open_case(body: OpenCase):
        if body.customer_id not in d()["customers"]:
            raise not_found("customer", body.customer_id, "Customer ids look like CUS-1001.")
        with st.lock:
            alerts = []
            for aid in body.alert_ids:
                a = alert_or_404(aid)
                if a["customer_id"] != body.customer_id:
                    raise conflict(f"Alert {aid} belongs to {a['customer_id']}, not {body.customer_id}. Nothing was changed.")
                if a["case_id"] or a["status"] != "open":
                    raise conflict(f"Alert {aid} is not open or already has a case. Nothing was changed.")
                alerts.append(a)
            cid = f"CASE-{st.next_number('case', 4101)}"
            rec = {"case_id": cid, "customer_id": body.customer_id, "alert_ids": body.alert_ids, "status": "open",
                   "priority": body.priority, "summary": body.summary, "opened": ctx.settings.bank_today.isoformat(),
                   "opened_by": body.opened_by, "opened_at": now_iso(), "narratives": []}
            for a in alerts:
                a["case_id"], a["status"] = cid, "case_opened"
            d()["cases"][cid] = rec
            st.save()
        return {"applied": True, "kind": "change", "case": rec}

    @reg(app, "post", "/cases/{case_id}/narrative", "save_case_narrative", "Save a case narrative (draft)",
         "Save a narrative for a case together with the list of evidence it relies on. This is a draft: stored with who wrote it, "
         "a timestamp and a version number, earlier versions kept. Nothing is filed with anyone.")
    def save_case_narrative(body: Narrative, case_id: str = Path(..., description="Case id, for example CASE-4101.")):
        c = d()["cases"].get(case_id)
        if not c:
            raise not_found("case", case_id, "Use open_case first.")
        v = st.add_draft(c, "narratives", {"narrative": body.narrative, "evidence": [e.model_dump() for e in body.evidence]},
                         body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    return app
