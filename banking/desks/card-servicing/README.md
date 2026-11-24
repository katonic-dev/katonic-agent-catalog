# Card servicing screen

The settings folder that turns the Katonic case desk into a screen for a member of the bank's staff who is on a call with a customer about a card. The case is the call: who the customer is, which card, and what the customer says. The agent reads the card, its recent payments, its disputes and the customer's recent contacts from the bank's systems, and writes the rows the member of staff needs to see, then a proposal: exactly which actions, on which card, for which payments, with the total. The member of staff reads it to the customer, edits it if the customer says otherwise, and takes one decision, "Confirm and carry out". The agent then carries it out through its tools and reports what the systems returned.

This is the first desk whose decision **does something**. On the other desks a decision only records what a person chose. Here "Confirm and carry out" sends the confirmed proposal to the agent, and the screen keeps what came back as the outcome of the call. On a platform with approval rules each change then waits for a second person to approve it, and the outcome says so.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, their cards and their payments are invented. Nothing here is a real card.

## The agent

| Agent | What it does | What goes to the person |
|---|---|---|
| [Card Servicing](../../agents/card-servicing/README.md) | Reads the card, its payments, its disputes and the customer's contacts, and proposes a block, a replacement, a dispute, or no change. After the member of staff confirms, it carries out exactly what was confirmed through its tools, reading the current state first and doing nothing that is already done | The rows and the proposal, to read to the customer; later, what each system returned |

The desk sends the agent one message to draft (the drafting instruction, then the call) and, after a confirmation, one message to carry it out (the act instruction, the call, the proposal as confirmed, the note). The drafting instruction and the act instruction in `desk.config.json` and the agent's `instructions.md` ask for the same things and must be changed together. The agent's file has one short section for the screen, "When the card servicing screen sends the case". The rest of that file is the chat agent as it was tested.

## What the person sees

- **A queue of calls.** The title is who is calling and the card ("Dorian Quillfeather, card ending 4821"). The line under it carries the topic and the card id. Card numbers are masked everywhere: the last four digits only.
- **The call beside the proposal.** The desk's note of the call is on one side: the customer id, the card id, the date and what the customer says. The agent's proposal is on the other.
- **The proposal first.** The agent's proposal leads the strip above the rows, in large type, with its first sentence set apart. The count of marks sits below it.
- **One table**, one row for each finding: the card; each payment that matters, with its date, time, how it was made and the town; each open dispute, or one row that says none is open; what the customer has already told the bank. Each row has a mark.
- **The decision.** Three buttons and the usual send back. The button that matches the agent's proposal is tagged "Agent's proposal". "Confirm and carry out" opens a form with an optional note and a second button before anything is sent.
- **The outcome**, once a decision is confirmed, in a card of its own above the proposal, under "What the bank's systems returned". It is set for reading: a line that starts "Outcome:", then one list item for each action. Each answer is added to the card with its time and who asked, newest first.
- **The register** afterwards: the decision, then a row for each answer of the agent, each with the first line of the answer.

### The marks

| Mark | Colour | Meaning |
|---|---|---|
| to change | amber, half circle | The proposal changes something because of this row |
| nothing to do | grey, dash | The row needs nothing |
| already in hand | blue, not equal sign | A dispute or a replacement already exists for it, so nothing new may be opened |
| ask the customer | grey, question mark | Only the customer can settle the point. Ask them |

No mark is red and none is green: none of them means that the desk failed or that a check passed.

## What the person decides

| Decision | What it records | Is anything sent to the agent? |
|---|---|---|
| Confirm and carry out | The member of staff confirms version N of the proposal, as edited if they edited it, with an optional note | Yes, once. The agent carries out exactly what was confirmed |
| No change | Nothing is changed. A note says what the customer was told | No |
| Refer to the disputes team | A note says what the disputes team should look at. The agent never decides whether the customer gets money back | No |
| Ask the agent to redo the proposal | A note that the agent sees, then a new version | No (a new draft is asked for) |

There is no four-eyes rule on this desk: the member of staff on the call enters and confirms the call. The second pair of eyes is the platform's approval rule on each changing tool, which the desk does not replace.

### After "Confirm and carry out"

1. The decision is recorded: who, when, the note and the version. The case shows "Carrying out" and the page refreshes on its own.
2. The agent answers. If the answer holds "waiting for approval", "awaiting approval" or "held for approval", the case shows "Waiting for approval" and stays open. One button, "Ask for the outcome again", asks the agent to read the state again. When an answer no longer holds those words the case shows "Carried out" and closes.
3. If the agent cannot be reached or answers with an error, nothing is lost. The decision stands, the case shows "Not carried out", the card says plainly what the agent said, and "Try again" sends the same message again. The message tells the agent to read the current state first and to do nothing that is already done, so a second try cannot do a thing twice.
4. One click sends one message. A double click, a reload and a click at the same time as another send nothing more.

The desk reads only the waiting words. If an answer says that the bank's system refused a change, the case still closes as carried out, and the member of staff reads the card.

## The four demo cases

Each follows the right answers in the invented bank's scenario list (Cards, and the subscription scenario for the fourth). Every date, id and figure in them was worked out by a script from the bank's data at the bank date.

| Call | What the agent should find | Proposal | Marks |
|---|---|---|---|
| CUS-1002, card CRD-2001 ending 4821. Lost card, two payments the customer does not recognise | The card is active. The customer lost it at about 17:00 on 22 Nov 2026 (CNT-5001) and wrote on 23 Nov 2026 that two payments are not his (CNT-5002). CTX-2001-U01 (Ironwood Electronics Online, USD 389.00, online, 22 Nov 2026) and CTX-2001-U02 (Quickfuel Station 44, USD 85.40, contactless, 23 Nov 2026) came after the loss: USD 474.40. CTX-2001-A01 and CTX-2001-A02 came before it and are not disputed | Block CRD-2001 (lost), request a replacement (lost, by post), dispute the two payments (not recognised), USD 474.40 in total | 3 to change, 5 nothing to do |
| CUS-1003, card CRD-2002 ending 7316. Card about to expire | It expires in Dec 2026 and she travels next month (CNT-5003). No replacement exists | Request a replacement (expiring, by post). Do not block the card | 1 to change, 1 ask the customer (post or branch), 3 nothing to do |
| CUS-1004, card CRD-2003 ending 2059. Double charge with a dispute already open | DSP-6001 is open for CTX-2003-D02 (USD 42.00, Harbourlight Cinema, one minute after CTX-2003-D01), waiting for the merchant. A second dispute is refused | No change. Nothing new may be opened | 2 already in hand, 3 nothing to do |
| CUS-1006, card CRD-2006 ending 6670. A charge called fraud that repeats a subscription | The USD 11.99 charge from Streamline Video Club on 22 Nov 2026 repeats three payments of the same amount on 24 Aug 2026, 23 Sep 2026 and 23 Oct 2026. No sign of loss. No dispute | No change. If the customer still says he never signed up, refer it to the disputes team | 1 ask the customer, 4 nothing to do |

**The demo cases are fixed at the bank date 2026-11-24.** The invented bank must be started with `BANK_TODAY=2026-11-24`, or the records the agent reads will not agree with the cases (the dates are relative to the bank date: the lost card, the expiry month, the open dispute). Every date is written as a date, never as a count of days ago.

The canned replies of the stand-in follow the same answers. For the two calls where something is carried out, the stand-in's first answer says that the requests are waiting for approval, as on a platform with approval rules. "Ask for the outcome again" then gives the references: for the lost card DSP-6002 (the dispute) and RPL-7001 (the replacement), the card now blocked; for the expiring card RPL-7002. These are the ids a fresh bank gives when the two calls are carried out in the order of the list.

**To see the failed screen:** add a call whose title holds the words **Failure drill** (for example "Failure drill, card ending 7316"). The stand-in answers its first request to carry out with an error and the second with success, so "Try again" can be seen.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and that reads `decisions[].act` (a decision the agent carries out) with its routes `POST /api/cases/:id/outcome/again` and `/outcome/retry`. It also reads the settings the other desks use: `decisions[].proposalPrefix` (a list), `draft.proposalFirst`, `draft.plainSource`, `draft.rowLabels`, the `info` and `plain` tones of a mark, `intake.fields[].options`, `case.jumpLabel`, and `rules.fourEyes: false`. In the stand-in's `demo-replies.json` it uses `actions`, `followUps` and `failActionOnce`.

**That version is on the branch `feat/desks-outside-the-repository` of katonic-case-desk**, in [pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2). It is not in `main` yet, and the engine on `main` will not run this folder. Until it is merged, clone that branch.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/card-servicing/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Card Servicing> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The Card Servicing agent. It drafts the proposal and carries out what is confirmed. `DESK_AGENT_ID` does the same and wins over it |
| `SEED_DEMO` | `true` loads the four demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agent reads the bank's systems |
| `TRUST_SIGN_IN_HEADERS`, `INTAKE_TOKEN`, `PORT`, `PUBLIC_URL` | As in the engine's own README |

The agent needs the two bank systems attached (the customer records and the card system) and, to hold each change for a second person, an approval rule on `block_card`, `request_card_replacement` and `open_card_dispute`. See the agent's README. Build it from [`card-servicing`](../../agents/card-servicing/README.md). The invented bank must be started with `BANK_TODAY=2026-11-24`.

**The approval rules are the control.** The desk sends what the member of staff confirmed. Whether a change waits for a second person is set on the platform, not here. Without approval rules the changes are made at once, and the outcome says so.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/card-servicing/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY` and for `KATONIC_AGENT_ID`. The file has a reply for each of the four demo cases, an act reply (`actions`) and a follow-up reply (`followUps`) for the two calls where something is carried out, `failActionOnce` for the failure drill, and a plain default for a call you enter by hand. Each reply says that it comes from the stand-in. The stand-in shows the screens and the flow. It is not an agent, it reads nothing from the bank, and it changes nothing.

## How a call reaches the desk

A member of staff enters it, or the contact centre's system sends it to `POST /api/intake` with the intake token. The system's own event for a new call carries a customer and a card, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through sixteen scenarios in a headless browser, with a recording proxy between the desk and the stand-in so that what the desk sent could be read. They covered: the four demo cases with their rows, the mark on each row, the date, place and ids in each row and the proposal line, against the right answers in the invented bank's scenario list; that no card number appears anywhere, only the last four digits; the buttons and the agent's proposal tagged on the right one; a question to the agent; a send back with a note and a new version; an edit of the proposal and the new version it records; "Confirm and carry out" with a double click (one message to the agent, read from the proxy), the act message (instruction, call, proposal as edited, note, the rule to read the state first), the waiting answer, "Ask for the outcome again", the second answer with the references, and the call closing as carried out; the issued document with the outcome; "No change" and "Refer to the disputes team", which send nothing to the agent; a closed call refusing a decision, an ask for the outcome and a new draft; the failure drill (the first request fails, the decision stands, "Try again" sends the same message once and succeeds); the register and its export with an outcome row for each answer; filters and search; a call entered by hand, with the error of an empty form; the three themes; a phone-width window at 390 and 360 with every control at least 40 px high and nothing wider than the screen; a reload; and the agent's files. All sixteen passed (341 checks) after rounds of fixes. It was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against a real agent on a platform, with approval rules, and the decision by the second approver. The agent's new section and its two tests (6 and 7) have not been run on a model.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, the drafting instruction, and the `act` of "Confirm and carry out": its instruction, the waiting words, the follow-up and the three statuses |
| `cases.json` | The four demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case, its act and follow-up replies, the failure drill and a plain default |
