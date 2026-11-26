# Pre-authorisation Preparation

Sets a provider's request for approval against the member's own plan and the insurer's medical policy, and prepares the file: what is met, what is not, and what the notes do not say. A clinician or an authorised assessor decides. The agent never approves and never refuses a request.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A pre-authorisation request arriving, which the health system can announce through its `pre-authorisation-request` event |
| How people meet it | An application: the Health claims desk |
| Reads from | The insurer's health system: one pre-authorisation request with the member's cover on the planned date, the row of the member's own plan, the plan's position, the medical policy with its criteria, and the provider's two documents |
| Changes | Saves the assessment as a draft. The draft approves nothing, declines nothing and contacts nobody |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the request once. It comes whole, so no second read is needed.
- Works in a fixed order: the member's cover on the planned date; whether the member's own plan covers the procedure; whether that plan needs pre-authorisation for it; only then the medical policy.
- Writes three rows for those three checks every time, each with the system's own sentence, dates and days.
- Stops where cover is not in force, the plan does not cover the procedure, or the plan needs no pre-authorisation. There are then no criterion rows, and the file goes to the assessor with the system's sentence.
- Otherwise writes one row for each criterion of the medical policy, in the criterion's own words, judged from the provider's documents alone.
- Marks a criterion met only when a document states the fact, with the figure the criterion asks for. The two figures stand side by side, with the document's id.
- Marks a criterion not stated when the notes say nothing about it, and proposes a question for the provider. It does not guess.
- Marks a criterion not met when a document plainly fails it, and refers the file to the medical reviewer. It does not decline.
- Saves the assessment as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: send to the assessor as met, ask the provider, refer to the medical reviewer, or refer to the assessor.

## What it does not do

- Approve or refuse a request. The assessor decides, and only the medical reviewer, a clinician, declines.
- Ask, tell or contact a provider or a member. The question for the provider is a proposal that a person sends.
- Use another plan's benefits, or a medical policy the system did not give for this request.
- Work out days, limits or what the member has left. The system gives them.
- Guarantee the same wording on every run. The file is a draft for the assessor. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's health system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others. The operation that records a person's decision is not given to the agent.
- The Health claims desk, which sends the request's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft pre-authorisation file. For the assessor. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:".
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `PA-8101`: an MRI scan of the lumbar spine on the basic plan. Cover in force, BEN-E05 covered, pre-authorisation needed. Criteria 1, 2 and 3 of MP-301 are met. Proposal: send to the assessor as met.
- `PA-8102`: a day-case knee arthroscopy. Criteria 1 and 3 of MP-303 are met. Criterion 2 is not met: physiotherapy for 2 weeks where at least 6 weeks are asked for. Proposal: refer to the medical reviewer.
- `PA-8103`: an MRI scan. Criteria 1 and 2 of MP-301 are met. The notes say nothing about an examination, so criterion 3 is not stated. Proposal: ask the provider.
- `PA-8104`: the member's cover ended on 27 Oct 2026, and the planned date, 6 Dec 2026, is 40 days after the end. No criterion rows. Proposal: refer to the assessor.
- `PA-8105`: the surgical removal of a wisdom tooth. BEN-E09 Dental treatment is not covered by the member's plan. No criterion rows. Proposal: refer to the assessor.
- `PA-8106`: an MRI scan on the fuller plan, which needs no pre-authorisation for BEN-F05. The medical policy is not read. Proposal: refer to the assessor.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The assessor reads the file and decides. Where a criterion is not met, the medical reviewer reads the request, and only the medical reviewer declines. Where the notes do not state a fact, a person asks the provider. The agent decides nothing and contacts nobody.
