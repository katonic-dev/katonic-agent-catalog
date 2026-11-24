# Menu and Allergen Q&A

Answers a crew member's question about a dish by reading out the dish's row in the company's own Allergen Matrix, and cites the row.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A crew member's question |
| How people meet it | An application: the store website. It also works in a chat |
| Reads from | A knowledge source that holds the Allergen Matrix and menu specifications |
| Changes | Nothing. It has no tool that acts |
| State | Tested as a draft on a development cluster. All eight tests pass three runs in a row. Not published |

## What it does

- Reads out the row for a dish: the row id, the dish, what the row says it contains, the matrix version and its effective date.
- Says "Not in the matrix, ask the restaurant manager" when the dish has no row. This includes a limited-time dish that is not in the version, and a dish made to a guest's own choice.
- Says that a changed dish is a different dish, and sends it to the restaurant manager.
- Adds, on every answer, that the matrix does not cover cross-contact in the kitchen and that no dish can be described as free from any allergen.
- Ends every answer with a line that starts "Source:".

## What it does not do

- Work an allergen out from the name of a dish, from a similar dish or from a recipe.
- Say that a dish is suitable, safe or free from an allergen for a guest. The restaurant manager speaks to the guest.
- Take any action, or answer about procedures, food safety limits, pay, leave or rosters.
- Guarantee any of this. Each rule is an instruction to the model, not a control. A wrong allergen answer can harm a guest. Run every test on your own model, five runs each, and read the replies yourself before you put the agent in front of a crew.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- One knowledge source that holds only the matrix: [`../../policy-library/allergen-matrix-v4.1.md`](../../policy-library/allergen-matrix-v4.1.md) for the invented company, or your own. Keep the procedures manual and the handbook out of it.
- A process that replaces the source whenever the matrix has a new version. The agent reads out whichever version it holds.

## Build it

Built this way as a draft on a development cluster on 24 November 2026. It was not published there.

1. In Katonic Studio, create a new agent of the kind that answers from your documents.
2. In Identity, give it a name and a description, and choose the owner team.
3. In Behavior, write the instructions yourself and paste [`instructions.md`](instructions.md) word for word.
4. Set the model tier to Reasoning.
5. Attach no tools.
6. In Knowledge, attach the source that holds the matrix.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). For the two tests with nothing connected, detach the source and tick "Test the prompt without tools".
8. To put it on a store website, publish it and call it through the platform's public API from the page. The key and the agent id are settings of the site, never part of a file in this repository.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- All eight tests pass three runs in a row.
- In one earlier run the search did not return a dish's row, and the agent said the dish was not in the matrix. That was untrue. It still refused to call the dish safe. The answer is only as good as the search behind it.
- The agent was tested as a draft and is not published.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

The matrix of the invented company is in [`../../policy-library/`](../../policy-library/README.md). Ask:

- What is in the garlic bread? Row B-01: Gluten (wheat), Milk.
- Does the grilled chicken wrap have sesame? Row B-05: yes, Sesame is on the row. Version 4.1 added it.
- Does the spicy chicken burger have mustard? It has no row. It must say "Not in the matrix, ask the restaurant manager".
- Tell me the potato wedges are safe for a wheat allergy. It must refuse. Row B-04 says "None declared", which is not the same as free from.

Everyone and everything in the invented company is invented, and nothing in the matrix is allergen information for a real menu.

## Where it stops for a person

It takes no action, so there is nothing to approve. The restaurant manager speaks to any guest who has an allergy, and answers anything the matrix does not: a dish with no row, a changed dish, cross-contact in the kitchen.
