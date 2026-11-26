# Periodic Review

Compares what the bank holds about a customer with the fresh documents received for a periodic review and with a fresh screening, and drafts the refreshed profile with every change marked.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | The list of customers due for review. A schedule starts the agent on each open review in the onboarding system's list |
| How people meet it | An application: the Onboarding and review desk |
| Reads from | The bank's onboarding system: the review, the profile the bank holds and the fresh documents. The bank's screening service: the watchlist |
| Changes | Saves a draft refreshed profile. The draft sends nothing and does not change the customer's record |
| State | Built on a development cluster. All six tests pass five runs in a row. Its desk is tested against a stand-in agent |

## How it writes

Plain statements, never in the first person. No count of marks in the Summary: the desk counts them from the table. Dates as 18 Nov 2026. An identity number only by its last four characters, as in ending 2045.

## What it does

- Reads the review: the profile the bank holds, the date of the last review, the risk rating and the fresh documents.
- Compares each field of the held profile that a fresh document speaks to. Equal values agree. Different values are changed, with the old value, the new value and the document id.
- For a business, compares the owners on the fresh registry extract and ownership declaration with the owners the bank holds, person by person and share by share.
- Screens the customer again, and for a business the company and every owner of 25 percent or more.
- Applies the bank's rule on higher-risk countries, and proposes a risk rating with the reason.
- Says which fields no fresh document covers, and does not mark them.
- Saves the refreshed profile as a draft and ends with one proposal line: approve for sign-off, send the rating change for approval, or ask the customer for a numbered list.

## What it does not do

- Complete a review, sign it off or change a risk rating. The reviewer signs off, and a change of rating needs the approval of a named person.
- Carry out enhanced checks on an owner in a higher-risk country. A person does.
- Fill a gap, or say that a field no fresh document covers is unchanged.
- Guarantee the same marks on every run. The profile is a draft for the reviewer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's onboarding system and screening service, connected as imported APIs, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Onboarding and review desk](../../desks/onboarding-and-review/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- A schedule that lists the open reviews and sends each one to the agent, if you want it to start on a clock. This is not written here.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft file. For the onboarding officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Periodic review" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `KYR-1001`: Cassius Dunmore (CUS-1013). Nothing changed. The fresh identity card and proof of address agree with the profile. The rating stays standard. Sign-off only.
- `KYR-1002`: Leopold Fenwick-Aral (CUS-1015). Two changes: the address, from 8 Kestrel Hill, Marlow Reach to 22 Barley Mill Lane, Tallowby, Meridia (source KYD-1002-01), and the occupation, from employee and quantity surveyor to self-employed building surveyor (source KYD-1002-02). The rating stays standard. Sign-off only.
- `KYR-1003`: Orchard Lane Dental Group (CUS-1024). Ownership changed from Ottoline Brackenridge 55 and Hamish Brackenridge 45 to 40, 30 and Tavish Orrelby 30, who lives in Gallowmere, Kharnovia, the higher-risk country. Propose the rating high, from standard, with that reason. The change needs the approval of a named person before the review is completed.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The reviewer signs off every review. A named person approves any change of risk rating. Nothing in the customer's record changes until a person completes the review.
