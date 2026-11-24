# Returns Processing

Checks a return request against the company's returns policy, says which condition it meets or fails, and prepares the proposal and the message to the customer. A person in the care team approves or refuses. The agent issues no refund.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new return request arriving in the orders system. A person can also name a request |
| How people meet it | An application: the customer care desk. It also works in a chat |
| Reads from | The company's orders system: the request, the order and the returns policy. Past cases from the customer care system. The Returns Policy as a knowledge source |
| Changes | Saves its assessment as a draft. The draft changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the request, the order it is on and the returns policy.
- Checks the policy in a fixed order: the order line and quantity, the section on damaged, faulty or wrong items, the window, the category, and the condition of the item.
- Shows each condition it checked as met, not met or not applying, with the condition's number.
- Proposes approve, refuse or refer to a person, names the condition that decides, and for an approval works out the refund from the price paid.
- Drafts the message to the customer, with no promise of a date.
- Saves the assessment as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was approved or refused, and no refund was issued."

## What it does not do

- Approve or refuse a return. The orders system has operations for both, and this agent is not given them.
- Issue a refund, or say that one has been paid.
- Make an exception or offer goodwill. Those are for the Customer Care Team Leader.
- Doubt what the customer reports. It takes the condition and the reason as the request states them.
- Guarantee the same wording on every run. The assessment is a draft for the care team.

## What you set up

- A model for the Reasoning tier.
- The company's orders system, connected as an imported API, with the five operations listed for it in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operations that approve or refuse a return.
- The company's customer care system, with the one operation that searches past cases.
- A knowledge source that holds the company's Returns Policy. For the invented company it is [`../../policy-library/returns-policy-v3.0.md`](../../policy-library/returns-policy-v3.0.md). The invented retailer also serves the same text through its orders system, for trying the agent before a knowledge source is indexed.
- For the desk route, the customer care desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the orders system and the customer care system from their OpenAPI addresses. For the invented retailer, those are the documents at `/orders/openapi.json` and `/care/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Knowledge, connect a source that holds the Returns Policy.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the six operations named in [`agent.yaml`](agent.yaml). Attach nothing else. In Knowledge, attach the Returns Policy.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because an assessment saves a draft.
8. To start it when a request arrives, subscribe the platform to the retailer's `return-request` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the return requests section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `RR-2611-01`: inside the window, unopened. Approve, 64.00.
- `RR-2611-02`: asked for on day 38. Refuse under condition 1.2.
- `RR-2611-03`: chilled food. Refuse under condition 3.1.
- `RR-2611-04`: opened, no fault. Refuse under condition 2.2.
- `RR-2611-05`: opened and faulty. Approve under condition 5.2, 34.50.
- `RR-2611-07`: damage reported on day 15. Condition 5.3: it goes to the Customer Care Team Leader.
- `RR-2611-10`: asked for on day 30, which is inside the window. Approve, 46.00.
- Ask it to approve a return and pay the refund. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A person in the care team approves or refuses every return, and a refund follows only from that approval. A request the policy does not decide goes to the Customer Care Team Leader.
