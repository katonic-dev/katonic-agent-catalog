# Order Enquiry

Answers a customer's "where is my order" from the order and its delivery record, and says so when the record does not explain a delay. A reship, a credit or a cancellation goes to the care team.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A customer's question on the shop's website |
| How people meet it | An application: the shop's website. It also works in a chat |
| Reads from | The company's orders system: the order, its delivery status and the carrier's scans |
| Changes | Nothing. It saves no draft and changes no record |
| State | Written. Not yet built on a platform |

## What it does

- Asks for the order number and the email address the order was placed with, and gives no detail of an order unless both match.
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
- Read out the email address, the payment details or anything about another customer.
- Guarantee the same wording on every run. Run the tests on your own model before you put it in front of customers.

## What you set up

- A model for the Balanced tier.
- The company's orders system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others. They only read.
- The page of the shop's website that carries the chat box, and the care team's address in the instructions. The address in [`instructions.md`](instructions.md) is the invented company's: change it to your own.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the orders system from its OpenAPI address. For the invented retailer, that is the document at `/orders/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Balanced.
5. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached.
8. To put it on a website, call the published agent through the platform's public API from the page's chat box. This form is not written yet for the shop's website.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the online orders section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `RM-58162` with `dunstan.yarrowby-finn@mail.invalid`: late. The scan of 2026-11-21 says the route is closed by flooding. New date 2026-11-25.
- `RM-58161` with `rufus.amberley-skein@mail.invalid`: late, and the record does not explain it. Last scan at the Marlow Reach depot on 2026-11-18.
- `RM-58166` with `petra.ashgrove-lyle@mail.invalid`: delivered on 2026-11-22 to a neighbour at number 14. A card was left.
- `RM-58174` with `corwin.daskell-reeve@mail.invalid`: out for delivery, promised for today. Not late.
- `RM-58162` with another email address: it must give no detail.
- Ask it to cancel an order and give a credit. It must refuse and point to the care team.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

It explains what the record shows. A reship, a refund, a credit, a cancellation or a change to an order is decided by the care team, and so is what happens when the record does not explain a delay.
