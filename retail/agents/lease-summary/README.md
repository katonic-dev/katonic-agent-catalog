# Lease Summary

Summarises a store or restaurant lease: the term, the rent, the review and break dates, and who repairs what, each with the clause it rests on. The property team checks the summary against the lease.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A colleague's request that names a lease or a site |
| How people meet it | Chat |
| Reads from | The company's property records: each lease with its full text in numbered clauses |
| Changes | Saves its summary as a draft. The draft changes nothing in the lease |
| State | Written. Not yet built on a platform |

## What it does

- Reads the whole lease, clause by clause, and gives the number of the clause behind every point.
- Sets out the term, the rent, each rent review date and how the rent is reviewed, each break option with who may break and the months of notice, and who repairs what.
- Works out the last day for a break notice, which a lease does not state: the break date less the months of notice. It says that it worked the day out.
- Lists first every date that falls in the next 90 days, with the number of days, counted from the date the records give as today.
- Says so plainly when a lease has no break clause, when only the landlord may break, and when the rent cannot go down on a review.
- Saves the summary as a draft and says so only when the records say it was applied.
- Ends on one fixed line: "This is a summary, not advice. The property team checks it against the lease."

## What it does not do

- Give legal advice, or say whether to break, renew, assign or sign a lease.
- Serve a notice, write to a landlord or change a lease.
- Fill a gap. Where the lease is silent, it says so.
- Guarantee that a summary is complete. It is a draft for the property team. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The company's property records, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml): list the leases, read one lease with its text, and save a summary as a draft.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the property system from its OpenAPI address. For the invented retailer, that is the document at `/property/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a summary saves a draft.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the leases section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `LS-2001` (store S-101): the tenant may break on 2027-07-01 with six months' notice, so the notice is due by 2027-01-01, 38 days away.
- `LS-2003` (store S-104): the rent review is upward only (clause 4.2).
- `LS-2005` (store S-108): no break clause, and its clauses are numbered differently from the others.
- `LS-2007` (restaurant R-031): the landlord repairs the roof (clause 5.1) and the tenant everything else (clause 5.2).
- `LS-2009` (restaurant R-058): only the landlord can break.
- Ask whether the company should break `LS-2001`. It must refuse to advise.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The property team checks every summary against the lease. Whether to break, renew, assign or sign is decided by the property team and the company's lawyers.
