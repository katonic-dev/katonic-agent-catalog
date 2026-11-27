# Certificate and Endorsement Preparation

Prepares the certificate of insurance from a certificate request, or the endorsement wording from a change request, from the insurer's own templates and the policy as it stands on the date asked. It says where the request asks for something the policy does not give: a higher limit, a party not on the policy, a date outside the period, a waiver the wording does not hold. It never writes onto a certificate anything the policy does not hold. The servicing officer issues every document.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A certificate request or a change request that arrives at the servicing desk. The desk sends its id |
| How people meet it | An application: the Policy servicing desk. It also works in a chat |
| Reads from | The insurer's policy servicing system: a certificate request with the system's check against the policy as it stands on the certificate date, a change request measured against the servicing rules, the certificate template and the endorsement templates |
| Changes | Saves the certificate or the endorsement as a draft. The draft issues nothing, adds nothing to a policy and sends nothing to anyone |
| State | Written. Not yet built on a cluster |

## What it does

For a certificate request:

- Reads the request once. It comes with the system's check: a row for cover on the certificate date and a row for each item asked, and the policy as it stands on that date with every endorsement in effect applied.
- Writes the certificate from template CT-COI-1, seven numbered paragraphs, with only what the policy holds on the certificate date.
- Where the request asks for a limit higher than the policy's, shows the policy's figure. Where it asks to name a party the schedule does not name, leaves the party out. Where it asks for a waiver the policy does not hold, writes none. Each difference is named in the table and in the proposal.
- Where the policy is not in force on the certificate date, writes no certificate text.
- Where an endorsement changed a limit mid-term, shows the figure that held on the certificate date.

For a change request:

- Writes the endorsement from the template for the kind of change: ET-ADDRESS, ET-VEHICLE, ET-SUM-INSURED, ET-DRIVER or ET-CANCELLATION.
- Fills the premium paragraph with the system's own note and working, or with "No change in premium." or "To be worked out after referral."
- Names each servicing rule that applies and each point the system says must be raised.

For both:

- Takes every comparison, sum and count of days from the system.
- Writes one table with a Mark column: as asked, differs or noted for a certificate; filled, cannot fill, to raise or noted for an endorsement.
- Gives the text of the draft under its own heading, exactly as it was saved.
- Saves the draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: ready for the servicing officer, refer to the servicing officer with each difference, or ask the requester.
- Asked in the same message to issue or send the document, prepares the draft and refuses the rest in one sentence of the summary.

## What it does not do

- Issue a certificate or an endorsement. The servicing officer does that.
- Write onto a certificate a limit, a party, a date or a waiver the policy does not hold, whoever asks.
- Change a policy, raise a limit, add a party or give a waiver. That starts with a change request and a person decides it.
- Send anything to a customer, a broker or a certificate holder.
- Work out a premium. The system does the sum.
- Decide whether a change is made. Policy Servicing prepares the change itself for the servicing officer.
- Guarantee the same wording on every run. The draft is for the servicing officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's policy servicing system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Policy servicing desk, which sends the request's id, if you want to meet the agent through a screen. The agent also works in a chat.
- A trigger that sends each new certificate request or change request by its id, if you want the drafts written before anybody asks.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft certificate. For the servicing officer. Not issued." or "Draft endorsement. For the servicing officer. Not issued.", a five-column table (the fourth column is called Mark), the text under the heading "Certificate text. Not issued." or "Endorsement text. Not issued.", and a last line that starts "Proposal:".
4. The ten tests are in [`tests.yaml`](tests.yaml).

One thing to know before the first build: the reply has a section the other servicing agent does not have, the text of the draft under its own heading. The desk must show it, because the servicing officer reads the wording before issuing it.

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`.

- "Prepare the certificate for certificate request CRQ-7401." Clean. The certificate shows the buildings sum insured, USD 310,000.00, and the period. Proposal: ready for the servicing officer.
- `CRQ-7402`: a third party property limit of USD 1,000,000.00 is asked and the schedule gives the same. Proposal: ready for the servicing officer.
- `CRQ-7403`: USD 2,000,000.00 is asked and the schedule gives USD 1,000,000.00. The certificate shows USD 1,000,000.00. Proposal: refer to the servicing officer.
- `CRQ-7404`: asks to name the certificate holder as an additional insured. It is not on the policy, so the certificate does not name it as insured. Proposal: refer to the servicing officer.
- `CRQ-7405`: a certificate date of 25 May 2027, 16 days after the period ends. No certificate text is written. Proposal: refer to the servicing officer.
- `CRQ-7406`: a certificate as at 12 Oct 2026. An endorsement raised the contents sum insured from 27 Oct 2026, so the certificate shows USD 35,000.00 and not USD 50,000.00. Proposal: ready for the servicing officer.
- `CRQ-7407`: asks for a waiver of rights of recovery. The wording holds none, so the certificate holds none. Proposal: refer to the servicing officer.
- "Prepare the endorsement for change request CHG-7308." The sum insured for the vehicle from USD 19,500.00 to USD 23,400.00, exactly 20.00 percent, so rule SR-3 does not apply. The premium paragraph gives the system's additional premium of USD 60.40 with its working. Proposal: ready for the servicing officer.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The servicing officer reads the draft and issues the document. Where a request asks for something the policy does not hold, the servicing officer decides what happens next: a higher limit, a new party or a waiver is a change to the policy and starts with a change request. Where a servicing rule sends a change request to underwriting or to the servicing team leader, that person reads it before the endorsement is issued. The agent issues nothing, changes nothing and contacts nobody.
