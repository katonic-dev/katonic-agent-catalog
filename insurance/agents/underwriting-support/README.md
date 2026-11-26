# Underwriting Support

Reads a broker's submission and prepares the underwriting file: each guideline of the class as within, outside, missing or cannot tell, what the submission lacks, and where a note contradicts a field of the form. The underwriter decides. The agent never accepts, declines, quotes or binds a risk and never contacts a broker.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A broker's submission arriving in the underwriting system |
| How people meet it | An application: the Underwriting desk |
| Reads from | The insurer's underwriting system: one submission with the broker's form, every document as text, the guidelines of its class, and the system's measure of the form against each guideline |
| Changes | Saves the underwriting file as a draft. The draft accepts nothing, declines nothing, quotes nothing and contacts nobody |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the submission once. It comes whole, so no second read is needed.
- Writes one row for each guideline of the submission's class of business, in the system's order.
- For a guideline with figures, uses the system's measure: the total, the limit, the amount over. It adds up nothing and compares nothing. A value exactly on a limit is within, as the system says.
- For a guideline with no figure, reads the occupancy or the use and the documents against the guideline's list.
- Reads every document against the form. Where a note contradicts the field a guideline turns on, it marks the guideline cannot tell, shows both accounts with the document's id, and chooses neither.
- Marks a guideline missing when the submission lacks what it needs, such as the claims history, and assumes nothing about it.
- Makes a risk outside a guideline ready for the underwriter. It does not decline it.
- Saves the file as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: ready for the underwriter, within every guideline or outside the guidelines it names; or ask the broker, with the question.

## What it does not do

- Accept, decline, quote or bind a risk. The underwriter decides.
- Ask, tell or contact a broker. The question for the broker is a proposal that a person sends.
- Change a submission, or choose between the form and a document.
- Work out totals, percentages or limits. The system gives them.
- Guarantee the same wording on every run. The file is a draft for the underwriter. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's underwriting system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Underwriting desk, which sends the submission's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft underwriting file. For the underwriter. Not issued.", a six-column table (the fourth column is called Mark), and a last line that starts "Proposal:".
4. The ten tests are in [`tests.yaml`](tests.yaml).

The invented insurer does not announce a new submission through an event today. Until it does, the desk or a person starts the agent with the submission's id.

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `SBM-6501`: a stationery warehouse, construction class A, total USD 1,800,000.00. Every guideline within. Proposal: ready for the underwriter, within every guideline.
- `SBM-6502`: a dairy's fleet of 24 vans. Every guideline within.
- `SBM-6503`: a timber-framed furniture showroom. UG-1 outside: the total of USD 1,350,000.00 is over the class C limit by USD 350,000.00. Proposal: ready for the underwriter, outside UG-1.
- `SBM-6504`: a scrap metal yard and waste recycling. Every figure is within. UG-2 outside on reading.
- `SBM-6505`: a garden centre's fleet of 40 vehicles. The claims history is missing, so UG-10 is missing. Proposal: ask the broker.
- `SBM-6506`: a print works. The form says sprinklers yes. The survey note SBM-6506-D2 says the system was decommissioned on 17 Sep 2026. UG-3 cannot tell. Proposal: ask the broker.
- `SBM-6507`: a chandlery. UG-1 outside by USD 600,000.00 and UG-4 outside with 4 claims where 3 are allowed. Proposal: ready for the underwriter, outside UG-1, UG-4.
- `SBM-6508`: a wool merchant. The total is exactly on the class B limit and the deductible equals the lowest. Both are within.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The underwriter reads the file and decides, whether the risk is within the guidelines or outside them. Where something is missing or two sources disagree, a person asks the broker. The agent decides nothing and contacts nobody.
