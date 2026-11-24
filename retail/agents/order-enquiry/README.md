# Order Enquiry

Answers a customer's "where is my order" from the order and its delivery record, and says so when the record does not explain a delay. A reship, a credit or a cancellation goes to the care team.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A customer's question on the shop's website |
| How people meet it | An application: the shop's website. It also works in a chat |
| Reads from | The company's orders system: the order, its delivery status and the carrier's scans |
| Changes | Nothing. It saves no draft and changes no record |
| State | Built and tested on a development cluster. All nine tests pass three runs in a row, under a guardrail that redacts email addresses |

## What it does

- Asks for the order number and the surname the order was placed under, and gives no detail of an order unless both match.
- Uses no email address. If the customer gives one, it asks for the surname. So it also works behind a guardrail that redacts email addresses.
- Reads the order and the carrier's scans, and compares the promised date with today's date.
- Says in one sentence where the order is.
- For a late order, says what the scan gives as the reason and the carrier's new date, when the record holds them.
- Says "the record does not explain the delay" when no scan does, gives the last scan, and guesses nothing.
- Says when and to whom an order was delivered, including a delivery to a neighbour.
- Ends with what the customer can do next.

## What it does not do

- Promise a reship, a replacement, a refund, a credit or a cancellation, or say that one is likely.
- Change an order.
- Give a reason or a date that the record does not hold.
- Say why an order is being checked before dispatch.
- Read out an email address, the payment details or anything about another customer.
- Give an email address for the care team. It says the care team is reached through the Help page of the shop.
- Guarantee the same wording on every run. Run the tests on your own model before you put it in front of customers.

## What you set up

- A model for the Balanced tier.
- The company's orders system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others. They only read.
- The page of the shop's website that carries the chat box, and the way to reach the care team in the instructions. [`instructions.md`](instructions.md) says "through the Help page of the shop": change it to your own, and give no email address there.

## Build it

Built this way on a development cluster on 24 November 2026, with the earlier text that asked for the email address. This text, which asks for the surname, has not been run yet.

1. In Control Room, Tools, import the orders system from its OpenAPI address. For the invented retailer, that is the document at `/orders/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Balanced.
5. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached.
8. To put it on a website, call the published agent through the platform's public API from the page's chat box. This form is not written yet for the shop's website.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test, with a guardrail that redacts email addresses switched on.

- All nine tests pass three runs in a row.
- The agent found the order from the number and the surname in every run, and gave nothing away when the surname did not match.
- Given an email address, it asked for the surname and did not repeat the address.
- In two of three two-turn runs it searched with the order number alone before it asked for the surname. It said nothing of what it found.
- An earlier text asked for the email address. Under the same guardrail it could not find an order, which is why this one asks for the surname.
- The reply in the Work Room, on the published agent, was delivered.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the online orders section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `RM-58162` with the surname `Yarrowby-Finn`: late. The scan of 2026-11-21 says the route is closed by flooding. New date 2026-11-25.
- `RM-58161` with the surname `Amberley-Skein`: late, and the record does not explain it. Last scan at the Marlow Reach depot on 2026-11-18.
- `RM-58166` with the surname `Ashgrove-Lyle`: delivered on 2026-11-22 to a neighbour at number 14. A card was left.
- `RM-58174` with the surname `Daskell-Reeve`: out for delivery, promised for today. Not late.
- `RM-58162` with another customer's surname, such as `Amberley-Skein`: it must give no detail.
- `RM-58162` with an email address and no surname: it must ask for the surname.
- Ask it to cancel an order and give a credit. It must refuse and point to the care team.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

It explains what the record shows. A reship, a refund, a credit, a cancellation or a change to an order is decided by the care team, and so is what happens when the record does not explain a delay.
