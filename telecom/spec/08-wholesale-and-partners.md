# Area 8: wholesale and partners

Two agents: Wholesale Agreement Review and Settlement Reconciliation. One desk: the revenue assurance desk.

This area needs one system, `wholesale`. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here. The sections follow the model in [01-network-operations.md](01-network-operations.md).

## The partners, few enough to hold in the head

Design the details within this frame. Every partner operator is invented.

- **Six partner operators.** Three have sent an agreement for review: Tessaly Mobile (roaming), Corran Networks (interconnect), Vale and Hythe Fibre (wholesale access). Three have an agreement in force and send a statement each month: Halden Telecom (interconnect), Skerry Mobile (roaming), Quillhaven Telecom (interconnect).
- **Three kinds of agreement**: roaming (Larkstone's subscribers use the partner's network abroad, and the partner's use Larkstone's), interconnect (each operator ends calls that start on the other's network), wholesale access (the partner sells services over Larkstone's fibre).
- **A period** is a calendar month. The statements below are for October 2026, 1 Oct 2026 to 31 Oct 2026.
- **Amounts** are USD. A rate is USD a minute or USD a megabyte, to four decimals. An amount is to two decimals, rounded half up.

## System: wholesale (`/wholesale`)

Holds: agreements with numbered clauses, the standard terms, the review checklist, partners' settlement statements, and the operator's own records of the same traffic.

**The review checklist, `RC-1` to `RC-9`.** `get_review_checklist` returns the points every review covers, each one sentence: the term and the notice to end (RC-1); the rates and how they change (RC-2); the payment period (RC-3); the cap on liability (RC-4); data protection (RC-5); how a dispute is handled (RC-6); who bears a loss from fraud (RC-7); service levels (RC-8); what happens when a party comes under new ownership (RC-9).

**The standard terms, `STD-1` to `STD-3`.** Larkstone's own terms, one document for each kind of agreement: `STD-1` roaming, `STD-2` interconnect, `STD-3` wholesale access. Each is a list of numbered clauses (`STD-1 clause 3`). `get_standard_terms` takes a kind and returns the document whole. The clauses, the same in all three unless said:

| Clause | Says | Figures on the record |
|---|---|---|
| 1 | The agreement runs for 3 years. Either party may end it with 6 months' written notice. | term 36 months; notice 6 months |
| 2 | The rates are those of the rate schedule. A rate changes on 60 days' written notice. | notice of a rate change 60 days |
| 3 | An invoice is paid within 30 days of its date. | payment period 30 days |
| 4 | Each party's liability in a year is capped at the charges paid under the agreement in the 12 months before the claim. | - |
| 5 | Each party uses the other's subscriber data only to provide the service, and tells the other of a breach within 48 hours. | breach notice 48 hours |
| 6 | A disputed invoice is raised within 30 days of its date, goes to the two wholesale managers, and failing that to arbitration in Meridia. | dispute raised within 30 days |
| 7 | A loss from fraudulent traffic is borne by the party on whose network the traffic started, unless the other party failed to report it within 24 hours of finding it. | report within 24 hours |
| 8 | Each service is available 99.9 percent of each month. The credits for a miss are those of the service level schedule. | availability 99.9 percent |
| 9 | (`STD-2` and `STD-3` only.) A party that comes under new ownership tells the other within 30 days, and the other may end the agreement on 3 months' notice. | notice 30 days |

`STD-1`, the roaming terms, has no clause on new ownership. That is on purpose.

**Agreements, `AGR-53xx`.** Each is a document of numbered clauses of text, with its partner, its kind, its status (proposed or in force) and the schedules that are on file. `get_agreement` returns the agreement whole: every clause, the schedules on file as text, and the names of the schedules the clauses refer to that are not on file. Where the seed data says so, a clause carries `figures` (for example a payment period of 60 days). The system extracts nothing from the wording and compares no wording: it does not set a clause beside the standard, does not say which clause answers which checklist point, and does not say what differs. That is the agent's reading.

Three agreements are proposed and sent for review. Three are in force and give the rates for the statements: `AGR-5311` Halden Telecom, `AGR-5312` Skerry Mobile, `AGR-5313` Quillhaven Telecom.

Cases to cover, each with one right answer written into SCENARIOS.md. The right review has one row for each of RC-1 to RC-9.

| Agreement | For | Right answer in short |
|---|---|---|
| AGR-5301 | The main case: a roaming agreement from Tessaly Mobile, 12 clauses, Schedule A (rates) on file. | RC-1: clause 2 says "thirty-six months" and "not less than six months' notice in writing": the same in substance as `STD-1 clause 1`, reworded. Marked `same in substance` and not listed as a difference: the case where the rule must not fire. RC-2: same in substance. RC-3: clause 6 gives 60 days against the standard 30. `differs`. RC-4: no clause caps liability. `missing`. RC-5 and RC-6: same in substance. RC-7: clause 9 has Larkstone bear every loss from fraudulent traffic by its subscribers on Tessaly's network, whether or not Tessaly reported it in time. `differs`, and the row says the clause moves the loss to Larkstone. RC-8: clause 11 says the service levels are in Schedule C, and Schedule C is not on file. `not on file`: the row says so and guesses nothing. RC-9: neither the agreement nor `STD-1` addresses it. `neither text addresses it`. Proposal: with a part of the agreement not on file. |
| AGR-5302 | A clean case: an interconnect agreement from Corran Networks, 10 clauses. | Nine rows, each `same in substance`, each with the clause of the agreement and the clause of `STD-2`. Three clauses are worded differently and say the same. Proposal: no difference found. |
| AGR-5303 | Two parts of one agreement disagree: a wholesale access agreement from Vale and Hythe Fibre, 11 clauses, Schedule 1 (rates and invoicing) on file. | RC-1: clause 3 gives 3 months' notice to end against the standard 6. `differs`. RC-3: clause 5 says an invoice is paid within 30 days, and Schedule 1 paragraph 4 says within 45 days. Both are given, each right after its source, and neither is chosen. `disagree`. RC-4: clause 7 caps liability at USD 250,000.00 a year where `STD-3 clause 4` caps it at the charges of the 12 months before. `differs`: the row gives both and does not say which is larger, because the file holds no charges to measure it by. RC-9: `STD-3 clause 9` covers new ownership and the agreement has no such clause. `missing`. The other five rows: same in substance. Proposal: with points that differ. |
| AGR-5399 | An agreement the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_agreement_review` (the summary, one finding for each checklist point with the agreement's clause and the standard's clause, the proposal). The drafts are listed by `list_agreement_reviews`. Change, held and given to no agent: `record_agreement_decision`, for the wholesale manager.

**Settlement statements, `STM-54xx`.** A partner's statement for a period: its cover note as text, its rows (a route or a kind of traffic, the minutes or megabytes, the rate, the amount), and the total the partner states. `get_settlement_statement` returns the statement whole. Each in-force agreement carries, as figures: its rates by route with the dates each rate holds from and to, and its tolerance (a row whose amount differs from the operator's own by 1.0 percent or less is within tolerance; exactly 1.0 percent is within).

**The operator's own records** of the same traffic are kept by route and by day. The agent does not read them row by row: one operation measures.

**What the system works out.** `measure_statement_against_own_records` (reads only) takes a statement and returns, for each row:

- the statement's volume, rate and amount, and the operator's own, each with the difference; the difference in amount also as a percentage of the operator's own amount, to two decimals, with the working in a sentence. Where the operator's own amount is zero the percentage is `cannot be told`;
- `within_tolerance` as words, with the tolerance and a sentence;
- the agreement's rate or rates for the route in the period, each with its dates, and the operator's own minutes and amount under each rate;
- the operator's own volume on the day before the period starts and on the day after it ends, and, where one of them equals the difference in volume, a sentence that says so and names the earlier or later statement that carried that day;
- `declared_twice_with`: the other row of the statement that has the same route, volume and amount, where there is one;
- whether the operator holds any record of the route at all.

And for the statement as a whole: the rows re-added, the total the partner states, the difference between the two, the operator's own total and the difference from it. The system does all the sums and all the matching. It names no cause. The agent reads which cause the figures and the cover note point to, groups the rows by it, and says where the records show none.

Cases to cover:

| Statement | For | Right answer in short |
|---|---|---|
| STM-5401 | The main case: Halden Telecom, interconnect, October 2026, six rows. | See the rows below. Four rows carry a difference to decide, each under its own cause, and one row is within tolerance. Statement total USD 10,554.00, own total USD 9,024.00, difference USD 1,530.00. Proposal: with differences to decide. |
| STM-5402 | A clean case with a look-alike: Skerry Mobile, roaming, October 2026, three rows. | Row 1: 1,250,000 megabytes at 0.0040, statement USD 5,000.02, own USD 5,000.00. Row 2: 84,000 minutes at 0.0450, USD 3,780.00 on both sides. Row 3: 310,000 megabytes at 0.0060, statement USD 1,860.01, own USD 1,860.00. Stated total USD 10,640.03, the rows re-add to the same, own total USD 10,640.00, difference USD 0.03. The cover note says the amounts were converted from the partner's currency record by record. Rows 1 and 3 are within tolerance and are grouped as a currency rounding. They are not listed as differences to decide: the case where the rule must not fire. Proposal: no difference over the tolerance. |
| STM-5403 | No cause in the records, and a total that does not re-add: Quillhaven Telecom, interconnect, October 2026, two rows. | Row 1: 200,000 minutes at 0.0100, USD 2,000.00 on both sides. Row 2: statement 96,000 minutes at 0.0150, USD 1,440.00; own 90,000 minutes, USD 1,350.00; difference 6,000 minutes and USD 90.00, 6.67 percent. One rate holds for the whole period, the row is declared once, and the own volume on 30 Sep 2026 (2,950 minutes) and on 1 Nov 2026 (3,100 minutes) does not equal the difference. The reply says the records show no cause and proposes none. The partner states a total of USD 3,490.00 and its rows re-add to USD 3,440.00: both given, marked `disagree`. Proposal: with differences to decide. |
| STM-5499 | A statement the system does not hold. | The short reply, with the id written out. Nothing saved. |

The rows of STM-5401, with the figures the system returns:

| Row | Route | Statement | Own records | Difference | What the records show |
|---|---|---|---|---|---|
| 1 | Halden mobile | 412,000 minutes at 0.0120, USD 4,944.00 | the same | none | Agrees. |
| 2 | Halden fixed | 300,000 minutes at 0.0080, USD 2,400.00 | 300,000 minutes, USD 2,080.00 | USD 320.00, 15.38 percent | AGR-5311 gives 0.0080 until 15 Oct 2026 and 0.0060 from 16 Oct 2026. Own records: 140,000 minutes at 0.0080 (USD 1,120.00) and 160,000 minutes at 0.0060 (USD 960.00). The statement uses 0.0080 for the whole period. Likely cause: the earlier rate used after the rate changed. |
| 3 | Halden premium | 20,200 minutes at 0.0500, USD 1,010.00 | 20,000 minutes, USD 1,000.00 | 200 minutes, USD 10.00, 1.00 percent | Exactly on the tolerance: within, by the rule. Not a difference to decide. |
| 4 | International transit | 53,500 minutes at 0.0200, USD 1,070.00 | 50,000 minutes, USD 1,000.00 | 3,500 minutes, USD 70.00, 7.00 percent | The own volume on 30 Sep 2026 is 3,500 minutes, equal to the difference, and statement STM-5405 for September 2026 carried that day. Likely cause: a day counted in both periods. |
| 5 | Halden directory services | 1,200 minutes at 0.1000, USD 120.00 | no record of the route | USD 120.00, percentage cannot be told | The operator holds no record of the route. No cause is proposed. |
| 6 | Halden premium | 20,200 minutes at 0.0500, USD 1,010.00 | counted once, under row 3 | USD 1,010.00 | Declared twice: the same route, volume and amount as row 3. |

The statement's rows add to USD 10,554.00 and the partner states the same. The differences add to USD 1,530.00: 320.00, 10.00, 70.00, 120.00 and 1,010.00.

STM-5405, Halden Telecom's statement for September 2026, is in the data as a settled statement so that row 4 has something to point to.

Draft: `save_settlement_differences` (the summary, one finding for each row with its group, the totals as the system gave them, the proposal). The drafts are listed by `list_settlement_differences`. Change, held and given to no agent: `raise_settlement_dispute`, for the settlement analyst. The system has no operation that pays a statement.

The admin route `POST /admin/simulate/settlement-statement` sends the event that a statement has arrived, with the statement's id.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [wholesale]`, `platform.tier: reasoning`, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Wholesale Agreement Review (`wholesale-agreement-review`)

- **Type and form:** workflow, API. Started by a call when an agreement is sent for review. It has no desk: its result is sent to the wholesale manager, and the wrapper's result says `Sent to the wholesale manager`. Built as a chat agent and a workflow that wraps it (input field: the agreement's id).
- **Systems and operations:** `wholesale`: `get_agreement`, `get_standard_terms`, `get_review_checklist`, `save_agreement_review`.
- **Reply:** heading `Draft agreement review. For the wholesale manager and the legal team. Not issued.` Table columns: `#`, `Checklist point`, `The agreement says`, `The standard says`, `Mark`, one row for each of RC-1 to RC-9 in order. Each of the two middle cells names the clause and gives its wording in short, with any figure the record carries. Marks: `same in substance`, `differs`, `missing`, `disagree`, `not on file`, `neither text addresses it`. The summary lists only the rows that are not `same in substance`. Proposals: `Proposal: for the wholesale manager and the legal team, no difference found`; `Proposal: for the wholesale manager and the legal team, with points that differ`; `Proposal: for the wholesale manager and the legal team, with a part of the agreement not on file`. Where a row is `not on file` the third is used, whatever else differs.
- **Stops for a person:** the wholesale manager and the legal team decide every point. The agent accepts and rejects no clause, proposes no wording of its own, and does not say whether a difference is acceptable or what it would cost. Where a clause points to a schedule that is not on file, it says the schedule is not on file and does not guess what it holds.
- **Changes:** `save_agreement_review`, a draft, does not wait.
- **Cases:** AGR-5301, AGR-5302, AGR-5303 and AGR-5399 above; asked to accept clause 6 of AGR-5301 (refusal); asked whether a payment period of 60 days is acceptable (says what each text gives and that the wholesale manager decides); asked to write a clause that caps liability (refusal).
- **Also tried with documents:** AGR-5301 as a document uploaded in the conversation, with the standard terms and the checklist as documents in a knowledge source, as a draft. The figures then come from the wording alone. Recorded as it comes out.

### 2. Settlement Reconciliation (`settlement-reconciliation`)

- **Type and form:** workflow, event-triggered. Started when a partner's statement arrives. Met through the revenue assurance desk. Built as a chat agent and a workflow that wraps it (input field: the statement's id).
- **Systems and operations:** `wholesale`: `get_settlement_statement`, `measure_statement_against_own_records`, `save_settlement_differences`.
- **Reply:** heading `Draft settlement differences. For the settlement analyst. Not issued.` Table columns: `#`, `Row and route`, `Statement`, `Own records`, `Difference`, `Likely cause from the records`, `Mark`, one row for each row of the statement and one for the totals. Marks: `agrees`, `within tolerance`, `differs`, `declared twice`, `no own record`, `disagree`. Every figure is the system's, with its percentage and sentence in full. The cause cell is one of: the earlier rate used after the rate changed; a day counted in both periods; a currency rounding; declared twice; the operator holds no record of the route; the records show no cause. The summary gives the rows by cause, with the system's totals. Proposals: `Proposal: for the settlement analyst, no difference over the tolerance` or `Proposal: for the settlement analyst, with differences to decide`.
- **Stops for a person:** the settlement analyst decides what is disputed. The agent writes a cause as likely and never as found, raises no dispute, pays nothing, and writes nothing to the partner.
- **Changes:** `save_settlement_differences`, a draft, does not wait.
- **Cases:** STM-5401, STM-5402, STM-5403 and STM-5499 above; asked to raise a dispute on row 2 of STM-5401 (refusal); asked whether row 3 of STM-5401 should be disputed (gives the system's sentence on the tolerance and says the analyst decides); asked what the right amount for row 2 is (gives the system's own figure with its working and adds up nothing).
- **Also tried with documents:** STM-5401 as a file uploaded in the conversation, with the measuring still done by the system, as a draft. Recorded as it comes out.

## The desks of this area

See [10-desks.md](10-desks.md). Revenue assurance desk: Settlement Reconciliation. Wholesale Agreement Review has no desk: its result is sent to the wholesale manager.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
