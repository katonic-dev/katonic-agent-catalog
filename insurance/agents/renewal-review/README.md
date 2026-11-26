# Renewal Review

Before a policy's period ends, sets the expiring terms beside the claims of the period, with the totals and the loss ratio the system works out, and the changes in the risk reported since the period started, and marks which renewal rule each finding touches. Where two records disagree it shows both figures and sends the point to a person. The underwriter decides the terms. The agent never renews, quotes, offers or refuses terms.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A schedule. Each renewal whose period ends within a set number of days, which the underwriting system lists, is sent to the agent by its id |
| How people meet it | An application: the Underwriting desk |
| Reads from | The insurer's underwriting system: one renewal with its expiring terms, the claims of the period, the totals and both loss ratios, any disagreement between records, the changes reported, and each renewal rule with whether it applies |
| Changes | Saves the review as a draft. The draft offers no terms, renews nothing and contacts nobody, and changes neither the policy nor a claim |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the renewal once. It comes whole, so no second read is needed.
- Writes a table of seven rows, always in the same order: the expiring terms, the claims of the period, then one row for each of the five renewal rules: the loss ratio (RN-1), a change of occupancy (RN-2), a change in protections (RN-3), an open claim (RN-4) and records that disagree (RN-5). An eighth row is written only for a reported change of another kind.
- Gives each rule's row the system's own sentence, word for word, and the mark the system gives: applies, does not apply, or depends on the disagreement.
- Takes every total, loss ratio and count of days from the system. It adds up nothing and divides nothing.
- Where a claim is open, gives the loss ratio on payments alone and with the reserves, and says the reserve may move.
- Where a change is reported, gives it as it was reported: the date, who reported it and the text.
- Where the claims record and the policy record disagree, gives both workings and both loss ratios, puts each account after the id of its record, and chooses neither.
- Saves the review as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: ready for the underwriter, refer to the senior underwriter, survey before terms, or ask the claims team.
- Asked in the same message to renew or to send terms, does the review and refuses the rest in one sentence of the summary.

## What it does not do

- Renew a policy, quote, set a premium, or offer, change or refuse terms. The underwriter decides.
- Refer a renewal, order a survey or ask the claims team. Each is a proposal that a person acts on.
- Choose between two records that disagree, or leave a claim out of the figures.
- Change a policy, a claim or a date.
- Tell or contact a broker or a policyholder.
- Find the renewals that are due. The schedule or the desk does that and sends each id.
- Guarantee the same wording on every run. The review is a draft for the underwriter. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's underwriting system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Underwriting desk, which sends the renewal's id, if you want to meet the agent through a screen. The agent also answers in a chat.
- A schedule that reads the renewals due and sends each id, if you want the reviews written before anybody asks.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft renewal review. For the underwriter. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:".
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `RNW-6701`: a clean renewal. One closed claim, USD 900.00 paid against a premium of USD 6,000.00: 15.00 percent. No rule applies. Proposal: ready for the underwriter.
- `RNW-6702`: two closed claims, USD 8,250.00 against USD 10,000.00: 82.50 percent, above the limit of 70.00 percent. RN-1 applies. Proposal: refer to the senior underwriter.
- `RNW-6703`: 20.00 percent, and a change of occupancy reported on 29 Jun 2026: half of the warehouse let to a tyre fitter. RN-2 applies. Proposal: survey before terms.
- `RNW-6704`: a home policy with one open claim, nothing paid and a reserve of USD 62,000.00 against a premium of USD 1,240.00. On payments alone 0.00 percent, with the reserve 5,000.00 percent. RN-1 and RN-4 apply. Proposal: refer to the senior underwriter.
- `RNW-6705`: no claim, and the sprinkler system reported out of service on 12 Oct 2026. RN-3 applies. Proposal: refer to the senior underwriter.
- `RNW-6706`: the claims record gives CCL-6906 a date of loss of 5 Jan 2026, 9 days before the period started on 14 Jan 2026 by the policy record. With every claim 76.00 percent, leaving out CCL-6906 31.00 percent. RN-5 applies and RN-1 depends on the disagreement. Proposal: ask the claims team.

`RNW-6704` reads its policy and its claim from the policy and claims systems as they stand, so its figures change once that claim is decided or paid.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The underwriter reads the review and decides the terms. Where the loss ratio is above the limit or a change in protections is reported, a senior underwriter reads the renewal first. Where a change of occupancy is reported, a person orders a survey. Where two records disagree, the claims team settles the point. The agent decides nothing and contacts nobody.
