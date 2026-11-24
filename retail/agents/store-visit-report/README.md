# Store Visit Report

Turns an area manager's visit checklist and notes into the visit report, with each finding tied to the brand standard it rests on. The area manager signs the report and owns the actions.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new area manager visit arriving in the stores system. A person can also name a visit |
| How people meet it | Inside the company's own system: the report is sent to the area manager. It also works in a chat |
| Reads from | The company's store records (the visit, its checklist and notes) and a knowledge source that holds the Brand Standards |
| Changes | Saves its report as a draft. The draft changes nothing in the visit |
| State | Tested as a draft on a development cluster. Seven of eight tests pass three runs in a row. Not published |

## What it does

- Reads the visit: every checklist item with its standard, its score and its note, and the area manager's notes.
- Lists every checklist item scored 1 or 0 as a finding, under the standard the checklist gives for it, with the wording of that standard from the Brand Standards.
- Reads the notes one sentence at a time. A sentence that says what was seen, and that one standard covers, becomes a finding tied to that standard.
- Lists a sentence that is too vague to tie to a standard under "To clarify with the area manager", in the area manager's own words, and ties it to nothing.
- Says so plainly when a visit has no finding.
- Leaves the actions to the area manager: the report has one line for them and proposes none.
- Saves the report as a draft and says so only when the records say it was applied.
- Ends on one fixed line: "The area manager signs this report and owns the actions."

## What it does not do

- Sign a report, set an action, name an owner or give a date.
- Draw a conclusion about a manager, a crew member or a team.
- Change a score or tidy up the notes.
- Write a report when the Brand Standards are not connected. It says so and stops.
- Guarantee that every sentence of the notes lands in the right place. Sorting a clear finding from a vague remark is a judgement the model makes. The area manager reads the report before signing it.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- The company's store records, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml): list the visits, read one visit, and save a report as a draft.
- One knowledge source that holds the Brand Standards: [`../../policy-library/brand-standards-v2.0.md`](../../policy-library/brand-standards-v2.0.md) for the invented company, or your own.

## Build it

Built this way on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the stores system from its OpenAPI address. For the invented retailer, that is the document at `/stores/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Knowledge, connect a source by file upload and add the Brand Standards.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
7. In Knowledge, attach the source that holds the Brand Standards.
8. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, the second with the tools attached and the source detached, and the others with both. Reset the retailer before each run, because a report saves a draft.
9. To start it when a visit arrives, subscribe a workflow or a webhook to the retailer's `site-visit` event and pass the visit number in the message. This route is not written yet.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- Seven of the eight tests pass three runs in a row.
- On the eighth every check passed, but the search never returned the wording of one standard, so the report named it without quoting it.
- Every report saved to the retailer was right.
- On that cluster the save needed one extra sentence in the instructions about the shape of the call. That sentence is not part of this folder.
- The agent was tested as a draft and is not published.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the area manager visits section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `SV-2610-01` (restaurant R-047): three findings on the checklist (BS-2.1, BS-3.2, BS-6.1), one in the notes (BS-5.2), and one sentence about the evening team to clarify.
- `SV-2610-02` (store S-106): three findings on the checklist (BS-4.3, BS-5.1, BS-7.1) and two sentences to clarify, one of them "Refunds seem high here". It must tie neither to a standard.
- `SV-2610-03` (restaurant R-014): no finding.
- `SV-2610-06` (store S-102): one finding on the checklist (BS-6.1) and one in the notes that rests on a different standard (BS-6.2).
- Ask it to sign the report and set a deadline. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The area manager signs every report, sets the actions and their dates, and agrees them with the site. A note that is too vague to tie to a standard goes back to the area manager.
