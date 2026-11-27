# Policy servicing desk

The settings folder that turns the Katonic case desk into a desk for an insurer's servicing team. Mid-term change requests and certificate requests sit in one queue. A change request is set against the numbered servicing rules, with the premium adjustment and the gap check as the servicing system worked them out. A certificate request is set against the policy as it stands on the certificate date, and the certificate is drafted from the insurer's template. Each kind goes to its own agent. A servicing officer decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its policyholders, its policies, its change requests, its certificate requests and the certificate holders are invented. Nothing here is a real change to a policy or a real certificate.

**Tested against the stand-in agent only.** The desk has not been run against real agents on a platform. See "How it was tested".

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Policy change | [Policy Servicing](../../agents/policy-servicing/README.md) | Reads the change request and sets out what is asked, each of the six referral rules with the system's sentence, the premium adjustment with the system's working, the gap in cover and the effective date against the insurer date | A draft policy change in eleven rows, for the servicing officer. The agent changes no policy, charges and returns no premium and cancels nothing |
| Certificate | [Certificate and Endorsement Preparation](../../agents/certificate-and-endorsement-preparation/README.md) | Reads the certificate request and the template, and sets each item asked against the policy as it stands on the certificate date | A row for each item and the certificate text, for the servicing officer. The agent issues nothing |
| Endorsement | [Certificate and Endorsement Preparation](../../agents/certificate-and-endorsement-preparation/README.md) | Reads the change request and the template for its kind of change, and fills the four paragraphs | A row for each paragraph and the endorsement text, for the servicing officer. The agent issues nothing and adds nothing to a policy |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Prepare the change on the change request named in the case below", "Prepare the certificate for the certificate request named in the case below", "Prepare the endorsement for the change request named in the case below"). The case names the request by its id. The agent reads the request itself from the insurer's servicing system.

The queue holds no endorsement case. One canned reply is kept for an endorsement entered by hand, so the third kind can be tried (see "Without a platform").

## What the person sees

- **A queue of servicing cases**, each with its request id and its status. The title says who it is about, what is asked and which work it is.
- **The case beside the draft.** The desk's short account of the case is on one side, with the request in the requester's words. The agent's draft is on the other. On a phone the account is folded, so the draft comes first.
- **One row for each point**, with a mark and a note. A policy change always has eleven rows. A certificate has a row for cover, a row for each item asked and a row for the endorsements. An endorsement has a row for each of its four paragraphs and a row for the rules and the points to raise.
- **The agent's summary**, folded above the rows.
- **The certificate text or the endorsement text** on a card of its own, each paragraph on its own line, under a line that says it is not issued.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

### The marks

| Mark | Used by | Meaning | Shown as |
|---|---|---|---|
| applies | Policy change | The servicing system says the referral rule applies. The person the rule names reads the request first | The colour for a point a person decides |
| does not apply | Policy change | The servicing system says the rule does not apply, also where a value is exactly on the limit | Grey, a dash, a thin edge |
| worked out | Policy change | The servicing system worked the premium adjustment out, and the row holds its working | Grey, an equals sign, a thin edge |
| not worked out | Policy change | The servicing system worked none out, and the row holds its reason | Amber, a dash |
| to raise | Policy change, endorsement | A day without cover, or an effective date before the insurer date, under rule SR-7. On an endorsement also a referral rule that applies | Amber, an exclamation mark |
| as asked | Certificate | The policy holds what the request asks on the certificate date | Green, a tick |
| differs | Certificate | The request asks for something the policy does not hold on the certificate date | Amber, a not-equal sign |
| filled | Endorsement | The paragraph is filled from the record | Green, a tick |
| cannot fill | Endorsement | The record does not give what the paragraph needs, so it is left out | Red, a cross |
| noted | All three | A row for reading only | Grey, a dot, a thin edge |

No mark is a decision on a policy. A mark is the agent's reading of what the servicing system says, for a person. The count above the rows lists the marks that were given, and no others.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the draft as the file note. It changes no policy, charges and returns no premium, cancels nothing and issues no certificate or endorsement, and it changes nothing in the insurer's servicing system |
| Wait for what is missing | What is missing, one item to a line. The case waits. When it has come in the person adds it, and the agent reads the record again. The desk sends nothing to anyone: the servicing team asks the requester, outside this desk |
| Refer on | Who it goes to and why: underwriting or the servicing team leader, as the servicing rule names them |
| Ask the agent to redo the draft | A note that the agent sees |

The desk has no decision that changes a policy, charges or returns a premium, cancels a policy or issues a document. The servicing officer does each of those, in the insurer's servicing system. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" only where the proposal is a step this desk has. "ready for the servicing officer" marks Accept the draft, also where the line goes on with "; to raise: ...". "ask the requester: ..." marks Wait for what is missing. "refer to underwriting: ..." and "refer to the team leader: ..." mark Refer on. "refer to the servicing officer: ..." is a reading for the person at the desk, and marks no button.

### What each kind shows

| Kind | Decisions | The lines of a row are labelled |
|---|---|---|
| Policy change | Accept the draft, Wait for what is missing, Refer on, redo | The record shows, Rule, Note |
| Certificate | Accept the draft, Wait for what is missing, Refer on, redo | The record shows, In the draft |
| Endorsement | Accept the draft, Wait for what is missing, Refer on, redo | The record shows, Note |

A case whose kind is none of the three offers Refer on and the redo only. The server refuses any other decision on it.

**A cell that holds only "-" is drawn with its label.** The policy change table writes "-" in the Rule cell of rows 1 and 2 and in the Note cell of most rows, as the agent's instructions ask. The engine draws every cell that holds text, so those rows show "Rule -" or "Note -".

## The fifteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| CHG-7301, a change of address in the same rating area | Policy change | No rule applies. Premium adjustment worked out: no change. Proposal: ready for the servicing officer |
| CHG-7302, a change of address to another rating area | Policy change | SR-2 applies. No premium adjustment worked out. Proposal: refer to underwriting |
| CHG-7303, contents sum insured up by 25.00 percent | Policy change | SR-3 applies. No premium adjustment worked out. Proposal: refer to underwriting |
| CHG-7304, an added driver, backdated 20 days | Policy change | SR-1 applies. SR-5 does not: the driver is 45. To raise: the effective date is 22 days before the insurer date. Proposal: refer to the team leader |
| CHG-7305, a cancellation with an open claim | Policy change | SR-4 applies (CLM-4005). No return premium worked out. No gap can be measured. Proposal: refer to the team leader |
| CHG-7306, a cancellation before the new policy starts | Policy change | No rule applies. Return premium USD 381.00. To raise: 4 days without cover, 7 Dec 2026 to 10 Dec 2026. Proposal: ready for the servicing officer, with the point to raise |
| CHG-7307, a change of vehicle | Policy change | No rule applies. Additional premium USD 73.00. Proposal: ready for the servicing officer |
| CHG-7308, a sum insured up by exactly 20.00 percent | Policy change | SR-3 does not apply: the increase is on the limit. Additional premium USD 60.40. Proposal: ready for the servicing officer |
| CRQ-7401, the buildings sum insured | Certificate | As asked. Buildings sum insured USD 310,000.00. Proposal: ready for the servicing officer |
| CRQ-7402, a limit the policy holds exactly | Certificate | As asked. Third party property limit USD 1,000,000.00. Proposal: ready for the servicing officer |
| CRQ-7403, a limit higher than the policy's | Certificate | Differs. The text shows USD 1,000,000.00, never the figure asked. Proposal: refer to the servicing officer |
| CRQ-7404, a party that is not on the policy | Certificate | Differs. The party is left out. Proposal: refer to the servicing officer |
| CRQ-7405, a date after the policy period ends | Certificate | Cover differs: 16 days after the end. No certificate text. Proposal: refer to the servicing officer |
| CRQ-7406, a date before an endorsement took effect | Certificate | As asked. Contents sum insured USD 35,000.00, the figure on 12 Oct 2026. Proposal: ready for the servicing officer |
| CRQ-7407, a waiver the wording does not hold | Certificate | Differs. No waiver is written. Proposal: refer to the servicing officer |

The broker questions of the invented insurer (BQ-76xx) do not belong to this desk. No demo case asks the requester, and none has a paragraph that cannot be filled: the invented insurer has no such record.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings here use `routing` with decisions, row labels and mark hints for each kind, `draft.sections` for the two text cards, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs an engine that reads a table by its own header row** (the `main` branch of the case desk repository from 26 November 2026). An older engine cannot read this desk's tables: one has six columns with the mark in the fifth, and two have five with the mark in the fourth.

`draft.rowLabels.citation` is set although no table of this desk has such a cell. The engine draws the lines of a row in two aligned columns only when that label is set. The label itself is never shown.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/policy-servicing/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
POLICY_SERVICING_AGENT_ID=<id of Policy Servicing> \
CERTIFICATE_AGENT_ID=<id of Certificate and Endorsement Preparation> \
KATONIC_AGENT_ID=<either of the two, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `POLICY_SERVICING_AGENT_ID` | The agent for cases of the kind Policy change. If it is empty, drafting such a case fails and says which variable to set |
| `CERTIFICATE_AGENT_ID` | The same, for Certificate and for Endorsement |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the fifteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's servicing system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Policy change`, `Certificate` or `Endorsement`.

Build the two agents from [`policy-servicing`](../../agents/policy-servicing/README.md) and [`certificate-and-endorsement-preparation`](../../agents/certificate-and-endorsement-preparation/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each follows the right answers in the invented insurer's scenario list, and every id, date, amount, sentence and template paragraph in it is what the invented insurer returns when it is started with the date 26 November 2026. Each reply says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/policy-servicing/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the three agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

To try the third kind, add a case by hand with the title `Venn, sum insured for the vehicle: endorsement`, the kind Endorsement and the request id CHG-7308. The stand-in answers with the endorsement for that change request.

## How a case reaches the desk

A member of the servicing team enters it, or the insurer's servicing system sends it to `POST /api/intake` with the intake token when a change request or a certificate request is received. The servicing system's own events carry a request id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 27 November 2026 the desk was run against the stand-in agent, and against nothing else, through fourteen scenarios in a headless browser: the shape of the canned replies and of the three instructions, set against the agents' own instructions and the invented insurer's own sentences; the fifteen demo cases with their rows, marks, cards and proposals; which agent and which instruction each kind used, and that the message names the request; a question to the agent; a redo with a note and an edit of the text; every decision (accept, wait for what is missing and then what came in, refer on, redo) on a case it fits; a decision the kind does not allow, refused by the server; the register and its export; filters and search; a case entered by hand, an endorsement entered by hand and a case of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360; and a reload.

All 14 scenarios passed (777 checks), with no console error, page error or failed request. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. No cluster was used.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three instructions |
| `cases.json` | The fifteen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo case, one for an endorsement entered by hand, and a plain default for any other case |
