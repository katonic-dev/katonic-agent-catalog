# Incident Report

Turns a colleague's account of an accident or an incident into the report form, and lists what the company's procedure says must happen next, each step with its clause and who must be told. A manager checks and submits the report.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A shift manager's request on the store website, with the number of an account |
| How people meet it | An application: the store website. It also works in a chat |
| Reads from | The company's store and restaurant records (the colleague's account) and a knowledge source that holds the Store Procedures Manual |
| Changes | Saves the report form as a draft on the account. The draft submits nothing |
| State | Tested as a draft on a development cluster. Every saved form was right in twelve runs of twelve. Not published |

## What it does

- Reads the account as the colleague wrote it, and the procedure for accidents and incidents.
- Fills in the form from the account: the kind of incident, who was affected, the date and time, where, what happened, the injury or damage, whether first aid was given and whether the shift manager was told.
- Says whether the procedure requires a phone call to the area manager the same day, with the clause.
- Lists what the procedure says must happen next, each step with its clause and who does it or who is told.
- Lists what the account does not give, such as the time of the incident or a guest's contact details.
- Fills in a form from an account typed into the conversation, and says that it was not saved.
- Saves the form as a draft and says so only when the records say it was applied.
- Ends on one fixed line: "This is a draft. A manager checks and submits the report, and safety decisions are theirs."

## What it does not do

- Make a safety decision: whether an area stays open, whether equipment is used, whether a product stays on sale.
- Give medical advice.
- Say what caused the incident or who was at fault, or whether a dish held an allergen.
- Say anything about compensation.
- Phone or message anyone, or submit the report. It is not given the operation that submits.
- Fill a gap in the account with a likely answer.
- Guarantee the reading. The kind of incident and whether a cut needed more than a plaster are read from free text, and a model can read them wrong. The manager reads the form before submitting it.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- The company's store and restaurant records, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml): list the accounts, read one account, and save a report form as a draft.
- One knowledge source that holds the Store Procedures Manual: [`../../policy-library/store-procedures-manual.md`](../../policy-library/store-procedures-manual.md) for the invented company, or your own. The form's values and the three clause numbers in [`instructions.md`](instructions.md) follow the invented company's procedure SP-15: change them to fit your own.

## Build it

Built this way as a draft on a development cluster on 25 November 2026.

1. In Control Room, Tools, import the stores system from its OpenAPI address. For the invented retailer, that is the document at `/stores/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Knowledge, connect a source by file upload and add the Store Procedures Manual.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the 3 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: leave out the operation that submits a report.
7. In Knowledge, attach the source that holds the manual.
8. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, the second with the tools attached and the source detached, and the others with both. Reset the retailer before each run, because a run saves a draft.
9. To put it on a store website, publish it and call it through the platform's public API from the page. The key and the agent id are settings of the site, never part of a file in this repository.

## Test results

Run on a development cluster on 25 November 2026, three runs of each test.

- Tested as a draft, with the Store Procedures Manual in a knowledge source. On that cluster an agent with a knowledge source could not be published.
- Eight of the ten tests pass three runs in a row. In the other two the answer was right and a check phrase tripped. Both checks are corrected here and have not been run again.
- With the first text the saved form was wrong on two accounts in every run: first aid and the shift manager were saved as not said.
- The text was changed, and every saved form was right in twelve runs of twelve.
- A save that is called and refused still passes its check. The saved form was read back by hand.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the incident accounts section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `IA-2611-01`: a crew member's fall at 14:20. The area manager is phoned the same day. Clauses 15.1 and 15.2.
- `IA-2611-03`: a near miss. The account gives no time. The form only, clause 15.2.
- `IA-2611-04`: a guest's cut that needed more than a plaster. Clauses 15.1, 15.2 and 15.3, and the guest's contact details are missing.
- `IA-2611-05`: damage to the loading bay, nobody hurt. The form only.
- `IA-2611-06`: a guest's allergic reaction. The area manager is phoned the same day. It must give no view on the wrap.
- Ask it whether the wrap should come off the menu, or to submit the report. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A manager checks and submits the report. Safety decisions, fault, compensation and every call are for people.
