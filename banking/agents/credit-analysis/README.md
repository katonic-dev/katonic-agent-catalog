# Credit Analysis

Spreads an application's financial figures, works out the ratios the bank's lending policy names, compares each with its limit, and drafts the credit memo with the source of every figure.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the Lending desk or from the bank's lending system, naming an application |
| How people meet it | An application: the Lending desk |
| Reads from | The bank's lending system (the application, its documents and the lending policy) and the bank's customer records (the customer's existing exposure) |
| Changes | Saves a draft credit memo. The draft does not decide the application |
| State | Built on a development cluster on 25 November 2026. All six tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the application, the lending policy for its product and the documents that hold figures.
- Works out every ratio the policy names, using the policy's own definition, shows the working with the actual numbers, and compares it with the limit: in order, or outside policy.
- Says which figure is missing when a ratio cannot be worked out, gives no value for it, and estimates nothing.
- Shows both values, and chooses neither, where two sources differ.
- For a business loan, adds the debt service cover with the new loan's own debt service, as its own calculation and not as a policy test.
- Reads the customer's existing exposure to the bank and states it apart from the ratios.
- Saves the memo with the source of every figure, and says it was saved only if the system's reply says so.
- Ends with one proposal line: refer to the credit officer, with the reason.

## What it does not do

- Approve or decline an application, or recommend either. The recommendation it saves is always to refer. The credit officer decides.
- Price a loan, set a limit or a rate, or call a customer sound or weak.
- Estimate a missing figure, or use a definition that the policy does not give.
- Write to the applicant.
- Guarantee the same figures on every run. The memo is a draft for the credit officer, and its arithmetic should be checked. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's lending system and customer records, each connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Lending desk](../../desks/lending/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft review. For the lending officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Credit analysis" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `LAP-8003`: a small business loan with three years of financial statements. Current ratio 1.43 (limit at least 1.20), debt to equity 0.26 (at most 2.50), debt service cover 3.31 (at least 1.25), and 2.39 with the new loan's debt service of about 29,892 a year. All three ratios are within policy. Revenue grew 6.7 percent then 8.3 percent. EBITDA margin is 15.7 percent.
- `LAP-8001`: a salaried personal loan. Debt to income is (450 + 576.59) / 5,200 = 0.197 against a limit of at most 0.40.
- `LAP-8002`: its financial statements give the latest year only, with no current assets, current liabilities, debt or interest. The three ratios cannot be worked out, and the agent must say so and estimate nothing.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The credit officer reads the memo and decides. A ratio outside policy, or one that could not be worked out, is for the credit officer to weigh.
