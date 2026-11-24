# Reconciliation desk

The settings folder that turns the Katonic case desk into a desk for a bank's reconciliation analysts. After each reconciliation run, every unmatched item becomes a break in the queue. The Reconciliation Break agent gathers both sides of the break, examines each candidate entry, and proposes the match or the adjusting entry with the evidence and the matching rule it relied on. Where nothing can be resolved, it says so, lists what it checked, and refers the break to a person. The analyst decides. Nothing is posted without approval.

Meridian Trust Bank (an invented bank in the invented country Meridia), its correspondent banks, its accounts and all their entries are invented. Nothing here is a real ledger.

## What the analyst sees

- **A queue of breaks.** Each is titled with the correspondent bank and what the item is, with the currency ("Quenmark National Bank, statement debit USD 3,275.40"), and the line under it starts with the break id, then the account and how long the break has been open. A break with no candidate that is older than five days says "over the 5-day limit": under RECON-RULE-005 it is escalated the same day.
- **The break beside the proposal.** The desk's short summary is on one side: the break, the account, the unmatched entry with its amount, value date, reference and narrative, and the candidates the system lists. On a phone it is folded under a heading so the proposal is on the first screen.
- **The agent's proposal first.** The strip above the rows leads with the action and the kind of break in large type ("Approve the match: mistyped reference."), then the entries and the rule, then the count of marks. The count is worked out by the desk from the table.
- **One row for each candidate or search.** In each row the break item and the entry it was compared with (or the entries a search did find) stand in two boxes of equal width, in the same form: entry id, amount with its currency, value date, reference. The note beside them gives the difference with its working ("10,000.00 less 9,985.00 is 15.00"). A search that found nothing has one box that says so ("No entry found"), under a title that says what the search was given ("Ledger search for the amount USD 3,275.40, any account, any date"). Amounts, dates and ids are not broken across lines.
- **The register** afterwards: who decided what, when, on which version of the proposal, and with which agent run and tool calls.

### The marks

Each mark has its own sign and a tone that says what it means. None is a pass or a fail, so none is red and none has a tick or a cross.

| Mark | Sign and tone | Meaning |
|---|---|---|
| Unmatched | `•`, brand colour | The item the break is about |
| Matches | `=`, green | The entry belongs with the break item under a matching rule. The note says which |
| Differs | `≠`, grey | The entry was examined and does not belong with the break item. The note says why |
| No counterpart | `∅`, grey | A search was made and found nothing on the other side. That is a finding, and the row says which search it was |

## What the analyst decides

| Decision | What it records |
|---|---|
| Approve the proposal | The analyst approves the match, the adjusting entry or the reversal. It posts nothing and changes no entry. A person with the authority posts it in the reconciliation system |
| Refer to the team lead | Why it goes to the team lead and what was checked. This is the decision to choose when the agent could not resolve the break |
| Ask the agent to redo the proposal | A note that the agent sees |

The desk has no decision that posts a match, writes off an item or reverses an entry. The person who entered a break cannot decide it. The decision that matches the agent's proposal carries a tag, "Agent's proposal".

## The five demo cases

The cases are fixed at the bank date **24 Nov 2026**. **The bank must be started with `BANK_TODAY=2026-11-24`** for its records and these cases to agree. The dates in `cases.json` and in the stand-in's replies were worked out by a script from the bank's own records at that date, so every date is written as a date.

| Break | What the agent should find |
|---|---|
| BRK-4001, statement credit STM-8101, 12,480.00, value date 19 Nov 2026, opened 19 Nov 2026 | Match with ledger entry LED-7101 (value date 18 Nov 2026, one day earlier): same amount, reference differs by one character (RECON-RULE-001). LED-7102 (12,408.00, another invoice, 72.00 lower) is not the match |
| BRK-4002, statement credit STM-8201, 8,000.00, value date 20 Nov 2026 | Match one to two: LED-7201 (5,250.00) and LED-7202 (2,750.00), both posted in BATCH-0457, which add up to 8,000.00 (RECON-RULE-002). LED-7203 (older batch, 11 Nov 2026) is not part of it |
| BRK-4003, statement credit STM-8301, 9,985.00, value date 21 Nov 2026 | Match with LED-7301 (10,000.00, same reference) and post an adjusting entry of 15.00: debit GL-6120, credit NOS-TESL-01 (RECON-RULE-003). 10,000.00 less 9,985.00 is 15.00, the difference is -15.00 |
| BRK-4004, ledger debit LED-7402, 4,175.50, value date 17 Nov 2026 | Duplicate of LED-7401, posted two minutes earlier and already matched to STM-8401. Reverse LED-7402, never LED-7401 (RECON-RULE-004) |
| BRK-4005, statement debit STM-8501, 3,275.40, value date 15 Nov 2026, opened 15 Nov 2026 (9 days old) | It cannot be resolved. No candidate exists. Say so, show the four searches that prove it (ledger by amount, ledger window 10 Nov 2026 to 20 Nov 2026, ledger by reference UNK-77QX, statement by amount) and refer it to a person. Do not match, write off or adjust (RECON-RULE-005). Older than five days, so the same day |

Only BRK-4005 carries "over the 5-day limit". The limit in the bank's data is part of RECON-RULE-005, which is about a break with no candidate. BRK-4004 is 7 days old and has a candidate, so the rule does not apply to it.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, and the `case.queryFields`, `decisions[].proposalPrefix` and `draft.rowLabels` settings, and the display settings this desk uses: `draft.markIcons` and `draft.markTones`, `draft.sideBySide`, `draft.proposalFirst`, `case.foldOnPhone`, `case.jumpLabel`, `draft.tallyLabels`, `intake.fields[].options` and `intake.fields[].shownAs`.

**That version of the engine is not published yet.** The engine on GitHub today can only be the regulatory change desk and will not run this folder. This page will name the version once it is out.

## Run it

If the agent reads the invented bank, start the bank with `BANK_TODAY=2026-11-24`: the demo cases and the stand-in's replies are fixed at that date. Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/reconciliation/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Reconciliation Break> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The id of the built Reconciliation Break agent. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the five demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agent reads the bank's reconciliation system |
| `TRUST_SIGN_IN_HEADERS`, `INTAKE_TOKEN`, `PORT`, `PUBLIC_URL` | As in the engine's own README |

Build the agent from [`reconciliation-break`](../../agents/reconciliation-break/README.md). Its `instructions.md` and the `draft.instruction` setting in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the break id in its title. Each follows the right answers in the invented bank's scenario list. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/reconciliation/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, and any value for `KATONIC_API_KEY` and `KATONIC_AGENT_ID`. A break you enter by hand gets a plain line saying the stand-in has nothing for it. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a break reaches the desk

A member of the reconciliation team enters it, or the bank's reconciliation run sends each unmatched item to `POST /api/intake` with the intake token. The bank's own event for a new break carries a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through 12 scenarios in a headless browser: the five demo cases with every row, the mark and sign on each row, both boxes of each row and the note's working checked against the invented bank's scenario list, the proposal and the button it marks, what the desk sent to the agent (one agent, the desk's own instruction), a question to the agent, a redo with a note and an edit of the text (each a new version), every decision (approve, refer to the team lead, redo), a referral without a note and decisions the desk does not have (both refused), the register and its export, filters and search by bank, break id, account and entry, a new break entered by hand (an invalid form, a valid one and the stand-in's plain default reply, then a removal), the three themes, a phone-width window at 390 and 360 (nothing wider than the screen, the queue folds, no amount broken across lines), and a reload. All 12 passed (283 checks) after the fixes the design review called for. It was reviewed screen by screen for visual design at desktop and phone width, in light and dark.

Not yet done: a run against a real agent on a platform. The wording a real agent gives to the four marks, the dates and the first sentence of the proposal line is asked for in `instructions.md` and has not been tried on a model.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the drafting instruction |
| `cases.json` | The five demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default |
