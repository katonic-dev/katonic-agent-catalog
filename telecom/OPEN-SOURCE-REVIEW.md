# What open source was read before the telecom pack was designed

Before the design in [spec/](spec/00-operator-and-rules.md) was written, public repositories were read in code: the agents and their prompts, the tools, how a person approves, the sample data and the tests. Reading a README is not enough: an earlier review of this kind, done from READMEs, missed pieces worth having.

**What was taken: ideas and designs. What was not taken: code, prompts, sample data, names.** Every agent, rule, record and case in this pack is our own. The vocabulary of the invented operator's systems follows two public standards, as section 3 says.

Nothing was installed, built or run. Each repository was read at the commit named, on 28 November 2026.

## 1. Customer care

### signaldesk

`github.com/binodsapkota/signaldesk`, commit `a48c435`, MIT. A small telecom customer-care desk: a concierge and five specialists (technical support, billing, account, plans, retention) that hand a conversation to one another, with an invented carrier's data and a set of scored test conversations. About 3,700 lines of C#. A hobby project with one commit, and the only telecom-specific find of the first scout.

Read: every agent definition, every tool, the approval pause, the data, the rule-based stand-in agents and the 19 test conversations.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| The bill read works out the difference from the last bill itself, so the agent explains and does not calculate | `get_bill` returns each line beside the same line on the previous bill, with the difference. Bill Explanation, [03](spec/03-customer-care.md) and [04](spec/04-billing-and-revenue.md) |
| A money limit is enforced in the tool, and the refusal says what is left of the allowance | The adjustment rules and the care agent's limit are measured by the system. Bill Dispute Investigation, [04](spec/04-billing-and-revenue.md) |
| A fixed order for a fault: is there an outage, then the test, then a visit | The diagnosis procedure as numbered steps, with "no visit while an outage is open". Fault Diagnosis, [07](spec/07-service-assurance-and-field.md) |
| A test names the tools that must not be called and the records that must not appear, as well as the ones that must | Every folder has a "rule must not fire" test and proves what was not saved. [BUILD-PLAN.md](BUILD-PLAN.md), steps 3 and 5 |
| A test where the person approves and the system still refuses, because a rule forbids it | A held change is refused with a plain sentence when its precondition fails. [spec/00](spec/00-operator-and-rules.md), rule 6 |
| An offer that must not be applied without a yes | Churn Prediction proposes from the approved list and contacts nobody. [03](spec/03-customer-care.md) |

Not taken, and why:

- **Who approves.** There the customer in the chat approves a change to their own account. Here a named member of staff decides, through a desk or an approval step, and the agent holds no tool that changes an account.
- **Agents that hand a conversation to one another.** This pack has one agent for one job. Only Field Operations is a manager with specialists.
- **Its data**: the carrier, the customers, the plans, the prices, and everything specific to one country.

### agent-desk

`github.com/huabeitech/agent-desk`, commit `0dde5e0`, Apache-2.0. A support desk where an AI answers first from a knowledge base and passes the conversation to a person. About 85,000 lines of Go and a web app. Not telecom.

Read: how the prompt is put together, the decision the model must return, the hand-over to a person, tickets, how an answer is tied to its sources, the evaluation cases.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| The model returns a decision (reply, hand over, ask whether to hand over) and the program acts on it. The model never claims a hand-over happened | The agent says a draft was saved only if the system's reply says so. A reply ends in exactly one proposal from a fixed list. [spec/00](spec/00-operator-and-rules.md) |
| With nothing in the knowledge base to support an answer, a set behaviour: say so, ask for the one missing detail, or pass to a person. Greetings may be answered freely; facts, prices and policies are never inferred | The answer states of the four agents that answer from documents, each reply exactly one state, with "the documents are silent" as a state of its own |
| A draft of a ticket that comes back with what is missing and the questions to ask, before anything is written | The call-back request: a draft that books nothing and promises no time. [03](spec/03-customer-care.md) |
| A rule for a tool sits with the tool, not in the main prompt | The description of every operation says what it does not do. [BUILD-PLAN.md](BUILD-PLAN.md), step 1 |
| A list of signs that a complaint is rising: the press, a lawyer, the regulator, money at risk | The complaint cases include one already with the ombudsman, which the agent does not draft for. [03](spec/03-customer-care.md) |

Not taken: its prompts and seed texts; its confirm-word matching; sorting a conversation by keywords.

### Conversation Knowledge Mining Solution Accelerator

`github.com/microsoft/Conversation-Knowledge-Mining-Solution-Accelerator`, commit `91a0ecc`, MIT. At this commit a general pipeline that extracts a summary, entities, key phrases and topics from documents and offers a chat over them. Tied to one cloud.

Read: every extraction prompt and its output shape, and the sample data. It holds five telecom call transcripts, each one unbroken paragraph with no speakers marked, and 188 processed helpdesk calls.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| The kinds of thing to pull from a contact: the issue, the resolution, the policy, the amount, the reference number | The parts of the case note Contact Summary writes: why the customer made contact, what was agreed, what is still to do. [03](spec/03-customer-care.md) |
| Numbers come from a query, words come from the documents | The system does the sums, the agent does the reading. [spec/00](spec/00-operator-and-rules.md), rule 1 |

What this pack does that it does not: our transcripts have numbered turns with a speaker and a time, and every point in a case note names the turn it rests on. A transcript as one paragraph gives nothing to cite.

Not taken: its transcripts, recordings and sample records; anything about sentiment or satisfaction, which this pack does not score.

## 2. Network operations

### Aurora

`github.com/Arvo-AI/aurora`, commit `9ad15d2`, Apache-2.0. Incident investigation for cloud systems: an alert comes in, a set of read-only investigators look at changes, history and runbooks, and a writer produces a root cause analysis and, as a separate step, a postmortem.

Read: the triage and synthesis steps, the investigator roles, the finding format and its check in code, the investigation and conclusion rules, how evidence is numbered and cited, the postmortem action, the change risk review, how one incident is matched to an earlier one.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| A conclusion is one of three classes, set by the investigation and obeyed by the writer: confirmed, likely, not determined. A report whose cause is not determined opens by saying so | The cause section of a review opens with one of three set sentences. Post-incident Review, [01](spec/01-network-operations.md) |
| "Ruled out" and "not checked" are parts of every finding | The two lists after the cause, and the marks `checked, nothing found` and `not checked`. [01](spec/01-network-operations.md) |
| A change counts only with proof that it was carried out. Merged is not deployed | An approved change is not a change that happened: only a completed change with its actual times is a recent change. Trouble Ticket Enrichment, [01](spec/01-network-operations.md) |
| An earlier conclusion is something to test, never a verdict. Earlier cases are matched by the service, not by a title | A similar past ticket is matched by the system on equipment model and probable cause, and the agent reports its recorded cause as that ticket's, not as this one's. [01](spec/01-network-operations.md) |
| Every statement cites a numbered piece of evidence that the program built, and nothing else may be cited | Every row of a table names the id of the record it rests on, and every id is one the system returned. [spec/00](spec/00-operator-and-rules.md) |
| The postmortem is a separate step with its own save, earlier versions are kept, and a contributing factor is written only where the conversation shows it | A draft save keeps every version. A contributing factor is written only where a bridge note or a ticket note states it. [01](spec/01-network-operations.md) |
| Looking up a runbook never carries out its steps, and a missing runbook is reported as a gap | Runbook Q&A quotes a step and runs nothing, and "no runbook covers this" is an answer. [01](spec/01-network-operations.md) |
| A review of a change asks one stated question and lists what to flag and what not to | One row for each change rule, in order, every time. Change Request Review, [01](spec/01-network-operations.md) |

Not taken: its prompts and role files; several investigators working at once (one agent does one job here); suggesting a fix with a command to run (no agent of this pack proposes a command for the network); anything specific to cloud systems.

### HolmesGPT

`github.com/HolmesGPT/holmesgpt`, commit `0e55d51`, Apache-2.0. One agent that investigates an alert with read-only tools and writes up what it found. A sandbox project of the Cloud Native Computing Foundation.

Read: the main prompt and its blocks, how a tool set is declared and what makes a tool read-only, how a runbook is matched to an alert, the shape of a finding, and the 294 evaluation cases.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| What an incident touched is written in four groups: affected, with the exact evidence that proves it; checked and healthy; changed in the window for another reason; not checked. The reach of a fault is never widened by inference | The four groups of Trouble Ticket Enrichment. Depending on faulty equipment is not being affected. [01](spec/01-network-operations.md) |
| A runbook has a short description used for matching and may be tied to named alerts. The agent reads it only on a clear match, says which it used and which steps it could not do | Runbooks carry a description and their alarms. Runbook Q&A, [01](spec/01-network-operations.md) |
| A tool's result can be "no data", apart from "error" | Nothing found is an answer, not an error. [spec/00](spec/00-operator-and-rules.md), rule 14 |
| When the exact thing asked about has no data and a thing with a similar name has, both facts are reported and never merged | Two records that disagree are kept disagreeing, and a record the system does not hold gets the short reply with the id written out. [spec/00](spec/00-operator-and-rules.md), rule 12 |
| A test case is a set-up, a question and a list of expected sentences, all of which must be present. Cases where nothing should be found are cases in their own right | The tests every folder has, with a case where a rule must not fire. [BUILD-PLAN.md](BUILD-PLAN.md), step 3 |
| A health check answers with its reason first, and what cannot be verified is not called healthy | A reading that is absent is "cannot be told", never zero and never "within". Network Optimization and Predictive Maintenance |

Not taken: its prompts, tool sets and test fixtures; a model as the judge of a test (here each run is judged against written lines, strictly); commands a user may approve and then save as always allowed.

### Keep

`github.com/keephq/keep`, commit `7761f0a`. MIT, except the folder `ee/`, which is under the project's enterprise licence. Nothing under `ee/` was read. Alert management: events are de-duplicated, enriched, grouped into incidents by rules, and shown to operators. No agents.

Read, in the MIT part: the alert and incident records, de-duplication, correlation rules, enrichment by mapping, maintenance windows, the service map, the trail of actions.

Designs taken:

| Design | Where it is in this pack |
|---|---|
| A repeating alert keeps one identity, with a count and its first and last times | A repeating alarm is one record with a count. [01](spec/01-network-operations.md) |
| What enrichment adds is kept apart from the event as received, and named as added | What was added is kept apart from what was received. [spec/00](spec/00-operator-and-rules.md), rule 15 |
| An alert inside a maintenance window is labelled, not removed | An alarm inside approved planned work is marked with the change's id. [01](spec/01-network-operations.md) |
| A lookup table that adds the site, the owner and the service to an alert by its equipment | The inventory's read of a resource returns what depends on it, so an agent never walks the map itself. [01](spec/01-network-operations.md) |
| A fixed list of kinds of event in an incident's trail | The timeline of an incident is put in order by the system from typed, timed entries, each with its source. [01](spec/01-network-operations.md) |
| A grouping proposed by a model is a candidate until a person confirms it | Scam Report Triage's groups by wording are the agent's proposal to the fraud team, beside the system's exact groups. [02](spec/02-fraud-and-security.md) |

Not taken: one instruction in its report code asks a model to find root causes "not explicitly mentioned" in the data. This pack's rule is the opposite. Also not taken: opening an incident for a whole application when any one of its services has an alert.

None of the three has a record of a change request or a review of a method of procedure. That part of the pack is our own.

## 3. The standards whose words the systems use

The files of fifteen TM Forum Open APIs (`github.com/tmforum-apis`) and six CAMARA APIs (`github.com/camaraproject`) were read. All are Apache-2.0. TM Forum's repositories say they mirror the official versions, whose authoritative source is TM Forum's own directory.

The invented operator borrows names and values. It is not an implementation of any of these APIs and claims no conformance. The values below are as the files spell them, and the build uses them as written.

**Which version.** TM Forum publishes a version 4 and a version 5 of most of these APIs, and they differ: version 4 of the alarm API has no fixed lists at all, and the resource states are spelled differently in the two. The invented operator follows **version 5** wherever one exists, and version 4.0.0 for change management, which has no version 5 in the repository.

| API | File read | Resource | Values the operator uses |
|---|---|---|---|
| TMF621 Trouble Ticket | v5.0.1 | `troubleTicket` | `status`: acknowledged, rejected, pending, held, inProgress, cancelled, closed, resolved. `severity`, `priority` and `ticketType` are free text in the standard (its examples: Critical, Major, Minor; Critical, High, Medium, Low; incident, complain, request) |
| TMF642 Alarm Management | v5.0.1 | `alarm` | `state`: raised, updated, cleared. `ackState`: unacknowledged, acknowledged. `perceivedSeverity`: critical, major, minor, warning, indeterminate, cleared. `alarmType`: communicationsAlarm, processingErrorAlarm, environmentalAlarm, qualityOfServiceAlarm, equipmentAlarm, and the violation kinds |
| TMF638 Service Inventory | v5.0.0 | `service` | `state`: feasibilityChecked, designed, reserved, inactive, active, suspended, terminated |
| TMF639 Resource Inventory | v5.0.0 | `resource` | `administrativeState`: locked, unlocked, shuttingDown. `operationalState`: enabled, disabled. `usageState`: idle, active, busy |
| TMF678 Customer Bill | v5.0.0 | `customerBill`, `appliedCustomerBillingRate` | `state`: new, onHold, validated, sent, partiallyPaid, settled. Amounts as `{unit, value}` |
| TMF635 Usage | v5.0.0 | `productUsage` | `status`: initialized, rejected, validated, rated, corrected, superseded, notRated, failed |
| TMF622 Product Ordering | v5.0.0 | `productOrder` | `state`: acknowledged, rejected, pending, held, inProgress, cancelled, completed, failed, partial, assessingCancellation, pendingCancellation. Item `action`: add, modify, delete, noChange |
| TMF620 Product Catalog | v5.0.0 | `productOffering`, `productOfferingPrice` | `lifecycleStatus` is free text in the standard. The operator's own values are named in [03](spec/03-customer-care.md) |
| TMF629 Customer | v5.0.1 | `customer` | `status` is free text in the standard |
| TMF683 Party Interaction | v5.0.0 | `partyInteraction` | `status`: open, inProgress, completed (the standard calls these examples) |
| TMF655 Change Management | v4.0.0 | `changeRequest` | `status`: acknowledged, requestForAuthorization, waitForApproval, approved, scheduled, inProgress, completed, failed, fallbackExecution, postImplementationReview, cancelled, rejected. `impact`, `risk` and `priority` are free text |
| TMF656 Service Problem | v5.1.0 | `serviceProblem` | The same status list as a trouble ticket. It names the affected services and resources, the underlying alarms and the root cause service and resource apart |
| TMF628 Performance | v4.0.0 | measurement jobs | Granularity names only (five minutes, an hour, a day). The operator's readings are its own |

Also read and not used: TMF657 (it defines service level targets, not measurements) and TMF681 (messages).

Things the build must know, all from the files:

- **The standards give no rules for moving from one status to another.** The operator's are its own, and each area file says which moves a held change may make.
- **A trouble ticket has no field for the affected service or equipment.** It points to things through `relatedEntity`, each with a `role`. The operator uses the roles `affectedService` and `affectedResource`.
- **An alarm names its equipment in `alarmedObject`**, and may carry `affectedService`, `correlatedAlarm`, `parentAlarm`, `isRootCause`, `serviceAffecting` and `plannedOutageIndicator`. The operator fills `alarmedObject`, `serviceAffecting` and `plannedOutageIndicator`. It leaves `isRootCause` and `correlatedAlarm` out: saying which alarm is the cause is not the system's to say, and not the agent's either.
- **What must be given to create a record** is small: for a ticket a description, a severity and a type; for a change request its target, priority, planned start and end, and type. The operator's cases are seeded, so this matters only for the events it simulates.
- **Notification operations** (hub and listener) make up about half of the operations in every file. The operator has none.

### CAMARA

| API | File read | What it gives | Used here |
|---|---|---|---|
| SIM Swap | `sim-swap.yaml`, working version (release 2.2.0) | Two look-ups, both sent as POST: the date of the last SIM change, and whether the SIM changed within a number of hours (`maxAge`, 1 to 2400, 240 if not given), answered as `swapped` true or false. Where the date may not be kept, it is returned as null | The shape of `check_recent_sim_change`. SIM Swap Check, [02](spec/02-fraud-and-security.md) |
| Call Forwarding Signal | working version | Whether unconditional call forwarding is active on a number | Not used. A candidate for a later fraud case |
| Know Your Customer, match | 0.3.0 | Each detail sent is answered as true, false or not available | Not used. The porting comparison in [05](spec/05-orders-and-activation.md) answers same, different or missing in the same spirit |
| Number Verification, Device Status, Quality on Demand | various | Look-ups on a device, and a request for a quality of service session | Not used |

Two points on the SIM swap look-up. The standard counts back from the moment of the call; the invented operator has a pinned date and no clock, so it counts back from the time of the request being checked, and its description says so. And the standard's file asks for a signed-in caller with a named permission for each look-up; the invented operator has one key for everything, so a real network's sign-in is not tried by this pack.

## 4. Telecom repositories

A first scout on 23 November 2026 found one telecom repository (signaldesk, above). A second, targeted look on 28 November went through the samples of the large vendors and the standards bodies. Open code is thin. It covers network operations and the SIM swap look-up. For customer care, quotes, orders, porting, billing, revenue assurance, settlement and regulatory returns it has nothing an operator's agent could be modelled on. Those parts of the pack are our own from the first line.

### Read in code

| Repository | Commit | Licence | What it is | Design taken |
|---|---|---|---|---|
| `aws-samples/sample-sop-agent-for-telco` | `72cf89d` | MIT-0 | Agents that carry out written procedures on a lab 5G core: an alarm comes in, it is correlated, a procedure is chosen and run | An alarm reference kept as data: for each kind of alarm its layer, the alarms it usually follows, its probable cause and its procedure. Correlation by a fixed rule (an alarm whose upstream alarm is open is a symptom), with judgement only where the rule cannot say. A procedure as numbered steps, each with what is expected after it |
| `aws-samples/sample-TelcoBuddy` | `6eed707` | MIT-0 | An alert is diagnosed by an agent, a person approves, then a fix runs. A catalogue of injected faults | Diagnosis first, action only after approval, with the diagnosis on the approval record. A repeat window and a correlation window as stated figures. A test scenario that lists what the agent is expected to do |
| `aws-samples/sample-multi-agent-collaboration-using-bedrock-for-telco-network-ops` | `8c5af52` | MIT-0 | A supervisor with a maintenance agent, an alarm agent and a performance agent | For a question about a site, read all three (planned work, alarms, readings) before answering. Never ask a person for what a tool can fetch |
| `Azure-Samples/multimodal-agent-telecom-anomaly-detection` | `3c2ca8a` | MIT | A detector compares a site's design with photographs of it, and a reviewer with no tools checks the report | A report always has a list of gaps. A report-only agent says in its report that nothing was sent and nobody was dispatched |
| `camaraproject/MCPEnablement_PI1` | `0c9d141` | Apache-2.0 | An MCP server over CAMARA's APIs: SIM swap, identity match, location, roaming, reachability | The SIM swap look-up as two reads (the date of the last change; whether it changed within a number of hours). A test case made by setting a number's last SIM change. A rule in the shape "a signal from the network, a rule of the business, a named anomaly, and a person to go to" |
| `gsma-labs/evals`, with one sample row of the TeleLogs data | (current) | MIT | The benchmark of the GSMA's Open Telco work. TeleLogs is a set of root cause cases | How a root cause case is laid out: the facts the reader needs, a small table of evidence, a closed list of causes, one right answer. Our cases are our own, and none of theirs is copied |
| `BubbleRAN/telco-network-configuration` | (current) | Apache-2.0, with other terms for the lab network | Agents that change radio settings on a lab network, measure, and put the setting back if it got worse | None taken. No agent of this pack changes the network |

Where these are in the pack:

- The **alarm reference** is a record in `assurance`: for each `specificProblem`, the layer it sits on, the problems it usually follows and the runbook written for it. `list_alarms_for_resource` uses it to mark an alarm as downstream. The agent reads it and does not guess. [01](spec/01-network-operations.md)
- **Diagnosis first, action after a person's approval** is Fault Diagnosis: the step is proposed with its reason, and the test that interrupts a service is a request that waits. [07](spec/07-service-assurance-and-field.md)
- **Planned work, alarms and readings read together** is what `get_trouble_ticket` returns in one call. [01](spec/01-network-operations.md)
- **The look-up in the shape of CAMARA's** is `check_recent_sim_change`. [02](spec/02-fraud-and-security.md)
- **"Nothing was sent"** is the last line of the Summary of every agent behind a desk, the line that starts `Saved:`, and the set sentences of every refusal. [spec/00](spec/00-operator-and-rules.md)

Not taken from any of them: an agent that runs commands on the network, with or without approval; a model's "confidence" as a figure; procedures written by a model when none exists; any sample data, site, city or number.

### Looked at and not read in code

| Repository | Licence | Why not |
|---|---|---|
| `netboxlabs/netbox-mcp-server` | Apache-2.0 | A read-only MCP server over an inventory tool. Worth a read when an agent is connected to a real inventory |
| `aws-samples/sample-devops-industry-expert-telco` | MIT-0 | One agent hands a question to a specialist in the mobile standards. Worth a later read |
| `gsma-labs/telco-expert` | MIT | Search over the published standards. For questions on standards, not for an operator's own work |
| `oopsyz/mcp` | MIT | A mock of the product catalogue API behind an MCP server. Infrastructure only |
| `NVIDIA-AI-Blueprints/ai-virtual-assistant` | Apache-2.0 | A retail assistant, marked as no longer maintained |
| `automateyournetwork/pyATS_MCP` | MIT | Runs device commands. Outside what this pack does |
| `open5gs/open5gs` | AGPL-3.0 | A mobile core, used as the lab by two of the samples. Not agent code, and its licence rules out copying |
| `killbill/killbill` | not read | A billing engine. No agent content known |

Searched for and not found as public code: an agent framework for network operations that one vendor has written about; the agent pieces that one industry catalyst project describes; any agent for customer care, bill explanation, revenue assurance, number porting, settlement or regulatory returns at an operator.

### Where open source is empty

| Area | What open source has | So |
|---|---|---|
| Customer care | One hobby desk and general support desks | Our own, on the standards' words for customers and bills |
| Business customers | A mock of the product catalogue | Our own |
| Orders and activation | Nothing | Our own, on the standards' words for an order |
| Billing and revenue | Nothing | Our own |
| Fraud and security | The SIM swap look-up | The look-up's shape taken. The patterns, the identity procedure and scam reports are our own |
| Network operations | The most: correlation, evidence rules, runbooks, approval before a fix | Designs taken as sections 2 and 4 say. Change review and planned work are our own |
| Service assurance and field | Fault diagnosis on lab networks | The order of a diagnosis taken. Maintenance and dispatch are our own |
| Wholesale and partners | Nothing | Our own |
| Regulatory and compliance | Nothing | Our own |
