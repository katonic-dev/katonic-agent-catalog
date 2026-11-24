# Complaint Handling

Classifies a complaint under the company's complaints procedure, sets out what happened from the order and the contact history, works out the date the response is due, and drafts the response and the log entry. The Customer Relations Lead approves every response and any goodwill payment.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new complaint arriving in the customer care system. A person can also name a complaint |
| How people meet it | An application: the customer care desk. It also works in a chat |
| Reads from | The company's customer care system: the complaint, its contact history and the complaints procedure. The orders system: the order and its carrier scans. The Complaints Procedure as a knowledge source |
| Changes | Saves a classification (the log entry) and a response as drafts. Neither changes a status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the complaint, the earlier contacts, the order and the procedure.
- Takes the procedure's classes in their order and stops at the first that fits: safety or legal, repeat contact, service failure, disagreement with a policy.
- Works out the date the response is due from the day the complaint was received, and says when that date has passed.
- Sets out what happened in dated statements, keeping apart what the customer says, what the order shows and what the contact history shows.
- Drafts the response. For a safety or legal complaint the draft is an acknowledgement only, and the complaint goes to the Customer Relations Lead the same day.
- Saves the classification first and then the response, and says so only when the system says they were applied.
- Ends on one fixed line: "Nothing was sent to the customer, and no fault was admitted."

## What it does not do

- Send a response. The care system has an operation that sends one, and this agent is not given it.
- Admit fault, say the customer is wrong, or blame a carrier or a colleague.
- Offer money, a refund, a credit or goodwill.
- Decide anything about an injury, an illness or a legal threat.
- Guarantee the same wording on every run. The class and the date should be the same every time, and the tests check them. The response is a draft.

## What you set up

- A model for the Reasoning tier.
- The company's customer care system, connected as an imported API, with the five operations listed for it in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that sends a response.
- The company's orders system, with the two operations that read an order and its carrier scans.
- A knowledge source that holds the company's Complaints Procedure. For the invented company it is [`../../policy-library/complaints-procedure-v2.1.md`](../../policy-library/complaints-procedure-v2.1.md). The invented retailer also serves the same text through its care system, for trying the agent before a knowledge source is indexed.
- For the desk route, the customer care desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the customer care system and the orders system from their OpenAPI addresses. For the invented retailer, those are the documents at `/care/openapi.json` and `/orders/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Knowledge, connect a source that holds the Complaints Procedure.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the seven operations named in [`agent.yaml`](agent.yaml). Attach nothing else. In Knowledge, attach the Complaints Procedure.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, the second with the care tools only, and the others with all seven. Reset the retailer before each run, because each one saves drafts.
8. To start it when a complaint arrives, subscribe the platform to the retailer's `complaint` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the complaints section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `CM-2611-02`: a third contact about a refund. `repeat_contact`, section 2.2, due 2026-11-26. The order shows 28.00 approved on 2026-11-12 and not paid.
- `CM-2611-03`: glass in a jar and a cut finger. `safety_or_legal`, section 2.1, due 2026-11-25. Acknowledgement only.
- `CM-2611-06`: "legal action". `safety_or_legal`, due 2026-11-24. The order shows one charge of 60.95.
- `CM-2611-04`: the delivery charge. `policy_disagreement`, section 2.4, due 2026-12-02.
- `CM-2611-07`: one earlier contact. `service_failure`, section 2.3, due 2026-12-03. Not a repeat.
- `CM-2611-08`: two earlier contacts. `repeat_contact`, due 2026-11-22, which has passed.
- Ask it to send a response and add goodwill. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The Customer Relations Lead approves every response before it is sent, reads a safety or legal complaint on the day it arrives, and decides whether the company was at fault and whether any goodwill is paid.
