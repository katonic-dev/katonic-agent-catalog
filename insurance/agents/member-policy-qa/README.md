# Member Policy Q&A

Answers a member's question about their own cover from the table of benefits of their own scheme, in one of four states: covered, covered with conditions, not covered, needs a person. Where the scheme's documents are silent it never infers cover: it says a person will answer and records a call-back request.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A member's question |
| How people meet it | Chat |
| Reads from | The insurer's health system: one member with the benefits of the member's own plan and what has been used, the member's own scheme with its exclusions, cover on a date, and the system's calculation on a bill |
| Changes | Saves a call-back request as a draft for the member services team. The draft books no call, promises no time and tells nobody |
| State | Built on a development cluster. All fourteen tests pass five runs in a row |

## Where the table of benefits comes from

An insurer would keep its tables of benefits as documents in a knowledge source, and this agent would answer from those documents. Here the table of benefits and the exclusions of each scheme are served by the invented insurer's health system instead. The reason is plain: an agent with a knowledge source cannot be published on the cluster used to build and test this catalog. The agent's rules are the same either way: it answers only from the member's own scheme, it names the benefit or the exclusion it rests on, and it infers nothing where the documents are silent.

## What it does

- Reads the member whose id the conversation gives, then only the table of benefits and the exclusions of that member's own scheme.
- Starts every answer with one of four phrases, alone on the first line: `Covered.`, `Covered with conditions.`, `Not covered.` or `Needs a person.` The state is the one the table gives the benefit.
- Then says what the plan gives: the benefit's name and id, the limit and the member's share as the table's own sentences, and every condition, with a need for pre-authorisation and a waiting period where there is one, with the date the system gives.
- Where the question is about the member's own use, gives what is used and what remains, as the system gives it.
- Where the member asks what the plan would pay on a bill, gives the system's calculation: the part within the limit, the part over it, the member's share, what the plan would pay and what the member would pay. It says this is an estimate and not a decision on a claim.
- Ends every answer with a source line: the scheme's id, the plan's name and the id of the benefit or the exclusion.
- Where the member's cover is not in force, says so with the system's sentence, and says nothing about benefits.
- Where neither the table nor the exclusions names what is asked, says the documents do not settle it, records a call-back request and says a person will call back, without promising a time. It says a request was recorded only if the system's reply says so.
- Takes every figure, every date and every count from the system. It adds up nothing and counts no days.

## What it does not do

- Infer cover. A treatment the documents do not name is not a yes and not a no.
- Read or quote another scheme, or say what another plan gives. The two schemes of the invented insurer have different plans, and the same question has a different right answer on each.
- Discuss another member. A dependant is another member: only the id given in the conversation is answered for.
- Give medical advice, or say whether a treatment is needed.
- Approve a treatment, a pre-authorisation or a claim, or say that a claim will be paid. It says what the plan's terms give.
- Book a call or promise a time for one.
- Check who the person asking is. The health system has no sign-in for a member, so the agent takes the member id the conversation gives. Put the agent behind a sign-in that already knows who the member is before you give it to members.
- Guarantee the refusals. Declining advice and declining another member's records are instructions to the model, not controls. Run the last two tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The insurer's health system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations that search members, list schemes and record decisions. Do not attach them to this agent.
- A way for the conversation to give the id of the member asking, as a signed-in member's id would be passed.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply is a chat reply, not a desk reply: no heading, no table. The first line is one of the four phrases and the last line starts "Source:".
4. The fourteen tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Each question starts with the member's id, for example "I am MEM-7201."

- `MEM-7201`, on the fuller plan, asks how many physiotherapy sessions are left: covered with conditions (BEN-F07), 12 of 12 sessions used, none remains.
- `MEM-7205`, on the basic plan, asks the same: covered with conditions (BEN-E07), 3 of 6 sessions used, 3 remain.
- `MEM-7202` asks whether dental treatment is covered: covered with conditions (BEN-F09), up to USD 500.00 in a benefit year, the member pays 20 percent up to USD 100.00. `MEM-7208` asks the same on the basic plan: not covered (BEN-E09).
- `MEM-7204` asks about maternity care: covered with conditions (BEN-F08), up to USD 6,000.00 for each pregnancy, pre-authorisation needed, and usable from 13 Aug 2027, after 300 days of cover.
- `MEM-7207` asks what the plan would pay on a bill of USD 100.00 for medicines: USD 70.00 is within the limit, USD 30.00 is over it, the share is USD 14.00, the plan would pay USD 56.00 and the member USD 44.00.
- `MEM-7203` asks whether hearing aids are covered: needs a person. A call-back request is recorded for the member services team.
- `MEM-7206` asks whether they are covered: not covered. The cover ended on 27 Oct 2026. Asked about 20 Oct 2026, the agent gives the system's answer for that date: the cover was in force.
- `MEM-7299`: the system holds no such member.
- A question about a dependant, and a request to say whether a scan is needed and to approve it: refused.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

Where the scheme's documents do not settle a question, a person from the member services team answers, and the agent records a call-back request for them. The insurer's assessors decide a request for pre-authorisation, and the claims team decides each claim. Whether a treatment is needed is for the member and their doctor.
