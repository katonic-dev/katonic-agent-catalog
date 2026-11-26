# Audit Evidence

For a control test, it collects the evidence the test plan names from tickets, change records, access reviews and recovery tests, and lists what it found, what is missing and the exceptions. It gives no conclusion: the auditor concludes.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock: each audit cycle it works through the test plan as a batch. It can also be asked for one control test |
| How people meet it | Through the bank's own system: the evidence pack goes to the auditor |
| Reads from | The bank's audit system: control tests, tickets, change records, access reviews and recovery tests |
| Changes | Nothing in the bank's records. It saves an evidence pack as a draft |
| State | Built on a development cluster. All seven tests pass five runs in a row |
| Website page | [katonic.ai/use-cases/banking-audit-evidence-agent](https://www.katonic.ai/use-cases/banking-audit-evidence-agent) |

## What it does

- Reads the control test: the policy clause, the objective, the steps, the period and the numbered evidence plan.
- For each plan item, finds the record the plan names and cites its id.
- Lists each item as found or missing. For a missing item it writes what it searched, then looks in the tickets for an explanation and reports what the ticket says without counting it as evidence.
- Lists the exceptions the records show, with record ids: a missing rollback plan, a missing approver, an exemption, a test older than the period, a recovery time over its target.
- Saves the pack as a draft and says it was saved only if the system's reply says so.
- In a batch, does the same for every open test, then ends with a "Batch:" line.

## What it does not do

- Conclude whether a control works, or mark a test passed or failed. The auditor concludes.
- Change a record, a ticket, a change record or a test status.
- Fill a gap, or count a record from another period or another system as evidence.
- Send anything. The pack reaches the auditor through the bank's own system.
- Guarantee the same wording on every run. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's audit system, connected as an imported API, with the eleven operations listed in [`agent.yaml`](agent.yaml) and no others.
- A clock that starts the batch each audit cycle, if you want it to run by itself. The agent also answers in a chat for one test.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the eleven tools above and no others.
3. The seven tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data (bank date 2026-11-24). Reset the bank before each try, because each one saves a draft:

- `CTL-1001`: access reviews, quarterly, three systems. Eleven of twelve exist. The review of payments-hub for 2026-Q2 is missing, and ticket TKT-3003 says it was postponed.
- `CTL-1002`: change control on five sampled changes. CHG-2203 has no rollback plan. CHG-2204 has no named approver.
- `CTL-1003`: yearly recovery tests on four systems. The card-platform test is 14 months old. The payments-hub test took 4.5 hours against a 4 hour target.
- `CTL-1004`: multi-factor sign-in. Two service accounts are exempt: svc-recon-batch and svc-card-feed, each with a ticket and no end date.
- Ask it to say whether the control works and to mark `CTL-1001` passed. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The auditor reads the pack and concludes whether the control works, and decides whether an exception matters. The agent gives no conclusion.
