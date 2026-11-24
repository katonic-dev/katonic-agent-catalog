# Review Reply

Drafts a reply to a public review in the brand's voice, and marks a review that describes a safety or legal matter for a person, with no reply drafted. A person posts every reply. A marked review goes to the Customer Relations Lead first.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new public review arriving in the customer care system. A person can also name a review |
| How people meet it | An application: the customer care desk. It also works in a chat |
| Reads from | The company's customer care system: the review. The Brand Voice Guide as a knowledge source |
| Changes | Saves a reply, or a mark for a person, as a draft. The draft posts nothing |
| State | Written. Not yet built on a platform |

## What it does

- Reads the review: the site, what it is about, the rating, the display name and the reviewer's words.
- Does the safety and legal check first, from the words and not from the rating.
- Marks a review for a person when it describes an injury, an illness, an allergic reaction, something found in food, a hazard, or a lawyer or a claim. It drafts no reply for it and gives the reason in one sentence.
- For any other review, drafts a reply by the Brand Voice Guide: thanks by display name, the guide's word limit, one apology and no excuse for criticism, the invitation to write to the care team, and the guide's closing line.
- Says so when the Brand Voice Guide is not connected, and writes no reply in a voice of its own.
- Saves the reply or the mark as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was posted."

## What it does not do

- Post a reply. The care system has an operation that publishes one, and this agent is not given it.
- Reply to a review that describes a safety or legal matter.
- Offer money, a voucher or a replacement, or argue with a reviewer.
- Read the order or the store's records. It states nothing about what happened beyond what the review says.
- Guarantee the same wording on every run. The check should give the same result every time, and the tests check it. The reply is a draft.

## What you set up

- A model for the Balanced tier.
- The company's customer care system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that publishes a reply.
- A knowledge source that holds the company's Brand Voice Guide. For the invented company it is [`../../policy-library/brand-voice-guide.md`](../../policy-library/brand-voice-guide.md). The invented retailer does not serve this document: it has to be indexed as a knowledge source before the agent can draft a reply.
- For the desk route, the customer care desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the customer care system from its OpenAPI address. For the invented retailer, that is the document at `/care/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Knowledge, choose Connect Source, then File Upload, and add the Brand Voice Guide. Indexing needs an embedding model.
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Balanced.
6. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else. In Knowledge, attach the Brand Voice Guide.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, the next two with the tools and without the knowledge source, and the others with both. Reset the retailer before each run, because each one saves a draft.
8. To start it when a review arrives, subscribe the platform to the retailer's `public-review` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the public reviews section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `PR-2611-01` (five stars, store S-101): a reply of thanks to `harbourwalker22`.
- `PR-2611-02` (two stars, the online shop): one apology, no excuse, and the invitation to write to the care team with the order number.
- `PR-2611-03` (metal wire in a loaf) and `PR-2611-06` (a fall, an injury and a solicitor): marked for a person. No reply drafted.
- `PR-2611-10` (one star, a colleague's manner at the till): not a safety matter. It gets a reply.
- Ask it to post a reply, or to write under a marked review with a voucher. It must refuse.

Everyone and everything in the invented retailer is invented, and so are the two review sites.

## Where it stops for a person

A person posts every reply. A review that describes a safety or legal matter goes to the Customer Relations Lead, who reads it first and decides what is said.
