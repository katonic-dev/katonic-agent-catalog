# Shift Handover

Drafts the handover note for the next shift from the day's log: what happened, what is still open, and what needs doing first. Every line rests on an entry of the log. The outgoing manager checks and signs the note.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, at the end of the trading day, for each site. A person can also name a site and a day |
| How people meet it | Inside the company's own system: the note is saved on the store's log. It also works in a chat |
| Reads from | The company's store and restaurant records: a site's shift log for a day |
| Changes | Saves its note as a draft on the log. The draft changes no entry |
| State | Built and tested on a development cluster. Every test passes three runs in a row, and the saved notes were right |

## What it does

- Reads every entry of the day: its number, its time, its kind, who logged it and what it says.
- Sorts the entries by their own words: finished, or still open.
- Lists what happened, leaving routine entries out.
- Lists each open entry with its number and its time.
- Puts first the open entries that name a time on the next day, earliest first.
- Says so plainly when the log leaves nothing open, and when no open entry names a time.
- Saves the note as a draft, each line tied to the entry it rests on, and says so only when the records say it was applied.
- Ends on one fixed line: "This is a draft from the log. The outgoing manager checks and signs it."

## What it does not do

- Add anything that is not in the log: no cause, no extra task, no advice.
- Say whether food was safe or whether equipment may be used.
- Say anything about a colleague. A colleague is the number the log gives.
- Sign the note, close an entry or contact anyone.
- Guarantee the reading. Whether an entry is finished or still open is read from free text, and a model can read it wrong. The outgoing manager reads the note before signing it.

## What you set up

- A model for the Reasoning tier.
- The company's store and restaurant records, connected as an imported API, with the 2 operations listed for it in [`agent.yaml`](agent.yaml): read a site's shift log for a day, and save a handover note as a draft.

## Build it

Built this way on a development cluster on 25 November 2026.

1. In Control Room, Tools, import the stores system from its OpenAPI address. For the invented retailer, that is the document at `/stores/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 2 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once for each site at the end of the trading day. This form is not written yet.

## Test results

Run on a development cluster on 24 and 25 November 2026, three runs of each test.

- Every test passes its checks three runs in a row.
- Every note was saved at the first call, and every note saved on the instructions here was right.
- The first text sometimes put the wrong entry first on one restaurant's log. A sentence on what goes first was added, and the three runs after it were right.
- The first text sometimes ended a reply with the note's last line when no note was written. A sentence was added, and that no longer happens.
- The reply in the Work Room, on the published agent, was delivered and the saved note was right.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, logs for 2026-11-23). The right answers are in the shift logs section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `R-014`: five entries are open. `LE-R014-1123-09` comes first: the engineer for the make-line chiller comes between 08:00 and 10:00.
- `R-031`: four entries are open. `LE-R031-1123-07` comes first: a new produce delivery at 07:30. The till that counted 35.00 short was reported, so it is not open.
- `R-058`: three entries are open. `LE-R058-1123-09` comes first, at 09:00, before the engineer at 14:00.
- `S-104`: three entries are open. `LE-S104-1123-06` comes first: the delivery at 06:30 has one colleague to unload it.
- `R-022`: no log. It must say so and write nothing.
- Ask it to add something that is not in the log. It must refuse.
- To see a log with nothing open, make one arrive with `POST /admin/simulate/shift-end`: the first one is for `R-022`.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The outgoing manager checks and signs the note. What is done about an open entry is for the manager of the next shift.
