# Colleague Assistant

The one assistant every colleague uses. It holds no documents and no systems of its own. It passes each request to the one specialist built for it, gives that specialist's answer back unchanged, and says which specialist answered.

| | |
|---|---|
| Type and form | Multi-agent, manager agent |
| What starts it | A colleague's request |
| How people meet it | Chat |
| Reads from | Nothing of its own. It calls six specialist agents |
| Changes | Nothing. It has no tool that acts |
| State | Built and tested on a development cluster with three of its six specialists. It called the right specialist every time |

## The six specialists

| Specialist | Folder | For |
|---|---|---|
| Staff Policy Q&A | [`../staff-policy-qa/`](../staff-policy-qa/README.md) | leave, sickness, hours, shift swaps, expenses, uniform, training, raising a concern |
| Store Procedures Q&A | [`../store-procedures-qa/`](../store-procedures-qa/README.md) | opening checks, temperature checks, remakes, click and collect, deliveries, cash, incidents, closing |
| Menu and Allergen Q&A | [`../menu-and-allergen-qa/`](../menu-and-allergen-qa/README.md) | a dish, its allergens, the menu |
| Food Safety Record Check | [`../food-safety-record-check/`](../food-safety-record-check/README.md) | a restaurant's records for a period against the food safety plan |
| Guest Feedback Analysis | [`../guest-feedback-analysis/`](../guest-feedback-analysis/README.md) | a period's guest comments, grouped into themes |
| Invoice Matching | [`../invoice-matching/`](../invoice-matching/README.md) | a supplier invoice against its order and goods received |

In [`agent.yaml`](agent.yaml) each specialist is a need of the kind `agent`. That kind is added by this pack: the four kinds in the folder format do not cover a manager that calls other agents. The id of such a need is the folder id of the specialist.

## What it does

- Applies one rule first: a question about leave, sickness, rosters, shift swaps, expenses, uniform, training or pay goes to Staff Policy Q&A, even when it mentions food, a kitchen or an illness. Food Safety Record Check reads records and answers no policy question.
- Calls the one specialist whose line covers the request, with the request word for word.
- Gives the answer back whole, with its figures, rows, tables, clause numbers and its last line, under one short line that says which specialist answered.
- Calls two specialists for a request with two parts, and gives each answer under the name of the specialist.
- Says so in one sentence when no specialist covers the request, and sends the colleague to their own manager.

## What it does not do

- Hold or read a document or a record itself.
- Decide anything for a person or change anything in any system.
- Change a specialist's answer, or work out an answer from two replies.
- Guarantee the routing. Choosing a specialist is an instruction to the model. Run the tests on your own model, and read which specialist was called as well as what was said.

## What you set up

- A model for the Reasoning tier.
- The six specialists, each built from its own folder and published on the same platform. The assistant is only as useful as they are: if one is missing, its requests are answered with its name and that it is not connected.

## Build it

Built this way on a development cluster on 24 November 2026, with three of the six specialists attached.

1. Build and publish the six specialists first, each from its own folder.
2. In Katonic Studio, create a new agent of the kind that manages other agents.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. Attach the six specialists as the agents it can call. Attach no tools and no knowledge source.
6. On the Test tab, run test 1 with no specialist attached and "Test the prompt without tools" ticked. Attach the six and run the others.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- Built with three of the six specialists attached: Invoice Matching, Food Safety Record Check and Guest Feedback Analysis. The three question-and-answer specialists were not published on that cluster, so they could not be attached.
- The three tests that could run pass three runs in a row. The five that need a missing specialist could not pass.
- For a request whose specialist was missing, the assistant called nobody, named the missing specialist and gave no answer of its own.
- In the Work Room the replies were delivered and the page showed that a specialist was called. It did not show which one: the name is in the reply's first line.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

With the six specialists attached and the invented company's documents and retailer behind them:

- How many days of annual leave in the first year? Staff Policy Q&A answers: 21 working days, HR-01 clause 1.1.
- I work in a kitchen. Who approves leave in the two busiest trading weeks? It must go to Staff Policy Q&A, not to Food Safety Record Check. The area manager, HR-01 clause 1.4.
- Which allergens are in the hazelnut cream doughnut? Menu and Allergen Q&A, row C-03.
- A till out by USD 35 and the carry-over of leave in one message. Two specialists, two answers.
- Set the price of the large pizza. No specialist covers it. It must say so and name the colleague's own manager.

Everyone and everything in the invented company is invented.

## Where it stops for a person

It takes no action and decides nothing. Each specialist stops for a person as its own folder says. A request no specialist covers goes to the colleague's own manager.
