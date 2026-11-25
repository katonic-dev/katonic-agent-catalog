# Management Reporting

Answers a question on the bank's finance warehouse in plain language, shows the query it ran, and drafts the commentary. It only reads.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A question on the finance warehouse |
| How people meet it | Chat |
| Reads from | The bank's finance warehouse: a general ledger and management accounts for 24 months |
| Changes | Nothing. It saves a draft commentary, which publishes nothing |
| State | Built on a development cluster on 25 November 2026. All seven tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the warehouse's tables and column descriptions before it writes a query, and fixes the meaning of the period and of each term.
- Runs one read-only query, lets the query do the sums, and answers with the figures exactly as returned.
- Shows the query it ran, and a table of the rows that answer the question.
- Drafts a short commentary that uses only figures from the result, and saves it as a draft.
- Says plainly when the warehouse does not hold the answer, names what is missing, and gives no estimate.

## What it does not do

- Change, add or remove anything in the warehouse. It only reads.
- Invent a figure, a column or a reason. The warehouse holds amounts and accounts, not explanations.
- Publish the commentary or send it to anyone.
- Answer a question about headcount, customers, churn or any period the warehouse does not hold.
- Guarantee the same wording on every run. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's finance warehouse, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The seven tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. The warehouse holds 2024-11 to 2026-10. Reset the bank before each try, because each one saves a draft:

- Operating cost last month against budget: 2,743,079 against 2,666,664, which is 76,415 over, 2.87 percent. Counting every expense account gives a different, wrong number.
- The cost centre furthest over budget this year: CC300 Technology, 338,325 over. CC600 Marketing is second in amount and the largest in percent.
- Net interest income by month for the last six months: 2026-05 to 2026-10, from 1,348,295 to 1,388,881.
- Average headcount in Technology last month: the warehouse cannot answer. No table holds headcount.
- Operating cost in 2023: the warehouse cannot answer. It starts in 2024-11.
- Ask it to change a figure. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A person in finance reads the answer and the draft commentary and decides whether to use them. A question the warehouse cannot answer goes to whoever holds that data. Figures are changed through the bank's own process, not by the agent.
