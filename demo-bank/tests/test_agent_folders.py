"""The agent folders in ../banking/agents name operations of this bank.

These tests keep the two in step: an agent file may only name an operation
that exists, in a system it lists, and it must say which of its operations
write something and which of those wait for a person.
"""
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from bank.app import create_app
from conftest import ALL_SYSTEMS, make_env

AGENTS = Path(__file__).resolve().parents[2] / "banking" / "agents"
if not AGENTS.is_dir():
    pytest.skip("the agent folders are not next to this copy of the bank", allow_module_level=True)

# Searches that are sent as a POST because the question goes in the body. They write nothing.
POST_READS = {"screen_name", "run_finance_query"}

AGENT_FILES = sorted(AGENTS.glob("*/agent.yaml"))
TEST_FILES = sorted(AGENTS.glob("*/tests.yaml"))


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def named_operations(agent):
    return [op for need in agent.get("needs") or [] for op in need.get("operations") or []]


@pytest.fixture(scope="module")
def bank():
    """Every operation of the bank: its system, whether it writes, and whether the bank calls it a change."""
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
    assert len(AGENT_FILES) >= 30
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


def test_the_post_reads_exist_and_are_not_marked_as_changes(bank):
    for name in POST_READS:
        assert name in bank, f"{name} is no longer an operation of the bank"
        assert not bank[name]["changes_a_record"]


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.parent.name)
def test_an_agent_names_only_operations_that_exist_in_a_system_it_lists(path, bank):
    agent = load(path)
    listed = agent.get("demo_bank_systems") or []
    named = named_operations(agent)
    assert len(named) == len(set(named)), "an operation is named twice"
    for system in listed:
        assert system in ALL_SYSTEMS, f"{system} is not a system of the bank"
    for op in named:
        assert op in bank, f"{op} is not an operation of the bank"
        assert bank[op]["system"] in listed, f"{op} is in {bank[op]['system']}, which demo_bank_systems does not list"
    if named:
        for system in listed:
            assert any(bank[op]["system"] == system for op in named), f"{system} is listed and none of its operations is named"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.parent.name)
def test_an_agent_lists_every_write_and_says_which_wait_for_a_person(path, bank):
    agent = load(path)
    named = named_operations(agent)
    changes = agent.get("changes") or []
    listed = {c["tool"]: c["waits_for_approval"] for c in changes}
    assert len(listed) == len(changes), "a tool is listed twice under changes"
    for tool, waits in listed.items():
        assert tool in named, f"{tool} is under changes and is not among the operations the agent needs"
        assert bank[tool]["writes"], f"{tool} is under changes and writes nothing"
        if bank[tool]["changes_a_record"]:
            assert waits is True, f"{tool} changes a record of the bank, so it waits for a person"
        else:
            assert waits is False, f"{tool} only saves a draft or a proposal, so it does not wait"
    for op in named:
        if bank[op]["writes"]:
            assert op in listed, f"{op} writes something and is not listed under changes"
