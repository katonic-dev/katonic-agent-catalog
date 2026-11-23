"""MCP doors: asked through a real client, over both transports."""

import asyncio

import httpx
import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from conftest import KEY, SYSTEMS


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


@pytest.mark.parametrize("system", SYSTEMS)
def test_every_operation_is_an_mcp_tool_streamable(live_server, client, system):
    tools = asyncio.run(list_tools_streamable(live_server, system))
    ops = doc_ops(client, system)
    assert {t.name for t in tools} == set(ops)
    for t in tools:
        assert t.description == ops[t.name]["description"]


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
