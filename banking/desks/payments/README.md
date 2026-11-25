# Payments desk

The settings folder that turns the Katonic case desk into a desk for a bank's payments operators. Two kinds of case sit in one queue. An investigation starts when another bank or a customer queries a payment: the payment is traced, its messages are lined up, and a reply is drafted. A repair starts when a payment is held in the repair queue because something in it is wrong: the correction is found in the bank's own records and proposed. Each kind goes to its own agent. A person decides. The desk releases no payment and sends no reply.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, its payments, the banks it pays and all their messages are invented. Nothing here is a real payment.

## The two kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Investigation | [Payment Investigation](../../agents/payment-investigation/README.md) | Traces the payment's status, lines up the messages exchanged, reads the bank rules the investigation lists, and drafts the reply to the customer or the other bank. It stops before any recall, amendment or return | The findings, and the reply as a card of its own, for the operator to approve or edit |
| Repair | [Payment Exception Repair](../../agents/payment-exception-repair/README.md) | Reads the held message and why it stopped, searches earlier payments to the same beneficiary by name and by account, and proposes the correction with the rule it relied on and the record the corrected value came from | The repair, for the operator to approve. Nothing is released until a person does it |

The desk sends the agent one message: the drafting instruction for the kind, then the case. The case names the investigation or the repair item and the payment. The agent reads the payment itself from the bank's payments system.

## What the person sees

- **A queue of payments cases.** The title is who it concerns and the amount ("Tobias Wrenfield, USD 4,200.00"). The line under it carries the kind and the ids ("Repair · REP-7001 · PAY-6101"). The kind and the ids are fields of their own, not part of the title. The case head, the register and the export use the same form.
- **The case beside the proposal.** The desk's short summary is on one side: the investigation or the held payment, the parties, the amounts, the dates ("18 Nov 2026"), and the message ids on file. The agent's proposal is on the other.
- **One table for both kinds**, one row for each finding (investigation) or each field to correct (repair), with a coloured mark. The labels differ by kind. An investigation row shows Evidence, The records show, Rule and Note. A repair row shows Evidence, The records show, Rule and source, and Note.
- **In a repair row, the correction on separate lines.** The row for a field to correct shows `Held` (what it was), `Corrected` (what it should be, in bold), then `Rule` and `Source`: the record the corrected value comes from (an earlier payment and its field, the bank directory entry, or the payment reference). Amounts, IBANs, bank identifiers and ids never break across lines.
- **In an investigation, the reply to send as a card of its own**, under the title "Draft reply", set in the reading face as a message: greeting, short paragraphs, sign-off. "Edit the text" gives it a box of its own. The reply is kept as approved in the issued document.
- **The agent's proposal**, one short line above the buttons: "approve the reply to the customer", "approve the reply to the other bank", "approve the repair: ...", or "refer to a person: ...". The button that matches it is marked "Agent's proposal".
- **The register** afterwards: who decided what, when, on which version of the proposal, and with which agent run and tool calls.

### The marks

| Mark | Colour | Meaning |
|---|---|---|
| confirmed | green, tick | The records show it, or a check agrees |
| to correct | amber, half circle | The records show something that must be put right (investigation), or a field with a proposed new value (repair) |
| missing | amber, half circle | The records do not hold a value or a fact that is needed |
| unclear | grey, question mark | The records do not settle the point. A person decides |

No mark is red: none of the four means the desk failed. Missing and to correct both ask a person to act, and the words on the mark tell them apart. Both kinds use all four. The count above the rows lists them in the order of the kind: an investigation starts with confirmed, a repair starts with to correct.

## What the person decides

Each kind offers only the buttons that fit it. The server refuses any other decision with a message.

| Decision | Kind | What it records |
|---|---|---|
| Approve the reply | Investigation | The person approves version N of the reply, as edited if they edited it. It sends nothing and changes no payment. A person with the authority sends the reply from the payments system |
| Ask the customer for more | Investigation | What to ask for, one item to a line. A letter is written, with a number that starts PY. The case waits until the reply is added, then the agent reads the case again |
| Approve the repair | Repair | The person approves version N of the repair. It releases nothing and changes no payment. A person with the authority releases the corrected payment from the payments system |
| Return the payment | Repair | The held payment cannot be repaired. The person says why and who is told. The status is "Return agreed". Nothing is returned on this desk |
| Refer to a person | Both | Who it goes to and why. Choose it when the agent could not settle the point |
| Ask the agent to redo the proposal | Both | A note that the agent sees, then a new version |

A case whose kind the desk does not know (`routing.other`) can only be referred or sent back for a new proposal. The desk has no decision that sends a reply, releases a payment, recalls one or returns one. The person who entered a case cannot decide it.

## The seven demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| INV-5001, payment PAY-6001, USD 1,850.00 | Investigation | The payment was credited on 21 Nov 2026. It was held at the correspondent bank until its next processing day, 3 days after sending. The status report (pacs.002) says ACSC. The system lists no bank rule, so no rule applies. The reply tells the customer it arrived, with the date |
| INV-5002, payment PAY-6002, USD 25,000.00 | Investigation | USD 37.50 was deducted by an intermediary bank, so 24,962.50 arrived. The charges were OUR, so the deduction is wrong under MTB-PAY-RULE-105, the one rule the system lists. The bank claims it back and tells the customer |
| INV-5003, payment PAY-6003, USD 3,200.00 | Investigation | The beneficiary account is closed (return reason AC04). The money was credited back to ACC-1006-01 on 22 Nov 2026. A new payment needs corrected details (MTB-PAY-RULE-106, the one rule the system lists), and the records hold none |
| REP-7001, payment PAY-6101 | Repair | Two digits of the IBAN are swapped. Replace XB82BRVN73201150000124 with XB82BRVN73201150000142, the IBAN on the earlier payment PAY-6050 to the same beneficiary (MTB-PAY-RULE-101). A search by that IBAN finds PAY-6050 only, and a search by the name finds PAY-6050 and the held PAY-6101 |
| REP-7002, payment PAY-6102 | Repair | The BIC does not match the bank. Replace QNMKXQQ1 with TESLXTT1, from the bank directory entry for Tessaly Mutual Bank (MTB-PAY-RULE-102) |
| REP-7003, payment PAY-6103 | Repair | No beneficiary address on a payment to Aldoria. Add Smelter Row 12, Velmora, Aldoria, the address on the earlier payment PAY-6051 to the same beneficiary (MTB-PAY-RULE-103). A search by name or by IBAN finds PAY-6051 and the held PAY-6103 only |
| REP-7004, payment PAY-6104 | Repair | No purpose code for the Meridia to Rovaland corridor. Add GDDS (goods), because the reference is "Invoice RD-88412 dental chair spare parts" (MTB-PAY-RULE-104) |

**The demo cases are fixed at the bank date 2026-11-24.** Every date in them ("18 Nov 2026" in the case text and the rows, "18 November 2026" inside a reply to a customer) was worked out by a script from the bank's data at that date. Start the invented bank with `BANK_TODAY=2026-11-24` so that the records the agent reads agree with the cases. Every date is written as a date, never as a count of days ago. A count of days may follow a date where it matters to a rule ("received 18 Nov 2026, 6 days after it was sent"). Both agents and both drafting instructions say so.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, and these settings: `routing` with `decisions`, `marks` and `rowLabels` for each kind, `draft.sections` (the reply card), `draft.rowLabels` (including `check`), `draft.plainSource`, `decisions[].proposalPrefix`, `routing.other` (the decisions of a kind the desk does not name), `letters.<outcome>.dates` (dates written as 24 Nov 2026), `case.jumpLabel`, `case.queryFields`, `intake.fields[].options`, and rows whose cells hold lines separated by `<br>`.

**That version is in `main` of katonic-case-desk** since 24 November 2026 ([pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2)). A copy of the engine cloned before that date will not run this folder. An earlier engine ignores `routing`, and every case would go to one agent with one instruction.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/payments/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
INVESTIGATION_AGENT_ID=<id of Payment Investigation> \
REPAIR_AGENT_ID=<id of Payment Exception Repair> \
KATONIC_AGENT_ID=<any one of the two, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `INVESTIGATION_AGENT_ID` | The agent for cases of the kind Investigation. If it is empty, drafting such a case fails and says which variable to set |
| `REPAIR_AGENT_ID` | The same, for Repair |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither. The desk asks it only to say that the kind is not recognised. It can be either of the two agents. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the seven demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the bank's payments system |
| `TRUST_SIGN_IN_HEADERS`, `INTAKE_TOKEN`, `PORT`, `PUBLIC_URL` | As in the engine's own README |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Investigation` or `Repair`. The form offers the two as a list.

Build the two agents from [`payment-investigation`](../../agents/payment-investigation/README.md) and [`payment-exception-repair`](../../agents/payment-exception-repair/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together. Both say that the summary carries no count of marks (the desk counts them from the table) and is written in plain statements, not in the first person. Only the draft reply speaks for the bank.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by a distinctive part of the case's title (the customer's name, and the amount where one customer has two cases). Each follows the right answers in the invented bank's scenario list, at the bank date 2026-11-24. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/payments/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the three agent ids. The stand-in does not read them. A case you enter by hand gets a plain line saying the stand-in has nothing for it. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the payments team enters it, or the bank's payments system sends it to `POST /api/intake` with the intake token. The bank's own events, one for a new payment investigation and one for a held payment, carry a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through thirteen scenarios in a headless browser: the seven demo cases with their rows, the mark on each row, the held, corrected, rule and source lines of each repair, the reply card of each investigation and the proposal line, against the right answers in the invented bank's scenario list; which agent and which instruction each kind used; the buttons each kind offers, and the server refusing a decision the kind does not allow; a question to the agent; a send back with a note and a new version; an edit of the reply and the new version it records; every decision (approve the reply with an edit, ask the customer for more with its letter and the reply coming back, approve the repair, return the payment, refer, redo); the register and its export; filters and search by kind, id, payment and customer; a case entered by hand for each kind with the error of an empty form, and one with a kind the desk does not know; the three themes; the letter's dates in a form a customer reads; a phone-width window at 390 and 360, with every control at least 40 px high and no amount, IBAN or id breaking across lines; and a reload. All thirteen passed (443 checks) after rounds of fixes. It was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two drafting instructions, the buttons, the marks and the row labels of each kind |
| `cases.json` | The seven demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default |
