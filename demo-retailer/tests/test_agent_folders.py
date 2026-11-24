"""The agent folders in ../retail/agents name operations of this retailer.

These tests keep the two in step: an agent file may only name an operation
that exists, in a system it lists, and it must say which of its operations
write something and which of those wait for a person.

The module is skipped when the folders are missing, and it works with any
number of folders from one upwards.
"""
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from retailer.app import create_app
from conftest import ALL_SYSTEMS, make_env

AGENTS = Path(__file__).resolve().parents[2] / "retail" / "agents"
if not AGENTS.is_dir():
    pytest.skip("the agent folders are not next to this copy of the retailer", allow_module_level=True)

# Searches that are sent as a POST because the question goes in the body. They write nothing. The retailer has none yet.
POST_READS: set = set()

AGENT_FILES = sorted(AGENTS.glob("*/agent.yaml"))
TEST_FILES = sorted(AGENTS.glob("*/tests.yaml"))
if not AGENT_FILES:
    pytest.skip("there is no agent.yaml under ../retail/agents yet", allow_module_level=True)


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def named_operations(agent):
    return [op for need in agent.get("needs") or [] for op in need.get("operations") or []]


@pytest.fixture(scope="module")
def retailer():
    """Every operation of the retailer: its system, whether it writes, and whether the retailer calls it a change."""
    client = TestClient(create_app(make_env()))
    operations = {}
    for system in ALL_SYSTEMS:
        document = client.get(f"/{system}/openapi.json").json()
        for item in document["paths"].values():
            for method, op in item.items():
                operations[op["operationId"]] = {
                    "system": system,
                    "writes": method.lower() != "get" and op["operationId"] not in POST_READS,
                    "changes_a_record": "(change)" in op.get("summary", ""),
                }
    return operations


def test_there_are_agent_folders():
    assert len(AGENT_FILES) >= 1
    assert [p.parent.name for p in TEST_FILES] == [p.parent.name for p in AGENT_FILES], "an agent folder has no tests.yaml"


@pytest.mark.parametrize("path", TEST_FILES, ids=lambda p: p.parent.name)
def test_a_tests_file_can_be_read_and_every_test_is_complete(path):
    doc = load(path)  # a line that is not valid YAML fails here, with its line number
    states = doc["states"]
    names = [test["name"] for test in doc["tests"]]
    assert names and len(names) == len(set(names)), "a test name is used twice"
    for test in doc["tests"]:
        assert test["given"] in states, f"{test['name']}: the state {test['given']} is not described under states"
        assert ("input" in test) != ("turns" in test), f"{test['name']}: a test has one input or a list of turns, not both"
        assert test["expected"] and test["checks"], f"{test['name']}: nothing is expected or nothing is checked"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.parent.name)
def test_an_agent_names_only_operations_that_exist_in_a_system_it_lists(path, retailer):
    agent = load(path)
    listed = agent.get("demo_retailer_systems") or []
    named = named_operations(agent)
    assert len(named) == len(set(named)), "an operation is named twice"
    for system in listed:
        assert system in ALL_SYSTEMS, f"{system} is not a system of the retailer"
    for op in named:
        assert op in retailer, f"{op} is not an operation of the retailer"
        assert retailer[op]["system"] in listed, f"{op} is in {retailer[op]['system']}, which demo_retailer_systems does not list"
    if named:
        for system in listed:
            assert any(retailer[op]["system"] == system for op in named), f"{system} is listed and none of its operations is named"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.parent.name)
def test_an_agent_lists_every_write_and_says_which_wait_for_a_person(path, retailer):
    agent = load(path)
    named = named_operations(agent)
    changes = agent.get("changes") or []
    listed = {c["tool"]: c["waits_for_approval"] for c in changes}
    assert len(listed) == len(changes), "a tool is listed twice under changes"
    for tool, waits in listed.items():
        assert tool in named, f"{tool} is under changes and is not among the operations the agent needs"
        assert retailer[tool]["writes"], f"{tool} is under changes and writes nothing"
        if retailer[tool]["changes_a_record"]:
            assert waits is True, f"{tool} changes a record of the retailer, so it waits for a person"
        else:
            assert waits is False, f"{tool} only saves a draft or a proposal, so it does not wait"
    for op in named:
        if retailer[op]["writes"]:
            assert op in listed, f"{op} writes something and is not listed under changes"
