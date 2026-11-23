# Katonic Agent Catalog

Agents and applications you can build on the Katonic platform. Each one has its own folder: the instructions, what the agent needs connected, its tests, invented sample data and a build guide.

The first pack is banking. It comes with an invented bank to build against.

**Status: work in progress.** The tables inside each pack say what is built and what is planned. Nothing here is a tested integration with a named banking product.

## What is in this repository

| Folder | What it holds |
|---|---|
| [`banking/`](banking/README.md) | The banking pack: 30 agents, and the desks people use them through |
| `demo-bank/` | Meridian Trust Bank, an invented bank: six back-office systems behind an API, each with an OpenAPI file and an MCP door. Being added |
| [`docs/`](docs/agent-folder-format.md) | The format every agent folder follows |

## How the pieces fit

- **An agent** is built in Katonic Studio from its folder here. The folder says which kind of agent it is, what starts it, what it reads, and where it stops for a person.
- **A desk** is an application: a queue of cases, the agent's findings and draft beside each one, approve or send back, and a register of who decided what. The desk engine is a separate project, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). Each desk in this repository is a settings folder for it.
- **The invented bank** stands in for a bank's own systems, so that an agent which reads a payment queue or a screening alert has something to read. You run your own copy next to your platform. When you move to real systems, you swap the bank's API for your own.

## Types and forms

Every agent is sorted the same way, by what starts it and who decides the next step.

| Type | Forms |
|---|---|
| Conversational | Answering agent, acting agent |
| Workflow | Scheduled agent, event-triggered agent, API agent |
| Autonomous | Autonomous agent |
| Multi-agent | Agent pipeline, manager agent, agent team, guardian agent |

The white paper [Types of AI agents](https://www.katonic.ai/resources/white-papers/types-of-ai-agents) explains each form.

One rule holds for every agent here: it prepares the work, and a person makes the decision.

## Invented data

Meridian Trust Bank does not exist. Every customer, account, payment, alert, loan and policy in this repository is invented, and is labelled as invented where it appears. Country codes in account numbers and bank identifiers are codes no real country uses.

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
