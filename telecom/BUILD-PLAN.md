# Building the telecom pack

This page is for whoever does the build: a person, or a coding assistant working for one. The design is in [spec/](spec/00-operator-and-rules.md). This page says in what order it is built, how each piece is checked, and what "done" means. Read it with the index in [README.md](README.md), whose State column is the record of where each agent stands.

Nothing here is secret. The address of your cluster, your sign-in and the operator's key are yours: they are not in this repository and must never be put into it.

## Where the build stands

| | Done | Of |
|---|---|---|
| Design written ([spec](spec/00-operator-and-rules.md)) | 10 files | 10 |
| Systems of the invented operator (`demo-operator/`) | 0 | 14 |
| Documents written from the data (`telecom/library/`) | 0 | 4 sets |
| Agent folders written (`telecom/agents/`) | 0 | 32 |
| Desks built and tested against a stand-in agent (`telecom/desks/`) | 0 | 8 |
| Agents built on a cluster and passing every test five runs in a row | 0 | 32 |
| Workflows that wrap an agent, started from Automations and checked | 0 | 25 |

Keep this table and the index true as you go. Change them in the same commit as the work they describe.

## The order of the work

The pack is built in seven groups. A group is finished before the next one starts: its systems, then its documents, then its folders, then its desks, then its agents on a cluster. The first group is the smallest way to show the pack, so do not start two groups at once.

| Group | Area files | Systems to build | Agents | Desks |
|---|---|---|---|---|
| 1 | [01](spec/01-network-operations.md) | inventory, assurance, performance, change | Runbook Q&A, Trouble Ticket Enrichment, Post-incident Review, Change Request Review, Planned Work Notification, Network Optimization | Network operations desk, Change desk |
| 2 | [02](spec/02-fraud-and-security.md) | fraud, customer (the part group 2 needs), assurance (security alerts) | Fraud Detection, SIM Swap Check, Scam Report Triage, Network Security | Fraud desk |
| 3 | [03](spec/03-customer-care.md), [04](spec/04-billing-and-revenue.md) | customer, catalogue, care, billing | Bill Explanation, Plan and Product Q&A, Complaint Handling, Contact Summary, Churn Prediction, Billing & Revenue, Bill Dispute Investigation | Customer care desk, Revenue assurance desk |
| 4 | [05](spec/05-orders-and-activation.md) | orders, inventory (what the network reports) | Order Fallout, Number Porting Check, Inventory Reconciliation | Order desk |
| 5 | [07](spec/07-service-assurance-and-field.md) | assurance (tests), performance (equipment readings), field | Predictive Maintenance, Fault Diagnosis, Field Operations | (Fault Diagnosis joins the network operations desk) |
| 6 | [06](spec/06-business-customers.md) | business, inventory (serviceability) | Enterprise Quote Preparation, Tender Response, Service Level Report | Business desk |
| 7 | [08](spec/08-wholesale-and-partners.md), [09](spec/09-regulatory-and-compliance.md) | wholesale, compliance | Wholesale Agreement Review, Settlement Reconciliation, Regulatory Monitoring, Regulatory Return Preparation, Data Subject Request, Policy and Procedure Q&A | Compliance desk (Settlement Reconciliation joins the revenue assurance desk) |

Steps 1 to 4 below need no cluster. Step 5 needs one, and a person to sign in.

## Before you start

1. Read [spec/00-operator-and-rules.md](spec/00-operator-and-rules.md) in full, then the area file of your group, then [OPEN-SOURCE-REVIEW.md](OPEN-SOURCE-REVIEW.md).
2. Read the pack this one follows, where every step below has already been done once: [insurance/README.md](../insurance/README.md), [insurance/BUILD-ON-A-CLUSTER.md](../insurance/BUILD-ON-A-CLUSTER.md), [demo-insurer/README.md](../demo-insurer/README.md), [demo-insurer/SCENARIOS.md](../demo-insurer/SCENARIOS.md), and [docs/agent-folder-format.md](../docs/agent-folder-format.md).
3. Read one system of the insurer in code, from its seed file to its tests: `demo-insurer/insurer/seed_claims.py`, `demo-insurer/insurer/systems/claims.py`, `demo-insurer/tests/test_scenarios.py`. And one agent folder that passed, all four files: `insurance/agents/coverage-check/`. Its `state.notes` says what had to change before it passed.
4. Run the insurer's tests once, so that you know the tools work: from `demo-insurer`, `python -m pytest -q`.

## Step 1: build the group's systems in the invented operator

The first group also creates the service. Copy the skeleton of `demo-insurer/` to `demo-operator/` (the app, the store, the common helpers, the MCP doors, the events, the config, `main.py`, the Dockerfile, the requirements, the test set-up) and change the names: the package is `operator_demo`, the settings are `OPERATOR_...`, the landing page says Larkstone Telecom. Take no insurer data with it. Add a workflow `demo-operator tests` beside the three that exist in `.github/workflows/`.

For each system of the group:

1. **The seed file** (`seed_<system>.py`): the records of the area file, with every date built from the operator date by the helpers. Start from the cases: each row of a case table in the area file is a record, or a few, that makes its right answer true. Then add the plain records around them, so that a case does not stand alone in an empty system.
2. **The system file** (`systems/<system>.py`): the operations the area file names. Every `operationId` is snake_case, verb first and unique across the service. Every description is written for a language model: what comes back, field by field in words, what the operation works out, which way a value exactly on a limit falls, and what the operation does not do. A draft's summary ends in "(draft)", a change's in "(change)", and a look-up sent as a POST says "(reads only)".
3. **SCENARIOS.md**: one section for the system in the style of the insurer's: every case, what it is for, and the right answer with its figures as the service gives them. The area file's "right answer in short" is the design. SCENARIOS.md is the truth, because the tests prove it against the running service. Where the two differ after the build, SCENARIOS.md is right and the area file is corrected in the same commit.
4. **Tests** (`tests/test_<system>.py`): every right answer of the section proved against the service; every refusal; that a draft changes no status and is not part of a read; that one system's reset leaves the others alone; that no text in the data counts time or names a weekday; and the system in the OpenAPI, MCP and reset tests.
5. **README.md** of the service: the system's row, its operation count, and its "things to know".

Done when: the whole suite passes; `GET /<system>/openapi.json` answers for every system of the group; SCENARIOS.md holds every case of the area file; and a person reading SCENARIOS.md alone could mark an agent's work.

Rules that are easy to break here, all from [spec/00](spec/00-operator-and-rules.md): the system does the sums and the agent does the reading; one read gives one whole case; a saved draft is not part of a record's read; no operation decides for a person; no real vendor, product, operator, regulator or code table appears anywhere.

## Step 2: write the group's documents from the data

Four agents answer from documents: Runbook Q&A, Plan and Product Q&A, Policy and Procedure Q&A, and Wholesale Agreement Review. For each, a script under `demo-operator/tools/` writes the numbered texts the system serves into `telecom/library/<set>/` as Markdown and PDF, and a test keeps the two in step. The insurer's `tools/make_wording_documents.py` is the model. Each document says "invented" on its first line.

## Step 3: write the group's agent folders

One folder for each agent, `telecom/agents/<agent-id>/`, in [the format every folder follows](../docs/agent-folder-format.md): `agent.yaml`, `instructions.md`, `tests.yaml`, `README.md`, and `workflow.yaml` for a workflow agent. In `agent.yaml` the pack is `telecom` and the systems field is `demo_operator_systems`. Add `telecom` to the list of packs in the format document, and the field's name beside the other two.

Write from the built service, never from the area file alone: read the system's code, or call it, to see exactly what each read returns and what each save accepts. For every save your agent makes, post the body its instructions would produce for each test case and confirm the service accepts it.

**Every folder has at least these tests:**

1. Nothing connected: the agent says so, reads nothing, saves nothing, gives no answer.
2. Two or three right-answer cases from SCENARIOS.md that differ in outcome.
3. A case where a rule must not fire.
4. A case where two records disagree, or where the rules are silent, whichever the area has.
5. A record the system does not hold.
6. A refusal: asked to do the thing a person decides, as a second turn after the work.
7. For an agent that answers questions: a follow-up question in the same conversation.

Every expected line of a test needs a sentence in the instructions that produces it. Every `does_not_say` phrase is an affirmative claim that only a wrong reply would hold, and is in neither the test's own input nor a right refusal. Where a wrong figure is likely, a check fails it.

**`workflow.yaml`**, for the 25 workflow agents: the trigger (by hand with a form, on a clock, by a webhook, by a call), the form's fields with their kinds, the one work step that hands the message to the agent and the exact message it builds from the fields, the approval step where the area file names one with who may approve, the step after approval, and which step's text is the workflow's result.

Add a check to `demo-operator/tests/test_agent_folders.py`, as the insurer has: each operation an agent names exists in a system it lists, and each operation that writes is listed under the agent's `changes`.

Done when: the folder check passes; every right answer in every `tests.yaml` is one SCENARIOS.md gives; and the index row links the folder and says "Written. Not yet built on a cluster".

## Step 4: build the group's desks

Each desk is a settings folder for [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), `telecom/desks/<desk>/`: `desk.config.json`, `cases.json`, `demo-replies.json`, `README.md`. [spec/10-desks.md](spec/10-desks.md) gives each desk's queue, kinds of case, decisions and register. The insurance desks are the model. Work on a clean clone of the engine's `main`. Do not change the engine for a desk: where the engine cannot draw something, write the gap in the desk's README and the index.

Done when: the desk runs end to end against a stand-in agent that returns the right answers, every case of `cases.json` matches SCENARIOS.md, and a person has looked at the desk on a desktop screen and a phone screen.

## Step 5: build and test the group's agents on a cluster

### What you need

1. **A development cluster and a sign-in on it** that may create agents and workflows, import tools and set tool approval policies. The person you work for signs in. An assistant never types a password, a token or a key into a sign-in page, and stops if one appears.
2. **The invented operator running on that cluster**, its key check on and its date pinned with `OPERATOR_TODAY=2026-11-28`. Deploy it from `demo-operator/main.py` as the [install guide](../demo-bank/docs/install-on-katonic.md) says. Check: `GET <operator>/health` gives the operator date, and `GET <operator>/<system>/openapi.json` answers for every system of the group.
3. **The operator's key**, from the person who deployed it, kept in a file outside this repository. Read it from the file when a command needs it. Never print it, and never write it into a report, a note, a message or a commit.

A redeploy puts all the operator's data back to the start, saved drafts included: redeploy only when no test is running. Only the person who owns the app can redeploy it.

### 5a. One tool connection for each system

In Control Room, Tools, import `<operator>/<system>/openapi.json` once for each system of the group: authentication "API key (header)", header name `X-API-Key`, the key as its value, the access group of the team that will own the agents, and a name of the form `Larkstone demo operator: <system>`. If a system gains an operation later, import again: the connection does not learn it by itself.

### 5b. Decide what waits for approval, before the first publish

Each `agent.yaml` lists the tools that change something under `changes`, with `waits_for_approval`.

- For every draft save (`waits_for_approval: false`), add an "Auto-approve" row in Studio, Tool approval policies, **before** you publish the agent that holds it. Add the rows one tool at a time. The same for a look-up that is sent as a POST: in this pack `check_recent_sim_change` and `measure_service_levels_with_exclusions`, and any other the area files mark "(reads only)".
- For a tool marked `waits_for_approval: true`, do not rely on the default. What holds it is a rule in Control Room, Policies: action "Requires approval", the tool connection as the server, the tool's name. A person with the right to govern the workspace creates that rule. An assistant asks for it and does not create it. In this pack one chat agent holds such tools: Fault Diagnosis (`run_intrusive_line_test`, `request_field_visit`). Ask for the two rules before that agent's first test.

### 5c. Build and test the chat agent

For each agent, as [insurance/BUILD-ON-A-CLUSTER.md](../insurance/BUILD-ON-A-CLUSTER.md) step 3 sets out, and with its rules that keep the result honest. In short:

1. Check that the connection holds the operations under `needs`.
2. Build a blank chat agent: the name, a description of at most 160 characters, the whole of `instructions.md` proved the same byte for byte, the model tier, no skills, knowledge or memory unless the folder says so.
3. Run the "nothing connected" test on the draft with no tools, five runs.
4. Attach exactly the operations under `needs`.
5. Publish to the development environment, in the Work Room, for the team.
6. Run the other tests in the Work Room: a new conversation for every run, five runs of every test, every reply kept word for word with the tool calls shown.
7. Judge every run against `tests.yaml`, strictly and literally. A test passes only at five passes in a row.
8. Prove what was saved, by reading the record from the operator. Prove what must not have changed.
9. Write a report.

Never change `instructions.md` to make a test pass while you are testing. Say which side is wrong (the instructions, the test, or the operator's data), fix that side in the repository in a commit that says so, publish the new version, and run the failed tests five times again with one run of each of the others as a control. A run lost to the cluster is no result. Touch nothing that is not yours. Say "not checked" where you did not check.

### 5d. Build and check the workflow that wraps it

Only after the chat agent passes. For each workflow agent, from its `workflow.yaml`:

1. **Build** a blank workflow with the agent's name and the words "(automation)". On its trigger, add the form's fields. Add one step that hands the work to the published agent, with the message built from the fields. Where the folder names an approval, add the approval step and the step after it. Set the workflow's result to the work step's text.
2. **Publish** it for the team.
3. **Start it from Work Room, Automations** with the form, once for each right-answer test of the folder. A run passes when the result is a reply that passes that test's checks, and the operator holds the draft the reply says was saved. One run each is enough here: the agent's five runs are already done.
4. **Where there is an approval step**, check on one run that the run waits, that nothing was sent or changed before a person decided, and that the page shows the person what they are approving. The tester never approves or declines: ask the person to approve one run and decline one, and record both outcomes and what the operator holds after each.
5. **Prove one real start in each group**: one scheduled workflow started by its clock, and one event-triggered workflow started by an event from the operator (`POST <operator>/admin/simulate/<event kind>` with a subscription pointed at the workflow's webhook). Record what started, when, and the run it made. Then pause the schedule.

Things met on the cluster the earlier packs were built on. They may be mended by the time you read this:

- A workflow's input fields were set on the canvas trigger, not in the wizard.
- A step read the form as `$trigger.<field>` and an earlier step as `$<step id>.text`.
- With an approval as the last step, the workflow's result was the approval record, because the default result read the last step. Set the result by hand.
- The workflow's tier did not change the tier of its steps. Set each step's.
- An approval step's own defaults (who is told, who may approve, how long before it declines by itself) were set on the canvas and were not what a business user would expect. Read them and set them.
- Publishing a workflow turned a paused schedule back on. Check the schedule after every publish.
- If the step that hands work to a published agent cannot be made to work on your cluster, do not rebuild the agent as model steps to get round it. Record exactly what happened and stop for the person's decision: the agent's tested instructions and tools must be what runs.

### 5e. The agents that are not a chat agent with a wrapper

- **Network Security** (autonomous): build it in the form the area file names. If the cluster's autonomous kind cannot hold the tools, build it as a chat agent, say so in its State, and do not call it tested as autonomous.
- **Field Operations** (a manager with two specialists): build the two specialists first as chat agents and test each alone, then the manager. A manager holds no tools of its own, and a team cannot be run with nothing connected: its `tests.yaml` says which tests run on the specialists.
- **The four agents that answer from documents**: after the tests with numbered records pass, run the same tests once more as an unpublished draft with the documents of `telecom/library/` in a knowledge source and without the read that serves the records. Make sure the tester is in the source's access group. Record the result as it comes out, pass or not, in the agent's State.

## Step 6: record the result in the repository

When an agent passes every test five runs in a row, three places say so and must agree: the `state` block of its `agent.yaml`, the State row of its `README.md`, and its row in the index. Copy `insurance/tools/set_state.py` to `telecom/tools/set_state.py` with the pack's paths, and use it. Add to `state.notes` whether the wrapping workflow was started from Automations and checked, and whether a clock or an event has started it.

An agent that is built and has not passed is recorded as exactly that, with which test is not finished and why.

Then update the table at the top of this page and the status paragraph of the index, run the operator's tests, and commit the named paths only.

## What the design leaves to the build

The area files were written side by side and then checked against each other. These points are known to be open. Settle each in the group that reaches it, and correct the area file in the same commit.

- **Ids that cross areas.** The service level cases of [06](spec/06-business-customers.md) speak of "outage 1, outage 2": give them outage and ticket ids in `assurance`. The reconciliation rows of [05](spec/05-orders-and-activation.md) name orders only: add the changes that touched a record where a case needs one. The complaint `CMP-1501` of [03](spec/03-customer-care.md) names a bill that [04](spec/04-billing-and-revenue.md) does not yet hold.
- **Figures that must agree.** The notice of 10 days in service level SL-5 of [06](spec/06-business-customers.md) and the contracts' notice terms in `change` ([01](spec/01-network-operations.md)). The complaint times of the complaints code in [03](spec/03-customer-care.md) and the obligations and the return format in [09](spec/09-regulatory-and-compliance.md). The plans and prices of the catalogue in [03](spec/03-customer-care.md) and the bills in [04](spec/04-billing-and-revenue.md).
- **The time of day.** The operator has a pinned date and no clock. Where a case counts hours (a stopped order, the age of a line test, a SIM change), the area file says what the count runs to. Keep one rule for each system and write it in the system's "things to know".
- **Ids added by later areas** to the inventory, the tickets, the outages and the changes are listed in the area file that adds them. When a later group adds records to a system an earlier group built, run the earlier group's tests again.
- **The fourteenth system.** `field` may be folded into `assurance` if it stays small.

## What "done" means for the pack

- Every row of the table at the top of this page reads full.
- Every right answer in every `tests.yaml` is proved by the operator's own tests.
- Every State says only what was run.
- The pack's row in the [repository's README](../README.md) says what is built.
- Nothing in the repository names a cluster, a person, a key, a ticket or a real company's product.

## What only a person does

- Signs in to the cluster, and deploys or redeploys the operator if they own the app.
- Gives the operator's key, in a file.
- Creates the "Requires approval" rule for a held tool.
- Approves or declines a run that waits at an approval step.
- Decides anything this page says to stop for.
