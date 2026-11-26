# First Notice of Loss Intake

Takes a new loss report, extracts who, what, when and where, finds the policy, checks it was in force on the date of the loss, prepares the claim file and lists what is missing. A claims handler decides.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new loss report arriving. The insurer's claims system can announce one through its `loss-report` event |
| How people meet it | An application: the Claims intake desk |
| Reads from | The insurer's claims system (the loss report) and its policy system (the policy, and whether it was in force on a date) |
| Changes | Saves the claim file as a draft. Asks for the claim to be registered, which waits for a claims handler's approval |
| State | Built on a development cluster on 26 November 2026. Six of seven tests pass five runs in a row. The step that registers a claim did not wait for approval on that cluster, so the seventh test is not finished |

## What it does

- Reads the loss report: the reporter, the policy number given and the text as it arrived.
- Finds the policy. The number a reporter gives may be wrong: when the insurer holds no such policy, it searches by the reporter's name, checks the holder and the address against the report, and shows both the number given and the policy found.
- Takes the claim type, the date of the loss, the place and what happened from the text, and says whether a person was injured and whether another party was involved.
- Has the policy system say whether the policy was in force on the date of the loss, and gives its reason. With no date of the loss, cover is not checked.
- Writes eight rows, one for each item, each with a mark: found, missing, differs, not in force or needs a person.
- Saves the claim file as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: register the claim, ask the reporter for what is missing, or refer to a handler.
- When the proposal is to register, asks for the registration with the version of the saved draft, and says that it is waiting for the handler's approval. It says a claim is registered only when the system's reply gives a claim id.

## What it does not do

- Refuse, decline or accept a claim, or accept cover. A policy that was not in force is a fact for the handler.
- Contact the reporter or anyone else. What is missing is listed for a person to ask.
- Ask for registration when its proposal is to ask the reporter or to refer to a handler, also when told to.
- Guess or correct a policy number, a date or a name. If no policy or more than one fits, it picks none and refers.
- Guarantee the approval step. Waiting for the handler is the platform's approval rule on the one tool that registers a claim: set it before you publish.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system and policy system, each connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- An approval rule on `register_claim`, so that a registration is held until a claims handler approves it. Check that a call is held on your own platform before you rely on the rule.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft claim file. For the claims handler. Not issued.", a six-column table of eight rows, and a last line that starts "Proposal:".
4. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `LR-3001`: a complete report. Policy `POL-2011` was in force on 25 Nov 2026, nobody was injured and no other party was involved. The proposal is to register, and the registration waits for approval.
- `LR-3002`: the number given, `POL-2021`, does not exist. The reporter's name finds `POL-2012`. The report gives no date of the loss, so cover is not checked. The proposal is to ask the reporter for the date.
- `LR-3003`: policy `POL-2013` was cancelled on 17 Oct 2026 and the loss was on 24 Nov 2026. The proposal is to refer to a handler. No registration is asked for and no claim is refused.
- `LR-3004`: a person was injured and another party is involved. The proposal is to refer to a handler.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

A claims handler approves every registration. A report with a person injured, a policy that was not in force or a policy that cannot be settled goes to a handler. The agent contacts nobody.
