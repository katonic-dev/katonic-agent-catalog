# Claim Pack Completeness

Compares a claim's documents with the checklist for its claim type and lists what is missing, what cannot be read and what does not show what it must. A claims handler decides what is asked of the customer.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | Documents arriving on a claim |
| How people meet it | An application: the Claims intake desk |
| Reads from | The insurer's claims system: the claim with every document and the checklist for its claim type |
| Changes | Saves the pack check as a draft. The draft contacts nobody and changes no status |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the claim with every document and the checklist for its claim type.
- Goes through the checklist in its own order and writes one row for every document type on it, each with a mark: received, missing, cannot be read, or does not show what it must.
- Reads each document that is in the file against what the checklist says it must show: a signature and a date, a report number, the registration of the insured vehicle, the insured home.
- Names a document that is in the file and not on the checklist in the summary, and gives it no row.
- Notes for the adjuster where two documents disagree on a fact, with both ids and both values, and chooses neither. That is no fault of the pack.
- Saves the pack check as a draft, one item for every checklist document, and says it was saved only if the system's reply says so.
- Ends with one proposal line: the pack is complete, ask the customer for the documents named, or refer to a handler.

## What it does not do

- Write to, email or call the customer. A person does.
- Add a document to the checklist from what is usual for such a claim. A police report is missing only where the checklist for the claim type asks for one.
- Say which of two documents that disagree is right.
- Accept cover, decline a claim, or read the loss against the policy wording.
- Guess what a document that cannot be read might show.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft pack check. For the claims handler. Not issued.", a six-column table, and a last line that starts "Proposal:".
4. The eight tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-4001`: four of four received. The pack is complete. No police report is on the checklist for this claim type, so none is missing.
- `CLM-4002`: the plumber's report is missing and the photographs, `DOC-4002-3`, cannot be read. Ask the customer.
- `CLM-4004`: four of four received. The valuation, `DOC-4004-5`, is in the file and is not a checklist item.
- `CLM-4005`: the police report is missing. The repair estimate, `DOC-4005-4`, names MR-7702-B and the insured vehicle is MR-7720-B. Ask the customer.
- `CLM-4007`: the list of contents damaged is missing. The claim form and the fire service report disagree on where the fire started: noted for the adjuster, and no fault of the pack.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The claims handler reads the pack check and decides what is asked of the customer. Where two documents disagree, the adjuster settles it.
