# Underwriting Referral Memo

Drafts the referral memo for a risk an underwriter has raised: the risk, the terms proposed, the rule that forces the referral and the grade it goes to, and the earlier referred risks with how each one is alike or differs. Says so when no referral is needed. It recommends no decision: an underwriter with the authority decides.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the underwriting system when an underwriter raises a referral |
| How people meet it | An application: the Underwriting desk |
| Reads from | The insurer's underwriting system: one referral with the system's authority check, and the earlier referred risks with the decisions taken |
| Changes | Saves the memo as a draft. The draft refers nothing, decides nothing and contacts nobody |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the referral once, with the system's authority check: each referral rule with whether it applies, the grade the referral goes to, and the discount as a percentage.
- Uses the system's answer as it is. It compares no figure with an authority and chooses no grade. A rule the system says does not apply is written as not applying.
- Searches the earlier referred risks, once for each rule that forces the referral and once for each guideline the risk is outside, within the referral's class of business.
- Sets each precedent beside the risk and marks it: agrees, differs, went against or not alike. A precedent that looks alike but differs on the fact its decision rested on is marked differs and is not counted as support.
- Says so when no precedent is found, and brings in none from another class of business.
- Says so when no referral is needed: the underwriter who asked may decide, and the memo names no grade and no forcing rule.
- Saves the memo as a draft, with one row for each precedent it cites, a precedent that is not alike included with the reason, and says it was saved only if the system's reply says so.
- Ends with one proposal line: refer to the grade the system names, with the rules that force it; or no referral needed.

## What it does not do

- Approve, decline, quote or bind a risk, or recommend a decision.
- Refer a risk, send a memo, or contact a broker or an underwriter. A person sends the memo.
- Judge whether an earlier decision was right.
- Work out a discount or compare a size with an authority. The system does both.
- Guarantee the same wording on every run. The memo is a draft. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's underwriting system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Underwriting desk, which sends the referral's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft referral memo. For the deciding underwriter. Not issued.", a five-column table (the fourth column is called Mark), and a last line that starts "Proposal:".
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `REF-6601`: a timber-framed furniture showroom, outside UG-1. RF-2 applies. PRC-6401 and PRC-6402 agree; PRC-6403, a class B grain warehouse, is not alike. Proposal: refer to the senior underwriter, forced by RF-2.
- `REF-6602`: a grain and seed warehouse with no sprinklers, outside UG-1 and UG-3. RF-1 and RF-2 apply. PRC-6403 looks alike but its decision rests on sprinklers in working order, so it differs. Proposal: refer to the senior underwriter, forced by RF-1 and RF-2.
- `REF-6603`: a fleet of 180 vehicles, asked by a senior underwriter. RF-1 applies; RF-2 does not, because a senior underwriter may decide a risk outside a guideline. No precedent found. Proposal: refer to the head of underwriting, forced by RF-1.
- `REF-6604`: offices at USD 3,200,000.00 with a discount of 15.00 percent, asked by a senior underwriter. No rule applies. Proposal: no referral needed.
- `REF-6605`: a tea warehouse with a discount of 18.00 percent, above the underwriter's 10.00 percent. RF-3 applies. PRC-6404 went against; PRC-6405 differs. Proposal: refer to the senior underwriter, forced by RF-3.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The underwriter the referral goes to reads the memo and decides. Where no referral is needed, the underwriter who asked decides. A person sends the memo and speaks to the broker. The agent decides nothing, recommends nothing and contacts nobody.
