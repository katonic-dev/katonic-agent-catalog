# Building the insurance agents on a cluster

This page is for whoever carries on the build. It says what is done, what is left, and how one agent is built and tested on a development cluster of the Katonic platform. Read it with the index in [README.md](README.md), whose State column is the record of where each agent stands.

Nothing here is secret. The address of your cluster, your sign-in and the insurer's key are yours: they are not in this repository and must never be put into it.

## Where the build stands

| | Done | Of |
|---|---|---|
| Systems of the invented insurer ([demo-insurer](../demo-insurer/README.md)) | 9 | 9 |
| Agent folders written ([agents](agents)) | 31 | 31 |
| Desks built and tested against a stand-in agent ([desks](desks)) | 8 | 8 |
| Agents built on a cluster and passing every test five runs in a row | 10 | 31 |

One more agent, First Notice of Loss Intake, is built and has one test unfinished (see "The one agent that is built and not passed"). The other twenty are written and not yet built.

## What you need before you start

1. **A development cluster and a sign-in on it** that may create agents, import tools and set tool approval policies. Each person signs in for themselves. If a sign-in page appears in the middle of the work, stop and ask them: nobody types another person's password, token or key.
2. **The invented insurer running on that cluster with all nine systems**, its key check on and its date pinned with `INSURER_TODAY=2026-11-26`. Deploy it from `demo-insurer/main.py` as the [install guide](../demo-bank/docs/install-on-katonic.md) says, with the settings `INSURER_API_KEY` and `INSURER_TODAY`. Check: `GET <insurer>/health` says `insurer_date` 2026-11-26, and `GET <insurer>/<system>/openapi.json` answers for each of `policy`, `claims`, `health`, `underwriting`, `investigations`, `servicing`, `conduct`, `portfolio`, `reinsurance`.
3. **The insurer's key**, from the person who deployed it. Keep it in a file outside this repository. Read it from the file when a command needs it; never print it, and never write it into a report, a note, a message or a commit.
4. **This repository, cloned**, and Python to run the insurer's tests: from `demo-insurer`, `python -m pytest -q`.

Two things to know about the insurer on a cluster:

- **A redeploy puts all its data back to the start**, saved drafts included. Redeploy only when no test is running against it.
- **Redeploy it as the person who owns the app.**

## Step 1: one tool connection for each system

In Control Room, Tools, import the insurer's OpenAPI document once for each system: `<insurer>/<system>/openapi.json`, authentication "API key (header)", header name `X-API-Key`, the key as its value, and the access group of the team that will own the agents. A name of the form `Thornmere demo insurer: <system>` keeps them easy to find.

The ten agents that pass use `policy`, `claims` and `health`. The twenty that are left need these six as well: `underwriting`, `investigations`, `servicing`, `conduct`, `portfolio`, `reinsurance`.

If a system gains an operation after you imported it, the connection does not learn it by itself: import again.

## Step 2: decide what waits for approval, before the first publish

Each `agent.yaml` lists the tools that change something under `changes`, with `waits_for_approval`. In this pack a draft save does not wait: it keeps a draft with its author, a time and a version number, and changes nothing else. Anything that really changes a record waits for a person.

- For every tool marked `waits_for_approval: false`, add an "Auto-approve" row in Studio, Tool approval policies, **before** you publish the agent that holds it. Without the row the run stops at the save and the test cannot pass. Add the rows one tool at a time.
- For a tool marked `waits_for_approval: true`, set the rule and check it. What holds the tool is a rule in Control Room, Policies: action "Requires approval", the tool connection as the server, the tool's name. A person with the right to govern the workspace creates that rule. Check on your own cluster that a call is held before you rely on it, and before you run a test that depends on it.

The draft saves of the twenty agents still to build:

| System | Agents | Draft saves to set to Auto-approve |
|---|---|---|
| `underwriting` | Underwriting Support, Risk Appetite Check, Underwriting Referral Memo, Renewal Review | `save_underwriting_file`, `save_referral_memo`, `save_renewal_review` (Risk Appetite Check saves nothing) |
| `investigations` | Claims Leakage Review, Fraud Detection, Investigation Case File | `save_leakage_finding`, `save_fraud_referral`, `save_case_file` |
| `servicing` | Policy Servicing, Certificate and Endorsement Preparation, Broker Query | `save_change_draft`, `save_certificate_draft`, `save_endorsement_draft`, `save_broker_call_back_request` |
| `conduct` | Compliance Audit, Regulatory Monitoring, Complaint Handling, Litigation Support | `save_audit_record`, `save_regulatory_impact_note`, `save_complaint_response`, `save_document_schedule` |
| `portfolio` | Product Change Analyst, Pricing Analyst, Risk Profiling | `save_portfolio_question_for_a_person` |
| `reinsurance` | Bordereaux Check, Treaty Recovery, Partner Quality | `save_bordereau_differences`, `save_recovery_list`, `save_partner_review` |

Check each list against the agent's own `agent.yaml` before you rely on it: the folder is the source, this table is a convenience.

## Step 3: build and test one agent

Build one group at a time, in the order of the table above, and one agent at a time within it. If several people test at once, keep it to four. For each agent read its whole folder first: `agent.yaml`, `instructions.md`, `tests.yaml`, `README.md`, and [docs/agent-folder-format.md](../docs/agent-folder-format.md) for what every field and every kind of check means. The right answer for every case is in [demo-insurer/SCENARIOS.md](../demo-insurer/SCENARIOS.md).

1. **Check the connection.** Open the connection or connections the agent needs and compare the tool names with the operations under `needs` in `agent.yaml`.
2. **Build the draft.** In Studio, a blank chat agent. Name: the `name` in `agent.yaml`. Description: at most 160 characters, made from its summary. Instructions: the whole of `instructions.md`, and prove it is the same byte for byte (the SHA-256 of the text in the box equals the SHA-256 of the file). Model tier: the `tier` under `platform`. No skills, no knowledge, no memory, unless the folder says otherwise.
3. **Run the "nothing connected" test first**, on the draft, before any tool is attached: the Test tab with "Test the prompt without tools" ticked, five runs, the page loaded again before each.
4. **Attach the tools**: exactly the operations under `needs`, no more and no fewer. Write down what the picker shows for each (a read or a write).
5. **Publish** to the development environment, reachable by the team, in the Work Room. Write down the agent's id and the words of the publish dialog, including anything it says about approval.
6. **Run the other tests** in the Work Room: a new conversation for every run, five runs of every test. A test with several turns is run as real turns in one conversation. Keep every reply word for word, with the tool calls the Work Room shows.
7. **Judge every run against `tests.yaml`, strictly and literally.** Each expected line is met or not met, each check is met or not met, with the words that decide it. A line met only by implication is not met. A run passes only if everything is met. A test passes only at five passes in a row. Do not round up.
8. **Prove what was saved.** After a run that should save, read the record from the insurer (with the key, from a command line) and write down what the newest draft holds. After a run that must not save or change anything, prove that too: the number of drafts and the status are unchanged.
9. **Write a report** and keep it with your own working notes: a summary table first (the agent's id, each test as "n of 5"), then the build, then every test with its five runs, then for every failure which side is wrong. Step 4 says what goes from it into the repository.

### Rules that keep the result honest

- **Never change `instructions.md` to make a test pass while you are testing.** Record the reply word for word and say which side is wrong: the instructions, the test (a check that catches a right answer, or a line stricter than the data supports), or the insurer's data. Then fix that side in the repository, in a commit that says so, publish the new version and run the failed tests five times again, plus one run of each of the others as a control.
- **A run lost to the cluster is no result.** A server restart, a connection or stream error, a timeout, a guardrail message in place of the reply, or a sign-in page in the middle of a run: write it down and run it again. Change no setting to get round it. If model calls fail twice in a row, wait two minutes, try once more, and stop if it still fails.
- **Touch nothing that is not yours.** One agent is created for each folder. No workspace setting, guardrail, policy, team, or another person's agent, tool or app is changed. A pending approval request is never approved or declined by the tester.
- **Say "not checked" where you did not check.** For example, a letter in Arabic that passes every literal check has still not been read by a reader of Arabic, and the State says so.

### The insurer is shared

Every test of every agent runs against the same insurer.

- Never send `POST /admin/reset` without a system.
- `POST <insurer>/admin/reset/<system>` puts back everything anyone saved in that system. Send it only when no other test is running against that system, and only where a `tests.yaml` asks for the starting data. Most tests do not need it: a draft save adds a new version and changes nothing else, so a second run simply gets the next version. Judge "saved" against what the insurer holds after the run, never against "version 1".
- Some tests read another system as it stands. Renewal Review's test of RNW-6704, for one, needs claim CLM-4007 open and unpaid as at the start. The comments at the top of each `tests.yaml` say what it needs.

## Step 4: record the result in the repository

When an agent passes every test five runs in a row, three places say so, and they must agree: the `state` block of its `agent.yaml`, the State row of its `README.md`, and its row in the index [README.md](README.md). The script does all three and refuses to write if it cannot find exactly one of each:

```
python insurance/tools/set_state.py <agent-folder> <note-file> "<state text for the agent's README>" "<end of its index row now>" "<end of its index row after>"
```

- `<agent-folder>` is the folder's name under `insurance/agents`, for example `renewal-review`.
- `<note-file>` is a text file with one paragraph for `state.notes`: which version passed, how many tests, anything a reader must know (a test line corrected, something not checked).
- The two index texts are the words at the end of the agent's row: usually `Written. Not yet built on a cluster` now, and for example `Built on a development cluster. All ten tests pass five runs in a row` after.

Then, in the agent's own `README.md`, replace the "Build it" placeholder with the steps as you ran them and add a "Test results" table (each test, "5 of 5"), as the banking folders have. Update the status paragraph at the top of the index and the table at the top of this page, run the insurer's tests (`python -m pytest -q` from `demo-insurer`, which also checks every agent folder), and commit the named paths only.

An agent that is built and has not passed is recorded as exactly that: `built_on_a_cluster: true`, `tests_passed: false`, and a State that says which test is not finished and why. The script writes only a pass, so make these three edits by hand.

## The one agent that is built and not passed

**First Notice of Loss Intake** passes six of its seven tests. The seventh checks that registering a claim (`register_claim`, a real change) waits for a person. The approval rule was not yet set on the cluster it was built on. It needs the rule described in step 2: in Control Room, Policies, "Requires approval" for `register_claim` on the claims connection, created by a person who governs the workspace. With the rule in place: put the claims system back to its start when no other test is running, run test 2 five times, and set the state.

## Not done, and not part of building the twenty

- **Coverage Check with the wording as documents.** With the two wordings of [policy-library](policy-library) as PDF files in a knowledge source, the agent quoted every clause exactly, but its save was refused in every run. The insurer has since been changed to read a plain-word value as its fixed choice. The test has not been repeated since.
- **One real trigger.** Every "Workflow" agent here is built as a chat agent and a person sends the message. An event or a clock has not yet started one of them on a cluster.
- **The desks against the real agents.** All eight desks are tested against a stand-in agent that returns the right answers. None has yet been pointed at the agents on a cluster.
- **The Arabic letter** of Claims Correspondence has not been read by a reader of Arabic.
