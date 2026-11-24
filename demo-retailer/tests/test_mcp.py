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


# One read call for each system: the tool, its arguments, and a field of the answer with the value it must have.
READ_CALLS = {
    "stores": ("get_site", {"site_id": "R-014"}, "site_id", "R-014"),
    "foodsafety": ("get_food_safety_records", {"site_id": "R-014", "period": "2026-10"}, "site_id", "R-014"),
    "care": ("get_guest_feedback", {"reference": "GF-2610-0001"}, "reference", "GF-2610-0001"),
    "purchasing": ("get_supplier_invoice", {"invoice_number": "INV-77102"}, "invoice_number", "INV-77102"),
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
    assert {t.name for t in tools} == set(ops) and len(tools) == len(ops)
    for t in tools:
        assert t.description == ops[t.name]["description"]
    tool, _, field, expected = READ_CALLS[system]
    assert tool in ops and tool.split("_")[0] in ("get", "list")
    assert not result.is_error, result.content[0].text
    body = json.loads(result.content[0].text)
    assert body["demo_data"] is True and body[field] == expected


def test_every_system_has_one_read_call_in_the_table():
    assert list(READ_CALLS) == ALL_SYSTEMS == SYSTEMS and len(ALL_SYSTEMS) == 4


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


def test_the_tool_names_of_each_door_are_the_openapi_operation_ids(client):
    expected = {"stores": 2, "foodsafety": 8, "care": 4, "purchasing": 10}
    for system, n in expected.items():
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        tools = client.post(f"/{system}/mcp", json=body, headers={"X-API-Key": KEY}).json()["result"]["tools"]
        assert len(tools) == n and {t["name"] for t in tools} == set(doc_ops(client, system))
        for t in tools:
            assert t["inputSchema"]["type"] == "object" and t["description"] and t["title"]


def test_a_tool_that_takes_a_path_and_a_body_is_described_with_both(client):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    tools = client.post("/foodsafety/mcp", json=body, headers={"X-API-Key": KEY}).json()["result"]["tools"]
    sign = next(t for t in tools if t["name"] == "sign_monthly_review")["inputSchema"]
    assert set(sign["properties"]) == {"site_id", "period", "signed_by", "note"}
    assert set(sign["required"]) == {"site_id", "period", "signed_by"}


def test_mcp_door_needs_key(client):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    for system in SYSTEMS:
        assert client.post(f"/{system}/mcp", json=body).status_code == 401
        assert client.get(f"/{system}/sse").status_code == 401
        assert client.post(f"/{system}/mcp", json=body, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200


def test_mcp_initialize_names_the_system_and_says_invented(client):
    body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}
    r = client.post("/purchasing/mcp", json=body, headers={"X-API-Key": KEY}).json()["result"]
    assert r["serverInfo"]["name"] == "rowanmere-group-purchasing" and "invented" in r["instructions"]


def test_mcp_tool_call_writes_through(client, store):
    body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "sign_monthly_review", "arguments": {"site_id": "R-022", "period": "2026-10", "signed_by": "B. Teague"}}}
    r = client.post("/foodsafety/mcp", json=body, headers={"X-API-Key": KEY}).json()
    assert "applied" in r["result"]["content"][0]["text"]
    assert store.data["fs_reviews"]["R-022:2026-10"]["status"] == "signed"
    r2 = client.post("/foodsafety/mcp", json=body, headers={"X-API-Key": KEY}).json()
    assert r2["result"]["isError"] is True
    assert "409" in r2["result"]["content"][0]["text"] and "already signed" in r2["result"]["content"][0]["text"]


def test_mcp_call_with_a_missing_argument_or_unknown_tool_is_an_error(client):
    head = {"X-API-Key": KEY}
    body = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_site", "arguments": {}}}
    r = client.post("/stores/mcp", json=body, headers=head).json()["result"]
    assert r["isError"] is True and "site_id" in r["content"][0]["text"]
    body["params"]["name"] = "nothing"
    assert "error" in client.post("/stores/mcp", json=body, headers=head).json()
    body["params"] = {"name": "get_site", "arguments": {"site_id": "R-999"}}
    r = client.post("/stores/mcp", json=body, headers=head).json()["result"]
    assert r["isError"] is True and "404" in r["content"][0]["text"]
