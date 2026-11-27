# Underwriting desk

The settings folder that turns the Katonic case desk into a desk for an insurer's underwriting team. Three kinds of case sit in one queue. A broker's submission is set against each guideline of its class of business. A referral raised by an underwriter is set out as a memo, with the rule that forces it and the earlier referred risks. A renewal that falls due is set out with the expiring terms, the claims of the period and the renewal rules. Each kind goes to its own agent. A person decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its brokers, its insureds, its submissions, its referrals, its precedents, its policies and its claims are invented. Nothing here is a real decision on a risk.

**Tested against the stand-in agent only.** The desk has not been run against real agents on a platform. See "How it was tested".

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Submission | [Underwriting Support](../../agents/underwriting-support/README.md) | Sets the submission against each guideline of its class: within, outside, missing or cannot tell, and where a document contradicts the form | An underwriting file, for the underwriter. The agent accepts, declines, quotes and binds nothing |
| Referral | [Underwriting Referral Memo](../../agents/underwriting-referral-memo/README.md) | Sets out the risk, the terms proposed, each referral rule as the system's authority check gives it, the guidelines the risk is outside, and each earlier referred risk with how it is alike or differs | A referral memo, for the deciding underwriter. The agent recommends no decision and sends no memo |
| Renewal | [Renewal Review](../../agents/renewal-review/README.md) | Sets the expiring terms beside the claims of the period and the changes in the risk, and marks which of the five renewal rules each finding touches | A renewal review, for the underwriter. The agent renews nothing and offers no terms |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Prepare the underwriting file for the submission named in the case below", "Draft the referral memo for the referral named in the case below", "Review the renewal named in the case below"). The case names the record by its id. The agent reads the submission, the referral or the renewal itself from the insurer's underwriting system.

## What the person sees

- **A queue of underwriting cases**, each with its record id and its status. The title names the insured and the kind of work.
- **The case beside the draft.** The desk's short account of the case is on one side. The agent's draft is on the other. On a phone the account is folded, so the draft comes first.
- **One row for each finding**, with a mark. A submission has a row for each guideline of its class. A referral has a row for the risk, the terms, each referral rule, each guideline the risk is outside and each precedent. A renewal has seven rows: the expiring terms, the claims of the period and one for each renewal rule.
- **The agent's summary**, folded above the rows.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

### The marks

| Mark | Used by | Meaning | Shown as |
|---|---|---|---|
| within | Submission | The guideline is met, by the system's measure or on reading | Green, a tick |
| outside | Submission, referral | The risk is outside the guideline. It is not declined here | Red, a cross |
| missing | Submission | The submission lacks what the guideline needs. Nothing is assumed | Amber, a question mark |
| cannot tell | Submission | The form and a document disagree, or the form does not state the fact. Neither is chosen | Amber, a question mark |
| applies | Referral, renewal | The rule applies, as the underwriting system says | The colour for a point a person decides |
| does not apply | Referral, renewal | The rule does not apply, as the underwriting system says | Grey, a dash, a thin edge |
| depends on the disagreement | Renewal | Whether the rule applies depends on how two records that disagree are settled | Amber, a question mark |
| agrees | Referral | The earlier risk matches on the fact its decision rested on, and was approved | Blue, an equals sign |
| differs | Referral | The earlier risk looks alike, and that fact is not there in this referral | Amber, a not-equal sign |
| went against | Referral | The earlier risk matches on that fact, and the request was declined | Amber, a dash |
| not alike | Referral | A different kind of premises or use, or a different construction class | Grey, a dash, a thin edge |
| none found | Referral | A referral is needed and no search returned an earlier risk | Grey, a dash |
| stated | Referral | The risk or the terms, as the referral gives them | Grey, a dot, a thin edge |
| noted | Renewal | A row that touches no renewal rule | Grey, a dot, a thin edge |

No mark is a decision on a risk. A mark is the agent's reading, for a person. A precedent is a past decision, not a rule, so "agrees" is not a green tick and "went against" is not a red cross. The count above the rows lists the marks that were given, and no others.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the draft as the file note. It accepts, declines, quotes and binds no risk, refers nothing and offers no renewal terms, and it changes nothing in the insurer's underwriting system |
| Wait for what is missing | What is missing, one item to a line. The case waits. When it has come in the person adds it, and the agent reads the record again. The desk sends nothing to anyone: the underwriting team asks the broker or the claims team, outside this desk |
| Refer on | Who it goes to and why: a senior underwriter, the head of underwriting, or the grade the memo names. The desk sends nothing: the referral is made in the insurer's underwriting system |
| Ask the agent to redo the draft | A note that the agent sees |

The desk has no decision that accepts, declines, quotes or binds a risk, or that offers renewal terms. A risk is accepted, declined or quoted by the underwriter, a referral is decided by an underwriter with the authority, and renewal terms are decided by the underwriter, each in the insurer's underwriting system. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" only where the proposal is a step this desk has. "ready for the underwriter ..." and "no referral needed: ..." mark Accept the draft. "ask the broker: ..." and "ask the claims team: ..." mark Wait for what is missing. "refer to the ..." marks Refer on. "survey before terms: ..." is a reading for the underwriter, who arranges the survey, and marks no button.

### What each kind shows

| Kind | Decisions | The lines of a row are labelled |
|---|---|---|
| Submission | Accept the draft, Wait for what is missing, Refer on, redo | The file shows, Source |
| Referral | Accept the draft, Refer on, redo | The record gives, Note |
| Renewal | Accept the draft, Wait for what is missing, Refer on, redo | The record shows, Rule, Note |

The server refuses a decision the kind does not offer.

**The Note of a submission row is not drawn in its row.** The underwriting file's table has two cells after the mark: Source and Note. The engine reads one. So the system's working of the total sum insured, what is missing, and the two accounts of a contradiction are not in the rows. They stay in the agent's summary, in the proposal, in the text the page shows under "The draft as the agent wrote it", and in the accepted draft.

## The nineteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| SBM-6501, Larkspur Lane Stationers | Submission | Every guideline within. Proposal: ready for the underwriter, within every guideline |
| SBM-6502, Wickerby Dairy Rounds, a motor fleet | Submission | UG-7 to UG-10 within. Proposal: ready for the underwriter, within every guideline |
| SBM-6503, Pellow & Strand Furniture Showrooms | Submission | UG-1 outside, over the class C limit by USD 350,000.00. Proposal: ready for the underwriter, outside UG-1 |
| SBM-6504, Grindlow Metals & Recycling | Submission | UG-2 outside on reading: a scrap yard and waste recycling. Proposal: ready for the underwriter, outside UG-2 |
| SBM-6505, Tarnbeck Garden Centres, a motor fleet | Submission | UG-10 missing: no claims history. Proposal: ask the broker for it |
| SBM-6506, Ottershaw Print Works | Submission | UG-3 cannot tell: the form says sprinklers yes, the survey note SBM-6506-D2 says the system is not live. Proposal: ask the broker which is right |
| SBM-6507, Saltmarsh Chandlery & Rope | Submission | UG-1 outside by USD 600,000.00 and UG-4 outside, 4 claims where 3 are allowed. Proposal: ready for the underwriter, outside UG-1, UG-4 |
| SBM-6508, Thimbleby Wool Merchants | Submission | Every guideline within: the total is exactly on the limit and the deductible is equal to the lowest. Proposal: ready for the underwriter |
| REF-6601, Pellow & Strand Furniture Showrooms | Referral | RF-2 applies. PRC-6401 and PRC-6402 agree, PRC-6403 not alike. Proposal: refer to the senior underwriter, forced by RF-2 |
| REF-6602, Marrowgate Grain & Seed Stores | Referral | RF-1 and RF-2 apply. PRC-6403 differs: its decision rests on sprinklers, and this risk has none. No precedent is outside UG-3. Proposal: refer to the senior underwriter |
| REF-6603, Hollinsworth Builders' Merchants, a motor fleet | Referral | RF-1 applies, RF-2 does not. No precedent found. Proposal: refer to the head of underwriting, forced by RF-1 |
| REF-6604, Quenby House Offices | Referral | No rule applies. Proposal: no referral needed, Isolde Varney may decide it without a referral |
| REF-6605, Wrenlow Tea Importers | Referral | RF-3 applies: 18.00 percent against 10.00 percent. PRC-6404 went against, PRC-6405 differs. Proposal: refer to the senior underwriter, forced by RF-3 |
| RNW-6701, Ivelet & Thorn Bookbinders | Renewal | Loss ratio 15.00 percent. No rule applies. Proposal: ready for the underwriter |
| RNW-6702, Dunmarrow Catering Supplies | Renewal | Loss ratio 82.50 percent. RN-1 applies. Proposal: refer to the senior underwriter |
| RNW-6703, Hartsease Garden Tools | Renewal | A change of occupancy reported on 29 Jun 2026. RN-2 applies. Proposal: survey before terms |
| RNW-6704, Aldous Pennicott, a home | Renewal | An open claim, all of it reserve: 0.00 percent on payments alone, 5,000.00 percent with the reserve. RN-1 and RN-4 apply. Proposal: refer to the senior underwriter |
| RNW-6705, Calloway & Finch Shopfitters | Renewal | No claim. The sprinklers are out of service. RN-3 applies. Proposal: refer to the senior underwriter |
| RNW-6706, Merrowdown Marine Stores | Renewal | Two records disagree on CCL-6906: 76.00 percent with every claim, 31.00 percent leaving it out. RN-5 applies, RN-1 depends on the disagreement. Proposal: ask the claims team |

Every proposal the three agents can make is in the queue.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings here use `routing` with decisions, row labels and mark hints for each kind, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs the engine change that reads a table by its own header row, which is on the engine's `main`.** An engine older than that cannot read this desk's tables: one has five columns with the mark in the fourth, one has six with the mark in the fourth, and one has six with the mark in the fifth.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/underwriting/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
UNDERWRITING_SUPPORT_AGENT_ID=<id of Underwriting Support> \
REFERRAL_MEMO_AGENT_ID=<id of Underwriting Referral Memo> \
RENEWAL_REVIEW_AGENT_ID=<id of Renewal Review> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `UNDERWRITING_SUPPORT_AGENT_ID` | The agent for cases of the kind Submission. If it is empty, drafting such a case fails and says which variable to set |
| `REFERRAL_MEMO_AGENT_ID` | The same, for Referral |
| `RENEWAL_REVIEW_AGENT_ID` | The same, for Renewal |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the nineteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's underwriting system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Submission`, `Referral` or `Renewal`.

Build the three agents from [`underwriting-support`](../../agents/underwriting-support/README.md), [`underwriting-referral-memo`](../../agents/underwriting-referral-memo/README.md) and [`renewal-review`](../../agents/renewal-review/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each follows the right answers in the invented insurer's scenario list, and every id, date, amount and sentence of the system in it is what the invented insurer returns when it is started with the date 26 November 2026. Each reply says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/underwriting/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the four agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How a case reaches the desk

A member of the underwriting team enters it, or the insurer's underwriting system sends it to `POST /api/intake` with the intake token: when a broker's submission arrives, when an underwriter raises a referral, or when a renewal falls due. The underwriting system's own events carry a record id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 27 November 2026 the desk was run against the stand-in agent, and against nothing else, through fourteen scenarios in a headless browser: the shape of the canned replies and of the three instructions, set against the agents' own instructions and the invented insurer's own sentences; the nineteen demo cases with their rows, marks and proposals; which agent and which instruction each kind used, and that the message names the record; a question to the agent; a redo with a note and an edit of the text; every decision (accept, wait for what is missing and then what came in, refer on, redo) on a case it fits; a decision the kind does not allow, refused by the server; the register and its export; filters and search; a case entered by hand and one of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360, with the new-case form; and a reload.

All 14 scenarios passed (906 checks), with no console error, page error or failed request. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. No cluster was used. The stand-in replies are the right answers written out by a script, so the run shows that the desk reads the agents' reply shape and draws it rightly. It does not show what the agents themselves write.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three instructions |
| `cases.json` | The nineteen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
