# Customer Onboarding

Reads the documents an individual applicant sent, extracts the details, checks them against the application form and the bank's screening service, and prepares the account opening file.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | An application from an individual arriving with its documents. The bank's onboarding system can announce one through its event for new onboarding applications |
| How people meet it | An application: the Onboarding and review desk |
| Reads from | The bank's onboarding system: the application, its documents and the account opening requirements. The bank's screening service: the watchlist |
| Changes | Saves a draft file. The draft sends nothing and changes no status |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## How it writes

Plain statements, never in the first person. No count of marks in the Summary: the desk counts them from the table. Dates as 18 Nov 2026. An identity number only by its last four characters, as in ending 2045.

## What it does

- Reads the application, its checklist of required documents, the bank's requirements and the text of each document.
- Extracts full name, date of birth, nationality, identity number and address from the documents and compares each with the form.
- Checks the dates: the identity document must be valid, and the proof of address must be dated within the last 3 months (90 days).
- Screens the applicant's name, date of birth and nationality, and reads the watchlist entry of any hit to see what agrees and what differs.
- Writes one row for each item with its source, and marks it agrees, differs, missing or needs a person.
- Saves the file as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: approve, ask the applicant for a numbered list, or refer to Compliance.

## What it does not do

- Open or decline an account, or say that one is opened or declined. A member of staff approves or declines every account.
- Assume that a difference between the form and a document is a typing error. A one-letter difference in a name is shown with both spellings, and neither is chosen.
- Tell the applicant anything. A strong watchlist match goes to Compliance, and nothing is said to the applicant about the reason.
- Fill a gap or guess a missing value.
- Guarantee the same marks on every run. The file is a draft for the officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's onboarding system and screening service, connected as imported APIs, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Onboarding and review desk](../../desks/onboarding-and-review/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft file. For the onboarding officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Individual onboarding" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `ONB-1001`: Odalys Merrowby. A clean pack. Name, date of birth, nationality, identity number and address agree, the bill is 26 days old, the card is valid, and screening finds no hit. Approve.
- `ONB-1002`: the form says Isadora Fenimore and the identity card says Isadora Fennimore. The proof of address is a water bill 150 days old. Ask the applicant.
- `ONB-1003`: Wynn Castellano. The documents agree, and screening returns WL-9001 with score 100, with the same identity number. Do not open. Refer to Compliance and say nothing to the applicant about the reason.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A member of staff reads the file and approves, declines, or asks the applicant for what is missing. Compliance decides a strong watchlist match. Nothing is sent to the applicant by the agent.
