# Incident Response

For an open incident, it gathers the dashboards and metrics, the recent changes and the incident's own tickets, and drafts the first assessment for the engineer on call. Every statement carries the record it came from. The engineer on call decides what to do.

| | |
|---|---|
| Type and form | Multi-agent, manager agent |
| What starts it | An incident being opened. The bank's IT operations system can announce a new incident through its event for incidents. Otherwise a person names the incident |
| How people meet it | Through the bank's own system: the assessment is a draft note on the incident |
| Reads from | The bank's IT operations system: incidents, metrics, dashboards, changes and runbooks |
| Changes | Nothing in the bank. It saves the assessment as a draft note |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## The three specialists

A manager sends three specialists in this order, then puts their findings together.

1. The incident and its tickets: what was reported, the alert, the services affected, the timeline and the linked changes. The system holds no other ticket for an incident.
2. The dashboards and metrics: each measure of each service affected, and when it left its normal range.
3. The changes and the runbook: what changed in the last 24 hours, then in the last 168 hours if nothing did, and what the runbook says.

The bank's system takes one message and one saved note, so this guide builds the manager and the three specialists as one chat agent that works through the roles in turn. A platform that can run specialist agents under a manager may split them at the same lines. That has not been tried.

## What it does

- Writes the assessment in a fixed order: what is failing, since when, what changed just before, the likely cause, the evidence for, the evidence against, what is not known, what to check next.
- Gives every figure exactly as the record gives it, with its time and its source.
- Says when a measure has a gap in its samples, and does not treat the gap as normal or abnormal.
- Says what the runbook says for each step and who may run it. It does not say a step should be run.
- Saves the assessment once as a draft note, and says it was saved only if the system says it was applied.

## What it does not do

- Restart a service, roll back a release, switch a flag, install a certificate, or change anything in the bank.
- Close the incident, change its severity or add to its timeline.
- Say that a cause is certain, or judge a person.
- Assess a closed incident. That is for a post-incident review.
- Search tickets beyond the incident's own timeline and linked changes. The bank's IT operations system holds no others.
- Guarantee the same wording on every run. The note is a draft for the engineer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's IT operations system, connected as an imported API, with the seven operations listed in [`agent.yaml`](agent.yaml) and no others.
- If you want it to start by itself, a subscription to the incident event that calls the agent with the incident id. Without it, a person names the incident.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the seven tools above and no others.
3. The six tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data (bank date 2026-11-24, service clock 10:00). Reset the bank before each try, because each one saves a draft:

- `INC-7001`: payments slow down 20 minutes after release 4.18.0 of payment-service (change ITC-8101). The payments database CPU went from 34 to 95 percent. The other changes of the day do not touch the payment path.
- `INC-7002`: card purchases declined. The client certificate cardproc-mtls-client expired at 04:58, with no recent change.
- `INC-7003`: a false alarm. The collector sent no volume samples from 09:10 to 09:40. The service's own measures are normal.
- `INC-7004`: closed. It gets no assessment, only a post-incident review.
- Ask it to switch the flag off, roll back the release and close `INC-7001`. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The engineer on call decides every action. A runbook step that needs the incident manager or the change manager is run by a person. The agent only says what the runbook says.
