# Reinsurance desk

The settings folder that turns the Katonic case desk into a desk for an insurer's reinsurance accounts team. Bordereaux and paid claims sit in one queue. A bordereau is set against the numbered terms of its binder or treaty, and the differences are listed. A paid claim is set against the treaty that answers, with what is to raise and the system's working. Each kind goes to its own agent. A reinsurance accountant decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its coverholders, its reinsurers, its binders, its treaties, its bordereaux, its paid claims and the insured are invented. Nothing here is a real bordereau or a real recovery.

**Tested against the stand-in agent only.** The desk has not been run against real agents on a platform. No cluster was used. See "How it was tested".

## The two kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Bordereau | [Bordereaux Check](../../agents/bordereaux-check/README.md) | Reads the bordereau with the system's measure of every row, lists each measured difference with its term and the system's sentence, and reads the description of each risk against the excluded risks | A list of differences and a closing row with the system's count of the rows within terms, for the reinsurance accountant. The agent rejects no bordereau, changes no figure and writes to nobody |
| Recovery | [Treaty Recovery](../../agents/treaty-recovery/README.md) | Reads the paid claim with the system's working, and gives the treaty, what was paid, what is to raise and the working | A row for each claim and a last row with what is to raise in all, for the reinsurance accountant. The agent raises no recovery, books nothing and writes to no reinsurer |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Check the bordereau named in the case below", "Check the paid claim named in the case below for a recovery"). The case names the bordereau or the paid claim by its id. The agent reads the record itself from the insurer's reinsurance system.

### What one recovery case is

A recovery case on this desk is **one paid claim**. The Treaty Recovery agent can be asked for one claim or for the paid claims of a period. The desk asks for one claim, so that each claim is decided on its own and the register shows who approved which.

There is one exception, which the agent's instructions ask for: **the claims of one event are one case**. The treaty adds them together and applies the attachment point and the limit once, so neither claim can be read alone. The two claims of the fire at Cinder Quay (RCL-8808 and RCL-8809, event EVT-8891) are one case with two rows.

The list of a whole period can still be tried by hand (see "Without a platform").

## What the person sees

- **A queue of reinsurance cases**, each with its bordereau or claim id and its status. The title says who it is about, what it is and which work it is.
- **The case beside the list.** The desk's short account is on one side: for a bordereau the totals stated and every row as it was sent, for a paid claim the payments and the recoveries already raised. The agent's list is on the other. On a phone the account is folded, so the list comes first.
- **One row for each finding**, with a mark. A bordereau has a row for each difference and a closing row. A recovery has a row for each claim and a last row with what is to raise in all.
- **The agent's summary**, folded above the rows.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the list, and with which agent.

### The marks

| Mark | Used by | Meaning | Shown as |
|---|---|---|---|
| measured | Bordereau | The reinsurance system measured the difference, or says the totals do not add up, or says the premium is late | Amber, a not-equal sign |
| read from the description | Bordereau | The words of the row put the risk in a group the term excludes. The agent read this. The system did not measure it | The colour for a point a person decides |
| within terms | Bordereau | The closing row, with the system's count of the rows within every measured term | Grey, a dot, a thin edge |
| to raise | Recovery | The system says a recovery, or a cash call, is due and none is raised | Amber, an exclamation mark |
| raised for too little | Recovery | The system says a recovery is raised for less than is due. The row gives what is still to raise | Amber, a not-equal sign |
| needs a person | Recovery | The system cannot settle the claim, for example a date of loss outside the treaty period. It carries no amount | The colour for a point a person decides |
| nothing due | Recovery | The system says nothing is to be raised now, also where the paid loss is exactly on the attachment point | Grey, a dash, a thin edge |
| worked out | Recovery | The last row, with what is to raise in all as the system gives it | Grey, an equals sign, a thin edge |

No mark is green with a tick and none is red with a cross. No mark on this desk is a pass or a failure: a difference is a point to query, and a recovery to raise is work for the reinsurance accountant. The count above the rows lists the marks that were given, and no others.

## What the person decides

| Decision | Kind | What it records |
|---|---|---|
| Approve the list | Both | The reinsurance accountant approves the list as it stands, in their name. It accepts and rejects no bordereau, raises no recovery and no cash call, books nothing and writes to no coverholder and no reinsurer, and it changes nothing in the insurer's reinsurance system |
| Query the sender | Bordereau | What is queried, one point to a line. The case waits. When the sender has answered, the person adds the answer and the agent reads the bordereau again. The desk sends nothing to anyone: the reinsurance accountant writes to the coverholder, or to whoever sent the bordereau, outside this desk |
| Refer on | Recovery | Who it goes to and why, for a claim the system cannot settle |
| Send back to the agent | Both | A note that the agent sees. A new version of the list comes back |

The desk has no decision that accepts or rejects a bordereau, raises a recovery or a cash call, books a reinstatement premium or tells a reinsurer. The reinsurance accountant does each of those, in the insurer's reinsurance system. The desk never says that a bordereau is rejected or that a recovery is raised. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" where the proposal line fits a step this desk has:

| The proposal starts | Button marked |
|---|---|
| "no differences: ..." | Approve the list |
| "query with the sender: ..." | Query the sender |
| "no action: nothing is to be raised on ..." | Approve the list |
| "for the reinsurance accountant: to raise:" and then a claim | Approve the list |
| "for the reinsurance accountant: to raise: none; needs a person:" and then a claim | Refer on |

A case whose kind is neither of the two offers Refer on and the send back only. The server refuses any other decision on it, as it refuses Query the sender on a recovery and Refer on on a bordereau.

### What each kind shows

| Kind | Decisions | The lines of a row are labelled |
|---|---|---|
| Bordereau | Approve the list, Query the sender, Send back to the agent | Term, Finding |
| Recovery | Approve the list, Refer on, Send back to the agent | Treaty, Paid, To raise, Working |

**The Term cell of a recovery row is not drawn.** The agent's recovery table has eight columns. The engine keeps three cells between the name of a row and its mark, so the fourth, Term, is left off the screen. Nothing is lost for the reader: the working names each term in brackets, and the whole table is under "The draft as the agent wrote it".

**A cell that holds only "-" is drawn with its label.** The closing row of a bordereau shows "Term -". The last row of a recovery shows "Treaty -", "Paid -" and, for one claim, "Working -". The engine draws every cell that holds text.

## The fourteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| BDX-8701, risks bound, Pellowmere Cover Agency | Bordereau | Row 5 over the maximum line (term 3), row 7 outside the territory (term 2), both measured. Row 8, a thatched roof, read from the description (term 7). Row 3 is exactly on the line and is not listed. 10 of 12 rows within. Proposal: query with the sender |
| BDX-8702, risks bound, Quillfeather Marine Agency | Bordereau | Row 5 too much commission (term 5), row 7 a start date before the period (term 4), row 9 declared twice (term 9). No description is an excluded risk. 7 of 10 rows within. Proposal: query with the sender |
| BDX-8703, claims paid, Pellowmere Cover Agency | Bordereau | Row 5 does not add up (term 9), and the totals do not add up (term 9). Row 4, exactly on the claims authority, and row 7, with an agreement reference, are not listed. 8 of 9 rows within. Proposal: query with the sender |
| BDX-8704, risks ceded to the engineering quota share | Bordereau | No differences. Row 5 cedes exactly the maximum line and is within. 8 of 8 rows within. Proposal: no differences |
| RCL-8801 | Recovery | Nothing due: below the attachment point |
| RCL-8802 | Recovery | Nothing due: close to the attachment point, and below it |
| RCL-8803 | Recovery | To raise: USD 160,000.00 |
| RCL-8804 | Recovery | Raised for too little: USD 50,000.00 more, with USD 300,000.00 raised by RCV-8851 |
| RCL-8805 | Recovery | Nothing due: exactly on the attachment point |
| RCL-8806 | Recovery | To raise: USD 750,000.00, capped at the limit |
| RCL-8807 | Recovery | Needs a person: the date of loss is 3 days before the treaty period. USD 0.00. Proposal marks Refer on |
| RCL-8808 and RCL-8809, event EVT-8891 | Recovery | One case, two rows. To raise USD 30,000.00 and USD 20,000.00: USD 50,000.00 for the event |
| RCL-8810 | Recovery | Nothing due: the share is collected in the quarterly account |
| RCL-8811 | Recovery | Nothing due: the cash call is raised in full by RCV-8852 |

The partners of the invented insurer (PTN-89xx) do not belong to this desk. No demo case has a late premium, and none has a bordereau row with two differences: the invented insurer has no such record.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings here use `routing` with decisions and row labels for each kind, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs an engine that reads a table by its own header row** (the `main` branch of the case desk repository from 26 November 2026). An older engine cannot read this desk's tables: one has five columns with the mark in the fourth, and one has eight with the mark in the seventh.

`draft.rowLabels.citation` is set for the whole desk. The engine draws the lines of a row in two aligned columns only when that label is set. On a recovery the label is shown ("To raise"). A bordereau has no such cell, so there the label is never shown.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/reinsurance/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
BORDEREAUX_CHECK_AGENT_ID=<id of Bordereaux Check> \
TREATY_RECOVERY_AGENT_ID=<id of Treaty Recovery> \
KATONIC_AGENT_ID=<either of the two, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `BORDEREAUX_CHECK_AGENT_ID` | The agent for cases of the kind Bordereau. If it is empty, drafting such a case fails and says which variable to set |
| `TREATY_RECOVERY_AGENT_ID` | The same, for Recovery |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither of the two. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the fourteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's reinsurance system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Bordereau` or `Recovery`.

Build the two agents from [`bordereaux-check`](../../agents/bordereaux-check/README.md) and [`treaty-recovery`](../../agents/treaty-recovery/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each follows the right answers in the invented insurer's scenario list. Every id, date, amount and sentence in it is what the invented insurer returns when it is started with the date 26 November 2026: the replies were built by a script from the insurer's own output, and no figure was typed. The one thing that is not the insurer's is the reading of a description against the excluded risks (row 8 of BDX-8701), which is the agent's own work. Each reply says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/reinsurance/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the three agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

To try the list of a period, add a case by hand with the title `Paid claims of 1 Oct 2026 to 31 Oct 2026: recovery` and the kind Recovery. The stand-in answers with the three paid claims of October (RCL-8806, RCL-8808 and RCL-8809) and USD 800,000.00 to raise in all.

## How a case reaches the desk

A member of the reinsurance accounts team enters it, or the insurer's reinsurance system sends it to `POST /api/intake` with the intake token when a bordereau is received or when the paid claims of a period are checked. The reinsurance system's own events carry a record id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 27 November 2026 the desk was run against the stand-in agent, and against nothing else, through fourteen scenarios in a headless browser: the shape of the canned replies and of the two instructions, set against the agents' own instructions and the invented insurer's own sentences and figures; the fourteen demo cases with their rows, marks, figures and proposals; which agent and which instruction each kind used, and that the message names the record and carries the whole case; a question to the agent; a send back with a note and an edit of the text; every decision (approve, query the sender and then the sender's answer, refer on, send back) on a case it fits; a decision the kind does not allow, refused by the server; the register and its export; filters and search; a case entered by hand, the paid claims of a period entered by hand and a case of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360; and a reload.

All 14 scenarios passed (719 checks), with no console error, page error or failed request. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. No cluster was used.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two instructions |
| `cases.json` | The fourteen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo case, one for a period entered by hand, and a plain default for any other case |
