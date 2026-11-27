# Investigations desk

The settings folder that turns the Katonic case desk into a desk for an insurer's investigator. Two kinds of case sit in one queue. A new claim is set against the insurer's own numbered indicators before anything is paid. A claim that a handler has referred to the desk gets a case file: the parties, their earlier claims, the links to other claims and parties, and the public notices that name a person on the claim. Each kind goes to its own agent. The investigator decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its claimants, its claims, its parties, its repairers and its public notices are invented. Nothing here is a finding about a claim or about any person.

## The wording of this desk

The wording is the point of this desk. No label, button, hint, notice or stand-in reply says that a claim is false, or says what a person did. The desk's words are "indicator met", "linked through" and "for the investigator".

- An indicator that is met is a reason for the investigator to look. It is not a finding about the claim or about any person.
- A link is a fact two records share. A shared repairer, phone number, address, bank account or witness can have an ordinary reason.
- A public notice about a party is a public record of what it says. Nothing is drawn from it about the claim. A notice about another person of the same name says nothing about the party, and what it says is not set out.
- A decision on this desk is the investigator's own. It is not a finding. It declines no claim, holds no payment and contacts nobody.

Two places hold words the desk cannot change. The first agent's reply has the fixed heading "Draft fraud referral. For the investigator. Not issued." It is shown only when the folded part "The draft as the agent wrote it" is opened. The case file of CLM-6304 quotes an invented court list in the list's own words, as the agent's instructions ask, with the note "A public record of what it says. Not a finding about this claim."

## The two kinds of case

| Kind | Agent | What the agent does | What goes to the investigator |
|---|---|---|---|
| Indicator check | [Fraud Detection](../../agents/fraud-detection/README.md) | Has the investigations system measure the six indicators on a new claim, reads the parties' earlier claims, and says which indicators are met and what each rests on | A draft referral with its reasons. The agent declines nothing and holds no payment |
| Case file | [Investigation Case File](../../agents/investigation-case-file/README.md) | For a claim referred to the desk, sets out the referral, the parties, their earlier claims, the links and the public notices, each with its source | A draft case file. The agent states what the records show and no more |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction opens with the request the agent's own tests use ("Check the claim named in the case below against the fraud indicators", "Build the case file for the claim named in the case below"). The case names the claim by its id. The agent reads the claim itself from the insurer's investigations system.

## What the investigator sees

- **A queue of cases**, each with its claim id and its status. The title gives the claimant's family name, the loss and the kind of work.
- **The case beside the draft.** The desk's short account of the claim is on one side and the agent's draft is on the other. On a phone the account is folded, so the draft comes first.
- **One row for each finding**, with a mark and a note. An indicator check always has six rows, one for each indicator, met or not. A case file has a row for the referral, each party, each earlier claim, each link and each public notice, and a row that says so where none was found.
- **The agent's summary**, folded above the rows.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

### The marks

| Mark | Shown as | Used by | Meaning | Colour and sign |
|---|---|---|---|---|
| met | Indicator met | Indicator check | The system gives the indicator as met. A reason to look, not a finding | The colour for a point a person decides. No tick, no cross |
| not met | Indicator not met | Indicator check | The system gives the indicator as not met | Grey, a dash, a thin edge |
| recorded | Recorded | Case file | The referral, a party or an earlier claim, as the records give it | Grey, a dot, a thin edge |
| linked | Linked | Case file | A fact this claim and another record share, as the system matched it | The colour for a point a person decides |
| about the party | About the party | Case file | The name, the date of birth and the address agree | Blue, a dot |
| not about the party | Not about the party | Case file | The date of birth differs: another person of the same name | Grey, a dash, a thin edge |
| cannot tell | Cannot tell | Case file | The identifiers do not settle it. A person checks | Amber, a question mark |
| none found | None found | Case file | No earlier claim, no link or no public notice was found | Grey, a dash, a thin edge |

No mark is red with a cross and no mark is green with a tick: on this desk no mark is a failure and none is a pass. The count above the rows of an indicator check always gives both numbers, for example "0 met, 6 not met".

## What the investigator decides

| Decision | What it records |
|---|---|
| Open an investigation | That an investigation is opened on the claim, with what is to be looked at and why. It is the investigator's own decision and not a finding about the claim or about any person |
| No further action | That the investigator has read the draft and nothing further is needed from this desk, with the reason. The claim stays with its handler |
| Wait for what is missing | What is missing, one item to a line. The case waits. When it has come in the investigator adds it and the agent reads the claim again. The desk sends nothing to anyone: the investigator asks the claim's handler, outside this desk |
| Send back to the agent | A note that the agent sees. The agent writes the draft again |

Every decision takes a note. No button is filled in advance: the choice is the investigator's. The desk has no decision that accepts, approves, declines or pays anything, and the server refuses one. None of these decisions changes anything in the insurer's investigations system. The person who entered a case cannot decide it.

A button is marked "Agent's proposal" only for "no referral: no indicator is met, the claim stays with its handler", which marks No further action. "refer to the investigations desk on ..., for the investigator to decide" and both case file proposals are readings for the investigator and mark no button: the agent never proposes an investigation.

The lines of a row are labelled Measured, Rests on and Note for an indicator check, and The records show, Record and Note for a case file.

## The fifteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| CLM-6201, Hollowell | Indicator check | No indicator met. Proposal: no referral |
| CLM-6202, Whitmarsh | Indicator check | Every figure under its threshold: 34 days, 2 earlier claims, 2 claims with one repairer, 91.0 percent. The account is also on CLM-6013 by a person at the claimant's own address, who is not counted. No indicator met. Proposal: no referral |
| CLM-6203, Farrowdale | Indicator check | FI-1 met: 12 days against 30 days or fewer. Proposal: refer on FI-1 |
| CLM-6204, Durrow | Indicator check | FI-2 met: 3 earlier claims against 3 or more. CLM-6014 is outside the 24 months and not counted. Proposal: refer on FI-2 |
| CLM-6205, Coombe | Indicator check | FI-4 met: 1 unrelated claimant against 1 or more. The account DEMO-ACCT-7741 is also on CLM-6021. Proposal: refer on FI-4 |
| CLM-6206, Ashdown | Indicator check | FI-5 met: invoice DOC-6206-2 is dated 6 days before the loss. Proposal: refer on FI-5 |
| CLM-6207, Wren | Indicator check | FI-1 met (9 days) and FI-6 met (98.0 percent). Proposal: refer on FI-1, FI-6 |
| CLM-6208, Marlowe | Indicator check | No indicator met. PTY-3011 has the same name and another date of birth: another person, whose three claims are not counted. Proposal: no referral |
| CLM-6301, Fenn | Case file | Linked to CLM-6302 and CLM-6303, each through the repairer and through the phone number. No public notice |
| CLM-6302, Rookhope | Case file | Linked to CLM-6301 and CLM-6303, through the same repairer and phone number |
| CLM-6303, Staveley | Case file | Linked to CLM-6301 and CLM-6302, through the same repairer and phone number |
| CLM-6304, Pryce | Case file | Public notice PN-901 is about the party. One earlier claim, CLM-6041. No links found |
| CLM-6305, Tansley | Case file | Public notice PN-902 is not about the party: another person of the same name. No earlier claim, no links |
| CLM-6306, Orrell | Case file | No earlier claim, no link and no public notice. The file reports the reason for the referral and adds nothing |
| CLM-6307, Lyle | Case file | Linked to CLM-6031 through the witness only. The witness is named as a fact of the records and nothing more is said |

The leakage review of closed claims (CLM-6101 to CLM-6108) does not belong to this desk.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at the `main` of 26 November 2026 or later: the engine must read a table by its own header row, because both tables have six columns with the mark in the fifth. The settings use `routing` with decisions, marks and row labels for each kind, `draft.markTones`, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.summaryAboveRows` and `case.foldOnPhone`.

Three things the engine does not do for this desk:

- A decided case offers no download of the draft as decided. The engine writes that document only for a decision whose outcome is called `issued`, and this desk's outcomes are an investigation opened and no further action. The draft stays on the case and the decision is in the register.
- A row's note that holds only a dash is still drawn, as "Note" with a dash.
- `draft.rowLabels.citation` is set although no row has that line. Without it the engine lays the first line of a row out in a way that breaks a sentence with ids into narrow columns.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/investigations/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
INDICATOR_CHECK_AGENT_ID=<id of Fraud Detection> \
CASE_FILE_AGENT_ID=<id of Investigation Case File> \
KATONIC_AGENT_ID=<either of the two, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `INDICATOR_CHECK_AGENT_ID` | The agent for cases of the kind Indicator check. If it is empty, drafting such a case fails and says which variable to set |
| `CASE_FILE_AGENT_ID` | The same, for Case file |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither. The desk asks it only to say that the kind is not recognised. Such a case offers no decision: it can be sent back or removed |
| `SEED_DEMO` | `true` loads the fifteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's investigations system |

Each agent folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one reply for each demo case, keyed by the case title. Each is the right answer of the invented insurer's scenario list in the agent's own reply shape, and every id, date, amount, count and sentence in it is what the invented insurer returns when it is started with the date 26 November 2026. Each reply says that it comes from the stand-in and that nothing was saved.

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/investigations/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in and any value for the key and the three agent ids. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How it was tested

On 27 November 2026 the desk was run against the stand-in agent only, through fourteen scenarios in a headless browser. No cluster was used and no real agent answered.

What was checked: the shape of the stand-in replies and of the two instructions, set against the agents' own instructions and the invented insurer's own sentences and figures; every string of the settings, the cases and the replies against the wording rule above; the fifteen demo cases with their rows, marks and proposals; which agent and which instruction each kind used; a question to the agent; a draft sent back with a note and an edit of the text; every decision on a case it fits (an investigation opened, no further action, waiting and then what came in, a decision that differs from the proposal); decisions the desk does not have, refused by the server; the register and its export; filters and search; a case entered by hand and one of a kind the desk does not know; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360; and a reload.

All 14 scenarios passed (889 checks), with no console error, page error or failed request. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform. The two agents are written and are not yet built on a cluster.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two instructions |
| `cases.json` | The fifteen demo cases. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's reply for each demo case, and a plain default for any other case |
