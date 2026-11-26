# Claims Processing

Sorts a new claim by the sorting rules of the insurer's claims handling guide so that it reaches the right team, with the rule and the reason. A claims handler decides.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A claim being registered |
| How people meet it | An application: the Claims intake desk |
| Reads from | The insurer's claims system: the claim with its whole file, and the claims handling guide |
| Changes | Saves how the claim is sorted as a draft. The draft assigns the claim to nobody and changes no status |
| State | Built on a development cluster on 26 November 2026. All eight tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the claim with its whole file: the documents, the handlers' notes, the estimate, what the system says about cover on the date of the loss, and the checklist of documents.
- Reads the sorting rules from the claims handling guide every time, and quotes each rule by its id.
- Applies the rules in order and stops at the first that applies. It writes one row for each rule down to and including that one, each marked applies or does not apply, with the fact from the file and its source. The rules after it get no row.
- Where a rule asks for a complete pack, reads the checklist and reads each document against what it must show.
- Takes the track, the team and the severity from the rule that applies, in the guide's words.
- Says when a point is for the coverage check and not for sorting, such as who was driving.
- Saves the sorting as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: sort as a track, a team and a severity under a rule, or refer to a handler.

## What it does not do

- Assign a claim to a person or a team. The claims handler does.
- Accept cover or decline a claim. A policy that was not in force is a fact a sorting rule uses, and no decision.
- Read the loss against the policy wording. That is the coverage check.
- Sort from a rule as it remembers it. It reads the guide in every request.
- Guess. Where the file does not settle which rule applies, it refers the claim to a handler.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft sorting. For the claims handler. Not issued.", a six-column table, and a last line that starts "Proposal:".
4. The eight tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-4001`: an estimate of USD 2,350.00 and a complete pack. Rule HG-3: fast track, fast-track team, severity low.
- `CLM-4003`: the loss was on 7 Nov 2026 and the policy period ended on 5 Nov 2026. Rule HG-2: complex, senior adjuster, severity medium.
- `CLM-4005`: a passenger was injured. Rule HG-1: person first, senior adjuster, severity high. Rule HG-2 gets no row, although another party is involved.
- `CLM-4007`: the customer is 81, lives alone and is out of his home, from a handler's note. Rule HG-1.
- `CLM-4008`: no earlier rule applies. Rule HG-4: standard, motor team, severity medium. Who was driving is for the coverage check.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The claims handler reads the sorting and assigns the claim. Whether the wording covers the loss is for the coverage check and an adjuster.
