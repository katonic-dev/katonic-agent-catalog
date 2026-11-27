# Fraud Detection

Before anything is paid, checks a new claim against the insurer's own numbered indicators and the parties' earlier claims, and prepares a referral with its reasons for the investigator. It says which indicators are met and what each rests on. It never says that a claim is false or that a person did wrong, and it declines nothing.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new claim reaching the fraud check, before anything is paid |
| How people meet it | An application: the Investigations desk |
| Reads from | The insurer's investigations system: the new claim with its parties, documents and policy; the measurement of every indicator on it; the earlier claims of every party |
| Changes | Saves a draft referral. The draft does not change the claim's status, holds no payment and tells nobody anything |
| State | Written. Not yet built on a cluster. Not on the Catalog shelf |

## What it does

- Reads the claim, has the system measure all six indicators on it, and reads the earlier claims of the parties, every time.
- Writes one row for each indicator, met or not: the measured value against the threshold, and the system's own sentence with the dates, claim ids and names it rests on.
- Uses the form "Indicator FI-1 is met: 9 days against 30 days or fewer" for an indicator that is met.
- Counts nothing. Every day count, count of claims and percentage is the system's. A figure close to a threshold that does not reach it is not met.
- Treats two people as the same person only when the name and the date of birth are both the same. A person with the claimant's name and another date of birth is named as another person, and that person's claims are left out.
- States a shared bank account, a repairer or a date as a fact of the records, with the ids, and says nothing about what it means about a person.
- Writes the file in full for a clean claim too. "No indicator is met" is a result of the check.
- Saves the referral as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: refer to the investigations desk on the indicators met, or no referral.

## What it does not do

- Say that fraud took place, that a claim is false, or that a person did wrong. It does not call anyone a fraudster or a suspect, and does not call a claim suspicious.
- Decline, delay, hold or pay a claim, change a record or block an account.
- Contact a claimant, a witness, a repairer, a bank or anyone else.
- Decide what an indicator means. The investigator does.
- Guarantee the same wording on every run. The referral is a draft for the investigator. Run the tests on your own model before you rely on it, and read the saved drafts for the wording as well as the replies.

Asked to name a person as having done wrong or to decline a claim while it checks one, it says in one line that it cannot, and still prepares the referral exactly as the measurement gives it.

## What you set up

- A model for the Reasoning tier.
- The insurer's investigations system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Investigations desk, which sends the claim's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft fraud referral. For the investigator. Not issued.", a six-column table with six rows (the fifth column is called Mark), and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-6201`: a clean claim. No indicator is met. Proposal: no referral.
- `CLM-6202`: every figure is close to its threshold and none reaches it: 34 days, 2 earlier claims, 2 claims with one repairer, 91.0 percent of the sum insured. The bank account is also on a claim by a person recorded at the claimant's own address, who is not counted. No indicator is met.
- `CLM-6203`: the loss was 12 days after the policy period started. FI-1 is met. Proposal: refer.
- `CLM-6204`: 3 earlier claims in the 24 months before the loss. FI-2 is met. A fourth earlier claim, `CLM-6014`, is outside the 24 months and not counted.
- `CLM-6205`: the bank account given for payment is also on `CLM-6021`, a claim by another claimant of another address. FI-4 is met. The referral states the shared account and says nothing more about either person.
- `CLM-6206`: the repair invoice `DOC-6206-2` is dated 6 days before the loss. FI-5 is met.
- `CLM-6207`: 9 days after the start of the policy period, and an estimate at 98.0 percent of the sum insured. FI-1 and FI-6 are met.
- `CLM-6208`: another person on the records has the claimant's name and another date of birth. That person's three claims are not the claimant's. No indicator is met.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The investigator reads the draft referral and decides what an indicator that is met means, and what to do next. A claim with no indicator met stays with its handler. The agent makes no finding about a claim or a person, decides nothing about payment and contacts nobody.
