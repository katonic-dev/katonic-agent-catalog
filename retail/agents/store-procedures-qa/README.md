# Store Procedures Q&A

Answers a store or restaurant colleague's question from the company's own Store Procedures Manual, and cites the procedure and clause for each rule.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A colleague's question |
| How people meet it | An application: the store website. It also works in a chat |
| Reads from | A knowledge source that holds the Store Procedures Manual |
| Changes | Nothing. It has no tool that acts |
| State | Written. Not yet built on a platform |

## What it does

- Answers a question about opening checks, temperature checks, order remakes, click and collect, deliveries, cash, incidents and closing from the manual, with the procedure number, its version and the clause.
- Ends every answer with a line that starts "Source:".
- Says so plainly when the manual is silent, when it covers only part of the question, and when the answer is in another document: the Food Safety Plan for temperature limits, the Allergen Matrix for allergens, the Staff Handbook for pay, leave and rosters.
- Leaves a refund, an exception or one guest's case to the restaurant manager.

## What it does not do

- Take any action. It does not record a remake, a till difference or an incident.
- Guarantee the referral. Leaving decisions to the restaurant manager is an instruction to the model, not a control. Run the refund test on your own model before you publish.
- Read the point of sale, the temperature log or the roster. Attach the manual only.
- Say that food is safe or that a guest may be served.
- Answer from general knowledge when the manual is silent.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- One knowledge source that holds the manual: [`../../policy-library/store-procedures-manual.md`](../../policy-library/store-procedures-manual.md) for the invented company, or your own. Keep the allergen matrix, the food safety plan and the handbook out of this source, so that the agent can say a question belongs to another document.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Katonic Studio, create a new agent of the kind that answers from your documents.
2. In Identity, give it a name and a description, and choose the owner team.
3. In Behavior, write the instructions yourself and paste [`instructions.md`](instructions.md) word for word.
4. Set the model tier to Reasoning.
5. Attach no tools.
6. In Knowledge, attach the source that holds the manual.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). For the two tests with nothing connected, detach the source and tick "Test the prompt without tools".
8. To put it on a store website, publish it and call it through the platform's public API from the page. The key and the agent id are settings of the site, never part of a file in this repository.

## Test results

Not yet built on a platform. No test has been run.

## Try it

The manual of the invented company is in [`../../policy-library/`](../../policy-library/README.md). Ask:

- A pizza stood on the hot rack for 20 minutes. SP-07 clause 7.1, shift manager approves (7.2), reason code R3 (7.3).
- What is the hot holding limit? The Food Safety Plan sets it, so it gives no number (SP-04 clause 4.4).
- Does the falafel wrap contain sesame? It must say the Allergen Matrix answers that.
- Approve a refund. It must refuse and name the restaurant manager (SP-07 clause 7.6).

Everyone and everything in the invented company is invented.

## Where it stops for a person

It takes no action, so there is nothing to approve. A situation the manual does not cover, a refund or compensation, and any limit set by the Food Safety Plan go to the restaurant manager or to the document that sets them.
