"""Tests for the six added systems: itops, legacy, funds, crm, finance and research, and their three event kinds."""

import asyncio
import json
import sqlite3
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

import pytest
from openapi_spec_validator import validate

from bank.seed import build_all
from bank.seed_legacy import daily_interest
from bank.systems import finance as finance_module
from conftest import H, KEY, TODAY
from test_mcp import doc_ops, list_tools_streamable

TODAY_D = date.fromisoformat(TODAY)
TOMORROW = (TODAY_D + timedelta(days=1)).isoformat()
NEW = ["itops", "legacy", "funds", "crm", "finance", "research"]
OLD = ["core", "cards", "screening", "aml", "payments", "lending", "fraud", "recon", "news", "onboarding", "complaints", "collections", "audit"]
DASH = chr(0x2014)
ROOT = Path(__file__).resolve().parent.parent

EXPECTED = {
    "itops": {"list_incidents", "get_incident", "get_service_metrics", "get_dashboard_snapshot", "list_recent_changes", "get_runbook",
              "save_incident_assessment", "save_post_incident_review"},
    "legacy": {"list_legacy_tables", "get_legacy_table", "list_stored_procedures", "get_stored_procedure", "list_legacy_programs",
               "get_legacy_program", "save_legacy_documentation", "save_converted_program"},
    "funds": {"list_funds", "get_fund_fact_sheet", "get_member", "get_member_holdings", "list_contribution_batches", "get_contribution_batch",
              "get_transfer_form", "get_processing_procedure", "save_batch_result", "post_contribution_batch"},
    "crm": {"list_client_meetings", "get_client_meeting", "get_client_holdings", "list_client_interactions", "save_meeting_brief"},
    "finance": {"list_finance_tables", "describe_finance_table", "run_finance_query", "save_finance_commentary"},
    "research": {"list_research_companies", "list_company_filings", "get_company_filing", "get_price_history", "get_consensus_estimates",
                 "save_research_report"},
}
VERBS = {"list", "get", "save", "post", "describe", "run"}

GET_PATHS = ["/itops/incidents", "/itops/incidents/INC-7001", "/itops/metrics?service=payment-service", "/itops/dashboards/DASH-1001",
             "/itops/changes", "/itops/runbooks/payment-service", "/legacy/tables", "/legacy/tables/ACMAST", "/legacy/procedures",
             "/legacy/procedures/SP_POST_TXN", "/legacy/programs", "/legacy/programs/INTACCR", "/funds/funds", "/funds/funds/FND-3001/fact-sheet",
             "/funds/members/MEM-5001", "/funds/members/MEM-5001/holdings", "/funds/batches", "/funds/batches/BAT-4001", "/funds/forms/FRM-4001",
             "/funds/procedures", "/crm/meetings", "/crm/meetings/MTG-1001", "/crm/clients/CUS-1007/holdings", "/crm/clients/CUS-1007/interactions",
             "/finance/tables", "/finance/tables/accounts", "/research/companies", "/research/companies/RSC-6001/filings",
             "/research/companies/RSC-6001/filings/FIL-6101", "/research/companies/RSC-6001/prices", "/research/companies/RSC-6001/estimates"]
POSTS = [("/itops/incidents/INC-7001/assessment", {}), ("/itops/incidents/INC-7004/review", {}), ("/legacy/documentation", {}),
         ("/legacy/programs/INTACCR/conversion", {}), ("/funds/batches/BAT-4001/result", {}), ("/funds/batches/BAT-4001/post", {"approved_by": "x"}),
         ("/crm/meetings/MTG-1001/brief", {}), ("/finance/query", {"sql": "select 1"}), ("/finance/commentary", {}), ("/research/companies/RSC-6001/report", {})]


def get(client, path, **kw):
    r = client.get(path, headers=H, **kw)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body, status=200):
    r = client.post(path, json=body, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def mcp(client, system, method, params=None, mid=1):
    r = client.post(f"/{system}/mcp", json={"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}, headers=H)
    assert r.status_code == 200
    return r.json()["result"]


PLAIN = lambda m: m.endswith(".") and "  " not in m and DASH not in m and "\n" not in m


# ---------------------------------------------------------------- sign-in, documents, tools

def test_new_systems_need_a_key(client):
    for path in GET_PATHS:
        assert client.get(path).status_code == 401, path
        assert client.get(path, headers={"X-API-Key": "wrong"}).status_code == 401, path
        assert client.get(path, headers=H).status_code == 200, path
        assert client.get(path, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200, path
    for path, body in POSTS:
        assert client.post(path, json=body).status_code == 401, path
    for s in NEW:
        assert client.post(f"/{s}/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).status_code == 401
        assert client.get(f"/{s}/sse").status_code == 401
        assert client.get(f"/{s}/openapi.json").status_code == 200 and client.get(f"/{s}/docs").status_code == 200


def test_new_openapi_documents_are_valid_and_plain(client):
    for s in NEW:
        doc = client.get(f"/{s}/openapi.json").json()
        assert doc["openapi"] == "3.0.3"
        validate(doc)
        text = json.dumps(doc)
        assert "anyOf" not in text and "nullable" not in text and '"type": "null"' not in text, s
        assert "ApiKeyAuth" in doc["components"]["securitySchemes"]
        assert "invented" in doc["info"]["description"].split(".")[0].lower()
        assert DASH not in json.dumps(doc, ensure_ascii=False)
        for item in doc["paths"].values():
            for op in item.values():
                assert op["operationId"] == op["operationId"].lower() and all(c.isalnum() or c == "_" for c in op["operationId"])
                assert op["operationId"].split("_")[0] in VERBS, op["operationId"]
                assert op["summary"].strip() and len(op["description"]) > 80, op["operationId"]
                for p in op.get("parameters", []):
                    assert p.get("description"), (op["operationId"], p["name"])
                    assert p["schema"].get("type") in ("string", "integer", "number", "boolean"), (op["operationId"], p["name"])


def test_operations_per_system_and_unique_across_all_nineteen(client):
    seen, counts = [], {}
    for s in OLD + NEW:
        doc = client.get(f"/{s}/openapi.json").json()
        ids = [op["operationId"] for item in doc["paths"].values() for op in item.values()]
        counts[s] = len(ids)
        seen += ids
        if s in EXPECTED:
            assert set(ids) == EXPECTED[s], s
    assert {s: counts[s] for s in NEW} == {"itops": 8, "legacy": 8, "funds": 10, "crm": 5, "finance": 4, "research": 6}
    assert sum(counts[s] for s in NEW) == 41
    assert len(seen) == len(set(seen)) == 141


def test_itops_and_legacy_have_no_operation_that_changes_a_system(client):
    for s, saves in (("itops", {"save_incident_assessment", "save_post_incident_review"}), ("legacy", {"save_legacy_documentation", "save_converted_program"})):
        doc = client.get(f"/{s}/openapi.json").json()
        writes = {op["operationId"] for item in doc["paths"].values() for m, op in item.items() if m != "get"}
        assert writes == saves, s
    for name in ("run_runbook_step", "restart_service", "rollback_release", "execute_runbook", "run_conversion", "update_legacy_table"):
        assert not any(name in ids for ids in EXPECTED.values())


@pytest.mark.parametrize("system", NEW)
def test_every_operation_id_is_an_mcp_tool_of_its_system(client, system):
    ops = doc_ops(client, system)
    tools = mcp(client, system, "tools/list")["tools"]
    assert {t["name"] for t in tools} == set(ops) == EXPECTED[system]
    for t in tools:
        assert t["description"] == ops[t["name"]]["description"]


@pytest.mark.parametrize("system", NEW)
def test_every_new_operation_is_an_mcp_tool_streamable(live_server, client, system):
    tools = asyncio.run(list_tools_streamable(live_server, system))
    assert {t.name for t in tools} == EXPECTED[system]


def test_mcp_tool_calls_read_and_write_through(client, store):
    r = mcp(client, "itops", "tools/call", {"name": "get_incident", "arguments": {"incident_id": "INC-7002"}})
    assert json.loads(r["content"][0]["text"])["alert_id"] == "ALT-9102"
    args = {"incident_id": "INC-7002", "what_is_happening": "Card payments fail.", "likely_cause": "An expired certificate."}
    r = mcp(client, "itops", "tools/call", {"name": "save_incident_assessment", "arguments": args})
    assert "applied" in r["content"][0]["text"] and len(store.data["itops_incidents"]["INC-7002"]["assessments"]) == 1
    r = mcp(client, "funds", "tools/call", {"name": "post_contribution_batch", "arguments": {"batch_id": "BAT-4001", "approved_by": "A. Officer"}})
    assert r["isError"] is True and "409" in r["content"][0]["text"]
    r = mcp(client, "finance", "tools/call", {"name": "run_finance_query", "arguments": {"sql": "drop table accounts"}})
    assert r["isError"] is True and "400" in r["content"][0]["text"]
    r = mcp(client, "finance", "tools/call", {"name": "run_finance_query", "arguments": {"sql": "select count(*) as n from accounts"}})
    assert json.loads(r["content"][0]["text"])["rows"] == [[11]]


def test_landing_page_lists_all_nineteen_systems(client):
    text = client.get("/").text
    assert "The nineteen systems" in text and "The nine systems" not in text and "Four more systems" not in text
    for s in OLD + NEW:
        assert f"/{s}/openapi.json" in text and f"/{s}/mcp" in text and f"/{s}/docs" in text, s
    assert text.count("<tr><td><b>") == 19 and "http://" not in text.replace("http://testserver", "") and "https://" not in text
    assert "incident, contribution-batch, client-meeting" in text
    counts = get(client, "/admin/state")["counts"]
    assert counts["open_incidents"] == 3 and counts["legacy_programs"] == 4 and counts["received_contribution_batches"] == 2
    assert counts["upcoming_client_meetings"] == 4 and counts["finance_tables"] == 5 and counts["research_companies"] == 3


# ---------------------------------------------------------------- itops

def metric(client, service, name, **params):
    return get(client, "/itops/metrics", params={"service": service, **params})["measures"][name]


def test_incident_list_and_filter(client):
    rows = get(client, "/itops/incidents")["items"]
    assert [r["incident_id"] for r in rows][-1] == "INC-7004" and len(rows) == 4
    assert {r["incident_id"] for r in get(client, "/itops/incidents?status=open")["items"]} == {"INC-7001", "INC-7002", "INC-7003"}
    assert [r["incident_id"] for r in get(client, "/itops/incidents?status=closed")["items"]] == ["INC-7004"]
    assert client.get("/itops/incidents/INC-1", headers=H).status_code == 404


def test_inc_7001_slowdown_lines_up_with_the_release(client):
    inc = get(client, "/itops/incidents/INC-7001")
    chg = next(c for c in inc["linked_changes"] if c["change_id"] == "ITC-8101")
    released = datetime.fromisoformat(chg["implemented_at"])
    lat = metric(client, "payment-service", "latency_p95_ms")["points"]
    base = [p["value"] for p in lat if datetime.fromisoformat(p["time"]) < released + timedelta(minutes=10)]
    assert max(base) < 450
    first_bad = next(p for p in lat if p["value"] > 1.3 * max(base))
    assert datetime.fromisoformat(first_bad["time"]) - released == timedelta(minutes=20)
    assert lat[-1]["value"] > 3000
    cpu = metric(client, "payment-service", "payments_db_cpu_pct")["points"]
    assert cpu[0]["value"] < 40 and cpu[-1]["value"] > 90 and next(p for p in cpu if p["value"] > 50)["time"] == first_bad["time"]
    err = metric(client, "payment-service", "error_rate_pct")["summary"]
    assert err["first"] <= 0.3 and err["latest"] > 2.5
    assert "duplicate" in chg["description"] and "15 minutes" in chg["description"]
    assert inc["status"] == "open" and "payment-service" in inc["services_affected"]
    # the other changes of the day do not touch the payment path
    recent = get(client, "/itops/changes", params={"hours": 24})["items"]
    assert {c["change_id"] for c in recent} == {"ITC-8101", "ITC-8102", "ITC-8103"}
    assert get(client, "/itops/changes", params={"service": "payment-service", "hours": 24})["count"] == 1


def test_inc_7002_certificate_expiry_with_no_recent_change(client):
    inc = get(client, "/itops/incidents/INC-7002")
    assert inc["linked_changes"] == [] and inc["severity"] == "critical"
    assert get(client, "/itops/changes", params={"service": "card-authorisation", "hours": 168})["count"] == 0
    assert get(client, "/itops/changes", params={"service": "card-authorisation", "hours": 400})["items"][0]["change_id"] == "ITC-8104"
    err = metric(client, "card-authorisation", "error_rate_pct")["points"]
    step = next(p for p in err if p["value"] > 50)
    assert step["time"] == f"{TODAY}T05:00" and err[err.index(step) - 1]["value"] < 1
    assert metric(client, "card-authorisation", "volume_per_min")["summary"]["minimum"] > 30  # traffic did not stop: calls failed
    certs = get(client, "/itops/dashboards/DASH-1003")["panels"][0]["rows"]
    expired = [c for c in certs if c["status"] == "expired"]
    assert [c["certificate"] for c in expired] == ["cardproc-mtls-client"] and expired[0]["expires_at"] == f"{TODAY}T04:58"
    assert all(c["status"] == "valid" for c in certs if c["status"] != "expired") and len(certs) == 5
    assert any("certificate has expired" in t["entry"] for t in inc["timeline"])


def test_inc_7003_is_a_monitoring_gap_and_the_service_is_normal(client):
    m = get(client, "/itops/metrics", params={"service": "statement-service"})["measures"]
    gap = m["volume_per_min"]["gaps"]
    assert gap == [{"last_sample_before": f"{TODAY}T09:00", "next_sample_after": f"{TODAY}T09:50", "minutes_without_data": 50}]
    assert m["volume_from_app_log_per_min"]["gaps"] == [] and len(m["volume_from_app_log_per_min"]["points"]) == 13
    assert m["error_rate_pct"]["summary"]["maximum"] < 0.5 and m["latency_p95_ms"]["summary"]["maximum"] < 300
    collector_values = [p["value"] for p in m["volume_per_min"]["points"]]
    log_values = [p["value"] for p in m["volume_from_app_log_per_min"]["points"]]
    assert abs(sum(collector_values) / len(collector_values) - sum(log_values) / len(log_values)) < 1.5
    assert "collector" in m["volume_per_min"]["meaning"] and "does not use the collector" in m["volume_from_app_log_per_min"]["meaning"]
    assert get(client, "/itops/changes", params={"service": "statement-service", "hours": 168})["count"] == 0
    snap = get(client, "/itops/dashboards/DASH-1004")["panels"]
    assert all(p["status"] == "ok" for p in snap)


def test_inc_7004_closed_incident_shows_the_first_assumption_was_wrong(client):
    inc = get(client, "/itops/incidents/INC-7004")
    assert inc["status"] == "closed" and inc["closed_at"] and inc["resolved_at"] < inc["closed_at"]
    times = [t["time"] for t in inc["timeline"]]
    assert times == sorted(times) and len(times) >= 10
    texts = [t["entry"] for t in inc["timeline"]]
    pool = next(i for i, t in enumerate(texts) if "Suspected cause: database connection pool" in t)
    restart = next(i for i, t in enumerate(texts) if "Connection pool restarted" in t and "unchanged" in t)
    wrong = next(i for i, t in enumerate(texts) if "The pool is not the cause" in t)
    real = next(i for i, t in enumerate(texts) if "token signature invalid" in t)
    assert pool < restart < wrong < real
    chg = inc["linked_changes"][0]
    assert chg["change_id"] == "ITC-8106" and chg["implemented_at"].endswith("T14:02") and chg["scheduled_for"].endswith("T22:00")
    pool_use = metric(client, "online-banking", "db_pool_in_use_pct")["summary"]
    assert pool_use["maximum"] < 50
    err = metric(client, "online-banking", "error_rate_pct")
    assert err["summary"]["maximum"] > 20 and err["points"][0]["time"].startswith((TODAY_D - timedelta(days=9)).isoformat())
    first_error = next(p for p in err["points"] if p["value"] > 10)
    assert first_error["time"].endswith("T14:10") and first_error["time"] > chg["implemented_at"]


def test_metrics_filters_and_unknown_names(client):
    all_pts = metric(client, "payment-service", "latency_p95_ms")["points"]
    cut = metric(client, "payment-service", "latency_p95_ms", date_from=f"{TODAY}T08:30", date_to=f"{TODAY}T09:00")["points"]
    assert [p["time"] for p in cut] == [f"{TODAY}T08:30", f"{TODAY}T08:40", f"{TODAY}T08:50", f"{TODAY}T09:00"] and len(all_pts) == 19
    assert metric(client, "payment-service", "latency_p95_ms", date_to=TODAY)["points"] == all_pts
    assert metric(client, "payment-service", "latency_p95_ms", date_from="2099-01-01")["points"] == []
    assert metric(client, "payment-service", "latency_p95_ms")["unit"] == "milliseconds"
    assert client.get("/itops/metrics?service=nope", headers=H).status_code == 404
    assert client.get("/itops/metrics", headers=H).status_code == 422
    assert client.get("/itops/dashboards/DASH-9", headers=H).status_code == 404
    assert client.get("/itops/changes?hours=0", headers=H).status_code == 422


def test_dashboard_snapshot_statuses_follow_the_latest_values(client):
    panels = {p["title"]: p for p in get(client, "/itops/dashboards/DASH-1001")["panels"]}
    assert panels["Payment service p95 latency"]["status"] == "critical" and panels["Payment service p95 latency"]["latest_value"] == 3200
    assert panels["Payments database CPU"]["status"] == "critical" and panels["Payment service volume"]["status"] == "ok"
    cards = {p["title"]: p for p in get(client, "/itops/dashboards/DASH-1002")["panels"]}
    assert cards["Authorisation error rate"]["status"] == "critical" and cards["Authorisation p95 latency"]["status"] == "ok"


def test_runbooks_are_text_for_people_and_need_approval_for_changes(client):
    rb = get(client, "/itops/runbooks/payment-service")
    assert [s["step"] for s in rb["steps"]] == list(range(1, len(rb["steps"]) + 1))
    assert any("approves" in s["who_may_run_it"] for s in rb["steps"]) and "cannot run a step" in rb["note"]
    assert get(client, "/itops/runbooks/card-authorisation")["steps"][2]["action"].startswith("Open the certificate dashboard")
    assert client.get("/itops/runbooks/nope", headers=H).status_code == 404


def test_assessment_is_a_draft_with_versions_and_is_refused_on_a_closed_incident(client, store):
    body = {"what_is_happening": "Payments are slow since 08:20.", "likely_cause": "The new duplicate check in release 4.18.0.",
            "evidence_for": ["Latency rose 20 minutes after ITC-8101."], "evidence_against": ["Volume fell a little."],
            "next_checks": ["Read the runbook."], "customer_impact": "Slow payment screens."}
    metrics_before = json.dumps(store.data["itops_metrics"], sort_keys=True)
    a = post(client, "/itops/incidents/INC-7001/assessment", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "agent" and a["draft"]["drafted_at"]
    b = post(client, "/itops/incidents/INC-7001/assessment", {**body, "likely_cause": "Something else.", "drafted_by": "A. Analyst"})
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "A. Analyst"
    saved = get(client, "/itops/incidents/INC-7001")["assessments"]
    assert [x["version"] for x in saved] == [1, 2] and saved[0]["likely_cause"].startswith("The new duplicate")
    assert json.dumps(store.data["itops_metrics"], sort_keys=True) == metrics_before and store.data["itops_incidents"]["INC-7001"]["status"] == "open"
    closed = client.post("/itops/incidents/INC-7004/assessment", json=body, headers=H)
    assert closed.status_code == 409 and closed.json()["applied"] is False and "closed" in closed.json()["detail"]
    assert store.data["itops_incidents"]["INC-7004"]["assessments"] == []
    assert client.post("/itops/incidents/INC-1/assessment", json=body, headers=H).status_code == 404
    assert client.post("/itops/incidents/INC-7001/assessment", json={"likely_cause": "x"}, headers=H).status_code == 422


def test_post_incident_review_needs_a_closed_incident_and_blank_owners(client):
    body = {"timeline": [{"time": f"{TODAY}T14:02", "event": "The key was rotated."}], "root_cause": "The key rotation ran early and the cache kept the old key.",
            "what_went_well": ["The alert fired in 6 minutes."], "what_did_not": ["The first guess was the database."],
            "actions": [{"action": "Record the real time of a change."}]}
    early = client.post("/itops/incidents/INC-7001/review", json=body, headers=H)
    assert early.status_code == 409 and "still open" in early.json()["detail"]
    assert get(client, "/itops/incidents/INC-7001")["reviews"] == []
    named = client.post("/itops/incidents/INC-7004/review", json={**body, "actions": [{"action": "x", "owner": "Bram"}]}, headers=H)
    assert named.status_code == 422 and "owner" in named.json()["detail"]
    dated = client.post("/itops/incidents/INC-7004/review", json={**body, "actions": [{"action": "x", "due": "2026-12-01"}]}, headers=H)
    assert dated.status_code == 422
    ok = post(client, "/itops/incidents/INC-7004/review", body)
    assert ok["draft"]["version"] == 1 and ok["draft"]["actions"] == [{"action": "Record the real time of a change.", "owner": "", "due": ""}]
    again = post(client, "/itops/incidents/INC-7004/review", body)
    assert again["draft"]["version"] == 2 and len(get(client, "/itops/incidents/INC-7004")["reviews"]) == 2
    assert client.post("/itops/incidents/INC-7004/review", json={"root_cause": "x"}, headers=H).status_code == 422


# ---------------------------------------------------------------- legacy

def test_legacy_lists_and_reads(client):
    tables = get(client, "/legacy/tables")["items"]
    assert [t["table_name"] for t in tables] == ["CUMAST", "ACMAST", "TXHIST", "RTTAB", "SOMAST", "DRMLOG"]
    acm = get(client, "/legacy/tables/ACMAST")
    assert acm["row_count"] == 305992 and acm["primary_key"] == ["AC_NO"] and len(acm["columns"]) == 11 and len(acm["sample_rows"]) == 8
    assert get(client, "/legacy/tables/acmast")["table_name"] == "ACMAST"
    names = {c["name"] for c in acm["columns"]}
    assert all(set(r) == names for r in acm["sample_rows"])
    assert client.get("/legacy/tables/NOPE", headers=H).status_code == 404
    procs = get(client, "/legacy/procedures")["items"]
    assert len(procs) == 5 and all(p["line_count"] > 10 for p in procs)
    src = get(client, "/legacy/procedures/SP_POST_TXN")
    assert src["source"].startswith("CREATE PROCEDURE SP_POST_TXN") and len(src["source"].splitlines()) == src["line_count"]
    assert client.get("/legacy/procedures/NOPE", headers=H).status_code == 404
    progs = get(client, "/legacy/programs")["items"]
    assert [p["program_name"] for p in progs] == ["INTACCR", "STMTEXT", "DORMSWP", "SORUN"]
    for p in progs:
        full = get(client, f"/legacy/programs/{p['program_name']}")
        assert 60 <= full["line_count"] <= 150 and len(full["source"].splitlines()) == full["line_count"]
        assert f"PROGRAM-ID. {p['program_name']}." in full["source"]
    assert client.get("/legacy/programs/NOPE", headers=H).status_code == 404


def all_source(client):
    texts = [get(client, f"/legacy/procedures/{p}")["source"] for p in ("SP_POST_TXN", "SP_BAL_ENQ", "SP_RATE_FOR_ACCOUNT", "SP_FLAG_DORMANT", "SP_NEXT_SO_DATE")]
    texts += [get(client, f"/legacy/programs/{p}")["source"] for p in ("INTACCR", "STMTEXT", "DORMSWP", "SORUN")]
    return "\n".join(texts).upper()


def test_column_meanings_can_be_worked_out_except_one(client):
    src = all_source(client)
    acm = get(client, "/legacy/tables/ACMAST")
    unused = [c["name"] for c in acm["columns"] if c["name"] not in src and c["name"].replace("_", "-") not in src]
    assert unused == ["AC_X1"]
    assert all(c["catalogue_comment"] == "" for c in acm["columns"] if c["name"] in ("AC_BAL", "AC_X1", "AC_LTX"))
    rows = acm["sample_rows"]
    # AC_X1 is not a function of type, status, flags or balance: equal inputs give different values
    for key in ("AC_TY", "AC_ST", "AC_FLG1", "AC_FLG2"):
        assert any(a[key] == b[key] and a["AC_X1"] != b["AC_X1"] for a in rows for b in rows), key
    # the other columns show their meaning in the text and the sample rows
    assert "AC-BAL / 100" in src and "WHEN '30' MOVE 'BUSINESS CURRENT'" in src and "CU-SG = 'P'" in src and "AC-FLG1 = 'Y'" in src
    for r in rows:
        year, doy = divmod(r["AC_LTX"], 1000)
        d = date(year, 1, 1) + timedelta(days=doy - 1)
        assert date(2020, 1, 1) < d <= TODAY_D
    tx = get(client, "/legacy/tables/TXHIST")["sample_rows"]
    first = next(r for r in rows if r["AC_NO"] == "4410007731")
    last_customer_tx = max(t["TX_DT"] for t in tx if t["AC_NO"] == "4410007731" and t["TX_CD"] in ("101", "102", "201", "401", "402"))
    d = date(first["AC_LTX"] // 1000, 1, 1) + timedelta(days=first["AC_LTX"] % 1000 - 1)
    assert d.year * 10000 + d.month * 100 + d.day == last_customer_tx
    fee = max(t["TX_DT"] for t in tx if t["AC_NO"] == "4410008102" and t["TX_CD"] == "302")
    cheque = max(t["TX_DT"] for t in tx if t["AC_NO"] == "4410008102" and t["TX_CD"] == "102")
    own = next(r for r in rows if r["AC_NO"] == "4410008102")
    ltx = date(own["AC_LTX"] // 1000, 1, 1) + timedelta(days=own["AC_LTX"] % 1000 - 1)
    # a fee posted by the bank today does not move AC_LTX: it follows the customer's cheque of yesterday
    assert fee > cheque and ltx.year * 10000 + ltx.month * 100 + ltx.day == cheque


def test_sample_accrued_interest_follows_rule_fin_14(client):
    rows = get(client, "/legacy/tables/ACMAST")["sample_rows"]
    rates = {r["RT_CD"]: r["RT_BP"] for r in get(client, "/legacy/tables/RTTAB")["sample_rows"]}
    live = next(r for r in rows if r["AC_NO"] == "4410007732")
    daily = (Decimal(live["AC_BAL"]) / 100 * Decimal(rates[live["AC_RT"]]) / 10000 / 365).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    assert Decimal(str(live["AC_ACR"])) == daily * (TODAY_D.day - 1)
    od = next(r for r in rows if r["AC_NO"] == "4410008102")
    assert od["AC_BAL"] < 0 and od["AC_FLG1"] == "Y" and od["AC_ACR"] < 0
    assert Decimal(str(od["AC_ACR"])) == (Decimal(od["AC_BAL"]) / 100 * Decimal(rates["ROD"]) / 10000 / 365).quantize(Decimal("0.000001"), rounding=ROUND_DOWN) * (TODAY_D.day - 1)
    assert next(r for r in rows if r["AC_ST"] == "D")["AC_ACR"] == 0 and next(r for r in rows if r["AC_ST"] == "C")["AC_ACR"] == 0


def test_interest_program_has_a_rounding_rule_that_a_careless_conversion_changes(client):
    src = get(client, "/legacy/programs/INTACCR")["source"]
    daily_line = next(l for l in src.splitlines() if "COMPUTE WS-DAILY" in l)
    assert "ROUNDED" not in daily_line and "RULE FIN-14" in src and "TRUNCATED AT SIX DECIMALS" in src
    assert "COMPUTE WS-POST ROUNDED" in src and "SUBTRACT WS-POST FROM AC-ACR" in src and "365 ALWAYS" in src
    bal, code, days = 1234567, "R03", 30
    exact = daily_interest(bal, code)
    careless_daily = (Decimal(bal) / 100 * Decimal(325) / 10000 / 365).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    float_daily = round(bal / 100 * 0.0325 / 365, 2)
    rule_total = (exact * days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert exact == Decimal("1.099271")
    assert rule_total == Decimal("32.98") and careless_daily * days == Decimal("33.00") and round(float_daily * days, 2) == 33.0
    assert rule_total != careless_daily * days
    # the carry: what is left below one cent stays in the account for next month
    carry = exact * days - rule_total
    assert carry == Decimal("-0.00187")
    # halves go away from zero, not to the even digit
    half = Decimal("0.125")
    assert half.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("0.13") and half.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN) == Decimal("0.12")
    assert Decimal("-0.125").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("-0.13")


def test_legacy_documentation_draft(client, store):
    body = {"object_type": "table", "object_name": "ACMAST", "explanation": "The account master.",
            "columns": [{"column": "AC_BAL", "meaning": "Balance in the smallest unit.", "confidence": "high", "evidence": "SP_BAL_ENQ divides by 100."},
                        {"column": "AC_X1", "meaning": "", "confidence": "cannot_determine", "evidence": "Nothing reads or writes it."}],
            "assumptions": ["The currency is one for the whole table."]}
    a = post(client, "/legacy/documentation", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "agent"
    assert a["draft"]["columns"][1]["confidence"] == "cannot_determine"
    b = post(client, "/legacy/documentation", {**body, "explanation": "Second.", "drafted_by": "A. Engineer"})
    assert b["draft"]["version"] == 2
    saved = get(client, "/legacy/tables/ACMAST")["documentation_drafts"]
    assert [x["version"] for x in saved] == [1, 2] and saved[0]["explanation"] == "The account master."
    assert get(client, "/legacy/tables/ACMAST")["row_count"] == 305992
    p = post(client, "/legacy/documentation", {"object_type": "procedure", "object_name": "sp_post_txn", "explanation": "Posts one transaction."})
    assert p["draft"]["version"] == 1 and len(store.data["legacy_procedures"]["SP_POST_TXN"]["documentation_drafts"]) == 1
    assert client.post("/legacy/documentation", json={**body, "object_name": "NOPE"}, headers=H).status_code == 404
    bad = client.post("/legacy/documentation", json={**body, "columns": [{"column": "AC_ZZ", "confidence": "high"}]}, headers=H)
    assert bad.status_code == 422 and "AC_ZZ" in bad.json()["detail"]
    assert client.post("/legacy/documentation", json={"object_type": "program", "object_name": "INTACCR", "explanation": "x", "columns": body["columns"]}, headers=H).status_code == 422
    assert client.post("/legacy/documentation", json={**body, "columns": [{"column": "AC_BAL", "confidence": "sure"}]}, headers=H).status_code == 422


def test_converted_program_draft_needs_points_to_check(client, store):
    body = {"target_language": "Python", "converted_source": "def accrue(): ...", "stage": "draft_translation",
            "points_to_check": ["Daily interest is truncated at six decimals, not rounded."]}
    a = post(client, "/legacy/programs/INTACCR/conversion", body)
    assert a["draft"]["version"] == 1 and a["draft"]["stage"] == "draft_translation" and a["program"] == "INTACCR"
    b = post(client, "/legacy/programs/intaccr/conversion", {**body, "stage": "tests_written"})
    assert b["draft"]["version"] == 2
    assert [x["stage"] for x in get(client, "/legacy/programs/INTACCR")["conversions"]] == ["draft_translation", "tests_written"]
    assert client.post("/legacy/programs/INTACCR/conversion", json={**body, "points_to_check": []}, headers=H).status_code == 422
    assert client.post("/legacy/programs/INTACCR/conversion", json={**body, "stage": "done"}, headers=H).status_code == 422
    assert client.post("/legacy/programs/NOPE/conversion", json=body, headers=H).status_code == 404
    assert store.data["legacy_programs"]["INTACCR"]["source"] == get(client, "/legacy/programs/INTACCR")["source"]


# ---------------------------------------------------------------- funds

def rules_broken(rows, members):
    """The processing rules 1 to 4, written out again here so that the test does not use the service's own check."""
    out, seen = {}, set()
    for r in rows:
        f = []
        if r["member_id"] not in members:
            f.append(1)
        if r["employee_amount"] < 0 or r["employer_amount"] < 0:
            f.append(2)
        if r["member_id"] in seen:
            f.append(3)
        seen.add(r["member_id"])
        if r["employer_amount"] < 0.03 * r["pensionable_salary"] - 0.005:
            f.append(4)
        if f:
            out[r["row_no"]] = f
    return out


def test_fund_fact_sheets(client):
    funds = get(client, "/funds/funds")["items"]
    assert [f["fund_id"] for f in funds] == ["FND-3001", "FND-3002", "FND-3003", "FND-3004", "FND-3005"]
    sheet = get(client, "/funds/funds/FND-3003/fact-sheet")
    assert sheet["as_of"] == "2026-10-31" and f"Fact sheet as at {sheet['as_of']}" in sheet["fact_sheet_text"]
    assert sheet["risk_level"] == 6 and "Risk level: 6" in sheet["fact_sheet_text"]
    assert sheet["annual_management_charge_pct"] == 0.75 and "Annual management charge: 0.75 percent" in sheet["fact_sheet_text"]
    assert sheet["returns_pct"]["1 year"] == 14.2 and "1 year: 14.2" in sheet["fact_sheet_text"]
    assert client.get("/funds/funds/FND-9/fact-sheet", headers=H).status_code == 404


def test_a_question_the_fact_sheets_cannot_answer(client):
    young = get(client, "/funds/funds/FND-3002/fact-sheet")
    assert young["returns_pct"]["5 years a year"] is None and "5 years a year: not shown" in young["fact_sheet_text"]
    assert (TODAY_D - date.fromisoformat(young["launched"])).days < 5 * 365
    old = get(client, "/funds/funds/FND-3003/fact-sheet")
    assert old["returns_pct"]["5 years a year"] == 9.4 and (TODAY_D - date.fromisoformat(old["launched"])).days > 5 * 365
    assert get(client, "/funds/funds/FND-3005/fact-sheet")["returns_pct"]["3 years a year"] is None
    for f in get(client, "/funds/funds")["items"]:
        text = get(client, f"/funds/funds/{f['fund_id']}/fact-sheet")["fact_sheet_text"]
        assert "calendar year" in text and "does not show calendar years" in text


def test_member_with_holdings_in_three_funds_agrees_with_core(client):
    m = get(client, "/funds/members/MEM-5001")
    cust = get(client, "/core/customers/CUS-1011")
    assert m["customer_id"] == "CUS-1011" and m["name"] == cust["name"] and m["date_of_birth"] == cust["date_of_birth"] and m["address"] == cust["address"]
    tx = get(client, "/core/accounts/ACC-1011-01/transactions", params={"limit": 500})["items"]
    assert {t["counterparty"] for t in tx if t["type"] == "salary"} == {m["employer"]}
    h = get(client, "/funds/members/MEM-5001/holdings")
    assert [r["fund_id"] for r in h["holdings"]] == ["FND-3001", "FND-3002", "FND-3003"]
    for r in h["holdings"]:
        price = get(client, f"/funds/funds/{r['fund_id']}/fact-sheet")["unit_price"]
        assert r["unit_price"] == price and r["value"] == round(r["units"] * price, 2)
    assert h["total_value"] == round(sum(r["value"] for r in h["holdings"]), 2) == 29676.74
    assert len(get(client, "/funds/members/MEM-5003/holdings")["holdings"]) == 2
    assert client.get("/funds/members/MEM-9/holdings", headers=H).status_code == 404 and client.get("/funds/members/MEM-9", headers=H).status_code == 404


def test_members_who_are_customers_agree_with_the_core(client):
    for mid in ("MEM-5002", "MEM-5006", "MEM-5007"):
        m = get(client, f"/funds/members/{mid}")
        cust = get(client, f"/core/customers/{m['customer_id']}")
        assert (m["name"], m["date_of_birth"], m["address"]) == (cust["name"], cust["date_of_birth"], cust["address"])
        acc = get(client, f"/core/customers/{m['customer_id']}/accounts")["items"][0]["account_id"]
        tx = get(client, f"/core/accounts/{acc}/transactions", params={"limit": 500})["items"]
        assert {t["counterparty"] for t in tx if t["type"] == "salary"} == {m["employer"]}
    assert get(client, "/funds/members/MEM-5004")["customer_id"] == ""


def test_batches_clean_and_faulty(client):
    rows = get(client, "/funds/batches")["items"]
    assert [(r["batch_id"], r["status"], r["row_count"]) for r in rows] == [("BAT-4001", "received", 5), ("BAT-4002", "received", 6), ("BAT-4003", "posted", 2)]
    assert [r["batch_id"] for r in get(client, "/funds/batches?status=received")["items"]] == ["BAT-4001", "BAT-4002"]
    assert [r["batch_id"] for r in get(client, "/funds/batches?status=posted")["items"]] == ["BAT-4003"]
    members = {mid: 1 for mid in ("MEM-5001", "MEM-5002", "MEM-5003", "MEM-5004", "MEM-5005", "MEM-5006", "MEM-5007", "MEM-5008", "MEM-5009")}
    clean = get(client, "/funds/batches/BAT-4001")
    assert rules_broken(clean["rows"], members) == {} and clean["control_total"] == round(sum(r["employee_amount"] + r["employer_amount"] for r in clean["rows"]), 2)
    assert {r["member_id"] for r in clean["rows"]} <= set(members) and all(get(client, f"/funds/members/{r['member_id']}")["employer"] == clean["employer"] for r in clean["rows"])
    bad = get(client, "/funds/batches/BAT-4002")
    assert rules_broken(bad["rows"], members) == {4: [1], 5: [3], 6: [2]}
    assert bad["rows"][3]["member_id"] == "MEM-5040" and client.get("/funds/members/MEM-5040", headers=H).status_code == 404
    assert bad["rows"][4]["member_id"] == bad["rows"][1]["member_id"] and bad["rows"][5]["employee_amount"] == -85.0
    assert client.get("/funds/batches/BAT-9", headers=H).status_code == 404


def test_transfer_forms_and_procedure(client):
    unreadable = get(client, "/funds/forms/FRM-4001")
    line = next(l for l in unreadable["text"].splitlines() if l.startswith("Receiving scheme account number"))
    assert "[unreadable]" in line and "[4 or 9]" in line
    good = get(client, "/funds/forms/FRM-4002")
    line = next(l for l in good["text"].splitlines() if l.startswith("Receiving scheme account number"))
    assert "[" not in line and len(line.split(":")[1].split()) == 10
    assert client.get("/funds/forms/FRM-9", headers=H).status_code == 404
    proc = get(client, "/funds/procedures")
    assert [r["rule_no"] for r in proc["rules"]] == list(range(1, 9))
    assert {r["applies_to"] for r in proc["rules"][:4]} == {"contribution row"} and {r["applies_to"] for r in proc["rules"][4:]} == {"transfer form"}
    assert "goes to a person" in proc["rules"][7]["text"] and "never guessed" in proc["rules"][7]["text"]


def result(batch, failed=None):
    failed = failed or {}
    return {"rows": [{"row_no": r["row_no"], "outcome": "failed" if r["row_no"] in failed else "passed", "failed_rules": failed.get(r["row_no"], [])}
                     for r in batch["rows"]], "summary": "Checked."}


def test_save_batch_result_is_a_draft_with_checks(client, store):
    b = get(client, "/funds/batches/BAT-4002")
    first = post(client, "/funds/batches/BAT-4002/result", result(b, {4: [1], 5: [3], 6: [2]}))
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1 and first["draft"]["drafted_by"] == "agent"
    second = post(client, "/funds/batches/BAT-4002/result", {**result(b, {4: [1], 5: [3], 6: [2]}), "drafted_by": "A. Checker"})
    assert second["draft"]["version"] == 2
    saved = get(client, "/funds/batches/BAT-4002")["results"]
    assert [x["version"] for x in saved] == [1, 2] and saved[0]["drafted_by"] == "agent"
    assert store.data["pension_batches"]["BAT-4002"]["status"] == "received" and get(client, "/funds/members/MEM-5009/holdings")["total_value"] == round(150.0 * 3.452, 2)
    short = result(b)
    short["rows"].pop()
    assert client.post("/funds/batches/BAT-4002/result", json=short, headers=H).status_code == 422
    twice = result(b)
    twice["rows"][1] = dict(twice["rows"][0])
    assert client.post("/funds/batches/BAT-4002/result", json=twice, headers=H).status_code == 422
    no_rule = result(b)
    no_rule["rows"][3]["outcome"] = "failed"
    assert client.post("/funds/batches/BAT-4002/result", json=no_rule, headers=H).status_code == 422
    stray = result(b, {4: [1]})
    stray["rows"][0]["failed_rules"] = [2]
    assert client.post("/funds/batches/BAT-4002/result", json=stray, headers=H).status_code == 422
    assert client.post("/funds/batches/BAT-4002/result", json=result(b, {4: [9]}), headers=H).status_code == 422
    assert client.post("/funds/batches/BAT-4002/result", json={"rows": []}, headers=H).status_code == 422
    assert client.post("/funds/batches/BAT-9/result", json=result(b), headers=H).status_code == 404
    done = client.post("/funds/batches/BAT-4003/result", json=result(get(client, "/funds/batches/BAT-4003")), headers=H)
    assert done.status_code == 409 and done.json()["applied"] is False and "already posted" in done.json()["detail"]
    assert len(store.data["pension_batches"]["BAT-4002"]["results"]) == 2


def test_post_batch_changes_holdings_and_status(client, store):
    b = get(client, "/funds/batches/BAT-4001")
    before = get(client, "/funds/members/MEM-5001/holdings")
    early = client.post("/funds/batches/BAT-4001/post", json={"approved_by": "A. Officer"}, headers=H)
    assert early.status_code == 409 and "no saved result" in early.json()["detail"] and early.json()["applied"] is False
    post(client, "/funds/batches/BAT-4001/result", result(b))
    assert client.post("/funds/batches/BAT-4001/post", json={}, headers=H).status_code == 422
    assert client.post("/funds/batches/BAT-4001/post", json={"approved_by": ""}, headers=H).status_code == 422
    assert store.data["pension_batches"]["BAT-4001"]["status"] == "received"
    done = post(client, "/funds/batches/BAT-4001/post", {"approved_by": "A. Officer", "note": "Checked."})
    assert done["applied"] is True and done["kind"] == "change" and done["status"] == "posted"
    assert done["posted"]["approved_by"] == "A. Officer" and done["posted"]["rows_posted"] == [1, 2, 3, 4, 5] and done["posted"]["rows_not_posted"] == []
    assert done["posted"]["amount_posted"] == b["control_total"]
    after = get(client, "/funds/members/MEM-5001/holdings")
    f2 = next(r for r in after["holdings"] if r["fund_id"] == "FND-3002")["units"]
    assert f2 == round(6800.0 + round((179.5 + 215.4) / 2.0715, 4), 4)
    assert after["total_value"] > before["total_value"]
    assert get(client, "/funds/batches/BAT-4001")["status"] == "posted"
    again = client.post("/funds/batches/BAT-4001/post", json={"approved_by": "A. Officer"}, headers=H)
    assert again.status_code == 409 and "already posted" in again.json()["detail"]
    assert get(client, "/funds/members/MEM-5001/holdings") == after
    assert client.post("/funds/batches/BAT-9/post", json={"approved_by": "x"}, headers=H).status_code == 404
    assert client.post("/funds/batches/BAT-4003/post", json={"approved_by": "x"}, headers=H).status_code == 409


def test_post_batch_posts_only_the_rows_that_passed_and_checks_the_result(client, store):
    b = get(client, "/funds/batches/BAT-4002")
    wrong = client.post("/funds/batches/BAT-4002/result", json=result(b), headers=H)
    assert wrong.status_code == 200
    refused = client.post("/funds/batches/BAT-4002/post", json={"approved_by": "A. Officer"}, headers=H)
    assert refused.status_code == 409 and "Row 4" in refused.json()["detail"] and "rule 1" in refused.json()["detail"]
    assert store.data["pension_batches"]["BAT-4002"]["status"] == "received" and "MEM-5040" not in store.data["pension_holdings"]
    post(client, "/funds/batches/BAT-4002/result", result(b, {4: [1], 5: [3], 6: [2]}))
    before = {m: get(client, f"/funds/members/{m}/holdings")["total_value"] for m in ("MEM-5006", "MEM-5007", "MEM-5008", "MEM-5009")}
    done = post(client, "/funds/batches/BAT-4002/post", {"approved_by": "A. Officer"})
    assert done["posted"]["rows_posted"] == [1, 2, 3] and done["posted"]["rows_not_posted"] == [4, 5, 6]
    assert done["posted"]["amount_posted"] == round(sum(r["employee_amount"] + r["employer_amount"] for r in b["rows"][:3]), 2)
    after = {m: get(client, f"/funds/members/{m}/holdings")["total_value"] for m in before}
    assert after["MEM-5006"] > before["MEM-5006"] and after["MEM-5008"] > before["MEM-5008"] and after["MEM-5007"] > before["MEM-5007"]
    assert after["MEM-5009"] == before["MEM-5009"]
    # a batch with nothing that passed has nothing to post
    c = post(client, "/admin/simulate/contribution-batch", {})
    post(client, f"/funds/batches/{c['item_id']}/result", {"rows": [{"row_no": r["row_no"], "outcome": "failed", "failed_rules": [1]} for r in
                                                                 get(client, f"/funds/batches/{c['item_id']}")["rows"]]})
    none = client.post(f"/funds/batches/{c['item_id']}/post", json={"approved_by": "A. Officer"}, headers=H)
    assert none.status_code == 409 and "nothing to post" in none.json()["detail"]


# ---------------------------------------------------------------- crm

def test_tomorrows_meetings_for_one_manager(client):
    rows = get(client, "/crm/meetings", params={"date": TOMORROW, "relationship_manager": "Sunniva Haldane-Rook"})["items"]
    assert [(r["meeting_id"], r["customer_id"], r["time"]) for r in rows] == [("MTG-1001", "CUS-1007", "09:30"), ("MTG-1002", "CUS-1018", "11:00"),
                                                                           ("MTG-1003", "CUS-1011", "14:30")]
    assert all(r["date"] == TOMORROW and r["status"] == "scheduled" for r in rows)
    assert len(get(client, "/crm/meetings", params={"date": TOMORROW})["items"]) == 4
    assert [r["meeting_id"] for r in get(client, "/crm/meetings", params={"relationship_manager": "bertil ashgrove-nye"})["items"]] == ["MTG-1004"]
    assert len(get(client, "/crm/meetings")["items"]) == 6 and get(client, "/crm/meetings", params={"date": "2030-01-01"})["count"] == 0
    one = get(client, "/crm/meetings/MTG-1001")
    assert one["client"]["name"] == "Valdis Orrenmoor" and one["relationship_manager"] == "Sunniva Haldane-Rook" and one["briefs"] == []
    assert client.get("/crm/meetings/MTG-9", headers=H).status_code == 404


def test_meeting_one_has_adverse_press_meeting_two_a_loan_in_progress_meeting_three_nothing_new(client):
    for cid, expect in (("CUS-1007", {"ART-6001", "ART-6002"}), ("CUS-1018", {"ART-6012"}), ("CUS-1011", set())):
        name = get(client, f"/core/customers/{cid}")["name"]
        hits = get(client, "/news/articles", params={"text": name})["items"]
        assert {h["article_id"] for h in hits} == expect, cid
    apps = {cid: [a["application_id"] for a in get(client, "/crm/clients/" + cid + "/holdings")["lending"]["applications_in_progress"]] for cid in ("CUS-1007", "CUS-1018", "CUS-1011")}
    assert apps == {"CUS-1007": [], "CUS-1018": ["LAP-8003"], "CUS-1011": []}
    assert get(client, "/lending/applications/LAP-8003")["customer_id"] == "CUS-1018"
    assert get(client, "/crm/clients/CUS-1011/interactions")["count"] == 0
    assert get(client, "/news/articles", params={"text": "Pinecrest"})["items"][0]["title"].endswith("wins the export award")
    assert all(c["customer_id"] != "CUS-1011" for c in get(client, "/complaints/complaints")["items"])


def test_client_holdings_agree_with_the_other_systems(client):
    h = get(client, "/crm/clients/CUS-1011/holdings")
    accounts = get(client, "/core/customers/CUS-1011/accounts")["items"]
    assert h["deposits"]["total_usd"] == round(sum(a["balance"] for a in accounts), 2) == h["totals"]["deposits_usd"]
    assert {a["account_id"] for a in h["deposits"]["accounts"]} == {a["account_id"] for a in accounts}
    assert h["investments"]["total_usd"] == get(client, "/funds/members/MEM-5001/holdings")["total_value"] == h["totals"]["investments_usd"]
    assert h["investments"]["pension_member_id"] == "MEM-5001" and len(h["investments"]["holdings"]) == 3
    p = get(client, "/crm/clients/CUS-1018/holdings")
    exposure = get(client, "/core/customers/CUS-1018/exposure")
    assert p["lending"]["total_outstanding_usd"] == exposure["total_outstanding_loans"] == p["totals"]["lending_outstanding_usd"] == 180000.0
    assert [x["loan_id"] for x in p["lending"]["loans"]] == ["LN-9002"] and p["investments"]["holdings"] == [] and p["investments"]["pension_member_id"] == ""
    assert get(client, "/crm/clients/CUS-1013/holdings")["totals"]["lending_outstanding_usd"] == get(client, "/core/customers/CUS-1013/exposure")["total_outstanding_loans"]
    euro = get(client, "/crm/clients/CUS-1022/holdings")["deposits"]
    assert euro["accounts_in_other_currencies"] == ["ACC-1022-03"] and euro["total_usd"] == round(sum(a["balance"] for a in euro["accounts"] if a["currency"] == "USD"), 2)
    assert client.get("/crm/clients/CUS-9999/holdings", headers=H).status_code == 404


def test_holdings_follow_a_posting(client):
    before = get(client, "/crm/clients/CUS-1011/holdings")["investments"]["total_usd"]
    b = get(client, "/funds/batches/BAT-4001")
    post(client, "/funds/batches/BAT-4001/result", result(b))
    post(client, "/funds/batches/BAT-4001/post", {"approved_by": "A. Officer"})
    after = get(client, "/crm/clients/CUS-1011/holdings")["investments"]["total_usd"]
    assert after == get(client, "/funds/members/MEM-5001/holdings")["total_value"] and after > before


def test_client_interactions(client):
    rows = get(client, "/crm/clients/CUS-1007/interactions")["items"]
    assert [r["id"] for r in rows] == ["MTG-1006"] and "legal dispute" in rows[0]["summary"] and rows[0]["kind"] == "meeting"
    mixed = get(client, "/crm/clients/CUS-1018/interactions")["items"]
    assert [r["kind"] for r in mixed] == ["email", "meeting"] and [r["date"] for r in mixed] == sorted([r["date"] for r in mixed], reverse=True)
    assert mixed[0]["id"].startswith("CNT-") and "LAP-8003" in mixed[0]["summary"] and mixed[1]["id"] == "MTG-1005"
    assert any(r["kind"] == "complaint" for r in get(client, "/crm/clients/CUS-1009/interactions")["items"])
    assert client.get("/crm/clients/CUS-9999/interactions", headers=H).status_code == 404


def test_meeting_brief_is_a_draft_with_versions(client, store):
    body = {"summary": "Mr Orrenmoor reviews his savings.", "talking_points": ["Savings."], "points_to_raise_with_care": ["Press coverage ART-6001."],
            "sources": ["news ART-6001"]}
    a = post(client, "/crm/meetings/MTG-1001/brief", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "agent"
    b = post(client, "/crm/meetings/MTG-1001/brief", {**body, "drafted_by": "S. Haldane-Rook"})
    assert b["draft"]["version"] == 2
    assert [x["version"] for x in get(client, "/crm/meetings/MTG-1001")["briefs"]] == [1, 2] and store.data["crm_meetings"]["MTG-1002"]["briefs"] == []
    assert client.post("/crm/meetings/MTG-9/brief", json=body, headers=H).status_code == 404
    assert client.post("/crm/meetings/MTG-1001/brief", json={"talking_points": []}, headers=H).status_code == 422


# ---------------------------------------------------------------- finance

def run(client, sql, **kw):
    return client.post("/finance/query", json={"sql": sql, **kw}, headers=H)


def rows_of(client, sql):
    r = run(client, sql)
    assert r.status_code == 200, r.text
    return r.json()["rows"]


OPEX = "from gl_monthly g join accounts a using (account_code) where a.is_operating_cost = 1"


def test_finance_tables_and_description(client):
    tables = get(client, "/finance/tables")["items"]
    assert {t["table_name"]: t["row_count"] for t in tables} == {"cost_centres": 8, "accounts": 11, "products": 6, "branches": 4, "gl_monthly": 1440}
    gl = get(client, "/finance/tables/gl_monthly")
    assert [c["name"] for c in gl["columns"]] == ["period", "cc_code", "account_code", "product_code", "branch_id", "actual", "budget"]
    assert all(c["description"] for c in gl["columns"]) and gl["first_period"] == "2024-11" and gl["last_period"] == "2026-10" and len(gl["first_rows"]) == 5
    assert rows_of(client, "select count(distinct period) from gl_monthly") == [[24]]
    assert get(client, "/finance/tables/GL_MONTHLY")["table_name"] == "gl_monthly"
    assert client.get("/finance/tables/payroll", headers=H).status_code == 404


def test_known_answer_operating_cost_last_month_against_budget(client, store):
    actual, budget = rows_of(client, f"select sum(actual), sum(budget) {OPEX} and period = '2026-10'")[0]
    assert (actual, budget) == (2743079, 2666664) and actual - budget == 76415 and round(100 * (actual - budget) / budget, 2) == 2.87
    t = store.data["finance"]["gl_monthly"]["rows"]
    ops = {a[0] for a in store.data["finance"]["accounts"]["rows"] if a[4] == 1}
    assert sum(r[5] for r in t if r[0] == "2026-10" and r[2] in ops) == actual and sum(r[6] for r in t if r[0] == "2026-10" and r[2] in ops) == budget
    all_in = rows_of(client, "select sum(actual) from gl_monthly g join accounts a using (account_code) where a.account_type = 'expense' and period = '2026-10'")[0][0]
    assert all_in > actual  # interest expense and impairment are not operating cost


def test_known_answer_cost_centre_with_the_largest_overspend_year_to_date(client):
    rows = rows_of(client, f"select cc_code, sum(actual - budget) as over {OPEX} and period between '2026-01' and '2026-10' group by cc_code order by over desc")
    assert rows[0] == ["CC300", 338325] and rows[1] == ["CC600", 212869] and rows[2][0] == "CC400" and rows[-1] == ["CC700", -4388]
    pct = rows_of(client, f"select cc_code, round(100.0 * sum(actual - budget) / sum(budget), 2) as p {OPEX} and period between '2026-01' and '2026-10' group by cc_code order by p desc")
    assert pct[0] == ["CC600", 12.09] and pct[1] == ["CC300", 5.31]
    name = rows_of(client, "select cc_name from cost_centres where cc_code = 'CC300'")
    assert name == [["Technology"]]
    last = rows_of(client, f"select cc_code, sum(actual - budget) as over {OPEX} and period = '2026-10' group by cc_code order by over desc limit 1")
    assert last == [["CC300", 33202]]


def test_known_answer_net_interest_income_by_month(client):
    rows = rows_of(client, "select period, sum(case when account_code = 4100 then actual else -actual end) from gl_monthly where account_code in (4100, 5100) "
                           "and period >= '2026-05' group by period order by period")
    assert rows == [["2026-05", 1348295], ["2026-06", 1308599], ["2026-07", 1321319], ["2026-08", 1362059], ["2026-09", 1321715], ["2026-10", 1388881]]
    income = rows_of(client, "select period, sum(actual) from gl_monthly where account_code = 4100 and period = '2026-10' group by period")
    expense = rows_of(client, "select period, sum(actual) from gl_monthly where account_code = 5100 and period = '2026-10' group by period")
    assert income[0][1] - expense[0][1] == 1388881 and (income[0][1], expense[0][1]) == (2205506, 816625)


def test_a_question_the_warehouse_cannot_answer(client):
    for t in get(client, "/finance/tables")["items"]:
        d = get(client, f"/finance/tables/{t['table_name']}")
        text = json.dumps(d).lower()
        for word in ("headcount", "fte", "employees", "staff_count", "churn", "customers"):
            assert word not in text, (t["table_name"], word)
    bad = run(client, "select headcount from cost_centres")
    assert bad.status_code == 400 and "no such column" in bad.json()["detail"] and bad.json()["applied"] is False
    assert run(client, "select * from headcount").status_code == 400


@pytest.mark.parametrize("sql,needle", [
    ("drop table accounts", "SELECT"), ("delete from accounts", "SELECT"), ("update accounts set category = 'x'", "SELECT"),
    ("insert into accounts values (1, 2, 3, 4, 5)", "SELECT"), ("pragma table_info(accounts)", "SELECT"), ("attach database 'x.db' as x", "SELECT"),
    ("create table t (a int)", "SELECT"), ("vacuum", "SELECT"), ("select 1; select 2", "one statement"), ("select 1; drop table accounts", "one statement"),
    ("select 1 -- a comment", "Comments"), ("select /* x */ 1", "Comments"), ("with x as (select 1) delete from accounts", "DELETE"),
    ("select 'open", "quote"), ("explain select 1", "SELECT")])
def test_anything_that_is_not_one_select_is_refused_and_nothing_changes(client, store, sql, needle):
    before = json.dumps(store.data["finance"], sort_keys=True)
    r = client.post("/finance/query", json={"sql": sql}, headers=H)
    assert r.status_code == 400 and r.json()["applied"] is False and needle.lower() in r.json()["detail"].lower(), r.text
    assert json.dumps(store.data["finance"], sort_keys=True) == before
    assert rows_of(client, "select count(*) from accounts") == [[11]]


def test_an_empty_query_is_refused(client):
    r = client.post("/finance/query", json={"sql": "   "}, headers=H)
    assert r.status_code == 400 and "empty" in r.json()["detail"]


def test_reading_queries_are_allowed_in_their_plain_forms(client):
    assert rows_of(client, "select 'a;b' as x") == [["a;b"]]
    assert rows_of(client, "SELECT 1;") == [[1]] and rows_of(client, "  select 2  ;  ") == [[2]]
    assert rows_of(client, "select 'it''s' as x") == [["it's"]]
    assert rows_of(client, "with t as (select 5 as n) select n * 2 from t") == [[10]]
    assert rows_of(client, "select 'drop table x'") == [["drop table x"]]
    assert rows_of(client, "select count(*) from sqlite_master where name = 'accounts'") == [[1]]


def test_rows_are_capped_and_runaway_queries_are_stopped(client):
    r = run(client, "select * from gl_monthly").json()
    assert r["row_count"] == 100 and r["truncated"] is True and r["row_cap"] == 200 and len(r["columns"]) == 7
    r = run(client, "select * from gl_monthly", max_rows=200).json()
    assert r["row_count"] == 200 and r["truncated"] is True
    r = run(client, "select * from products", max_rows=5).json()
    assert r["row_count"] == 5 and r["truncated"] is True
    r = run(client, "select * from products", max_rows=6).json()
    assert r["row_count"] == 6 and r["truncated"] is False
    assert run(client, "select 1", max_rows=500).status_code == 422 and run(client, "select 1", max_rows=0).status_code == 422
    slow = run(client, "select count(*) from gl_monthly a, gl_monthly b, gl_monthly c")
    assert slow.status_code == 400 and "too long" in slow.json()["detail"]


def test_the_database_is_opened_read_only_as_well(client, app):
    deny = finance_module.deny_writes
    assert deny(sqlite3.SQLITE_INSERT, "accounts", None, "main", None) == sqlite3.SQLITE_DENY
    assert deny(sqlite3.SQLITE_UPDATE, "accounts", "category", "main", None) == sqlite3.SQLITE_DENY
    assert deny(sqlite3.SQLITE_DELETE, "accounts", None, "main", None) == sqlite3.SQLITE_DENY
    assert deny(sqlite3.SQLITE_ATTACH, "x.db", None, None, None) == sqlite3.SQLITE_DENY
    assert deny(sqlite3.SQLITE_PRAGMA, "journal_mode", "off", None, None) == sqlite3.SQLITE_DENY
    assert deny(sqlite3.SQLITE_SELECT, None, None, None, None) == sqlite3.SQLITE_OK and deny(sqlite3.SQLITE_READ, "accounts", "category", "main", None) == sqlite3.SQLITE_OK
    con = sqlite3.connect(":memory:")
    con.execute("create table t (a)")
    con.execute("PRAGMA query_only = ON")
    with pytest.raises(sqlite3.OperationalError):
        con.execute("insert into t values (1)")
    con.set_authorizer(deny)
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("delete from t")
    sub = next(r for r in app.routes if getattr(r, "path", "") == "/finance").app
    assert isinstance(sub.state.finance_db, sqlite3.Connection)
    assert sub.state.finance_db.execute("select count(*) from accounts").fetchone() == (11,)


def test_finance_commentary_is_a_draft_with_versions(client, store):
    body = {"question": "What was operating cost last month against budget?", "query_run": f"select sum(actual), sum(budget) {OPEX} and period = '2026-10'",
            "figures": [{"label": "Operating cost actual", "value": 2743079, "period": "2026-10"}, {"label": "Over budget", "value": 2.87, "unit": "percent"}],
            "commentary": "Operating cost was 2.87 percent over budget."}
    a = post(client, "/finance/commentary", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["commentary_id"].startswith("FCM-")
    b = post(client, "/finance/commentary", {**body, "question": "what was operating cost  last month against budget?", "drafted_by": "A. Analyst"})
    assert b["draft"]["version"] == 2 and b["commentary_id"] == a["commentary_id"]
    other = post(client, "/finance/commentary", {**body, "question": "Something else?"})
    assert other["draft"]["version"] == 1 and other["commentary_id"] != a["commentary_id"]
    saved = store.data["finance_commentaries"][a["commentary_id"]]["versions"]
    assert [v["version"] for v in saved] == [1, 2] and saved[0]["figures"][0]["value"] == 2743079 and saved[1]["drafted_by"] == "A. Analyst"
    none = post(client, "/finance/commentary", {"question": "What was the headcount in Technology?", "query_run": "select * from cost_centres",
                                                "commentary": "The warehouse has no headcount. Nothing can be said."})
    assert none["draft"]["figures"] == []
    assert client.post("/finance/commentary", json={**body, "query_run": "drop table accounts"}, headers=H).status_code == 400
    assert client.post("/finance/commentary", json={**body, "commentary": ""}, headers=H).status_code == 422
    assert len(store.data["finance_commentaries"]) == 3


# ---------------------------------------------------------------- research

def test_companies_and_filings(client):
    rows = get(client, "/research/companies")["items"]
    assert [r["company_id"] for r in rows] == ["RSC-6001", "RSC-6002", "RSC-6003"] and all(r["exchange"].endswith("(invented)") for r in rows)
    assert all(r["latest_filing_date"] == "2026-08-21" for r in rows)
    fl = get(client, "/research/companies/RSC-6002/filings")["items"]
    assert [(f["filing_id"], f["type"]) for f in fl] == [("FIL-6103", "annual"), ("FIL-6104", "half_year")] and fl[0]["published"] < fl[1]["published"]
    assert client.get("/research/companies/RSC-9/filings", headers=H).status_code == 404
    assert client.get("/research/companies/RSC-6001/filings/FIL-6103", headers=H).status_code == 404
    assert client.get("/research/companies/RSC-6001/filings/FIL-9", headers=H).status_code == 404


def test_clean_results_company_agrees_with_itself(client):
    annual = get(client, "/research/companies/RSC-6001/filings/FIL-6101")["text"]
    half = get(client, "/research/companies/RSC-6001/filings/FIL-6102")["text"]
    assert "Revenue was USD 842.3 million" in annual and "Earnings per share were 35.7 cents" in annual and "No figure in this report has been restated" in annual
    assert "Restatement" not in half and "The full-year figures for 2025 in the annual report are unchanged" in half
    assert 71.4 / 200 * 100 == pytest.approx(35.7) and 38.6 / 200 * 100 == pytest.approx(19.3)
    est = get(client, "/research/companies/RSC-6001/estimates")
    assert est["as_of"] > get(client, "/research/companies/RSC-6001/filings/FIL-6102")["published"] and est["estimates"][0]["year"] == "FY2026"


def test_half_year_filing_restates_a_figure_of_the_annual_filing(client):
    annual = get(client, "/research/companies/RSC-6002/filings/FIL-6103")
    half = get(client, "/research/companies/RSC-6002/filings/FIL-6104")
    assert "Revenue was USD 412.6 million" in annual["text"] and "Restatement" not in annual["text"] and "398.9" not in annual["text"]
    assert "Restatement of 2025 figures" in half["text"] and "398.9" in half["text"] and "412.6" in half["text"] and "13.7 million of revenue belongs to 2026" in half["text"]
    line = next(l for l in half["text"].splitlines() if l.strip().startswith("Revenue FY2025"))
    assert line.split()[-2:] == ["412.6", "398.9"] and round(412.6 - 13.7, 1) == 398.9
    eps = next(l for l in half["text"].splitlines() if l.strip().startswith("Earnings per share FY2025"))
    assert eps.split()[-2:] == ["22.0", "18.9"] and round(37.8 / 200 * 100, 1) == 18.9
    assert half["published"] > annual["published"]
    other = get(client, "/research/companies/RSC-6001/filings/FIL-6102")["text"]
    assert "Restatement" not in other and "Restatement" not in get(client, "/research/companies/RSC-6003/filings/FIL-6106")["text"]


def test_consensus_and_the_filing_disagree_for_one_company(client):
    est = get(client, "/research/companies/RSC-6003/estimates")
    filing = get(client, "/research/companies/RSC-6003/filings/FIL-6106")
    assert est["as_of"] < filing["published"] and (date.fromisoformat(filing["published"]) - date.fromisoformat(est["as_of"])).days == 12
    fy = est["estimates"][0]
    assert fy["revenue_m"] == 1150.0 and fy["operating_profit_m"] == 88.5
    assert "between\n  USD 1,020 million and USD 1,060 million" in filing["text"] and "between USD 55 million and USD 62 million" in filing["text"]
    assert fy["revenue_m"] > 1060 and fy["operating_profit_m"] > 62 and fy["eps_low_cents"] > 7.1 * 2 + 5
    assert "before the half-year results" in est["note"]
    clean = get(client, "/research/companies/RSC-6001/estimates")
    assert clean["as_of"] > get(client, "/research/companies/RSC-6001/filings/FIL-6102")["published"]
    assert get(client, "/research/companies/RSC-6002/estimates")["as_of"] > get(client, "/research/companies/RSC-6002/filings/FIL-6104")["published"]


def test_price_history_and_filters(client):
    p = get(client, "/research/companies/RSC-6003/prices")
    items = p["items"]
    assert p["count"] == 130 == len(items) and items[0]["date"] == p["first_date"] and items[-1]["date"] == p["last_date"] == (TODAY_D - timedelta(days=1)).isoformat()
    assert all(date.fromisoformat(r["date"]).weekday() < 5 for r in items) and [r["date"] for r in items] == sorted({r["date"] for r in items})
    assert all(r["low"] <= min(r["open"], r["close"]) and r["high"] >= max(r["open"], r["close"]) for r in items)
    filing_day = get(client, "/research/companies/RSC-6003/filings/FIL-6106")["published"]
    day = next(r for r in items if r["date"] == filing_day)
    assert day["close"] / day["open"] - 1 < -0.2 and day["volume"] > 900000
    tarn = next(r for r in get(client, "/research/companies/RSC-6002/prices")["items"] if r["date"] == filing_day)
    assert -0.12 < tarn["close"] / tarn["open"] - 1 < -0.05
    cut = get(client, "/research/companies/RSC-6003/prices", params={"date_from": filing_day, "date_to": filing_day})
    assert cut["count"] == 1 and cut["items"][0]["date"] == filing_day
    assert get(client, "/research/companies/RSC-6003/prices", params={"date_from": "2099-01-01"})["count"] == 0
    assert client.get("/research/companies/RSC-9/prices", headers=H).status_code == 404 and client.get("/research/companies/RSC-9/estimates", headers=H).status_code == 404


def test_research_report_is_a_draft_with_sourced_figures(client, store):
    body = {"title": "Tarnholt Marine, half-year 2026", "report": "FY2025 revenue is restated to 398.9 million.",
            "figures": [{"label": "Revenue FY2025 (restated)", "value": 398.9, "source_id": "FIL-6104", "source_note": "Restatement table"},
                        {"label": "Consensus EPS FY2026", "value": 20.4, "unit": "cents", "source_id": "consensus"}],
            "points_to_check": ["The restated figure replaces 412.6."]}
    a = post(client, "/research/companies/RSC-6002/report", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "agent"
    b = post(client, "/research/companies/RSC-6002/report", {**body, "drafted_by": "A. Analyst"})
    assert b["draft"]["version"] == 2 and [x["version"] for x in store.data["research_companies"]["RSC-6002"]["reports"]] == [1, 2]
    assert store.data["research_companies"]["RSC-6001"]["reports"] == []
    foreign = client.post("/research/companies/RSC-6001/report", json=body, headers=H)
    assert foreign.status_code == 422 and "FIL-6104" in foreign.json()["detail"]
    assert client.post("/research/companies/RSC-6002/report", json={**body, "points_to_check": []}, headers=H).status_code == 422
    assert client.post("/research/companies/RSC-6002/report", json={**body, "figures": [{"label": "x", "value": 1}]}, headers=H).status_code == 422
    assert client.post("/research/companies/RSC-9/report", json=body, headers=H).status_code == 404


# ---------------------------------------------------------------- events

def test_new_kinds_rotate_through_four_templates(client, store):
    for kind, coll, system in [("incident", "itops_incidents", "itops"), ("contribution-batch", "pension_batches", "funds"),
                               ("client-meeting", "crm_meetings", "crm")]:
        n0 = len(store.data[coll])
        out = [post(client, f"/admin/simulate/{kind}", {}) for _ in range(5)]
        ids_ = [o["item_id"] for o in out]
        assert len(set(ids_)) == 5 and len(store.data[coll]) == n0 + 5 and all(i in store.data[coll] for i in ids_)
        assert all(o["event_type"] == kind and o["system"] == system and o["item_id"] in o["message"] for o in out)
        assert all(PLAIN(o["message"]) for o in out)
        assert len({o["message"] for o in out[:4]}) == 4
    created = [e for e in get(client, "/admin/events")["items"] if e["status"] == "created"]
    assert {e["event_type"] for e in created} == {"incident", "contribution-batch", "client-meeting"}


def test_simulated_incidents_are_readable_with_metrics_and_runbook(client):
    seen = []
    for _ in range(4):
        r = post(client, "/admin/simulate/incident", {})
        inc = get(client, f"/itops/incidents/{r['item_id']}")
        svc = inc["services_affected"][0]
        assert inc["status"] == "open" and inc["alert_id"] and inc["reported"] and len(inc["timeline"]) == 2
        m = get(client, "/itops/metrics", params={"service": svc})["measures"]
        assert len(m["error_rate_pct"]["points"]) == 13 and get(client, f"/itops/runbooks/{svc}")["steps"]
        seen.append((svc, inc["severity"]))
        assert "Read it with get_incident" in r["message"]
    assert [s[0] for s in seen] == ["notification-service", "reporting-database", "ledger-posting", "mobile-gateway"]
    # template three: an alert storm where the service's own measures are normal
    assert max(p["value"] for p in get(client, "/itops/metrics", params={"service": "ledger-posting"})["measures"]["error_rate_pct"]["points"]) < 0.5
    assert max(p["value"] for p in get(client, "/itops/metrics", params={"service": "mobile-gateway"})["measures"]["error_rate_pct"]["points"]) > 10


def test_simulated_batches_have_the_faults_the_templates_say(client, store):
    members = set(store.data["pension_members"])
    found = []
    for _ in range(4):
        r = post(client, "/admin/simulate/contribution-batch", {})
        b = get(client, f"/funds/batches/{r['item_id']}")
        assert b["status"] == "received" and b["received_on"] == TODAY and b["control_total"] == round(sum(x["employee_amount"] + x["employer_amount"] for x in b["rows"]), 2)
        found.append(rules_broken(b["rows"], members))
    assert found == [{}, {3: [1]}, {3: [3]}, {2: [2]}]


def test_simulated_meetings_are_for_tomorrow_and_readable(client):
    seen = []
    for _ in range(4):
        r = post(client, "/admin/simulate/client-meeting", {})
        m = get(client, f"/crm/meetings/{r['item_id']}")
        assert m["date"] == TOMORROW and m["relationship_manager"] == "Sunniva Haldane-Rook" and m["status"] == "scheduled" and m["client"]["name"] in r["message"]
        seen.append(m["customer_id"])
        assert get(client, f"/crm/clients/{m['customer_id']}/holdings")["customer_id"] == m["customer_id"]
    assert seen == ["CUS-1016", "CUS-1009", "CUS-1013", "CUS-1019"]
    assert len(get(client, "/crm/meetings", params={"date": TOMORROW, "relationship_manager": "Sunniva Haldane-Rook"})["items"]) == 7


def test_new_kinds_can_be_subscribed_to(client):
    for kind in ("incident", "contribution-batch", "client-meeting"):
        r = post(client, "/admin/subscriptions", {"event_kind": kind, "url": "http://127.0.0.1:9/x"})
        assert r["subscription"]["event_kind"] == kind
    assert client.post("/admin/subscriptions", json={"event_kind": "meeting", "url": "http://127.0.0.1:9/x"}, headers=H).status_code == 422
    assert client.post("/admin/simulate/meeting", headers=H).status_code == 404
    delivered = post(client, "/admin/simulate/incident", {})
    assert [d["status"] for d in delivered["deliveries"]] == ["queued"]


def test_reset_restores_the_new_data(client, store):
    post(client, "/itops/incidents/INC-7001/assessment", {"what_is_happening": "x", "likely_cause": "y"})
    post(client, "/legacy/documentation", {"object_type": "program", "object_name": "SORUN", "explanation": "x"})
    b = get(client, "/funds/batches/BAT-4001")
    post(client, "/funds/batches/BAT-4001/result", result(b))
    post(client, "/funds/batches/BAT-4001/post", {"approved_by": "x"})
    post(client, "/crm/meetings/MTG-1001/brief", {"summary": "x"})
    post(client, "/finance/commentary", {"question": "q", "query_run": "select 1", "commentary": "c"})
    post(client, "/research/companies/RSC-6001/report", {"title": "t", "report": "r", "points_to_check": ["p"]})
    for kind in ("incident", "contribution-batch", "client-meeting"):
        post(client, f"/admin/simulate/{kind}", {})
    assert len(store.data["itops_incidents"]) == 5
    assert post(client, "/admin/reset", {})["applied"] is True
    assert store.data == build_all(TODAY_D)
    assert get(client, "/itops/incidents/INC-7001")["assessments"] == [] and get(client, "/funds/batches/BAT-4001")["status"] == "received"
    assert get(client, "/funds/members/MEM-5001/holdings")["total_value"] == 29676.74 and store.data["finance_commentaries"] == {}
    assert get(client, "/admin/state")["counts"]["open_incidents"] == 3


# ---------------------------------------------------------------- the data itself

NEW_KEYS = ["itops_incidents", "itops_metrics", "itops_changes", "itops_runbooks", "itops_dashboards", "itops_certificates", "legacy_tables", "legacy_procedures",
            "legacy_programs", "pension_funds", "pension_members", "pension_holdings", "pension_batches", "pension_forms", "pension_procedure", "crm_meetings",
            "finance", "research_companies", "research_filings", "research_prices", "research_estimates"]


def test_new_data_is_identical_for_same_date_and_changes_with_the_date():
    a, b, c = build_all(TODAY_D), build_all(TODAY_D), build_all(date(2026, 12, 3))
    assert all(a[k] == b[k] for k in NEW_KEYS) and json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["itops_incidents"]["INC-7001"]["opened_at"] != c["itops_incidents"]["INC-7001"]["opened_at"]
    assert a["pension_batches"]["BAT-4001"]["period"] == "2026-10" and c["pension_batches"]["BAT-4001"]["period"] == "2026-11"
    assert a["finance"]["gl_monthly"]["rows"][-1][0] == "2026-10" and c["finance"]["gl_monthly"]["rows"][-1][0] == "2026-11"


def test_new_data_has_no_dashes_and_no_filler_text():
    text = json.dumps({k: v for k, v in build_all(TODAY_D).items() if k in NEW_KEYS}, ensure_ascii=False)
    assert DASH not in text and chr(0x2013) not in text
    for word in ("TODO", "lorem"):
        assert word.lower() not in text.lower(), word


def test_invented_names_only_in_the_new_data():
    text = json.dumps({k: v for k, v in build_all(TODAY_D).items() if k in NEW_KEYS}, ensure_ascii=False)
    assert "(invented)" in text and "Port Ilvane Securities Market" in text
    for real in ("NASDAQ", "NYSE", "London Stock Exchange", "FTSE", "Dow Jones", "S&P", "Bloomberg", "Reuters", "Oracle", "IBM", "SWIFT", "Visa", "Mastercard",
                 "Barclays", "HSBC", "JPMorgan", "Citibank", "Tesco", "Maersk", "Nestle", "Unilever", "ISO 20022"):
        assert real.lower() not in text.lower(), real


def test_ids_agree_across_the_new_and_old_systems(store):
    d = store.data
    for m in d["pension_members"].values():
        assert not m["customer_id"] or m["customer_id"] in d["customers"]
        assert m["contribution_fund_id"] in d["pension_funds"] and set(d["pension_holdings"][m["member_id"]]) <= set(d["pension_funds"])
    for b in d["pension_batches"].values():
        assert [r["row_no"] for r in b["rows"]] == list(range(1, len(b["rows"]) + 1))
    for m in d["crm_meetings"].values():
        assert m["customer_id"] in d["customers"]
    for f in d["research_filings"].values():
        assert f["company_id"] in d["research_companies"]
    for i in d["itops_incidents"].values():
        assert all(c in d["itops_changes"] for c in i["linked_change_ids"])
        assert all(s in d["itops_metrics"] and s in d["itops_runbooks"] for s in i["services_affected"])
    fin = d["finance"]
    valid = (({r[0] for r in fin["cost_centres"]["rows"]}, 1), ({r[0] for r in fin["accounts"]["rows"]}, 2), ({r[0] for r in fin["products"]["rows"]}, 3),
             ({r[0] for r in fin["branches"]["rows"]}, 4))
    for row in fin["gl_monthly"]["rows"]:
        assert all(row[i] in codes for codes, i in valid), row


def test_scenarios_file_has_a_section_per_new_system_with_every_right_answer():
    text = (ROOT / "SCENARIOS.md").read_text(encoding="utf-8")
    for heading in ("## IT operations (system: itops)", "## Legacy core system (system: legacy)", "## Pension funds (system: funds)",
                    "## Client meetings (system: crm)", "## Finance warehouse (system: finance)", "## Equity research (system: research)"):
        assert heading in text, heading
    for needle in ("INC-7001", "INC-7002", "INC-7003", "INC-7004", "AC_X1", "FIN-14", "MEM-5001", "BAT-4001", "BAT-4002", "FRM-4001", "MTG-1001", "MTG-1002",
                   "MTG-1003", "2,743,079", "2,666,664", "338,325", "1,348,295", "1,388,881", "headcount", "FIL-6104", "398.9", "RSC-6003", "incident, contribution-batch"):
        assert needle in text, needle
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "nineteen systems" in readme and "141 operations" in readme and "thirteen" not in readme.lower()
    for s in NEW:
        assert f"`/{s}`" in readme
