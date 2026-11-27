# Complaint Handling

On a new complaint, sorts it by the insurer's numbered complaint categories, gathers the policy and the claim history it concerns, gives the deadlines as the system worked them out, says who must handle it, links a repeat to the first complaint, and drafts the response and the log entry. A complaints officer decides and sends.

| | |
|---|---|
| Type and form | Workflow, event-triggered |
| What starts it | A new complaint arriving. Here the desk, or a person, sends the message with the complaint's id; an event has not started it |
| How people meet it | An application: the Complaints desk. It also works in a chat |
| Reads from | The insurer's conduct system: the complaint with its customer care record, policy, claims, earlier complaints and deadlines, and the complaints procedure with its categories and handling rules |
| Changes | Saves the draft response and the log entry as a draft. The draft sends nothing, acknowledges nothing and leaves the complaint, the policy and the claims unchanged |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Reads the customer's words and says whether the item is a complaint or a question. Any dissatisfaction makes it a complaint (rule CH-6).
- Gives a complaint one category, CC-1 to CC-6: the one that fits the main thing the customer is unhappy with.
- Gives the acknowledgement date and the final response date exactly as the system worked them out, with the system's sentence. It counts no days. A complaint on its last day is due today and is not late.
- Checks the three special rules and says for each whether it applies: a customer marked vulnerable on the customer care record (CH-3: 15 days in place of 30, contact in the preferred way), a mention of the regulator, a lawyer or legal action (CH-4: to the senior complaints officer), and a repeat of an earlier complaint about the same matter (CH-5: linked by id). An earlier complaint about a different matter is not linked.
- Gathers the policy, with cover on the day the complaint was received, and every claim on it with its status, decision and notes.
- Says who handles it, by role and by the name the procedure gives.
- Where the records do not show whether something the customer describes happened, says so. The officer finds out.
- Drafts the response: what we received, what we understood, what will be looked at, who will look at it and the date of the final response. The sentence that gives the outcome is left for the officer, and the summary says so.
- Drafts the entry for the complaints log.
- Saves both as one draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: for the complaints officer, for the senior complaints officer, or for the policy servicing team.

## What it does not do

- Uphold or reject a complaint, or say whether a claim decision was right. A complaints officer decides (rule CH-7).
- Offer, promise or pay money or a refund.
- Admit fault, or apologise for what the customer says happened.
- Send a response, acknowledge or close a complaint, or contact a customer.
- Change a policy, a claim or a payment.
- Answer the customer's question where the message is not a complaint. The policy servicing team answers it.
- Count days or work out a date of its own.
- Guarantee the same wording on every run. The response is a draft for the complaints officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's conduct system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Complaints desk, which sends the message with the complaint's id, if you want to meet the agent through a screen. The desk is not written yet. The agent also works in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft complaint response. For the complaints officer. Not issued.", one six-column table with a column called Mark, the letter under the heading "Draft response. Not sent.", and a last line that starts "Proposal:". The summary holds no count and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

Two things to know before the first build:

- The system's record carries an acknowledgement date and a final response date for every item, also for one that is not a complaint. The agent gives them only for a complaint.
- The log entry stands in the last row of the table, on one line, exactly as it was saved.

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Prepare complaint" and the complaint id.

- `CMP-7101`: a plain service complaint, two long waits on the telephone and no call back. CC-1, to the complaints officer. Acknowledgement due 27 Nov 2026, final response due 24 Dec 2026.
- `CMP-7102`: she does not accept the decline of claim `CLM-4010`. CC-2. The draft gives the adjuster's decision of 20 Nov 2026 under clause 2.2 as recorded and does not say whether it will stand. Final response due 25 Dec 2026.
- `CMP-7103`: no news on a theft claim, and the customer mentions the Meridia Insurance Authority. CC-3, CH-4: to the senior complaints officer. Acknowledged on 25 Nov 2026, in time.
- `CMP-7104`: a customer the customer care record marks as vulnerable. CC-3, CH-3: to the complaints officer on the day, contact by telephone, final response due 10 Dec 2026, 15 days in place of 30.
- `CMP-7105`: a repeat. A premium of USD 31.50 collected twice was the matter of `CMP-7051`. CC-4, CH-5: linked to `CMP-7051`. The records do not show whether the refund was paid, and the draft does not say that it is overdue.
- `CMP-7106`: a question about a courtesy car and a named driver. Not a complaint (CH-6): no category, no time limit, to the policy servicing team.
- `CMP-7107`: a certificate not sent. CC-6. The acknowledgement was due 19 Nov 2026 and is late by 5 working days (Charter Day, 16 Nov 2026, is left out of the count). Final response due 11 Dec 2026. The earlier complaint `CMP-7052` was about a different matter and is not linked.
- `CMP-7108`: a charge of USD 25.00 nobody told him about. CC-4. The acknowledgement is due today, 26 Nov 2026, and is not late.

Everyone and everything in the invented insurer is invented, and so is the regulator it names.

## Where it stops for a person

The complaints officer, or the senior complaints officer where the procedure sends the complaint there, reads the draft, decides whether the complaint is upheld or rejected, writes that sentence into the response, and signs and sends it. Whether money is offered or refunded is for that person. The agent does none of this.
