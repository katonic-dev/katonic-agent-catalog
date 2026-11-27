# Complaints desk

The settings folder that turns the Katonic case desk into a desk for an insurer's complaints officer. New complaints sit in one queue, each with its next deadline. One agent, Complaint Handling, prepares each one: it sorts it by the complaint categories, gives the deadlines as the conduct system counted them, says who handles it, links a repeat complaint to the first, and drafts the response to the customer and the entry for the complaints log. A complaints officer decides.

Thornmere Mutual Insurance (an invented insurer in the invented country Meridia), its customers, their policies, claims and complaints are invented. Nothing here is a real complaint.

**Tested against the stand-in agent only.** The desk has not been run against the real agent on a platform. See "How it was tested".

## What the desk does not do

The desk and the agent uphold no complaint, reject none, offer no money, admit no fault and send nothing. Whether a complaint is upheld or rejected is the complaints officer's decision. The officer writes that sentence into the response, signs it and sends it, from the insurer's conduct system. The draft response leaves that sentence out.

## The agent

| Agent | What it does | What goes to the person |
|---|---|---|
| [Complaint Handling](../../agents/complaint-handling/README.md) | Reads the complaint and the complaints procedure from the insurer's conduct system. Says whether the item is a complaint or a question, gives one category, gives the two deadlines in the system's own sentences, checks the rules on a vulnerable customer, a regulator or lawyer, and a repeat complaint, and sets out the policy and its claims | A table of points, a draft response to the customer and a log entry, for the complaints officer |

The desk sends the agent one message: the instruction, then the case. The instruction opens with "Prepare the complaint named in the case below", which is the request the agent's own tests use. The case names the complaint by its id. The agent reads the complaint itself from the conduct system.

## What the officer sees

- **A queue of complaints**, the nearest deadline first. Each line shows the customer, the complaint id and the next deadline: "Acknowledge by 19 Nov 2026", or "Respond by 24 Dec 2026" once the complaint is acknowledged. A complaint whose deadline is late carries a red mark "Late". One that is due on the day carries an amber mark "Due today". A customer the care record marks as vulnerable carries the mark "Vulnerable". Once the agent has read an item as a question, it carries "Not a complaint".
- **The complaint beside the draft.** The customer's own words and the deadlines, in the conduct system's own sentences, are on one side. The agent's draft is on the other. On a phone the complaint's text is folded, so the draft comes first.
- **One row for each point**, with the rule it turns on, what the record shows, a mark and a note.
- **The draft response to the customer**, as a card of its own below the rows. It says "Not sent."
- **The agent's summary**, folded above the rows, and **the agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the draft, and with which agent.

The deadlines in the queue are the ones the conduct system counted, with Meridia's public holidays left out, on 26 November 2026. The desk does not count days itself.

### The marks

| Mark | Meaning | Shown as |
|---|---|---|
| late | The conduct system says the deadline has passed, or was met late | Red, a cross |
| due today | The conduct system says the deadline falls on this day. It is not late | Amber, an exclamation mark |
| on time | The conduct system says the deadline was met in time, or is not yet due | Green, a tick |
| applies | The rule in the row turns on this item. It is the agent's reading, for the officer to confirm | The colour for a point a person decides |
| does not apply | The rule was checked and does not turn on this item | Grey, a dash, a thin edge |
| noted | A fact gathered for the officer. It is not a finding | Grey, a dot, a thin edge |

No mark is a finding on the complaint. No mark says who is right.

## What the officer decides

| Decision | What it records |
|---|---|
| Approve the draft | The officer takes the draft response and the log entry, as written or as edited. It upholds nothing, rejects nothing, offers nothing and sends nothing |
| Refer to senior officer | Why the complaint goes to the senior complaints officer, for example because it mentions the regulator. The time limits do not change |
| Pass to policy servicing | Why the item is not a complaint. The policy servicing team answers the question. No time limit of the complaints procedure applies |
| Send back to the agent | A note that the agent sees. A new version of the draft comes back |

The desk sends nothing to anyone. Each step is carried out in the insurer's conduct system. The person who entered a complaint cannot decide it.

A button is marked "Agent's proposal" where the proposal names that step. "for the complaints officer: ..." marks Approve the draft. "for the senior complaints officer: ..." marks Refer to senior officer. "for the policy servicing team: ..." marks Pass to policy servicing.

The letter can be edited in a box of its own ("Edit the text"). An edit is kept as a new version in the officer's name.

## The eight demo complaints

| Complaint | In the queue | What the agent should find |
|---|---|---|
| CMP-7107, Bram Tollermoor | Acknowledge by 19 Nov 2026, Late | CC-6. The acknowledgement is late by 5 working days, with Charter Day, 16 Nov 2026, left out of the count. Final response due 11 Dec 2026. CMP-7052 is a different matter and is not linked |
| CMP-7108, Teodor Brackwell | Acknowledge by 26 Nov 2026, Due today | CC-4. The acknowledgement is due on this day and is not late. Final response due 23 Dec 2026 |
| CMP-7101, Corwin Ashgrove | Acknowledge by 27 Nov 2026 | CC-1. Not yet due. Final response due 24 Dec 2026. No special rule |
| CMP-7104, Aldous Pennicott | Acknowledge by 30 Nov 2026, Vulnerable | CC-3. CH-3 applies: the care record marks him vulnerable, contact by telephone. Final response due 10 Dec 2026, 15 days in place of 30 |
| CMP-7102, Yvaine Corrimond | Acknowledge by 30 Nov 2026 | CC-2. The letter gives the decision on claim CLM-4010 as the claims record gives it and does not say whether it will stand. Final response due 25 Dec 2026 |
| CMP-7106, Isaura Venn | Acknowledge by 30 Nov 2026 | Not a complaint under CH-6: a question, for the policy servicing team. No category and no time limit |
| CMP-7105, Henrietta Quillby | Respond by 23 Dec 2026 | CC-4. CH-5 applies: a repeat, linked to CMP-7051. The records do not show whether the payment was refunded |
| CMP-7103, Odalys Fenwright | Respond by 24 Dec 2026 | CC-3. CH-4 applies: the complaint mentions the Meridia Insurance Authority. For the senior complaints officer |

For CMP-7106 the queue shows the date the conduct system holds, because the system does not read the words. Once the draft is in, the line also says "Not a complaint".

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The settings use a long-writing section in `draft.sections`, `case.flags`, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.summaryAboveRows`, `case.foldOnPhone` and `desk.documentLinkLabel`.

**The desk needs the engine change that reads a table by its own header row, which is on the engine's `main`.** The agent's table has six columns with the mark in the fifth. An older engine cannot read it.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm ci
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/complaints/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
DESK_AGENT_ID=<id of Complaint Handling> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `DESK_AGENT_ID` | The Complaint Handling agent. `KATONIC_AGENT_ID` does the same where `DESK_AGENT_ID` is not set |
| `SEED_DEMO` | `true` loads the eight demo complaints on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. The agent reads the insurer's conduct system |

Build the agent from [`complaint-handling`](../../agents/complaint-handling/README.md). Its `instructions.md` and the `draft.instruction` in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo complaint, keyed by the case title. Each follows the right answers in the invented insurer's scenario list. Every id, date, count of days and sentence on a deadline in it is what the invented insurer returns when it is started with the date 26 November 2026. Each reply says that it comes from the stand-in and that nothing was saved.

```bash
DESK_CONFIG=../katonic-agent-catalog/insurance/desks/complaints/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in and any value for the key and the agent id. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the insurer.

## How a complaint reaches the desk

A member of the complaints team enters it, or the insurer's conduct system sends it to `POST /api/intake` with the intake token when a complaint is logged. The conduct system's own events carry a complaint id and its deadlines, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 27 November 2026 the desk was run against the stand-in agent, and against nothing else, through fourteen scenarios in a headless browser: the shape of the canned replies and of the instruction, set against the agent's own instructions and the invented insurer's own sentences; the queue with its deadlines and marks; the eight complaints with their rows, rules, marks, letter and proposal; what the desk sent to the agent; a question to the agent; a draft sent back with a note, and an edit of the letter; every decision (approve, refer to senior officer, pass to policy servicing, send back) on a complaint it fits; what the server refuses; the register and its export; filters and search; a complaint entered by hand; the three themes, with contrast measured in light and in dark; a phone-width window at 390 and 360, with the new-case form; and a reload.

All 14 scenarios passed (611 checks), with no console error, page error or failed request. The desk was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against the real agent on a platform. No cluster was used. The stand-in replies are the right answers written out by a script, so the run shows that the desk reads the agent's reply shape and draws it rightly. It does not show what the agent itself writes.

## Known limits

- The queue's order is the order of the cases in `cases.json`. The engine cannot sort the queue by a deadline that the conduct system gives, and its own due date counts Monday to Friday with no public holidays. So the deadline and its state are fields of the case, as the conduct system gave them. A complaint entered later goes to the top of the queue whatever its deadline.
- Every complaint shows all three decision buttons. The engine limits buttons by kind of work only, and this desk has one kind.
- A row whose Rule or Note is empty shows a line that holds only a dash.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the instruction sent to the agent |
| `cases.json` | The eight demo complaints. The desk lists the newest case first, so the file is written last to first |
| `demo-replies.json` | The stand-in's canned reply for each demo complaint, and a plain default for any other case |
