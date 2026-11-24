# Customer Service

Drafts a reply to each customer ticket from the company's help articles and past cases, with the article cited, and says so when no article answers the question. A member of the care team sends every reply.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new customer ticket arriving in the customer care system. A person can also name a ticket |
| How people meet it | An application: the customer care desk. It also works in a chat |
| Reads from | The company's customer care system: the ticket, the help articles and past cases. The help articles as a knowledge source |
| Changes | Saves its reply as a draft. The draft sends nothing and changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the ticket: the customer's own words, the subject and the order number if there is one.
- Searches the help articles for the one that states what the customer asked, and the past cases for how the team answered before.
- Writes a reply of no more than 120 words that rests on the article, and cites the article by number and title.
- Says "No help article answers this question." when that is so, writes a holding reply, and proposes that the ticket is passed to a colleague.
- Saves the reply as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was sent to the customer."

## What it does not do

- Send a reply. The care system has an operation that sends one, and this agent is not given it.
- Promise a refund, a replacement, a credit, a cancellation or a delivery date.
- Answer a question the help articles do not answer, or say whether a food is safe for someone with an allergy.
- Read the order. It works from the ticket and the articles. An agent that explains an order's delivery is Order Enquiry.
- Guarantee the same wording on every run. The reply is a draft for the care team.

## What you set up

- A model for the Reasoning tier.
- The company's customer care system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that sends a reply.
- A knowledge source that holds the company's help articles. For the invented company these are in [`../../policy-library/help-articles.md`](../../policy-library/help-articles.md). The invented retailer also serves the same text through its care system, for trying the agent: with the five operations attached, the agent can be tried before a knowledge source is indexed.
- For the desk route, the customer care desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the customer care system from its OpenAPI address. For the invented retailer, that is the document at `/care/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Knowledge, connect a source that holds the help articles.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the five operations named in [`agent.yaml`](agent.yaml). Attach nothing else. In Knowledge, attach the help articles.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a reply saves a draft.
8. To start it when a ticket arrives, subscribe the platform to the retailer's `customer-ticket` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the customer tickets section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `CT-2611-004`: when a refund arrives. Article `HA-05`: within 5 working days of the approval.
- `CT-2611-002`: whether an order placed twenty minutes ago can be changed. Article `HA-03`: for 60 minutes, or until the status is packed.
- `CT-2611-017`: next-day delivery. Article `HA-01`: USD 7.95, ordered before 14:00.
- `CT-2611-014` (a price match), `CT-2611-015` (a business account) and `CT-2611-016` (a nut allergy): no article answers them. Each goes to a colleague.
- Ask it to send a reply or to promise a refund. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A member of the care team reads and sends every reply. A ticket no article answers goes to a colleague, and any refund, replacement or exception is the care team's decision.
