"""MCP doors: asked through a real client, over both transports."""

import asyncio
import json

import httpx
import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from conftest import ALL_SYSTEMS, KEY

# One read call for each system: the tool, its arguments, and a field of the answer with the value it must have.
READ_CALLS = {
    "policy": ("get_policy", {"policy_id": "POL-2001"}, "policy_id", "POL-2001"),
    "claims": ("get_claim", {"claim_id": "CLM-4001"}, "claim_id", "CLM-4001"),
    "health": ("get_member", {"member_id": "MEM-7201"}, "member_id", "MEM-7201"),
    "underwriting": ("get_submission", {"submission_id": "SBM-6501"}, "submission_id", "SBM-6501"),
    "investigations": ("get_claim_for_checking", {"claim_id": "CLM-6201"}, "claim_id", "CLM-6201"),
}


def doc_ops(client, system):
    doc = client.get(f"/{system}/openapi.json").json()
    return {op["operationId"]: op for item in doc["paths"].values() for op in item.values()}


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
    _, _, field, expected = READ_CALLS[system]
    assert not result.is_error, result.content[0].text
    body = json.loads(result.content[0].text)
    assert body["demo_data"] is True and body[field] == expected


def test_every_system_has_one_read_call_in_the_table():
    assert list(READ_CALLS) == ALL_SYSTEMS


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
