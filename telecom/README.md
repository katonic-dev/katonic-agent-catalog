# Telecom pack

32 agents a telecom operator can build on the Katonic platform, and the desks people use them through. They are specified against one invented company, Larkstone Telecom: mobile, home broadband, business services and wholesale in the invented country Meridia.

**Status: specified, nothing built.** The pack is at its first step. The design is written: the invented operator and its systems, the cases with their right answers, every agent and every desk. The operator's service, the agent folders and the desks are not written yet, and no agent is built on a cluster. The State column says where each one stands.

- To read the design, start at [spec/00-operator-and-rules.md](spec/00-operator-and-rules.md). The files `01` to `09` give one area each, and [spec/10-desks.md](spec/10-desks.md) gives the desks.
- To do the build, read [BUILD-PLAN.md](BUILD-PLAN.md): the order of the work, how each piece is checked, and what "done" means.
- To see what open source was read first, and what was taken from it, read [OPEN-SOURCE-REVIEW.md](OPEN-SOURCE-REVIEW.md).

Every agent follows one rule: it prepares the work, and an engineer or a named member of staff decides. No agent changes the network, a bill or a customer's account. A tool that changes something waits for approval unless the operator has decided otherwise for that tool.

## Four things to know before you read the tables

- **A workflow agent is built twice over.** It is a chat agent that holds the instructions and is tested five runs a test, and a workflow that wraps it, so that staff start it from Work Room, Automations with a form, and a clock or an event can start it. The banking and insurance packs built the first half only.
- **Rules and documents are records here.** A real operator keeps its runbooks, tariffs, complaints code and change rules as documents. The invented operator serves them as numbered sections, so that an agent can be tried before any document store is connected. The same texts are kept as documents in `library/`, and the four agents that answer from documents are also tried with them in a knowledge source.
- **The system does the sums.** Minutes between two alarms, working days to a deadline, a bill line against the last bill, a reading against its threshold, a statement against the operator's own records: these come from the operator's systems as figures. The agent's work is the reading: which rule bears on the facts, what a note contradicts, what a document does not say, where two records disagree.
- **The systems speak the words of the public standards.** Tickets, alarms, services, bills, orders and change requests use the resource names, field names and status values of TM Forum's Open APIs, and the SIM swap look-up has the shape of CAMARA's. The invented operator is not an implementation of either and claims no conformance.

## The agents

| # | Agent | What it does | Type and form | How people meet it | State |
|---|---|---|---|---|---|
| | **Customer care** ([spec](spec/03-customer-care.md)) | | | | |
| 1 | Bill Explanation | Explains a bill line by line: what each charge is, which tariff or usage produced it and what changed since the last bill, and says when it cannot account for a charge | Conversational, answering | Chat | Specified. Not yet written |
| 2 | Plan and Product Q&A | Answers a question about plans, roaming, devices and terms from the operator's own catalogue and published terms, with the source, and says when they are silent | Conversational, answering | Chat | Specified. Not yet written |
| 3 | Complaint Handling | Classifies a complaint, sets out the timeline from the account and the contact history, and drafts the response and the log entry with the dates the complaints code sets | Workflow, event-triggered | Customer care desk | Specified. Not yet written |
| 4 | Contact Summary | Writes the case note after a call or a chat: why the customer made contact, what was agreed and what is still to do, each point with its place in the transcript | Workflow, API | Customer care desk | Specified. Not yet written |
| 5 | Churn Prediction | Lists the subscribers whose records show signs of leaving, with the reason for each, and proposes an offer from the approved list | Workflow, scheduled | Sent to the retention team | Specified. Not yet written |
| | **Business customers** ([spec](spec/06-business-customers.md)) | | | | |
| 6 | Enterprise Quote Preparation | Reads a business customer's requirement, checks each site and service against the catalogue and the serviceability records, and drafts the quote with what could not be confirmed listed | Workflow, event-triggered | Business desk | Specified. Not yet written |
| 7 | Tender Response | Drafts answers to a tender's questions from the approved answers and certificates, each with its source, and lists the questions nothing answers | Workflow, API | Business desk | Specified. Not yet written |
| 8 | Service Level Report | Prepares a business customer's service report from tickets, outages and measured performance against the contract's targets, and marks each target that was missed, with the evidence | Workflow, scheduled | Business desk | Specified. Not yet written |
| | **Orders and activation** ([spec](spec/05-orders-and-activation.md)) | | | | |
| 9 | Order Fallout | Lists the orders that have stopped part-way, finds where each one stopped and why, and proposes the fix | Workflow, scheduled | Order desk | Specified. Not yet written |
| 10 | Number Porting Check | Checks a porting request against the porting rules and the account: the details that must match, what is missing and the date the rules allow | Workflow, event-triggered | Order desk | Specified. Not yet written |
| 11 | Inventory Reconciliation | Sets what the inventory says is in service beside what the network reports, and lists the differences by likely cause | Workflow, scheduled | Order desk | Specified. Not yet written |
| | **Billing and revenue** ([spec](spec/04-billing-and-revenue.md)) | | | | |
| 12 | Billing & Revenue | Compares usage records with billing records, lists where the two disagree and groups the differences by likely cause | Workflow, scheduled | Revenue assurance desk | Specified. Not yet written |
| 13 | Bill Dispute Investigation | For a disputed charge, assembles the usage, the tariff, the earlier bills and the contacts, sets out what the records show and proposes an outcome under the adjustment rules | Workflow, event-triggered | Customer care desk | Specified. Not yet written |
| | **Fraud and security** ([spec](spec/02-fraud-and-security.md)) | | | | |
| 14 | Fraud Detection | Flags patterns that suggest SIM cloning, subscription fraud, call spoofing or a billing anomaly, with the records that show it | Workflow, scheduled | Fraud desk | Specified. Not yet written |
| 15 | SIM Swap Check | Sets a request to move a number to a new SIM against the identity procedure and the account's recent history, and lists what is missing or unusual | Workflow, event-triggered | Fraud desk | Specified. Not yet written |
| 16 | Scam Report Triage | Classifies the scam calls and messages customers report, groups the reports that share a sender or a wording, and drafts the blocking request with the evidence | Workflow, scheduled | Fraud desk | Specified. Not yet written |
| 17 | Network Security | Takes a security alert, gathers the readings and logs around it and past incidents like it, and writes up what it found | Autonomous | Network operations desk | Specified. Not yet written |
| | **Network operations** ([spec](spec/01-network-operations.md)) | | | | |
| 18 | Network Optimization | Finds where load is heading towards congestion and recommends rerouting or capacity changes, with the readings behind each | Workflow, scheduled | Sent to the capacity planning team | Specified. Not yet written |
| 19 | Trouble Ticket Enrichment | Gathers the alarms on the same equipment, the services and customers that depend on it, recent changes and past tickets like it, and adds a summary to the ticket | Workflow, event-triggered | Network operations desk | Specified. Not yet written |
| 20 | Change Request Review | Checks a change request against the change rules: the method of procedure, the rollback plan, the window, the services affected and other changes on the same equipment | Workflow, event-triggered | Change desk | Specified. Not yet written |
| 21 | Post-incident Review | Sets out the timeline of an incident from the tickets, the alarms and the bridge notes, lists the decisions and the gaps, and drafts the review in the operator's own format | Workflow, API | Network operations desk | Specified. Not yet written |
| 22 | Planned Work Notification | For a piece of planned work, lists the services and customers it will affect and drafts the notice each contract requires | Workflow, event-triggered | Change desk | Specified. Not yet written |
| 23 | Runbook Q&A | Answers an engineer's question from the operator's own runbooks and equipment manuals, with the section cited, and says when they are silent or disagree | Conversational, answering | Chat | Specified. Not yet written |
| | **Service assurance and field** ([spec](spec/07-service-assurance-and-field.md)) | | | | |
| 24 | Predictive Maintenance | Lists the sites and devices whose readings look like those before earlier faults, and proposes maintenance with the evidence | Workflow, scheduled | Sent to the maintenance planners | Specified. Not yet written |
| 25 | Fault Diagnosis | For a fault a customer reports, reads the service's records, the known outages and the last test results, and proposes the next step with the reason | Conversational, acting | Network operations desk, and chat | Specified. Not yet written |
| 26 | Field Operations | Proposes which technician to send to each job from skills, location and urgency, and answers a technician's question on site from the manuals, citing the page | Multi-agent, manager | Chat | Specified. Not yet written |
| | **Wholesale and partners** ([spec](spec/08-wholesale-and-partners.md)) | | | | |
| 27 | Wholesale Agreement Review | Reads a roaming, interconnect or wholesale agreement against the standard terms and lists each clause that differs, with the standard wording beside it | Workflow, API | Sent to the wholesale manager | Specified. Not yet written |
| 28 | Settlement Reconciliation | Sets a partner's settlement statement beside the operator's own records of the same traffic and lists the differences by route, period and likely cause | Workflow, event-triggered | Revenue assurance desk | Specified. Not yet written |
| | **Regulatory and compliance** ([spec](spec/09-regulatory-and-compliance.md)) | | | | |
| 29 | Regulatory Monitoring | Reads the regulators the operator names, summarises what changed and maps each change to the obligations register | Workflow, scheduled | Regulatory change desk | Specified. Not yet written |
| 30 | Regulatory Return Preparation | Prepares a return the regulator requires from the operator's records and in the regulator's format, and lists what the records do not hold | Workflow, scheduled | Compliance desk | Specified. Not yet written |
| 31 | Data Subject Request | For a request to see or erase personal data, lists the systems that hold it, assembles what is in scope and marks what concerns other people or must be kept by law | Workflow, event-triggered | Compliance desk | Specified. Not yet written |
| 32 | Policy and Procedure Q&A | Answers a member of staff's question from the operator's own policies and procedures, with the section cited, and says when they are silent | Conversational, answering | Chat | Specified. Not yet written |

When an agent's folder is written, its name here becomes a link to it and its State becomes "Written. Not yet built on a cluster".

## The desks

A desk is the shared case desk ([katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk)) with a different queue. Each one shows the cases, the agent's findings and draft, approve or send back, and a register of who decided what. [spec/10-desks.md](spec/10-desks.md) specifies each.

| Desk | Agents behind it | Who decides | State |
|---|---|---|---|
| Network operations desk | Trouble Ticket Enrichment, Post-incident Review, Fault Diagnosis, Network Security | The engineer who owns the ticket; the incident manager; the security team | Specified. Not yet written |
| Change desk | Change Request Review, Planned Work Notification | The change board; the service manager | Specified. Not yet written |
| Fraud desk | Fraud Detection, SIM Swap Check, Scam Report Triage | The fraud team | Specified. Not yet written |
| Customer care desk | Complaint Handling, Contact Summary, Bill Dispute Investigation | The complaints officer; the care agent; billing staff | Specified. Not yet written |
| Order desk | Order Fallout, Number Porting Check, Inventory Reconciliation | The order desk; the porting desk; the inventory team | Specified. Not yet written |
| Revenue assurance desk | Billing & Revenue, Settlement Reconciliation | The revenue assurance team; the settlement analyst | Specified. Not yet written |
| Business desk | Enterprise Quote Preparation, Tender Response, Service Level Report | The account manager and the pricing desk; the bid manager; the service manager | Specified. Not yet written |
| Compliance desk | Regulatory Return Preparation, Data Subject Request | The compliance officer; the privacy officer | Specified. Not yet written |

Regulatory Monitoring uses the regulatory change desk the catalog already has.

## A short way in

Once the first group is built, three agents will show the pack in a quarter of an hour, against the invented operator:

1. **Trouble Ticket Enrichment** on ticket `TT-6002`: the alarms, what depends on the router, and a software upgrade carried out on it 19 hours before the first alarm. The agent puts the change first among the points worth a look and does not say the change caused the fault.
2. **Post-incident Review** on incident `INC-8002`: the service came back after a restart and nobody recorded why it failed. The review says the records name no cause.
3. **Change Request Review** on change `CHG-9003`: another change in the same window is on the second path of the same service.

## How an agent reaches an operator's systems

1. **An imported API.** The operator gives the platform the OpenAPI file of an API it already runs, and each operation becomes a tool. Where a system follows a TM Forum Open API, or the network follows CAMARA, the file is already public.
2. **An MCP server** from the Catalog, running inside the operator's own cluster.
3. **A knowledge source.** Runbooks, manuals, tariffs, product terms, policies and the complaints code, indexed with each reader's permissions kept.
4. **A file the user uploads** in the conversation.

To try an agent before your own systems are connected, the invented operator in `demo-operator/` will offer the first two routes, and its scenario list will give the right answer for every case. It is not written yet.

## Where the designs come from

The agents and desks are our own. Before the design was written, public code was read for ideas, and no code and no sample data was taken: [OPEN-SOURCE-REVIEW.md](OPEN-SOURCE-REVIEW.md) names every repository, its licence, what was read in it and what was taken from it as a design. The vocabulary of the systems comes from TM Forum's Open APIs and CAMARA's APIs, both Apache-2.0.
