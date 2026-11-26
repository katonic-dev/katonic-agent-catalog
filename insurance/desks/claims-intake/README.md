# Claims intake desk

The settings folder that turns the Katonic case desk into a desk for an insurer's claims intake team. Four kinds of case sit in one queue. A new loss report is made into a draft claim file. A registered claim is sorted by the rules of the claims handling guide. A claim's documents are checked against the checklist for its type. A claim an adjuster is about to open gets a summary. Each kind goes to its own agent. A claims handler decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its customers, its policies, its claims and all their documents are invented. Nothing here is a real claim or a decision on one.

## The four kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Loss report | [First Notice of Loss Intake](../../agents/first-notice-of-loss-intake/README.md) | Takes from the report who reports, what happened, when and where. Finds the policy, has the policy system say whether it was in force on the date of the loss, and lists what is missing | The draft claim file, for the claims handler. The agent refuses no claim and contacts nobody |
| Sorting | [Claims Processing](../../agents/claims-processing/README.md) | Tests the sorting rules of the claims handling guide in order and stops at the first that applies | The track, the team and the severity that rule gives, with the reason. The agent assigns no claim |
| Pack check | [Claim Pack Completeness](../../agents/claim-pack-completeness/README.md) | Compares the documents in the file with the checklist for the type of claim | What is missing, what cannot be read and what does not show what it must. The handler decides what is asked of the customer |
| Summary | [Claim Summary](../../agents/claim-summary/README.md) | Writes what the adjuster reads first: the loss, the policy, the documents, the amounts, the people, recovery and the open points, each with its source | The summary. It does not say whether the loss is covered |

The desk sends the agent one message: the instruction for the kind, then the case. The instruction starts as a person would ask ("Prepare the claim file for the loss report named in the case below.") and then repeats the reply shape the agent's own instructions set. The case names the loss report or the claim by its id. The agent reads the report, the claim, the policy and the handling guide themselves from the insurer's systems.

## What the desk does not decide

The desk decides nothing about a claim. Accepting a draft records that a person accepts the agent's draft as the file note, and nothing more. Registering a claim, cover, payment, a decline and anything sent to a customer are decided by the claims handler or the adjuster, in the claims system.

**Loss reports.** Registration happens in the claims system, not on this desk. On a platform the agent asks the claims system to register the claim when its proposal is to register, and the platform is meant to hold that request for a claims handler's approval. That hold has not yet been shown working. So the desk never says that a claim was registered. Accepting a loss report's draft means accepting the draft claim file.

## What the person sees

- **A queue of claims cases**, each with its kind, its id and the name of the reporter or claimant. A case in which a person was injured, or whose customer may be vulnerable, carries a short flag, taken from the agent's proposal.
- **The case beside the draft.** What the desk holds of the case is on one side: the loss report as it arrived, or the claim with the documents on file and their ids. The agent's draft is on the other. On a phone the case is folded under its heading, so the draft comes first.
- **One table for every kind**, one row for each item. Each row has what the report or the file shows, the source, a mark and a note. The agent's own summary is folded above the rows.
- **The agent's proposal**, one line, and a tag on the button it points to.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent run and tool calls.

### The marks

| Kind | Mark | Meaning | Shown as |
|---|---|---|---|
| Loss report | found | The report gives it, or the policy system confirms it | green, tick |
| Loss report | missing | The report does not give it, or cover could not be checked | red, cross |
| Loss report | differs | What the reporter gave is not what the insurer's records hold. Both are shown | amber |
| Loss report | not in force | The policy system says the policy was not in force on the date of the loss. A fact for the handler, not a decision on the claim | red, cross |
| Loss report | needs a person | A person was injured, or no policy or more than one fits | brand colour, for a person |
| Sorting | applies | The file shows every part the rule needs. This rule gives the track, the team and the severity | blue, dot |
| Sorting | does not apply | The file shows that the rule's words on when it applies are not met | grey, quiet |
| Pack check | received | In the file, readable, and it shows what the checklist says it must | green, tick |
| Pack check | missing | Not in the file | red, cross |
| Pack check | cannot be read | In the file, and it cannot be read | amber |
| Pack check | does not show what it must | In the file and readable, and it lacks or contradicts what the checklist asks | red, cross |
| Summary | stated | The file holds it and no record contradicts it | grey, dot, quiet |
| Summary | open | A person must supply or settle something before the claim can move on | brand colour, for a person |
| Summary | records disagree | Two records give different accounts of the same point. Both are shown and neither is chosen | amber |
| Summary | not provided | The file holds nothing on the point | grey, question mark |

A mark that is not a failure is never red with a cross, and a mark that is not a pass is never green with a tick. The rule of a sorting that applies is not a pass, and a stated fact in a summary is not one either: an injured passenger can be a stated fact.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the draft as the file note. It registers no claim, decides nothing on cover or payment, and changes nothing in the claims system |
| Ask for more | What to ask for, one item to a line. A letter is written, with no policy number in it. A handler reads and sends it. The case waits until the reply is added, then the agent reads the case again |
| Refer on | Who it goes to and why: a senior adjuster, the liability team or the claims manager |
| Ask the agent to redo the draft | A note that the agent sees |

The person who entered a case cannot decide it. The desk has no pass mark: the four kinds use different marks, and the engine takes one pass mark for a whole desk. So accepting a draft never asks for a reason.

## The fourteen demo cases

| Case | Kind | What the agent should find | Proposal |
|---|---|---|---|
| LR-3001, Isaura Venn | Loss report | Complete. POL-2011 was in force on 25 Nov 2026. Nobody injured, no other party | register the claim |
| LR-3002, Elric Stannaway | Loss report | The number given, POL-2021, does not exist. POL-2012 is found by name. No date of the loss, so cover is not checked | ask the reporter: the date of the loss |
| LR-3003, Ludovic Harrowell | Loss report | POL-2013 was cancelled on 17 Oct 2026, 38 days before the loss: not in force | refer to a handler |
| LR-3004, Ansel Whitlocke | Loss report | In force. His wife was taken to hospital. The other driver and van are named | refer to a handler: a person was injured |
| CLM-4001, Corwin Ashgrove | Sorting | HG-1 and HG-2 do not apply. HG-3 applies: USD 2,350.00 is under USD 2,500.00 and the pack is complete | sort as fast track, fast-track team, severity low, under HG-3 |
| CLM-4003, Dariusz Kellhaven | Sorting | HG-2 applies: the policy period ended on 5 Nov 2026 and the loss was on 7 Nov 2026 | sort as complex, senior adjuster, severity medium, under HG-2 |
| CLM-4005, Bram Tollermoor | Sorting | HG-1 applies: a passenger was taken to hospital. No later rule is tested | sort as person first, senior adjuster, severity high, under HG-1 |
| CLM-4008, Marisol Underhay | Sorting | HG-4 applies. Who was driving is for the coverage check, not for sorting | sort as standard, motor team, severity medium, under HG-4 |
| CLM-4001 | Pack check | Four of four received | the pack is complete |
| CLM-4002, Elspeth Marrowdene | Pack check | The plumber's report is missing. The photographs cannot be read | ask the customer for: Plumber's report; Photographs of the damage |
| CLM-4005 | Pack check | The police report is missing. The repair estimate names MR-7702-B and the insured vehicle is MR-7720-B | ask the customer for: Police report; Repair estimate |
| CLM-4001 | Summary | Nothing open. No recovery indicated | ready for the adjuster |
| CLM-4002 | Summary | Open points: the plumber's report, and photographs that can be read | open points first |
| CLM-4007, Aldous Pennicott | Summary | The claim form and the fire service report disagree on where the fire started. The customer is 81, lives alone and is out of his home. The contents list is missing | refer to a handler |

Every id, date, amount and sentence of reason in the canned replies was read from the invented insurer by a script, with the insurer date set to 26 Nov 2026.

Two proposals the agents can make have no demo case, because the insurer's data holds no case that leads to them: a sorting that is referred to a handler because the file does not settle a rule, and a pack check that is referred to a handler. The mark "not provided" of a summary does not occur in the demo either.

## What each kind shows

Each kind names its own decisions and marks (`routing.kinds.<kind>.decisions` and `.marks`). The server refuses a decision the kind does not offer.

| Kind | Decisions | Lines of a row |
|---|---|---|
| Loss report | Accept the draft, Ask for more, Refer on, redo | The report says, Source, Note |
| Sorting | Accept the draft, Refer on, redo | The file shows, Source, Note |
| Pack check | Accept the draft, Ask for more, Refer on, redo | Must show, In the file, Note |
| Summary | Accept the draft, Ask for more, Refer on, redo | The file shows, Source, Note |

A sorting asks nobody for anything, so it has no "Ask for more". The tag "Agent's proposal" sits on Accept for "register the claim", "sort as", "the pack is complete" and "ready for the adjuster"; on Ask for more for "ask the reporter", "ask the customer for" and "open points first"; and on Refer on for "refer to a handler".

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), with the `routing` setting and the per-kind decisions, marks and row labels.

**The desk needs the engine change in pull request 4 of the case desk repository, which is open and not yet merged.** The four agents write a table of six columns (number, item, what the file shows, source, mark, note). With that change the engine reads a table by its header: the two cells before the mark are the lines of the row, the Mark cell is the mark, and the cell after it is the note. Without it the engine reads the note as the mark, and no row gets a mark.

The first line of a row is labelled by `draft.rowLabels.source` and the second by `draft.rowLabels.policy`. A kind that names them differently gives its own `rowLabels`: "The report says" for a loss report, "Must show" and "In the file" for a pack check.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/claims-intake/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
LOSS_REPORT_AGENT_ID=<id of First Notice of Loss Intake> \
SORTING_AGENT_ID=<id of Claims Processing> \
PACK_CHECK_AGENT_ID=<id of Claim Pack Completeness> \
SUMMARY_AGENT_ID=<id of Claim Summary> \
KATONIC_AGENT_ID=<any one of the four, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `LOSS_REPORT_AGENT_ID` | The agent for cases of the kind Loss report. If it is empty, drafting such a case fails and says which variable to set |
| `SORTING_AGENT_ID` | The same, for Sorting |
| `PACK_CHECK_AGENT_ID` | The same, for Pack check |
| `SUMMARY_AGENT_ID` | The same, for Summary |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the four. The desk asks it only to say that the kind is not recognised. `DESK_AGENT_ID` does the same and wins over it |
| `SEED_DEMO` | `true` loads the fourteen demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the insurer's systems |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Loss report`, `Sorting`, `Pack check` or `Summary`.

Build the four agents from their folders under [`insurance/agents`](../../agents). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case title. Each has the shape the agent's instructions set and follows the right answers in the invented insurer's scenario list. Each says that it comes from the stand-in, that nothing was saved, and, for a loss report, that registration was not asked for. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/claims-intake/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the five agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How a case reaches the desk

A member of the claims team enters it, or the insurer's claims system sends it to `POST /api/intake` with the intake token. The insurer's own events (a loss report arrived, a claim was registered, a document arrived) carry a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 26 November 2026 the desk was run against the stand-in through thirteen scenarios in a headless browser: the fourteen demo cases with their rows, marks, mark colours and proposals; which agent and which instruction each kind used, and that each message names its record; a question to the agent; a redo with a note and an edit of the text; every decision (accept, ask for more with its letter and the reply, refer on); a decision the kind does not allow; the register and its export; filters and search by kind, id and name; a case entered by hand for each kind and one of a kind the desk does not know; the themes; a phone-width window at 390 and 360; and a reload.

Against the engine with the change of pull request 4 (the branch `feat/read-a-table-by-its-header`), all 13 scenarios pass (409 checks). Against the engine without it, 10 of 13 pass (342 of 409 checks): the marks are not read.

It was reviewed for visual design at desktop and phone width, in light and dark, on the engine with the change.

Not yet done: a run against real agents on a platform.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the four instructions |
| `cases.json` | The fourteen demo cases, written last case first so that the loss reports lead the queue |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
