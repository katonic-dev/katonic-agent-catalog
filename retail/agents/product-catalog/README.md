# Product Catalog

Drafts a new product's description and image tags to the style guide, from the supplier's specification and the photo studio's image descriptions as text. It has seen no image and says so. A content lead publishes every description.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new product arriving in the catalogue system. A person can also name a product |
| How people meet it | An application: the product data desk. It also works in a chat |
| Reads from | The company's catalogue system: new products with their image descriptions as text, the supplier's specification, and the style guide |
| Changes | Saves a description as a draft on the listing. The draft publishes nothing |
| State | Written. Not yet built on a platform |

## What it does

- Reads the style guide first, and writes to its rules: the length, the words that are not used, the tags.
- Takes every fact from the supplier's specification: the net quantity, the pack size, the country of origin.
- Copies the allergen statement word for word from the specification.
- Writes three to six image tags, each naming something the image descriptions say is in the picture.
- Ends the description of an age-restricted line with the sentence the style guide gives.
- Lists each place where an image description and the specification disagree, and uses the specification.
- Says plainly that it has seen no image.
- Saves the description as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "I have seen no image. A content lead reads and publishes every description."

## What it does not do

- Publish a listing.
- Work out an allergen from the ingredients, the name or a picture.
- Make a health claim, or a claim the specification does not make.
- Describe what is in a picture beyond what the image description says.
- Write a description for a product that already has a published one.

## What you set up

- A model for the Reasoning tier.
- The company's catalogue system, connected as an imported API, with the 4 operations listed for it in [`agent.yaml`](agent.yaml).
- For the desk route, the product data desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the catalogue system from its OpenAPI address, one system at a time. For the invented retailer, that is the document at `/catalogue/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: the operation that changes a record (`publish_product_description`) stays out of this agent on purpose.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To start it when a product arrives, add a webhook trigger on the retailer's `new-product` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the new products and descriptions section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md), and the rules in [`../../policy-library/product-style-guide.md`](../../policy-library/product-style-guide.md):

- `AG-4411` Oat granola: 500 g, pack size 1, "Contains: oats, almonds (nuts)", Meridia.
- `FZ-5606` Frozen berry mix: the pack in the image description reads 450 g and the specification gives 500 g. It uses 500 g and lists the difference.
- `DR-5906` White wine: the description ends with "For adults aged 18 or over."
- `AG-4412` Peanut butter: it already has a published description, so nothing is drafted.
- Ask it to publish, or to call the granola healthy. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A content lead reads every description, asks the supplier about any difference, and publishes.
