# Health claims desk

The settings folder that turns the Katonic case desk into a desk for an insurer's health claims team. Three kinds of case sit in one queue. A provider's request for approval is set against the member's plan and the medical policy. A medical claim that the claims engine has held is set out with a suggested determination. A provider's invoice is set out line by line against the tariff and the contract. Each kind goes to its own agent. A person decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its members, its providers, its claims, its invoices and all their documents are invented. Nothing here is a real decision on a member's care or on a claim.

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Pre-authorisation | [Pre-authorisation Preparation](../../agents/pre-authorisation-preparation/README.md) | Sets the request against the member's own plan and the medical policy: cover on the planned date, the plan's benefit, whether pre-authorisation is needed, and each criterion of the medical policy | A prepared file, for the assessor. The agent approves nothing and refuses nothing |
| Held claim | [Medical Claims Adjudication Support](../../agents/medical-claims-adjudication-support/README.md) | Says why the claims engine held the claim, sets out the earlier claims, the cover, the plan's limit or the medical policy, and what the plan's terms give | A suggested determination, for the assessor. The agent pays nothing and declines nothing |
| Provider invoice | [Provider Invoice Check](../../agents/provider-invoice-check/README.md) | Sets the invoice out line by line against the agreed tariff and the provider's contract, with the totals as the health system works them out | The differences, for a claims officer. The agent queries nothing and contacts nobody |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Prepare the file for the pre-authorisation request named in the case below", "Review the medical claim named in the case below, which the claims engine has held", "Check the provider invoice named in the case below against the contract"). The case names the record by its id. The agent reads the request, the claim or the invoice itself from the insurer's health system.

## What the person sees

- **A queue of health cases**, each with its record id and its status. The title says who it is about, what it is and which work it is.
- **The case beside the draft.** The desk's short account of the case is on one side. The agent's draft is on the other. On a phone the account is folded, so the draft comes first.
- **One row for each finding**, with a mark and a note. A pre-authorisation has three rows for the plan and then a row for each criterion of the medical policy. A held claim has a row for the hold reason, each earlier claim, the cover, each line against the plan's limit or each criterion, and what the plan's terms give. An invoice has a row for each line and then the three totals.
- **The agent's summary**, folded above the rows.
- **The working of an invoice** on a card of its own: the health system's own lines, unchanged.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

### The marks

| Mark | Used by | Meaning | Shown as |
|---|---|---|---|
| in force | Pre-authorisation, held claim | The member's cover is in force on the date that matters | Green, a tick |
| not in force | Pre-authorisation, held claim | The member's cover is not in force on that date | Red, a cross |
| covered | Pre-authorisation | The member's own plan covers the benefit, with or without conditions | Green, a tick |
| not covered | Pre-authorisation | The member's own plan does not cover the benefit | Red, a cross |
| needed | Pre-authorisation | The plan needs pre-authorisation for the procedure | Blue, a dot, a thin edge |
| not needed | Pre-authorisation | The plan needs none, or does not cover the procedure | Amber, a dash |
| met | Pre-authorisation, held claim | A document states the fact the criterion turns on | Green, a tick |
| not met | Pre-authorisation, held claim | A document states a fact that plainly fails the criterion | Red, a cross |
| not stated | Pre-authorisation, held claim | The documents say nothing about the fact. Nothing is guessed | Amber, a question mark |
| duplicate | Held claim | The same member, provider, code and date of service as an earlier claim | Red, a cross |
| not a duplicate | Held claim | An earlier claim that differs, or none | Green, a tick |
| within the limit | Held claim | The line is within the plan's limit | Green, a tick |
| over the limit | Held claim | Part of the line is over the plan's limit | Amber, a half circle |
| agrees | Provider invoice | The line is charged as the tariff and the contract agree | Green, a tick |
| over the tariff | Provider invoice | The line is charged above the agreed price | Red, a cross |
| under the tariff | Provider invoice | The line is charged below the agreed price | Amber, a dash |
| not on the tariff | Provider invoice | The service is not on the tariff, and no agreement in writing is on file | The colour for a point a person decides |
| not chargeable | Provider invoice | A follow-up consultation inside the contract's free period | Red, a cross |
| discount not applied | Provider invoice | A medicine charged without the contract's discount | Red, a cross |
| worked out | Held claim, provider invoice | A figure the system worked out | Grey, an equals sign, a thin edge |

No mark is a decision on a member's care, on a claim or on an invoice. A mark is the agent's reading, for a person. The count above the rows lists the marks that were given, and no others.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the draft as the file note. It approves no care, refuses no request, pays no claim and queries no invoice, and it changes nothing in the insurer's health system |
| Wait for what is missing | What is missing, one item to a line. The case waits. When it has come in the person adds it, and the agent reads the record again. The desk sends nothing to anyone: the health claims team asks the provider, outside this desk |
| Refer on | Who it goes to and why: the medical reviewer, who is a clinician, an authorised assessor, a claims officer or the provider relations team |
| Ask the agent to redo the draft | A note that the agent sees |

The desk has no decision that approves or refuses a pre-authorisation, pays or declines a claim, or queries an invoice. A pre-authorisation is approved or refused by a clinician or an authorised assessor, a claim is paid or not by the assessor, and an invoice is queried by a claims officer, each in the insurer's health system. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" only where the proposal is a step this desk has. "send to the assessor as met", "pay as the plan allows: ..." and "the invoice agrees with the tariff and the contract" mark Accept the draft. "ask the provider: ..." marks Wait for what is missing. "refer to the medical reviewer: ..." marks Refer on. "refer to the assessor: ...", "do not pay: ...", "query with the provider: ..." and "refer to a claims officer: ..." are readings for the person who decides, and mark no button.

### What each kind shows

| Kind | Decisions | The lines of a row are labelled |
|---|---|---|
| Pre-authorisation | Accept the draft, Wait for what is missing, Refer on, redo | Plan or policy, The file shows, Note |
| Held claim | Accept the draft, Wait for what is missing, Refer on, redo | The file shows, Record, Note |
| Provider invoice | Accept the draft, Refer on, redo | Charged, Agreed, Difference, Note |

The server refuses a decision the kind does not offer.

**The clause of an invoice line is not drawn in its row.** The invoice check's table has eight columns, with four cells between the line and the mark: Charged, Agreed, Difference and Clause. The engine reads three. The clause stays in the agent's text, which the page shows under "The draft as the agent wrote it", and in the accepted draft.

## The seventeen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| PA-8101, an MRI scan of the lower back | Pre-authorisation | Cover in force, BEN-E05 covered, pre-authorisation needed, criteria 1 to 3 of MP-301 met. Proposal: send to the assessor as met |
| PA-8103, an MRI scan, nothing about an examination | Pre-authorisation | Criteria 1 and 2 met, criterion 3 not stated. Proposal: ask the provider what the examination found |
| PA-8102, a knee arthroscopy after 2 weeks of physiotherapy | Pre-authorisation | Criteria 1 and 3 of MP-303 met, criterion 2 not met. Proposal: refer to the medical reviewer |
| PA-8104, cover ended 40 days before the planned date | Pre-authorisation | Not in force. Three rows, no criterion read. Proposal: refer to the assessor, with the system's sentence on cover |
| PA-8105, removal of a wisdom tooth | Pre-authorisation | BEN-E09 not covered, so nothing to pre-authorise. Proposal: refer to the assessor |
| PA-8106, an MRI scan on the fuller plan | Pre-authorisation | No pre-authorisation needed for BEN-F05. Proposal: refer to the assessor |
| MC-9101, a first consultation claimed twice | Held claim | A duplicate of MC-9011. Proposal: do not pay, for the assessor to decide |
| MC-9102, a physiotherapy session 7 days after another | Held claim | Not a duplicate of MC-9012. Proposal: pay as the plan allows, USD 33.60 |
| MC-9103, a consultation 18 days after cover ended | Held claim | Not in force. Proposal: do not pay, for the assessor to decide |
| MC-9104, medicines over the yearly limit | Held claim | USD 70.00 within the limit, USD 43.40 over it. Not a duplicate of MC-9013. Proposal: pay as the plan allows, USD 56.00 |
| MC-9105, an MRI scan held for medical necessity | Held claim | Criteria 1 to 3 of MP-301 met. Proposal: pay as the plan allows, USD 620.00 |
| MC-9106, three physiotherapy sessions beyond the plan's | Held claim | Criteria 1 and 3 of MP-302 met, criterion 2 not stated. Proposal: ask the provider for the physiotherapist's report |
| PI-9501, four lines | Provider invoice | Every line agrees. The follow-up is 16 days after the first consultation and is rightly charged. Proposal: the invoice agrees |
| PI-9504, a follow-up after 5 days | Provider invoice | Line 3 not chargeable under clause 4.1. Difference USD 35.00. Proposal: query with the provider |
| PI-9502, an X-ray at USD 80.00 | Provider invoice | Line 2 over the tariff. Difference USD 15.00. Proposal: query with the provider |
| PI-9503, a shockwave therapy session | Provider invoice | Line 2 not on the tariff, no agreement in writing. Difference USD 55.00. Proposal: query with the provider |
| PI-9505, two medicines at the full price | Provider invoice | Lines 2 and 3, discount not applied. Difference USD 4.20. Proposal: query with the provider |

Every proposal the three agents can make is in the queue, except three the invented insurer has no record for: a held claim referred to the medical reviewer, and an invoice referred to a claims officer (a line under the tariff, or a decision already recorded).

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings here use `routing` with decisions, row labels and mark hints for each kind, `draft.sections` for the Working card, `draft.markIcons`, `draft.quietMarks`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs the engine change of pull request 4 of the case desk repository, which was merged into `main` on 26 November 2026.** That change reads a table by its own header row. An engine older than that cannot read this desk's tables: two of them have six columns with the mark in the fifth, and one has eight with the mark in the seventh.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/health-claims/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
PRE_AUTHORISATION_AGENT_ID=<id of Pre-authorisation Preparation> \
MEDICAL_CLAIM_AGENT_ID=<id of Medical Claims Adjudication Support> \
INVOICE_AGENT_ID=<id of Provider Invoice Check> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `PRE_AUTHORISATION_AGENT_ID` | The agent for cases of the kind Pre-authorisation. If it is empty, drafting such a case fails and says which variable to set |
| `MEDICAL_CLAIM_AGENT_ID` | The same, for Held claim |
| `INVOICE_AGENT_ID` | The same, for Provider invoice |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the seventeen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's health system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Pre-authorisation`, `Held claim` or `Provider invoice`.

Build the three agents from [`pre-authorisation-preparation`](../../agents/pre-authorisation-preparation/README.md), [`medical-claims-adjudication-support`](../../agents/medical-claims-adjudication-support/README.md) and [`provider-invoice-check`](../../agents/provider-invoice-check/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each follows the right answers in the invented insurer's scenario list, and every id, date, amount, sentence, clause and working line in it is what the invented insurer returns when it is started with the date 26 November 2026. Each reply says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/health-claims/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the four agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How a case reaches the desk

A member of the health claims team enters it, or the insurer's health system sends it to `POST /api/intake` with the intake token: when a provider's request arrives, when the claims engine holds a claim, or when a provider's invoice is received. The health system's own events carry a record id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 26 November 2026 the desk was run against the stand-in through fourteen scenarios in a headless browser: the shape of the canned replies and of the three instructions, set against the agents' own instructions and the invented insurer's own sentences; the seventeen demo cases with their rows, marks, cards and proposals; which agent and which instruction each kind used, and that the message names the record; a question to the agent; a redo with a note and an edit of the text; every decision (accept, wait for what is missing and then what came in, refer on, redo) on a case it fits; a decision the kind does not allow, refused by the server; the register and its export; filters and search; a case entered by hand and one of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360; and a reload.

All 14 scenarios passed (784 checks), with no console error, page error or failed request. A second short script checked the queue and the new-case form at 390 and 360 (8 checks). The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. The three agents are not yet built on a cluster.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three instructions |
| `cases.json` | The seventeen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
