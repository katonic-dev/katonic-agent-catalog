# Sanctions desk

The settings folder that turns the Katonic case desk into a desk for a bank's compliance officer who works screening alerts. An alert arrives. The Sanctions Alert Review agent compares the customer's record with the watchlist entry field by field and recommends clear or escalate, with the reason beside each field. The compliance officer decides.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, its watchlist and its alerts are invented. Nothing here is a real screening decision.

## What the person sees

- **A queue of screening alerts.** Each is titled with the customer's name and the alert id, for example "Anselm Drozdowich (SCR-2005)", so the lines differ at a glance. The line under it reads "against WL-9005 Anselm Drozdovic", and the match score is a chip in the case head. The same title is used in the register and the export, and for an alert entered by hand.
- **The alert beside the review.** The desk's short summary is on one side: who, against which list entry, the match score, what the matcher flagged, and the earlier alerts on the pair. The agent's review is on the other.
- **One row for each field compared**: name, aliases, date of birth, place of birth, nationality, identity number, address, related persons where the entry lists any, and the earlier alerts on the same pair. Each row shows the customer's value and the list entry's value side by side in two boxes of equal width, then the reason, then the ids the values came from, and a mark. The earlier-alerts row has one box, because it is the same text for both. Dates read like 21 Jul 1990 everywhere.
- **The agent's recommendation first.** The top of the review says in large type what the agent proposes, clear or escalate, with its reason. The count of marks is written by the desk from the table, below it. The button for the proposed decision carries a small tag. Once the officer has decided, the proposal is shown in the past tense and the decision leads.
- **The register** afterwards: who decided what, when, on which version of the review, and with which agent run and tool calls.

### The marks

None of the marks is a pass or a fail. A match on a watchlist is the alarming result, so it is the only mark in the alert colour (red). Each mark has its own sign and no tick or cross is used.

| Mark | Sign and colour | Meaning |
|---|---|---|
| matches | `=` red | Both records hold the field and the values are the same. This is the agent's reading, not a finding |
| partly matches | `≈` amber | Close but not the same: a spelling variant, a shared surname, a birth year against a full date, or a place or an address against an entry that gives only the country |
| differs | `≠` grey | Both records hold the field and the values are different. One difference may be a move, so the officer judges it with the others |
| not on the entry | `–` grey | The list entry holds no value for the field, or neither record does. It is a gap, not a difference |
| noted | `•` grey | Background, such as an earlier alert on the same pair. It is not a comparison |

## What the person decides

| Decision | What it records |
|---|---|
| Record as a false positive | Why the alert is a false positive. The desk closes nothing in the screening system: the officer closes the alert there, under their own name |
| Record as a true match | What makes it a true match and what happens next. The desk closes nothing and files nothing |
| Escalate | Who it goes to and why, for example the head of compliance or enhanced due diligence |
| Ask for more information | What to find out, one item to a line. It is an internal request and nothing is sent to the customer. The case waits until the reply is added, then the agent reads the alert again |
| Ask the agent to redo the review | A note that the agent sees |

Every decision needs a note. Escalate asks who it goes to and why, and the register keeps that note beside the decision "Escalated". An escalated alert stays open in the screening system until the person named decides, and the desk says so. The person who entered an alert cannot decide it. The desk has no decision that closes an alert, freezes an account or files a report. The agent saves only a draft recommendation, and the alert stays open. The agent's recommendation has two values, clear and escalate, so a record in which every field agrees is escalate, and the reason says that the officer decides whether it is a true match. The agent also saves the comparison row by row, and the system takes five words for each row: matches, partly_matches, differs, not_on_entry and noted. The agent saves the review as a draft, or says what the system refused.

The desk sends no letter. A letter about a screening alert to the customer is not the desk's to write.

## The six demo cases

| Alert | What the agent should find | Recommendation |
|---|---|---|
| SCR-2001, Wynne Castellane (CUS-1005) against WL-9001, Wynn Castellano | A false positive. Date of birth differs (21 Jul 1990 against 2 Feb 1962), nationality differs (Meridia against Brevnia), place of birth differs (Marlow Reach, Meridia against Corrowick, Brevnia) and address differs (9 Orchard Gate, Marlow Reach, Meridia against Foundry Lane 40, Corrowick, Brevnia). The earlier alert on the pair, SCR-1990, was closed as a false positive | Clear |
| SCR-2002, Oskar Brindlemoor (CUS-1006) against WL-9002, Oscar Brindlemore | A false positive. Date of birth differs (3 Nov 1978 against 17 May 1955), nationality differs (Meridia against Rovaland), place of birth differs (Tallowby, Meridia against Duskmere, Rovaland), address differs (51 Foxglove Walk, Tallowby, Meridia against Saw Lane 22, Duskmere, Rovaland), no identity number matches | Clear |
| SCR-2003, Valdis Orrenmoor (CUS-1007) against WL-9003 | Name, date of birth 30 Sep 1971, nationality Quenmark and identity number QNP-4417-2290 all agree. Place of birth (Hartsfell, Quenmark) and address (6 Cinder Quay, Port Ilvane, Meridia) agree too | Escalate, for the officer to decide a true match |
| SCR-2004, Katrin Elsdottir-Vance (CUS-1008) against WL-9004, Katrin Elsdottir | Uncertain. The entry holds a birth year only (1969) and the country of birth (Tessaly), with no nationality, no number and no address. The year agrees, the country agrees with the customer's place of birth (Ambrel, Tessaly) but identifies no one, and the name is partly the same | Escalate |
| SCR-2005, Anselm Drozdowich (CUS-1009) against WL-9005, Anselm Drozdovic | Uncertain. A spelling variant that the entry lists as an alias. Date of birth, place of birth (Duskmere, Rovaland) and nationality agree. The entry has no identity number. Its address (Fenwick Row 8, Duskmere, Rovaland) differs from her current one in Meridia, which could be a move | Escalate |
| SCR-2006, Perdita Vanhollow (CUS-1010) against WL-9006, Leopold Vanhollow | The entry is a politically exposed person, not a sanctions entry, and lists her as the spouse. An earlier alert, SCR-1991, was closed as a true match with enhanced due diligence applied. It is not a reason to refuse the customer. Her place of birth differs from his (Brindlecombe against Hartsfell, both in Quenmark), and the address is the same, as a shared home would be | Escalate for enhanced due diligence |

Every customer who is a person has a place of birth, and every list entry has a place of birth and an address, though some are left empty on purpose. Where the entry holds none, the row is marked not on the entry and no value is filled in.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, `waitingStatuses`, `closedStatuses`, `case.jumpLabel`, `case.foldOnPhone`, `decisions[].proposalPrefix`, `draft.rowLabels`, `draft.plainSource`, `draft.markTones`, `draft.markIcons`, `draft.tallyLabels`, `draft.sideBySide`, `draft.singleValueMarks`, `draft.proposalFirst` and `intake.fields[].shownAs` and `intake.fields[].hint`. An earlier engine ignores the settings for the signs on the marks, the values side by side, the proposal first, the folded alert text and the words round the score, and its marks would carry ticks and crosses.

**That version is on the branch `feat/desks-outside-the-repository` of katonic-case-desk**, in [pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2). It is not in `main` yet, and the engine on `main` will not run this folder. Until it is merged, clone that branch.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/sanctions/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Sanctions Alert Review> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The agent the desk calls: Sanctions Alert Review. `DESK_AGENT_ID` does the same and wins over it. A file cannot override it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address, key and agent id, when several desks share one |
| `SEED_DEMO` | `true` loads the six demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DATABASE_URL` | Keeps the records in PostgreSQL instead of a file |
| `INTAKE_TOKEN` | Turns on intake by webhook. The sender gives it as `X-Intake-Token` |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The officer's name when the desk does not trust sign-in headers. Every register row says which it was |
| `TRUST_SIGN_IN_HEADERS` | `true` only where nothing can reach the desk except through the platform's sign-in |
| `PORT`, `PUBLIC_URL` | The port the desk listens on, and its public address when it sits behind a prefix |
| `KATONIC_MAX_MESSAGE_CHARS` | The longest message the desk sends. The default is 15,000 characters |
| `DESK_LIBRARY_DIR`, `KATONIC_LIBRARY_NAME` | Not used. This desk has no library: the agent reads the bank's screening system |

Build the agent from [`sanctions-alert-review`](../../agents/sanctions-alert-review/README.md). Its `instructions.md` and the `draft.instruction` setting in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the alert id in the case title. Each follows the right answers in the invented bank's scenario list. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/sanctions/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, and any value for `KATONIC_API_KEY` and `KATONIC_AGENT_ID`. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the compliance team enters it, or the bank's screening system sends it to `POST /api/intake` with the intake token. The bank's own event for a new screening alert carries a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through 12 scenarios in a headless browser: the six demo cases with every row, the mark on each row and both values (the customer's and the list entry's) checked against the invented bank's scenario list, the proposal and the button it marks, what the desk sent to the agent (one agent, the desk's own instruction), a question to the agent, a redo with a note and an edit of the text (each a new version), every decision (record as a false positive, record as a true match, escalate, ask for more information with the reply coming back, redo), a decision without a note and a decision the desk does not have (both refused), the register and its export, filters and search by alert id, customer and list entry, a new alert entered by hand (an invalid form, a valid one and the stand-in's plain default reply, then a removal), the three themes, a phone-width window at 390 and 360, and a reload. All 12 passed (315 checks) after the fixes the first run and the design review called for. It was reviewed screen by screen for visual design at desktop and phone width, in light and dark.

Not yet done: a run against a real agent on a platform. The wording a real agent gives to the five marks, the dates and the recommendation line is asked for in `instructions.md` and has not been tried on a model.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the drafting instruction |
| `cases.json` | The six demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
