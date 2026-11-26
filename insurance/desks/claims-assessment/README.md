# Claims assessment desk

The settings folder that turns the Katonic case desk into a desk for an insurer's claims assessment team. Three kinds of case sit in one queue. A claim is read against the policy wording, clause by clause. A claim whose invoices are in has its settlement worked out, line by line. A letter that a claims handler asks for is drafted from the claim file and the insurer's own template. Each kind goes to its own agent. A person decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its claimants, its claims, its policies and all their documents are invented. Nothing here is a real decision on a claim.

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Coverage check | [Coverage Check](../../agents/coverage-check/README.md) | Sets the loss against the policy wording: the clause that covers, the exclusions, the limits, the deductible, the conditions and the endorsements, and says where the wording is silent | A reading, for the adjuster. The agent accepts no cover and declines no claim |
| Settlement | [Settlement Calculation](../../agents/settlement-calculation/README.md) | Says which invoice lines the wording does not cover, and shows the amount payable as the claims system works it out | The figure and its working, for the adjuster and for the person who approves the amount. The agent pays nothing and approves nothing |
| Letter | [Claims Correspondence](../../agents/claims-correspondence/README.md) | Drafts the letter to the claimant from the claim file and the template, and checks it against what the template says the letter must include | The letter and the check, for a claims handler, who reads and sends every letter |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Check the claim named in the case below against the policy wording", "Work out the settlement for the claim named in the case below", "Draft the letter named in the case below, for the claim it names"). The case names the claim by its id and, for a letter, which letter is wanted. The agent reads the claim, the policy, the wording and the templates themselves from the insurer's systems.

## What the person sees

- **A queue of assessment cases**, each with its claim id and its status. The title says who the claimant is, what happened and which work it is.
- **The case beside the draft.** The desk's short account of the case is on one side. The agent's draft is on the other. On a phone the account is folded, so the draft comes first.
- **One row for each finding**, with a mark and a note. A coverage check has a row for each clause, a settlement a row for each invoice line and then the three rows the claims system worked out, a letter a row for each item the template says the letter must include.
- **The agent's summary**, folded above the rows. It holds the recovery line of a coverage check and the decision on cover of a settlement.
- **The working of a settlement** on a card of its own: the claims system's own lines, unchanged.
- **The letter** on a card of its own, from the greeting to the sign-off, with a box of its own when the text is edited.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

### The marks

| Kind | Mark | Meaning | Shown as |
|---|---|---|---|
| Coverage check | applies | A clause that covers the loss or a cost claimed | Green, a tick |
| Coverage check | does not apply | A covering clause or an endorsement that was read, and that the facts fall outside of | Amber, a dash |
| Coverage check | excludes | A clause or an endorsement that takes the loss, or one line of it, out of cover | Red, a cross |
| Coverage check | limits | A limit or a deductible | Blue, a dot |
| Coverage check | condition met | A condition, met as the file shows it | Green, a tick |
| Coverage check | condition not met | A condition, not met as the file shows it | Red, a cross |
| Coverage check | cannot tell | The file does not hold the fact the clause turns on | Amber, a question mark |
| Coverage check | wording silent | A fact that matters and that no clause speaks of. Nothing is inferred | The colour for a point a person decides |
| Settlement | allowed | The claims system allowed the line in full | Green, a tick |
| Settlement | limited | The claims system allowed less than was claimed, because a limit applies | Amber, a half circle |
| Settlement | not covered | A clause of section 2 of the wording takes the line out | Red, a cross |
| Settlement | worked out | The total allowed, the deductible or the amount payable | Grey, an equals sign |
| Letter | included | The letter holds the item, and the records give it | Green, a tick |
| Letter | cannot include | The records do not give the item, so the letter does not hold it | Amber, a half circle |

No mark is a decision on a claim. A mark is the agent's reading, for a person.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the draft as the file note. It accepts no cover, declines no claim, approves no payment and sends no letter, and it changes nothing in the claims system |
| Wait for what is missing | What is missing, one item to a line. The case waits. When it has come in the person adds it, and the agent reads the claim again. The desk sends nothing to anyone: a claims handler asks the claimant for a document, and the adjuster records a decision on cover in the claims system |
| Refer on | Who it goes to and why: a senior adjuster, the person who approves the amount under rule HG-5, a claims handler or the recoveries team |
| Ask the agent to redo the draft | A note that the agent sees |

The desk has no decision that accepts cover, declines a claim, approves a payment or sends a letter. The adjuster, the person with the authority for the amount or a claims handler does that, in the claims system. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" only where the proposal is a step this desk has. "within the wording, for the adjuster to confirm", "pay USD ..." and "approve the letter" mark Accept the draft. "refer to the adjuster: no decision on cover is recorded ..." marks Wait for what is missing. "refer to a handler: ..." marks Refer on. The other proposals of a coverage check are readings for the adjuster, and mark no button.

### What each kind shows

| Kind | Decisions | Rows are labelled |
|---|---|---|
| Coverage check | Accept the draft, Wait for what is missing, Refer on, redo | The clause says, The file shows, Note |
| Settlement | Accept the draft, Wait for what is missing, Refer on, redo | Claimed, Allowed, Clause, Note |
| Letter | Accept the draft, Refer on, redo | Comes from, Note |

The server refuses a decision the kind does not offer.

### A short reply

Each agent has replies that are only a sentence or two, with no table and no proposal: a settlement asked for on a claim that an adjuster declined, a decline letter asked for where no decision to decline is recorded. The desk shows such a reply as plain text in the place of the rows. No count of marks and no proposal are shown, and no button is marked. The person accepts it as the file note, refers it on or asks for a redo.

## The thirteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| CLM-4004, a vehicle driven off with the key in it | Coverage check | Clause 1.2 applies. No clause speaks of a key left in the vehicle: the wording is silent. Proposal: refer to the adjuster |
| CLM-4006, a theft with the back door unlocked | Coverage check | Clause 1.4 does not apply and clause 2.3 excludes: no forced entry. Proposal: outside the wording, for the adjuster to decide |
| CLM-4003, a vehicle taken two days after the policy ended | Coverage check | One row, the policy period. Proposal: the policy was not in force on the date of the loss, for the adjuster to decide |
| CLM-4001, a gate post and a cracked rear windscreen | Coverage check | Clauses 1.1 and 1.4 apply, clause 2.5 excludes the valet, clause 3.2 limits the windscreen. Proposal: within the wording, for the adjuster to confirm |
| CLM-4002, water through a kitchen ceiling | Coverage check | Clauses 1.3 and 2.1 cannot be told: no document says where the water came from. Proposal: refer to the adjuster, with the plumber's report that would settle it |
| CLM-4009, a failed pipe joint, cover accepted | Settlement | The underfloor heating is not covered (2.5), trace and access is limited to USD 1,500.00 (3.4). Payable USD 5,100.00. Proposal: pay, for the approval of the senior adjuster |
| CLM-4001, no decision on cover | Settlement | The valet is not covered (2.5), the windscreen is limited to USD 500.00 (3.2). The amount would be USD 1,900.00. Proposal: refer to the adjuster |
| CLM-4010, declined by an adjuster | Settlement | A short reply: the claim was declined, so no settlement was worked out |
| CLM-4004 | Letter, acknowledgement | All five items included. Proposal: approve the letter |
| CLM-4002 | Letter, missing documents | Asks for the plumber's report and for photographs that can be read. Proposal: approve the letter |
| CLM-4010 | Letter, decline | Gives the adjuster's reason and clause 2.2 in its own words. Proposal: approve the letter |
| CLM-4006 | Letter, decline | A short reply: no decision to decline is recorded, so no letter was written |
| CLM-4001 | Letter, acknowledgement | The claim record names no handling team, so the team cannot be included. Proposal: refer to a handler |

Every proposal the three agents can make is in the queue, except the settlement's "refer to the adjuster" for a line the file does not settle: the invented insurer has no claim that gives it.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings here use `routing` with decisions, marks and row labels for each kind, `draft.sections` for the two cards, `draft.markIcons`, `draft.quietMarks`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs the engine change in pull request 4 of the case desk repository, which is open and not yet merged.** That change reads a table by its own header row. The coverage check's table has six columns with the mark in the fifth, and the letter check's has five with the mark in the fourth. The engine in `main` reads only a table of seven columns with the mark in the sixth, which fits the settlement's table and no other: on it a coverage check's rows carry no mark and a letter check's table is shown as text.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/claims-assessment/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
COVERAGE_AGENT_ID=<id of Coverage Check> \
SETTLEMENT_AGENT_ID=<id of Settlement Calculation> \
LETTER_AGENT_ID=<id of Claims Correspondence> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `COVERAGE_AGENT_ID` | The agent for cases of the kind Coverage check. If it is empty, drafting such a case fails and says which variable to set |
| `SETTLEMENT_AGENT_ID` | The same, for Settlement |
| `LETTER_AGENT_ID` | The same, for Letter |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the thirteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's claims and policy systems |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Coverage check`, `Settlement` or `Letter`. A letter case also carries "Letter wanted": `Acknowledgement of a claim`, `Request for missing documents` or `Decline of a claim`.

Build the three agents from [`coverage-check`](../../agents/coverage-check/README.md), [`settlement-calculation`](../../agents/settlement-calculation/README.md) and [`claims-correspondence`](../../agents/claims-correspondence/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each follows the right answers in the invented insurer's scenario list, and every id, date, amount, clause and working line in it is what the invented insurer returns when it is started with the date 26 November 2026. Each full reply says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/claims-assessment/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the four agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How a case reaches the desk

A member of the claims team enters it, or the insurer's claims system sends it to `POST /api/intake` with the intake token: when a claim reaches assessment, when its invoices are in, or when a handler asks for a letter. The claims system's own events carry a claim id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 26 November 2026 the desk was run against the stand-in through fourteen scenarios in a headless browser: the shape of the canned replies and of the three instructions, set against the agents' own instructions; the thirteen demo cases with their rows, marks, cards and proposals; which agent and which instruction each kind used, and that the message names the claim; a question to the agent; a redo with a note and an edit of a letter; every decision (accept, wait for what is missing and then what came in, refer on, redo) on a case it fits, and on the two short replies; a decision the kind does not allow, refused by the server; the register and its export; filters and search; a case entered by hand and one of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360; and a reload.

On the engine with the change of pull request 4, all 14 scenarios passed (536 checks). On the engine in `main`, before that change, 12 of the 14 passed (458 of 536 checks), and the 78 checks that failed all came from the table reader. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. The coverage check agent is not yet built on a cluster.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three instructions |
| `cases.json` | The thirteen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
