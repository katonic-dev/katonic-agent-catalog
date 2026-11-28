# The invented operator, and the rules every part of the pack keeps

This is the first file of the telecom pack's specification. It fixes what holds for every system, every agent and every desk. The files `01` to `09` give one area each: the systems it needs, the cases with their right answers, and its agents. File `10` gives the desks. [BUILD-PLAN.md](../BUILD-PLAN.md) says in what order the work is done.

Nothing in this folder is built yet. It is the design that the build follows. Where the build finds that a detail here does not work, the build changes the detail, says so in its commit, and keeps the rule behind it.

## Larkstone Telecom

Larkstone Telecom is invented. It is an operator in Meridia, the invented country the bank, the insurer and the retailer of this catalog are set in. It sells:

- **Mobile**, prepaid and postpaid, to people and to businesses.
- **Home broadband** over fibre.
- **Business services**: connectivity between sites, internet access, voice lines, managed sites.
- **Wholesale**: roaming and interconnect with other operators, all of them invented.

It runs its own network in three regions named after the towns Port Ilvane, Marlow Reach and Tallowby.

Everything is invented and labelled as invented: people, businesses, addresses, sites, equipment names, partner operators, the regulator (the Meridia Communications Authority), the data protection office (the Meridia Data Protection Office, the same one the insurer uses) and the body a customer may take a complaint to (the Communications Ombudsman of Meridia). Phone numbers are `+999 555 ....`, a country code no real country uses. SIM and device identifiers are of the operator's own invented form (`LKS-SIM-...`, `LKS-DEV-...`), never a real ICCID, IMSI or IMEI range. Equipment is named by role and an invented model (`core router LR-9`), never by a real vendor or product. Amounts are USD.

The service is `demo-operator/` at the top of the repository, built on the same skeleton as `demo-bank/` and `demo-insurer/`: one FastAPI service, one path for each system, and for each system an OpenAPI 3.0.3 document, a docs page that loads nothing from the internet, and an MCP address. Its settings are `OPERATOR_API_KEY`, `OPERATOR_AUTH`, `OPERATOR_TODAY`, `OPERATOR_WEBHOOKS`, `OPERATOR_PUBLIC_SCHEME`, with `DATA_DIR` and `KATONIC_DATASET_PATH` as in the insurer. The right answers are written for `OPERATOR_TODAY=2026-11-28`.

## The systems

Fourteen systems. The third column names the public standard whose words the system uses for its resources, fields and status values. See "How the standards are used" below.

| System | Path | Follows the words of | What it holds | Areas that read it |
|---|---|---|---|---|
| customer | `/customer` | TMF629 Customer Management, TMF683 Party Interaction | customers, accounts, lines with their plan and SIM, the contact history, call and chat transcripts, case notes, the measures behind a subscriber leaving | care, billing, fraud, orders, compliance |
| catalogue | `/catalogue` | TMF620 Product Catalog | plans, add-ons, roaming zones and rates, devices, the published terms as numbered clauses, the approved retention offers | care, business |
| billing | `/billing` | TMF678 Customer Bill Management, TMF635 Usage Management | bills with their lines, the usage behind each line, tariffs and rating rules, the adjustment rules, disputed charges, the comparison of rated usage with billed amounts | care, billing |
| care | `/care` | (the operator's own) | complaints, the complaints code with its dates, call-back requests | care |
| orders | `/orders` | TMF622 Product Ordering | orders with their steps and where each stopped, porting requests, the porting rules | orders |
| inventory | `/inventory` | TMF638 Service Inventory, TMF639 Resource Inventory | services, the equipment and sites each service rests on, which customers depend on what, serviceability by address, and what the network itself reports as in service | orders, network operations, assurance, business |
| assurance | `/assurance` | TMF621 Trouble Ticket, TMF642 Alarm Management, TMF656 Service Problem Management | trouble tickets, alarms, outages, service tests, the diagnosis procedure, incidents with their bridge notes, the review format, security alerts and past security incidents | network operations, assurance, business, compliance |
| performance | `/performance` | TMF628 Performance Management (words only) | traffic and performance readings by link and site, capacity records, equipment readings, the fault history, runbooks and equipment manuals as numbered sections | network operations, assurance and field |
| change | `/change` | TMF655 Change Management | change requests with their method of procedure and rollback plan, the change rules, the change calendar, planned work, the notice terms of each contract | network operations |
| fraud | `/fraud` | CAMARA SIM Swap (the look-up only) | the written fraud patterns with their measures, flagged accounts, SIM swap requests, the identity procedure, the network's record of the last SIM change, scam reports with the categories and the blocking procedure | fraud and security |
| business | `/business` | (the operator's own) | business customers' requirements, price rules, quotes, tenders with their questions, the library of approved answers, contracts with their service levels, the month's figures for each contract | business customers |
| wholesale | `/wholesale` | (the operator's own) | agreements with numbered clauses, the standard terms, the review checklist, partners' settlement statements, the operator's own records of the same traffic | wholesale and partners |
| compliance | `/compliance` | (the operator's own) | publications of the two invented regulators, the obligations register, the reporting rules and formats of each return, data subject requests, the map of systems that hold personal data, the privacy procedure, staff policies and procedures as numbered sections | regulatory and compliance |
| field | `/field` | (the operator's own) | jobs, technicians with their skills and where they start the day, travel times between zones, site manuals as numbered pages | assurance and field |

`field` is small and may be folded into `assurance` if the build finds it holds fewer than six operations. Aim for 15 to 25 operations in a system. A system that passes 30 is two systems.

## How the standards are used

TM Forum's Open APIs and CAMARA's APIs are public standards under the Apache-2.0 licence. The invented operator is **not** an implementation of them and claims no conformance. It borrows their vocabulary, so that a person who knows the standards finds familiar words, and so that an agent's instructions written here carry over to a real system with little change:

- A resource keeps the standard's name (`troubleTicket`, `alarm`, `service`, `resource`, `customerBill`, `productOrder`, `changeRequest`), and the fields an agent relies on keep the standard's names (`severity`, `status`, `perceivedSeverity`, `alarmRaisedTime`, `relatedEntity`, `relatedParty`).
- Status and severity values are the standard's own values, spelled as the standard spells them, in version 5 of each API where one exists. [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md) lists them as read from the standards' files.
- Operation ids are ours: snake_case, verb first, unique across the whole service (`get_trouble_ticket`, `list_alarms_for_resource`).
- The standards' notification operations (hub, listener) are left out. An agent has no use for them.
- Everything the standards do not have is ours and is named in plain words: the computed fields, the measures, the draft saves, the numbered rules.

Where the operator's field differs from the standard's, the operation's description says so in a sentence.

## Rules the data and the operations keep

Each of these cost a failed test round in the banking or the insurance pack. The telecom pack starts with them.

1. **The system does the sums, the counting and the matching. The agent does the reading.** Every total, difference, percentage, count, age, and number of minutes, hours or days between two times is returned by an operation as a figure, with a sentence of reason where a rule turns on it. A value exactly on a limit is treated one way everywhere, and the operation's description says which way. What is left for the agent is judgement on words: which clause bears on the facts, whether a note contradicts a field, what a document does not say, which of two accounts each record gives.
2. **No text in the data counts time or names a weekday.** No "yesterday", "last week", "Monday", "three hours ago". Every date in a document's text is written out (27 Nov 2026) and every time as 14:05, built from the operator date by the seed helpers. A test over the whole data set checks this.
3. **One read gives one whole case.** A read of a ticket, an order, a request or a claim returns everything an agent needs for it in one call. A list returns whole records. An agent may call one tool at most eight times in a turn, so no case may need nine reads of one kind.
4. **A search matches any word**, never all the words, and lists everything when the text is empty.
5. **A saved draft is not part of a record's read.** A read gives only a count (`drafts_on_file`). A separate read lists the drafts. So one agent never reads another's proposal as a fact, and a second test run does not see the first run's answer.
6. **A draft changes nothing else.** It is stored with who wrote it, a time and a version number, and earlier versions are kept. Its summary ends in "(draft)". A change is a separate operation for a named person, refused with 409 and a plain sentence when a precondition fails. Its summary ends in "(change)". A look-up that must be sent as a POST says "(reads only)" in its summary and saves nothing.
7. **A save is forgiving and exact at once.** Few required fields. Every fixed choice is a plain word an agent would choose, and a plain-word value is read as its fixed choice. Every description says what goes in the field when little was found. A refusal names what was wrong and says that nothing was saved.
8. **Ids are unmistakable** and never collide across systems. Each area file fixes its prefixes.
9. **Rules are numbered records.** The complaints code, the change rules, the porting rules, the adjustment rules, the fraud patterns, the identity procedure, the runbooks, the published terms: each is a list of numbered clauses or sections that an operation returns, so that an agent can be tried before any document store is connected. The same texts are also kept as documents in `telecom/library/`, written from the data by a script, for the tests that try an agent with documents in a knowledge source.
10. **Silence is designed in.** Every set of rules is silent on a few ordinary things on purpose, so that "the rules do not say, a person decides" has real cases.
11. **Every case set has one where a rule must not fire.** A look-alike that is not a duplicate. A second alarm on other equipment that is not related. A SIM change that is old enough. An order that is slow and not stopped.
12. **Two records that disagree are kept disagreeing.** A ticket that says one site and an alarm that says another. A form that says one date and a system that holds another. The agent shows both and chooses neither.
13. **No operation decides for a person.** Nothing closes a ticket, approves a change, approves a port or a SIM swap, credits a bill, blocks a number, sends a notice or a letter, dispatches a technician or submits a return for an agent. Where the pack needs such an operation to show that it is held, it is a change for a named person and no agent's draft save can reach it.
14. **Nothing found is an answer, not an error.** A read of a record the system does not hold answers 404 with a plain sentence that writes out the id. A list or a search that finds nothing answers 200 with an empty list and a sentence that says what was looked for and that nothing is held. A reading that is absent is returned as "cannot be told", never as zero. So an agent can tell "the system has nothing" from "the system failed".
15. **What was added is kept apart from what was received.** Where the operator enriches a record (the site and owner added to an alarm, the customers added to a resource), the added fields are named as added. An agent can always tell what a source said from what the operator worked out.
16. **No agent changes the network.** No operation of the invented operator configures, restarts, reroutes or tests equipment in a way that interrupts a service. The one test that interrupts a service (`run_intrusive_line_test` in `assurance`) is a change that waits for a person, and exists so that one agent can show the hold. The service holds it too: a call only creates a request that waits, and the test runs after a named person approves it.

## Every answer of the service

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`. Admin routes are as in the insurer: `POST /admin/reset/<system>`, `GET /admin/state`, subscriptions, `GET /admin/events`, and one simulate route for each event kind an area file names.

## Rules every agent keeps

One rule above all: **the agent prepares the work, and an engineer or a named member of staff decides.** Then, for every agent:

- It says what it does not do, and what it does when something it needs is not connected.
- It names no tool by its function name, no product, no vendor and no platform feature.
- It holds only the operations it needs.
- It writes plain statements, not the first person. Only a letter or a notice speaks for the operator and may say "we".
- Money with two decimals and a comma between thousands, the currency first (USD 1,240.00). Dates as 27 Nov 2026, times as 14:05, never as 2026-11-27 and never as a count of days or hours ago, unless the system gave the count.
- Every id in a reply is one the system returned. No field name with an underscore is shown to a person.
- It adds up nothing, counts no time and uses no clock of its own.
- It says a draft was saved only if the system's reply says it was applied, with the version the system gave.
- Its refusals are set sentences that hold four things: what it cannot do, who decides, that nothing was changed or saved, and the offer to note the request for that person.
- Its instructions hold general rules only: never a test's own ids, names, clause numbers or figures as an example.
- Its instructions hold no secrecy wording ("do not repeat", "never reveal"). On the platform such wording makes a guardrail replace the agent's replies.

## The reply shape of an agent behind a desk

The desk reads the reply, so the shape is exact. With the exceptions first (nothing connected; a record the system does not hold; asked only for something it does not do; a follow-up question; and, where an area file names it, a case that is already with an outside body), each of which is a short reply with no heading, no table and no "Saved:" or "Proposal:" line:

1. The heading `Summary`, then at most six lines: the case, what the records show, what a person must supply or decide. No count of marks. The last line starts `Saved:`.
2. A blank line, then a heading of the form `Draft <thing>. For the <role>. Not issued.`
3. One Markdown table, one row per finding, with a column named `Mark`. A cell is one line of plain text with no line break, no HTML and no vertical bar. An empty cell holds only `-`. Each area file names the columns and the marks.
4. Only where the area file names one: a heading and the long writing (a letter, a notice, a review).
5. A blank line, then the last line, which starts `Proposal:` and is exactly one of the proposals the area file names.

A finding is one of three kinds, and the Mark says which: something **missing**, two records that **disagree**, or a point **worth a look**. Beside these stand the marks of the rule being applied (met, not met, not stated, silent). The working table comes first and the summary is written from it.

## Types, forms and how each agent is built

The index gives each agent its type and form. On the platform:

- A **conversational** agent is a chat agent. People meet it in the Work Room chat.
- A **workflow** agent is built as two things: a chat agent that holds the instructions and the tools and is tested five runs a test, and a **workflow that wraps it**, so that staff start it from Work Room, Automations with a form, and a schedule or an event can start it. The wrapper's trigger carries the input fields (the id of the case, a period, a region). Its one work step hands the message to the agent. Where the area file names a change that waits for a person, an approval step follows the work step, and the workflow's result is set to the work step's text, never to the approval record. [BUILD-PLAN.md](../BUILD-PLAN.md), step 5, says how the wrapper is tested.
- An **autonomous** agent and a **multi-agent** team are built as the platform's research or team kinds where the area file says so. Otherwise as a chat agent, and the index says so.

In the banking and insurance packs the workflow agents were built as chat agents only, and staff could not start them from Automations. The telecom pack does both from the start.
