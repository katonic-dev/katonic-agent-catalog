# Payment Exception Repair

Reads a payment held in the repair queue and the reason it stopped, and proposes the correction with the rule it relied on and the record the corrected value came from. An operator approves every repair.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A payment landing in the repair queue. The bank's payments system can announce one through its event for held payments |
| How people meet it | An application: the Payments desk |
| Reads from | The bank's payments system: the repair item, the rule that stopped it, the payment, earlier payments found by beneficiary name or account, the check of an IBAN and the bank directory |
| Changes | Saves a draft repair proposal. The draft releases nothing: the payment stays held |
| State | Built on a development cluster on 25 November 2026. All seven tests pass five runs in a row. Not on the Catalog shelf |
| Website page | [katonic.ai/use-cases/banking-payment-exception-repair-agent](https://www.katonic.ai/use-cases/banking-payment-exception-repair-agent) |

## What it does

- Reads the repair item: the held message, why it stopped, the bank rule with its text, and the reason code where there is one.
- Finds the corrected value from a record, in the way the rule allows: an earlier payment to the same beneficiary of the same customer (found by searching on the beneficiary's name or account), the bank directory, or the invoice reference.
- Checks the corrected value, for example with the system's check of an IBAN and a search of the payments that used the corrected IBAN.
- Writes one row for each field it proposes to correct, then one for each check that supports it. Each row has the evidence ids, the held and corrected values, the rule, the source of the value, and a mark: to correct, confirmed, missing or unclear.
- Saves the repair as a draft proposal, with the explanation of where each value came from, and says it was saved only if the system's reply says so.
- Ends with one proposal line: approve the repair, or refer it to a person.

## What it does not do

- Release a repaired payment, send one, cancel one or amend one. A person does that after the operator approves.
- Guess a value. If no record gives it, it proposes none and refers the repair to a person.
- Take a value from a payment that is not to the same beneficiary, or from another customer.
- Decide that a payment is safe to send.
- Guarantee the same marks on every run. The proposal is a draft for the payments operator. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's payments system, connected as an imported API, with the seven operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Payments desk](../../desks/payments/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the seven tools above and no others. The operation that releases a repaired payment is not attached.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft proposal. For the payments operator. Not issued.", a seven-column table, and a last line that starts "Proposal:". In the row for a field to correct, the held and the corrected value are separated by <br> ("Held: ..." then "Corrected: ..."), and so are the rule and the source ("Rule: ..." then "Source: ..."): the desk shows each on a line of its own. The summary holds no count of marks and is not in the first person. Change the instructions and the desk's `routing` setting for "Repair" together.
4. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, started with `BANK_TODAY=2026-11-24` so that the dates agree with the desk's demo cases:

- `REP-7001`: two digits of the beneficiary IBAN are swapped (rule MTB-PAY-RULE-101, reason code AC01). The corrected IBAN is XB82BRVN73201150000142, from the earlier payment PAY-6050 to the same beneficiary. A search by that IBAN finds PAY-6050 only. A search by the name finds PAY-6050 and the held PAY-6101, which is not a source.
- `REP-7002`: the BIC QNMKXQQ1 does not match the bank named in the payment (MTB-PAY-RULE-102, RC01). The corrected BIC is TESLXTT1, from the bank directory entry for Tessaly Mutual Bank.
- `REP-7003`: no beneficiary address on a payment to Aldoria (MTB-PAY-RULE-103, BE04). The address is Smelter Row 12, Velmora, Aldoria, from the earlier payment PAY-6051 to the same beneficiary. A search by name or by IBAN finds PAY-6051 and the held PAY-6103 only.
- `REP-7004`: no purpose code for the Meridia to Rovaland corridor (MTB-PAY-RULE-104). The code is GDDS (goods), chosen from the reference "Invoice RD-88412 dental chair spare parts", which the proposal must name.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The payments operator approves every repair. The payment stays held until a person releases it in the payments system, with their name. Nothing is released by the agent.
