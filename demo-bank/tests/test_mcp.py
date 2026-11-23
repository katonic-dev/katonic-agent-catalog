"""MCP doors: asked through a real client, over both transports."""

import asyncio
import json

import httpx
import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from conftest import ALL_SYSTEMS, KEY, SYSTEMS


def doc_ops(client, system):
    doc = client.get(f"/{system}/openapi.json").json()
    ops = {}
    for item in doc["paths"].values():
        for op in item.values():
            ops[op["operationId"]] = op
    return ops


async def list_tools_streamable(base, system):
    async with httpx.AsyncClient(headers={"X-API-Key": KEY}) as http:
        async with streamable_http_client(f"{base}/{system}/mcp", http_client=http) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                return (await session.list_tools()).tools


async def list_tools_sse(base, system):
    async with sse_client(f"{base}/{system}/sse", headers={"X-API-Key": KEY}) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            result = await session.call_tool("validate_iban" if system == "payments" else tools[0].name,
                                             {"iban": "XM00MRTB00000000000000"} if system == "payments" else {})
            return tools, result


# One read call for each of the nineteen systems: the tool, its arguments, and a field of the answer with the value it must have.
READ_CALLS = {
    "core": ("get_customer", {"customer_id": "CUS-1001"}, "customer_id", "CUS-1001"),
    "cards": ("get_card", {"card_id": "CRD-2001"}, "card_id", "CRD-2001"),
    "screening": ("get_watchlist_entry", {"entry_id": "WL-9001"}, "entry_id", "WL-9001"),
    "aml": ("get_monitoring_rule", {"rule_id": "MTB-AML-RULE-001"}, "rule_id", "MTB-AML-RULE-001"),
    "payments": ("get_payment_rule", {"rule_id": "MTB-PAY-RULE-101"}, "rule_id", "MTB-PAY-RULE-101"),
    "lending": ("get_loan_application", {"application_id": "LAP-8001"}, "application_id", "LAP-8001"),
    "fraud": ("get_fraud_rule", {"rule_id": "FRD-RULE-001"}, "rule_id", "FRD-RULE-001"),
    "recon": ("get_ledger_entry", {"entry_id": "LED-7101"}, "entry_id", "LED-7101"),
    "news": ("get_news_article", {"article_id": "ART-6001"}, "article_id", "ART-6001"),
    "onboarding": ("get_onboarding_application", {"application_id": "ONB-1001"}, "application_id", "ONB-1001"),
    "complaints": ("get_complaints_procedure", {}, "procedure_id", "MTB-PROC-CMP-1"),
    "collections": ("get_conduct_rules", {}, "count", 7),
    "audit": ("get_control_test", {"test_id": "CTL-1001"}, "test_id", "CTL-1001"),
    "itops": ("get_incident", {"incident_id": "INC-7001"}, "incident_id", "INC-7001"),
    "legacy": ("get_legacy_table", {"table_name": "ACMAST"}, "table_name", "ACMAST"),
    "funds": ("get_member", {"member_id": "MEM-5001"}, "member_id", "MEM-5001"),
    "crm": ("get_client_meeting", {"meeting_id": "MTG-1001"}, "meeting_id", "MTG-1001"),
    "finance": ("list_finance_tables", {}, "count", 5),
    "research": ("list_research_companies", {}, "count", 3),
}


async def tools_and_read_streamable(base, system, tool, args):
    async with httpx.AsyncClient(headers={"X-API-Key": KEY}) as http:
        async with streamable_http_client(f"{base}/{system}/mcp", http_client=http) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                return tools, await session.call_tool(tool, args)


async def tools_and_read_sse(base, system, tool, args):
    async with sse_client(f"{base}/{system}/sse", headers={"X-API-Key": KEY}) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            return tools, await session.call_tool(tool, args)


def check_system(client, system, tools, result):
    ops = doc_ops(client, system)
    assert {t.name for t in tools} == set(ops)
    for t in tools:
        assert t.description == ops[t.name]["description"]
    tool, _, field, expected = READ_CALLS[system]
    assert tool in ops and tool.split("_")[0] in ("get", "list")
    assert not result.is_error, result.content[0].text
    body = json.loads(result.content[0].text)
    assert body["demo_data"] is True and body[field] == expected


def test_every_system_has_one_read_call_in_the_table():
    assert list(READ_CALLS) == ALL_SYSTEMS and len(ALL_SYSTEMS) == 19


@pytest.mark.parametrize("system", ALL_SYSTEMS)
def test_every_operation_is_an_mcp_tool_and_a_read_works_streamable(live_server, client, system):
    tool, args, _, _ = READ_CALLS[system]
    tools, result = asyncio.run(tools_and_read_streamable(live_server, system, tool, args))
    check_system(client, system, tools, result)


@pytest.mark.parametrize("system", ALL_SYSTEMS)
def test_every_operation_is_an_mcp_tool_and_a_read_works_sse(live_server, client, system):
    tool, args, _, _ = READ_CALLS[system]
    tools, result = asyncio.run(tools_and_read_sse(live_server, system, tool, args))
    check_system(client, system, tools, result)


def test_sse_transport_lists_and_calls(live_server, client):
    tools, result = asyncio.run(list_tools_sse(live_server, "payments"))
    assert {t.name for t in tools} == set(doc_ops(client, "payments"))
    assert "valid" in result.content[0].text


def test_mcp_door_needs_key(client):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    assert client.post("/core/mcp", json=body).status_code == 401
    assert client.get("/core/sse").status_code == 401
    assert client.post("/core/mcp", json=body, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200


def test_mcp_tool_call_writes_through(client, store):
    body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "block_card", "arguments": {"card_id": "CRD-2001", "reason": "lost"}}}
    r = client.post("/cards/mcp", json=body, headers={"X-API-Key": KEY}).json()
    assert "applied" in r["result"]["content"][0]["text"]
    assert store.data["cards"]["CRD-2001"]["status"] == "blocked"
    r2 = client.post("/cards/mcp", json=body, headers={"X-API-Key": KEY}).json()
    assert r2["result"]["isError"] is True
    assert "409" in r2["result"]["content"][0]["text"]
