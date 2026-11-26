# Business Onboarding

Reads a company's registry extract and constitutional documents, draws its ownership chain, lists its directors and owners for screening, and prepares the account opening file.

| | |
|---|---|
| Type and form | Multi-agent, pipeline |
| What starts it | An application from a company arriving with its documents. The bank's onboarding system can announce one through its event for new onboarding applications |
| How people meet it | An application: the Onboarding and review desk |
| Reads from | The bank's onboarding system: the application, its documents and the account opening requirements. The bank's screening service: the watchlist |
| Changes | Saves a draft file. The draft sends nothing and changes no status |
| State | Built on a development cluster. All six tests pass five runs in a row. Its desk is tested against a stand-in agent |
| Website page | [katonic.ai/use-cases/banking-business-onboarding-agent](https://www.katonic.ai/use-cases/banking-business-onboarding-agent) |

## How it writes

Plain statements, never in the first person. No count of marks in the Summary: the desk counts them from the table. Dates as 18 Nov 2026. An identity number only by its last four characters, as in ending 2045. A row about a gap in the ownership chain begins with GAP:.

## The four stages

The stages are fixed and run in this order.

1. Read the company registry extract and the constitutional documents.
2. Draw the ownership chain from the registry extract and the ownership declaration, down to the people behind it.
3. List every director and every owner of 25 percent or more, and screen each of them and the company.
4. Prepare the file and save it as a draft.

The desk sends one message and reads one reply, so this guide builds the pipeline as one chat agent that works through the four stages in turn. A platform that can run the stages as a team of specialists may split them at the same lines. That has not been tried.

## What it does

- Checks that the registry extract was issued within the last 3 months, and that the company name, registration number and registered address agree with the form.
- Notes who may open and operate accounts under the articles.
- Draws the ownership chain: each owner, whether a person or a company, the share, the country and the document that shows it.
- Lists every gap in the chain. A gap is an owner that is a company when no document shows who owns it. The agent says what is missing and stops there.
- Compares the directors on the registry extract with the directors on the form. A director on the extract who is not on the form is a difference.
- Screens the company, each director and each owner of 25 percent or more that a document names, and reports what the screening service returns.
- Writes one row for each item with its source, marks it agrees, differs, missing or needs a person, saves the file as a draft, and ends with one proposal line.

## What it does not do

- Open or decline an account. A member of staff approves or declines every account.
- Fill a gap in the ownership chain. It never names an owner behind a company, never infers one from a name, a country or a note on the form, and never takes one from memory.
- Screen an owner that no document names. It says so.
- Tell the applicant anything.
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
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft file. For the onboarding officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Business onboarding" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `ONB-1004`: Cobblegate Print Supplies Ltd. One owner and director with 100 percent. All three documents are in, and the registry extract and the declaration agree with the form. Approve. Screening also returns a weak hit on the director's surname, WL-9007 with score 79, which the officer clears.
- `ONB-1005`: Larkfield Marine Services Ltd. 60 percent is held by Vardane Holdings Ltd in Quenmark and 40 percent by Corwin Ashdown. No document shows who owns Vardane Holdings Ltd, so 60 percent, above the 25 percent threshold, is not traced to people. List the gap and the missing document. Never name or guess the owners. Ask the applicant.
- `ONB-1006`: Thistlewick Bakehouse Ltd. The registry extract lists directors Nerys Hallowfield and Garrick Oldacre. The form lists only Nerys Hallowfield. Garrick Oldacre, appointed 21 days ago and a 30 percent owner, must be listed, identified and screened. Ask the applicant.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A member of staff reads the file and approves, declines, or asks the applicant for what is missing. A gap in the ownership chain is closed only by a document from the applicant. Nothing is sent to the applicant by the agent.
