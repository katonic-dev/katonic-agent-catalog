# Complaints desk

The settings folder that turns the Katonic case desk into a desk for a bank's complaints officer. A customer's complaint arrives. The Complaint Handling agent classifies it, gathers the customer's history and the records it points at, and drafts the response to the customer and the entry for the complaints log, with the dates the bank's procedure sets. The complaints officer approves the response.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, their records and the five complaints are invented. Nothing here is a real complaint.

## What the officer sees

- **A queue of complaints**, each titled with the customer and the complaint id, for example `Anselm Drozdowich (CMP-1001)`. Each shows what it is about and a due chip: the day the final response is due. The chip counts 15 working days (Monday to Friday, the day of receipt not counted, no holidays), as the procedure does (`due.workingDays`).
- **The complaint beside the review.** The customer's own words, the dates the procedure sets and the linked records are on one side, with every date written as 18 Nov 2026. The agent's review is on the other. On a phone the complaint text is folded under a heading (`case.foldOnPhone`) so the review is what the officer sees first.
- **One row for each fact or procedural point**, marked supports the complaint, does not support it, procedure point or needs a person. Each row shows the customer's claim or the procedure's rule and what the records show in two boxes side by side (`draft.sideBySide`), which stand one above the other on a phone (`draft.stackOnPhone`), then a note and the source (the record id or the procedure clause).
- **The agent's proposal first** (`draft.proposalFirst`): its first sentence in large type, which is the outcome in a few words ("Approve the response: upheld."). Where priority applies, the second sentence, in normal type, starts "Priority handling:" and says why: a customer who may be vulnerable, or a time limit that is near. The count of marks sits below it.
- **A chip for priority** (`case.flags`) in the case head and on the case's line in the queue, read from that second sentence of the agent's proposal: "Vulnerable customer" where the sentence names a vulnerable customer or a bereavement, "Urgent" where it names an urgent or a time limit, otherwise "Priority". The sentence stays in the proposal. A closed complaint shows no chip. The chip appears when the draft is in.
- **The draft response to the customer and the log entry**, below the table. The desk declares both as sections (`draft.sections`), so the page shows each on a card of its own under the table: "Draft response to the customer" and "Entry for the complaints log". The cards are set for reading. "Edit the text" gives each section its own box, and what is approved is the edited text. The text is also in the document that is issued when the officer approves.
- **The register** afterwards: who decided what, when, on which version of the response, and with which agent run and tool calls.

### The marks

No mark here is a pass or a failure. A mark says whether the records back the customer, so none is red with a cross or green with a tick. Each has a sign (`draft.markIcons`) and a tone (`draft.markTones`).

| Mark | Sign and colour | Meaning |
|---|---|---|
| supports the complaint | = in amber | The records back what the customer says. It is not yet the outcome |
| does not support it | ≠ in grey | The records differ from what the customer says, or explain it |
| procedure point | § in grey | A rule, a date or a time limit of the complaints procedure |
| needs a person | ◆ in the brand colour | The records do not show it, or only a person can do or decide it. It is not a failure |

The count above the rows reads "2 for the complaint, 1 against it, 4 procedure, 2 left to a person" (`draft.tallyLabels`).

## What the officer decides

| Decision | What it records |
|---|---|
| Approve the response | The officer approves version N of the response and the log entry. The desk sends nothing and credits nothing: the response is sent, and any redress credited, from the bank's complaints system |
| Refer on | Who it goes to and why |
| Ask the agent to redo the review | A note that the agent sees |

The person who entered a complaint cannot decide it. The agent's proposal line starts "approve the response", and the desk marks that decision.

## The five demo cases

| Case | What the complaint is | What the agent should find |
|---|---|---|
| CMP-1001, Anselm Drozdowich | A monthly fee of USD 12.00 taken twice on ACC-1009-01 | Fees and charges, upheld. Refund one fee, USD 12.00, and apologise. The earlier complaint CMP-0901 was not upheld and is a different matter |
| CMP-1002, Rosalind Heathcote-Brae | Payment PAY-6001 arrived late | Payments, not upheld, no bank error. Explain with the dates in the payment and in INV-5001. No redress |
| CMP-1003, Isolde Pennywhistle | Loan LAP-8010 declined | Lending decision, not upheld, not a service failure. Debt to income 0.48 against the 0.40 limit of MTB-POL-030. How to ask for a review. Promise nothing |
| CMP-1004, Ilvane Marrowick | Card CRD-2004 blocked after a death in the family | Possibly vulnerable, a recent bereavement. Priority, one named person, a kind plain letter. Upheld: the block was applied to her own card by mistake. Replace the card |
| CMP-1005, Sabine Tarrowgate | Received 13 working days ago, never acknowledged | Admit the acknowledgement is 11 working days late and apologise. The final response is due in 2 working days: urgent |

The dates and the working-day counts in the cases are as at the bank date 24 Nov 2026 (`BANK_TODAY=2026-11-24`). Start the invented bank with that value so that the records the agent reads match the cases.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, and the `case.queryFields`, `decisions[].proposalPrefix`, `draft.rowLabels`, `due` (with `workingDays`), `draft.sideBySide`, `draft.stackOnPhone`, `case.flags`, `draft.proposalFirst`, `draft.markIcons`, `draft.tallyLabels`, `case.foldOnPhone` and `intake.fields[].options` and `shownAs` settings.

**That version is in `main` of katonic-case-desk** since 24 November 2026 ([pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2)). A copy of the engine cloned before that date will not run this folder.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/complaints/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Complaint Handling> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The id of the built Complaint Handling agent |
| `DESK_AGENT_ID` | The same, and it wins over `KATONIC_AGENT_ID`. Set it in the process environment when several desks share one key file |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the five demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `PORT` | The port the desk listens on |
| `INTAKE_TOKEN` | Turns on intake by webhook. The bank's system sends it as `X-Intake-Token` |
| `TRUST_SIGN_IN_HEADERS`, `LOCAL_USER`, `LOCAL_USER_NAME` | Who the desk believes is signed in. Without the headers it uses the local user, and every register row says which it was |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agent reads the bank's complaints system |

Build the agent from [`complaint-handling`](../../agents/complaint-handling/README.md). Its `instructions.md` and the `draft.instruction` setting in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case's id in its title. Each follows the right answers in the invented bank's scenario list, with a draft response and a log entry. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/complaints/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, and any value for `KATONIC_API_KEY` and `KATONIC_AGENT_ID`. A complaint you enter by hand gets a plain line saying the stand-in has nothing for it. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a complaint reaches the desk

A member of the complaints team enters it, or the bank's complaints system sends it to `POST /api/intake` with the intake token. The bank's own event for new complaints carries a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 Nov 2026 the desk was run end to end in a headless browser against the engine's stand-in platform, with a recording proxy between them, on the bank date 24 Nov 2026. The script has 12 scenarios and 229 checks, and every one passes. It covers:

- the desk opening with the five complaints, each with its subject and its due day in working days (9 Dec, 10 Dec, 8 Dec, 11 Dec, 26 Nov), and the subject printed once in the case head;
- for each of the five complaints: the number of rows, each mark, its sign (= ≠ § ◆) and that none is red or green, the claim and the records side by side and not in a typewriter face, the proposal's first sentence (the outcome, eight words at most) and its second ("Priority handling:" for CMP-1004 and CMP-1005), the count of marks, the letter (the customer's full name, the key facts and dates, the right to escalate, the placeholder for the name and direct line, Yours sincerely, no cause or promise the records do not give) and the log entry on its own card;
- what the desk sent to the agent: the instruction (plain statements, dates as 18 Nov 2026, no count of marks, the four marks, the placeholder);
- a question to the agent, a draft sent back with a note and redone, an edit of the letter that becomes a new version and reaches the issued document;
- the decisions: Approve the response (with and without an edit), Refer on (needs a note; the server refuses it without one and refuses a decision the desk does not have);
- the register and the CSV export, filters, and search by id, customer, customer id and subject;
- a complaint entered by hand (an empty form shows the errors, a valid one is accepted and gets the stand-in's plain default reply, the person who entered it cannot decide it, it can be corrected and removed);
- the light and dark themes, with the mark text at 3.5 to 1 or better in dark;
- a phone at 390 and 360 wide: no sideways scrolling, the queue folds, the jump bar works, every button is 40 px high or more, ids and dates are not broken across lines, the proposal is on the first screen;
- a reload that loses nothing.

The same run took screenshots of every state at 1440 and 390 wide, in light and dark, and they were read one by one. The engine was used as it is, with no change. Not yet done: a run against a real agent on a platform.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the drafting instruction |
| `cases.json` | The five demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case |
