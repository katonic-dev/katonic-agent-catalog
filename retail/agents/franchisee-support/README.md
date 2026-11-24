# Franchisee Support

Answers a franchisee's question from the company's Franchise Operations Manual and its Brand Standards, and cites the section or the standard for each rule. Anything about the franchise agreement itself goes to the franchise team.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A franchisee's question |
| How people meet it | An application: the franchisee website. It also works in a chat |
| Reads from | A knowledge source that holds the Franchise Operations Manual and the Brand Standards |
| Changes | Nothing. It has no tool that acts |
| State | Written. Not yet built on a platform |

## What it does

- Answers a question about fees and reporting dates, brand standards audits, menu and pricing freedom, local marketing, equipment and refits, and supply through approved suppliers, with the section of the manual.
- Answers a question about what a brand standard requires from the Brand Standards, with the standard's number.
- Gives the whole rule: the figure, the deadline, who must be asked or told, and how long an approval takes.
- Ends every answer with a line that starts "Source:".
- Says so plainly when the two documents are silent, and sends the question to the franchise team.
- Sends anything about the franchise agreement itself to the franchise team, with the address the manual gives: renewal, the territory, a sale or a transfer, ending the agreement, a change to the fee rates, a dispute, and what follows a late payment.
- Answers the part of a question the manual covers, and says which part it does not.

## What it does not do

- Explain or guess what a franchise agreement says.
- Approve a local menu item, own artwork, a local promotion, a local supplier or refit plans. The manual gives each to a team.
- Take any action. It sends no report and no request.
- Read sales, audit results or invoices. Attach the two documents only.
- Give legal or financial advice.
- Guarantee the referral. Sending an agreement question to the franchise team is an instruction to the model, not a control. Run the agreement tests on your own model before you publish.
- Answer from general knowledge of franchising when the documents are silent.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- One knowledge source that holds the two documents: [`../../policy-library/franchise-operations-manual-v3.0.md`](../../policy-library/franchise-operations-manual-v3.0.md) and [`../../policy-library/brand-standards-v2.0.md`](../../policy-library/brand-standards-v2.0.md) for the invented company, or your own. Keep the franchise agreement out of this source, and keep the food safety plan, the procedures manual, the allergen matrix and the staff handbook out of it too, so that the agent can say a question belongs elsewhere.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Knowledge, connect a source by file upload and add the two documents.
2. In Katonic Studio, create a new agent of the kind that answers from your documents.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, write the instructions yourself and paste [`instructions.md`](instructions.md) word for word.
5. Set the model tier to Reasoning.
6. Attach no tools.
7. In Knowledge, attach the source that holds the two documents.
8. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). For the test with nothing connected, detach the source and tick "Test the prompt without tools".
9. To put it on a franchisee website, publish it and call it through the platform's public API from the page. The key and the agent id are settings of the site, never part of a file in this repository.

## Test results

Not yet built on a platform. No test has been run.

## Try it

The two documents of the invented company are in [`../../policy-library/`](../../policy-library/README.md). The invented retailer's franchise system holds seventeen questions franchisees have asked, and the franchisees and their questions section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md) gives the section for each. Ask:

- By when do I send the weekly sales report? By 12:00 on the Tuesday after the week ends (section 1.2).
- We scored 19 on the audit. Below the pass score of 20: an action plan within 14 days and a second audit within 60 days (sections 2.2 and 2.3).
- My supplier did not deliver. Milk, fresh produce and ice from a local shop for up to 3 days, and the supply team is told within 24 hours (section 6.3).
- How long do I have to take the posters down? Within 24 hours (Brand Standards, standard 5.2).
- Can I close early on a public holiday? The documents are silent, so it goes to the franchise team (section 7.4).
- How do I renew my agreement? It must send this to the franchise team (section 7.1) and guess nothing.
- Approve my new local dish. It must refuse and name the menu team (section 3.2).

Everyone and everything in the invented company is invented.

## Where it stops for a person

It takes no action, so there is nothing to approve. Anything about the franchise agreement, and anything the two documents do not answer, goes to the franchise team. An approval the manual gives to a team is that team's.
