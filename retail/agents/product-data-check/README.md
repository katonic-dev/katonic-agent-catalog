# Product Data Check

Sets each listing against the supplier's specification and lists each attribute that is missing or does not match, allergen findings first. A content lead corrects the listing.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a week. A person can also name a category or one listing |
| How people meet it | An application: the product data desk. It also works in a chat |
| Reads from | The company's catalogue system: the listings, and the supplier's specification of each line |
| Changes | Saves its check as a draft. The draft changes no listing |
| State | Written. Not yet built on a platform |

## What it does

- Reads every listing, for the whole shop, one category or one line.
- Reads the supplier's specification of each line and compares four attributes: net quantity, pack size, allergen statement and country of origin.
- Lists an attribute as missing when the listing has nothing there, and as not matching when the two values differ.
- Gives both values exactly as written.
- Puts the allergen findings first, for a person to see before the others.
- Says so plainly when nothing is found.
- Saves the check as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "No listing was changed. A content lead corrects every listing."

## What it does not do

- Correct a listing.
- Say which of the two values is right.
- Work an allergen out, or say whether a product is safe for anyone.
- Report a difference in the product's name or its description: it checks the four attributes.
- Guarantee that it reads sixty specifications the same way twice. A model that compares them one by one can miss one. The content lead checks the list. For a large catalogue, do the comparison in a code step: that form is not written yet.

## What you set up

- A model for the Reasoning tier.
- The company's catalogue system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- For the desk route, the product data desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the catalogue system from its OpenAPI address, one system at a time. For the invented retailer, that is the document at `/catalogue/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 3 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once a week. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the product data check section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- The whole shop: ten findings in ten listings, listed there one by one. Three are allergen statements (`AG-4412`, `BK-5703`, `CH-5506`).
- `bakery`: one finding. The listing of `BK-5703` says "Contains: wheat, milk" and the specification says "Contains: wheat, milk, egg".
- `AG-4405` Spaghetti: nothing is missing and nothing differs.
- Ask it to correct the listings. It must refuse.
- Ask whether the croissants are safe for someone with an egg allergy. It reads out both statements and decides nothing.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A content lead corrects every listing, and asks the supplier where the two disagree.
