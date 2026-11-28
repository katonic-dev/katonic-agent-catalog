# Area 4: billing and revenue

Two agents: Billing & Revenue, Bill Dispute Investigation. Two desks: the revenue assurance desk and the customer care desk. This file also specifies the bills that the Bill Explanation agent of area 3 reads.

It needs one system of its own, `billing`, and three reads of `customer`. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here. The sections are those of [01-network-operations.md](01-network-operations.md), in the same order.

## Bills, small enough to hold in the head

Design the details within this frame.

- **One bill cycle in the cases.** Every bill of the cases is on the cycle that closes on the 20th. The period is 21 Oct 2026 to 20 Nov 2026, 31 days. The bills were issued on 23 Nov 2026 and are due on 7 Dec 2026. The period before is 21 Sep 2026 to 20 Oct 2026, 30 days. A cycle has no id: it is named by its closing date.
- **No tax line.** Every price includes tax, so that every bill adds up from its lines alone.
- **Tariffs, `TF-..`**, seven. A tariff is the price record behind a plan or a list of charges, with its terms as short numbered sentences. `TF-11` Mobile Start, USD 24.00 a month, roaming in zone 1 included, an early termination charge of USD 50.00 only inside the 12-month minimum term. `TF-12` Mobile Plus, USD 31.00 a month. `TF-13` Mobile Max, USD 62.00 a month. `TF-21` Home Fibre 300, USD 45.00 a month. `TF-22` Home Fibre 1000, USD 62.00 a month. `TF-31` one-off charges: a replacement SIM USD 5.00, a connection charge USD 20.00. `TF-41` add-ons: Data Boost 10 GB USD 8.00, Roam Pass zone 2 USD 12.00 for 7 days from the time of purchase. The plan names are the catalogue's. The catalogue is not specified in this file.
- **Rating rules, `RR-..`**, nine. A rating rule turns usage into money. Each has a start date and, where it has ended, an end date.

| Rule | What it says |
|---|---|
| RR-01 | Calls inside Meridia beyond the plan's minutes: USD 0.05 a minute. In force from 1 Jan 2026. |
| RR-02 | Data inside Meridia beyond the plan's allowance: USD 2.00 a GB. In force from 1 Jan 2026. |
| RR-03 | Roaming in zone 1: the plan's own allowance is used as at home, with no extra charge. |
| RR-04 | Roaming data in zone 2: USD 6.00 a GB. Zone 2 holds the invented countries Sandrake and Velmora. |
| RR-05 | Roaming data in zone 3: USD 12.00 a GB. |
| RR-06 | International calls to zone A: USD 0.20 a minute. In force from 1 Nov 2026. |
| RR-07 | A monthly charge for part of a period is the monthly charge, times the days in service, divided by the days in the period, to the nearest cent with a half rounded up. |
| RR-08 | International calls to zone A: USD 0.25 a minute. In force from 1 Nov 2025 to 31 Oct 2026. Ended. RR-06 replaced it. |
| RR-09 | A discount is applied once in a period, to the line it names, for the months its record gives. |

- **Customers, accounts and lines** are specified in [03-customer-care.md](03-customer-care.md) (system `customer`). This file names the ones its cases use, by id and an invented name, in the ranges CUS-1040 to CUS-1052, ACC-1140 to ACC-1164 and LIN-1240 to LIN-1251.

## System: billing (`/billing`)

Holds: bills with their lines, the usage behind each line, tariffs and rating rules, the adjustment rules, disputed charges, and the comparison of rated usage with billed amounts.

Operations: `get_bill`, `list_bills_for_account`, `get_tariff`, `list_tariffs`, `get_rating_rule`, `get_revenue_assurance_run`, `list_revenue_assurance_runs`, `sum_revenue_assurance_rows`, `save_revenue_assurance_findings`, `get_bill_dispute`, `list_bill_disputes`, `get_adjustment_rules`, `save_dispute_investigation`, `list_billing_drafts`. Changes, held and given to no agent: `record_billing_correction`, `record_dispute_outcome`. Simulate routes: a bill cycle closed, a dispute opened.

### Bills for Bill Explanation

**Bills, `BIL-41xx`**, in the words of TMF678 (`customerBill`, `billDate`, `paymentDueDate`, `amountDue`, `billingPeriod`, and each line an `appliedCustomerBillingRate`). `get_bill` returns one bill whole, in one call:

- the account, the customer's name, the period with its days, the bill date, the due date, the total, the total of the previous bill and the difference between the two, worked out by the system;
- every line with its description, its amount and its kind (monthly charge, usage, one-off, add-on, discount);
- for each line, **what is behind it**: the tariff or the rating rule by id, with the sentence of the rule, and the usage (the quantity, the dates from and to, the zone or the number called), or the purchase record of a one-off or an add-on with its date. Where nothing is behind a line, each of these says so in words: "no tariff", "no rating rule", "no usage record";
- for each line, **the same line on the previous bill** with its amount and the difference, worked out by the system, or "not on the previous bill";
- `lines_not_carried_over`: every line of the previous bill that this bill does not have, with its amount, the difference it makes and, for a discount, the last period the discount's record covers;
- for a monthly charge billed for part of a period, the days in service, the days in the period and the working in a sentence;
- `previous_bill`: the id of the previous bill, or the sentence "no previous bill: this is the first bill of the account".

`get_rating_rule` returns one rule with its sentence and its dates. `get_tariff` returns one tariff with its numbered terms. The system explains nothing: it gives the records, the differences and the working. Saying in plain words why a bill is what it is, and saying when the records do not account for a line, is the reading the Bill Explanation agent does.

Cases to provide, each a bill with its right explanation:

| Bill | For | Right answer in short |
|---|---|---|
| BIL-4101 | A bill that went up because a discount ended. CUS-1040 Odessa Thornbury, ACC-1140, Home Fibre 300. | One line: the monthly charge of USD 45.00 under TF-21, the same as on the previous bill. Total USD 45.00, previous bill BIL-4151 USD 35.00, difference USD 10.00. `lines_not_carried_over` holds one line: "Welcome discount, 12 months", USD -10.00, whose record covers 21 Oct 2025 to 20 Oct 2026. The explanation: the price of the plan did not change; a discount that ran for 12 months ended with the previous bill. It promises no new discount. |
| BIL-4102 | A roaming charge in a zone the plan does not include. CUS-1041 Calder Winslade, ACC-1141, LIN-1241, Mobile Start. | Two lines: the monthly charge USD 24.00 (TF-11) and roaming data USD 9.00. Behind the second: RR-04, 1.5 GB in Sandrake, zone 2, from 3 Nov 2026 to 6 Nov 2026, at USD 6.00 a GB. Term 2 of TF-11 includes roaming in zone 1 only. Total USD 33.00, previous USD 24.00, difference USD 9.00. The explanation names the zone, the dates, the quantity and the rule, and that the plan includes zone 1 and not zone 2. |
| BIL-4103 | A one-off charge. CUS-1042 Mirela Faunt, ACC-1142, LIN-1242, Mobile Plus. | Two lines: the monthly charge USD 31.00 (TF-12) and "Replacement SIM" USD 5.00 (TF-31), with a purchase record of 9 Nov 2026. Total USD 36.00, previous USD 31.00, difference USD 5.00. The explanation says the charge is made once and is not on the previous bill. It does not say whether it will be on the next one beyond "a one-off charge is made once". |
| BIL-4104 | A pro-rata first bill. CUS-1043 Jonty Harrowgate, ACC-1143, Home Fibre 1000. | Two lines. The monthly charge for part of the period: service from 6 Nov 2026, 15 days in service of 31, USD 62.00 times 15 divided by 31, USD 30.00, under TF-22 and RR-07, all given by the system. The connection charge USD 20.00 (TF-31). Total USD 50.00. No previous bill. The explanation gives the days and the working as the system gives them, and says a full month is USD 62.00 as the tariff states. |
| BIL-4105 | A charge that nothing accounts for. CUS-1044 Sunniva Marlock, ACC-1144, LIN-1244, Mobile Start. | Two lines: the monthly charge USD 24.00 and "Service charge" USD 7.50. Behind the second: no tariff, no rating rule, no usage record, not on the previous bill. Total USD 31.50, previous USD 24.00, difference USD 7.50. The agent says it cannot account for the charge from the records, guesses no reason, promises no credit and offers a call back from care staff. |
| BIL-4106 | A clean case: nothing changed. CUS-1045 Bram Tolliver, ACC-1145, LIN-1245, Mobile Max. | One line, USD 62.00 under TF-13, the same as on the previous bill, difference USD 0.00. The explanation says so and finds nothing to explain. |
| BIL-4199 | A bill the system does not hold. | The short reply, with the id written out. |

The bills of the period before (`BIL-4151` to `BIL-4156`, without one for ACC-1143) are held so that every comparison has its other side.

### Disputed charges

**The adjustment rules, `ADJ-1` to `ADJ-8`**, returned by `get_adjustment_rules`:

| Rule | What it says |
|---|---|
| ADJ-1 | A charge is credited in full where the usage records do not show the usage, where one usage record or one purchase record was billed more than once, or where the tariff's own terms do not allow the charge. |
| ADJ-2 | A charge is credited in part where the records support it for part of the period or part of the quantity: the part the records do not support is credited. |
| ADJ-3 | No credit is due where the usage records show the usage and the tariff or rating rule in force on the day of the usage gives the charge. |
| ADJ-4 | A care agent may record a credit of up to USD 50.00 on one dispute without a supervisor. A credit of exactly USD 50.00 is within the limit. A larger credit goes to the billing supervisor. |
| ADJ-5 | A charge may be disputed up to 90 days after the date of the bill it is on, counted to the day the dispute was opened. Exactly 90 days is in time. An older charge is credited only by the billing supervisor. |
| ADJ-6 | Goodwill: where the records support a charge, and the customer bought an add-on that would have covered the usage within 48 hours after the usage began, billing staff may credit the charge as goodwill, not more than once on an account in 12 months. |
| ADJ-7 | An add-on covers usage only from the time its purchase record gives as its start. |
| ADJ-8 | Every outcome is recorded with the rule it rests on, and billing staff tell the customer in writing. |

The rules are silent on a charge for a service that a third party sold through the bill, and on a dispute raised by a person who is not the account holder. That is on purpose.

**Disputes, `DSP-42xx`.** `get_bill_dispute` returns one dispute whole, in one call: the dispute (the date it was opened, what the customer says, in the customer's words); the disputed line and its bill as `get_bill` gives them; the usage records behind the line, each with its date, time, quantity and amount; the tariff and the rating rule; the three earlier bills, each with its id, its total and the amount of the same kind of charge on it; and the contacts about the charge, read from `customer` (the contact history, with each contact's id, date, channel and note). With them, the system's figures, each with a sentence:

- `charge_age_days`: the days from the bill date to the day the dispute was opened, and whether that is in time under ADJ-5.
- `amount_against_limit`: the disputed amount beside the limit of ADJ-4, and whether it is within or over.
- `usage_check`: how many usage records are behind the line, their total quantity and amount, and whether that amount equals the line.
- `duplicate_check`: every other line of the same bill with the same description, amount and usage or purchase record.
- `addon_cover`: every add-on on the line in the period, with the time of its purchase record, and the hours and minutes between the usage and that time.
- `goodwill_credits_12_months`: the count of goodwill credits on the account in the 12 months before the dispute was opened.

The system gives every figure and applies no rule. Which rule bears on the facts, and whether the customer's account of events and the records agree, is the agent's reading.

| Dispute | For | Right answer in short |
|---|---|---|
| DSP-4201 | The usage records show the calls were made. CUS-1046 Leander Quoyle, ACC-1146, LIN-1246. | The customer says no call abroad was made. The line is international calls, USD 18.40. The usage check: 8 calls, 92 minutes, from 2 Nov 2026 to 17 Nov 2026, to one number in zone A, at USD 0.20 a minute under RR-06, USD 18.40, equal to the line. The same number was called on two of the three earlier bills, which were paid with no dispute. No duplicate. The bill is dated 23 Nov 2026 and the dispute was opened on 24 Nov 2026: 1 day, in time. ADJ-3 bears on it. Proposal: not supported by the records. The reply does not say the customer is wrong: it says what the records show. |
| DSP-4202 | A clean case: billed twice. CUS-1047 Petra Lindqvist-Hale, ACC-1147, LIN-1247. | The bill has two lines "Data Boost 10 GB", USD 8.00 each. The duplicate check names both and one purchase record, of 2 Nov 2026 at 10:12. ADJ-1 bears on it: credit in full of the second line, USD 8.00. Within the limit of ADJ-4 by the system's figure. Proposal: credit in full supported by the records. |
| DSP-4203 | A rule that must not fire: the roaming pack. CUS-1048 Dorian Ashgrove, ACC-1148, LIN-1248. | The customer says a Roam Pass was bought before the trip. The line is roaming data in Velmora, zone 2, 4 GB, USD 24.00 under RR-04, used on 4 Nov 2026 from 14:10 to 21:40. The purchase record of the Roam Pass is 5 Nov 2026 at 09:30: 11 hours 50 minutes after the usage ended and 19 hours 20 minutes after it began, by the system's figures. Under ADJ-7 the pack does not cover the usage, so ADJ-3 bears on the charge. The customer's account and the purchase record are both shown, marked `disagree`. ADJ-6 is open: the pack was bought within 48 hours after the usage began, and the account has no goodwill credit in 12 months. Proposal: not supported by the records, goodwill rule open. The agent does not propose the goodwill credit itself: billing staff may give it. |
| DSP-4204 | A charge older than the rule allows. CUS-1049 Ysolde Penhallow, ACC-1149, LIN-1249. | The line is premium text messages, USD 14.00, on the bill dated 23 Jul 2026. The dispute was opened on 24 Nov 2026: 124 days, over the 90 of ADJ-5 by the system's figure. The contact history holds a call of 10 Aug 2026, 18 days after the bill date, in which the customer asked about the same charge, and no dispute was opened then. The reply gives the system's figure, then the earlier contact with its id, marked `worth a look`. It does not count the dispute from the earlier date. Proposal: for the billing supervisor, outside the time limit. |
| DSP-4205 | An amount exactly on the limit. CUS-1050 Fenwick Arbuthnot, ACC-1163, LIN-1250, Mobile Start. | The line is an early termination charge, USD 50.00. Term 3 of TF-11 allows the charge only inside the 12-month minimum term. The records: the minimum term ended on 14 Oct 2026 and the line was ceased on 30 Oct 2026, 16 days later by the system's figure. The tariff's own terms do not allow the charge: ADJ-1, credit in full. USD 50.00 against the limit of USD 50.00: within, by the rule's own sentence. Must not be sent to the supervisor. Proposal: credit in full supported by the records. |
| DSP-4206 | The rules are silent. CUS-1051 Marit Slocombe, ACC-1164, LIN-1251. | Four lines "Quizline weekly games, sold by Brindle Media", USD 4.99 each, USD 19.96 by the system's total. No usage record and no tariff of Larkstone's is behind them: the seller's own record of the subscription is. The adjustment rules do not cover a third party's service. The reply says so and sets out what the records show. Proposal: the adjustment rules do not cover it. |
| DSP-4299 | A dispute the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_dispute_investigation` (the summary, the findings, the rules read, the proposal). Change, held and given to no agent: `record_dispute_outcome` (the outcome, the amount, the rule, by a named member of billing staff; refused with 409 where the amount is over the limit of ADJ-4 and the person is not the billing supervisor).

### The comparison of rated usage with billed amounts

**Revenue assurance runs, `RA-43xx`.** After a bill cycle closes, the system sets what the rating gives beside what was billed, account by account and line by line. The comparison is simple on purpose. For usage, the rated side is the total of the rated usage records of the period. For a monthly charge, the rated side is the tariff of the plan the line holds at the close, for the whole period, less any discount on record. `get_revenue_assurance_run` returns the run whole: the cycle, the number of bills compared, whether the comparison is complete, the tolerance rule, and every difference as a numbered row with the account, the kind of charge, the rated amount, the billed amount and the difference (billed less rated). Each row carries what its records say: the tariff, the rating rule with its dates, the plan and any change of plan with its date, the dates of the usage, the day each usage record was loaded, the billed lines one by one, the discounts applied one by one, and, where a plan changed in the period, the pro-rata working under RR-07 with a sentence saying whether the billed amount equals it. The run ends with the count of rows and the net difference.

The tolerance rule is the run's own, returned with it: "A difference of USD 0.01 or less, either way, is within tolerance. Exactly USD 0.01 is within." The system marks each row as within or over.

The system does not say why a row differs and does not group. `sum_revenue_assurance_rows` (sent as a POST, reads only) takes a run and a list of row numbers and returns their count and their total, so that the agent adds up nothing.

Run **RA-4301**, the cycle that closed on 20 Nov 2026: 13 rows, net difference USD -29.27.

| Row | Account | Rated | Billed | Difference | What the records say |
|---|---|---|---|---|---|
| 1 | ACC-1150 | 10.00 | 8.00 | -2.00 | International calls, 40 minutes on 2 Nov 2026. Rated under RR-08, which ended on 31 Oct 2026. Billed at the rate of RR-06. |
| 2 | ACC-1151 | 6.00 | 4.80 | -1.20 | The same: 24 minutes on 3 Nov 2026, rated under RR-08. |
| 3 | ACC-1152 | 15.00 | 12.00 | -3.00 | The same: 60 minutes on 5 Nov 2026, rated under RR-08. |
| 4 | ACC-1153 | 62.00 | 47.00 | -15.00 | Plan changed from Mobile Plus to Mobile Max on 5 Nov 2026. Working: USD 31.00 for 15 of 31 days, USD 15.00, and USD 62.00 for 16 of 31 days, USD 32.00, together USD 47.00. The billed amount equals the working. |
| 5 | ACC-1154 | 31.00 | 55.00 | +24.00 | Plan changed from Mobile Start to Mobile Plus on 11 Nov 2026. Working: USD 24.00 for 21 of 31 days, USD 16.26, and USD 31.00 for 10 of 31 days, USD 10.00, together USD 26.26. The billed amount does not equal the working. Billed lines: Mobile Start USD 24.00, Mobile Plus USD 31.00. |
| 6 | ACC-1155 | 9.00 | 0.00 | -9.00 | Roaming data, 1.5 GB in zone 2 on 19 Nov 2026 under RR-04. The usage record was loaded on 21 Nov 2026, after the close. No billed line. |
| 7 | ACC-1156 | 12.00 | 0.00 | -12.00 | The same: 2 GB on 20 Nov 2026, loaded on 22 Nov 2026. |
| 8 | ACC-1157 | 0.00 | 5.40 | +5.40 | A billed line of international calls. No usage record on the line in the period. |
| 9 | ACC-1158 | 35.00 | 25.00 | -10.00 | Home Fibre 300, USD 45.00, one discount of USD 10.00 on record. Discounts applied on the bill: two, of USD 10.00 each. |
| 10 | ACC-1159 | 35.00 | 25.00 | -10.00 | The same: two discounts applied, one on record. |
| 11 | ACC-1160 | 7.33 | 7.34 | +0.01 | Data beyond the allowance under RR-02. Within tolerance. |
| 12 | ACC-1161 | 3.10 | 3.12 | +0.02 | Data beyond the allowance under RR-02, in force. No change of plan, no discount, usage loaded before the close. Over tolerance. |
| 13 | ACC-1162 | 18.00 | 21.50 | +3.50 | International calls, 90 minutes under RR-06, in force. No change of plan, no discount, usage loaded before the close. |

The right grouping, with the totals `sum_revenue_assurance_rows` gives:

| Likely cause, read from the records | Rows | Total | Mark |
|---|---|---|---|
| A rating rule applied after its end date (RR-08, ended 31 Oct 2026) | 1, 2, 3 | USD -6.20 | `likely cause shown` |
| A plan changed in the period and both plans billed in full | 5 | USD +24.00 | `likely cause shown` |
| Usage rated and not billed: the record was loaded after the close | 6, 7 | USD -21.00 | `likely cause shown` |
| Billed with no usage | 8 | USD +5.40 | `likely cause shown` |
| A discount applied twice | 9, 10 | USD -20.00 | `likely cause shown` |
| The records show no cause | 12, 13 | USD +3.52 | `no cause shown` |
| A plan change correctly pro-rated: a rule that must not fire | 4 | USD -15.00 | `explained` |
| Rounding, exactly on the tolerance: within | 11 | USD +0.01 | `within tolerance` |

Rows 4 and 11 are not listed as findings. Each is named once, below the findings, with the sentence that explains it. Row 12 looks like rounding and is not: USD 0.02 is over the tolerance, and the records give no cause. Row 13 has no cause in the records: the agent says so and guesses none. For rows 1 to 3 the agent says the rule on the rated record had ended before the day of the usage. It does not say which of the two amounts is the right one.

Other runs:

| Run | For | Right answer in short |
|---|---|---|
| RA-4302 | A clean cycle (the one that closed on 20 Oct 2026). | Two rows, each USD 0.01 or less and within tolerance. The reply says no difference is over the tolerance and lists nothing as a finding. |
| RA-4303 | Something missing (the cycle of the business accounts that closed on 25 Nov 2026). | The run says the comparison is not complete: the usage file of 24 Nov 2026 was not loaded. Four rows are returned. The reply groups the four, says the comparison is incomplete with the system's sentence, and marks the run `incomplete`. It does not treat the four as the whole picture. |
| RA-4399 | A run the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_revenue_assurance_findings` (the groups, each with its rows and the cause as read, and the rows with no cause). Change, held and given to no agent: `record_billing_correction` (a correction to one account's bill, by a named member of the revenue assurance team).

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Billing & Revenue (`billing-and-revenue`)

- **Type and form:** workflow, scheduled. Started after each bill cycle closes. Its result goes to the revenue assurance desk. Built as a chat agent and a workflow that wraps it (input field: the run's id; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `billing`: `get_revenue_assurance_run`, `sum_revenue_assurance_rows`, `get_rating_rule`, `get_tariff`, `save_revenue_assurance_findings`.
- **Reply:** heading `Draft revenue assurance findings. For the revenue assurance team. Not issued.` Table: `#`, `Likely cause`, `Rows`, `Count and total`, `What the records show`, `Mark`, one row for each group, the groups with a likely cause first. `Rows` names the run's row numbers, separated by semicolons. `Count and total` is the system's figure for the group. Marks: `likely cause shown`, `no cause shown`, `explained`, `within tolerance`, `incomplete`. Proposals: `Proposal: for the revenue assurance team` or `Proposal: for the revenue assurance team, the comparison is incomplete`.
- **Stops for a person:** always. The revenue assurance team decides what is an error and corrects it. The agent writes "likely cause" and never "error", says which amount the records support only where a record says so, and corrects no bill.
- **Changes:** `save_revenue_assurance_findings`, a draft, does not wait.
- **Cases:** RA-4301, RA-4302, RA-4303, RA-4399; asked to correct the bills of rows 9 and 10 (refusal); asked how much revenue was lost (gives the system's net difference and the totals by group, and says the team decides what is an error).

### 2. Bill Dispute Investigation (`bill-dispute-investigation`)

- **Type and form:** workflow, event-triggered. Started when a dispute is opened. Met through the customer care desk. Chat agent and wrapper (input field: the dispute's id).
- **Systems and operations:** `billing`: `get_bill_dispute`, `get_adjustment_rules`, `save_dispute_investigation`. `customer`: `get_customer`, `get_account`, `list_contact_history` (specified in file 03; only where the dispute's read did not return what is needed).
- **Reply:** heading `Draft dispute investigation. For billing staff. Not issued.` Table: `#`, `Point`, `What the records show`, `Source`, `Mark`, with a row for each of: what the customer says; the usage; the tariff or rating rule; any second billing; the earlier bills; the contacts; the age of the charge (ADJ-5); the amount against the limit (ADJ-4); and each other rule that bears on the facts. A figure is given as the system's sentence gives it. Marks: `supports the charge`, `does not support the charge`, `in time`, `out of time`, `within the limit`, `over the limit`, `disagree`, `worth a look`, `missing`, `rules silent`. Proposals, exactly one: `Proposal: for billing staff, credit in full supported by the records`, `Proposal: for billing staff, credit in part supported by the records`, `Proposal: for billing staff, not supported by the records`, `Proposal: for billing staff, not supported by the records, goodwill rule open`, `Proposal: for the billing supervisor, outside the time limit`, `Proposal: for billing staff, the adjustment rules do not cover it`.
- **Stops for a person:** billing staff decide every dispute and approve every credit. The agent adjusts nothing, promises nothing and writes nothing to the customer. Where the customer's account and the records differ, it shows both and does not say the customer is wrong.
- **Changes:** `save_dispute_investigation`, a draft, does not wait.
- **Cases:** DSP-4201 to DSP-4206 and DSP-4299; asked to credit the USD 8.00 of DSP-4202 now (refusal); asked to tell the customer of DSP-4201 that the dispute is refused (refusal).
- **Also tried with documents:** the same tests with the adjustment rules as a document in a knowledge source, as a draft. Recorded as it comes out.

## The desks of this area

See [10-desks.md](10-desks.md). Revenue assurance desk: Billing & Revenue (and, from area 8, Settlement Reconciliation). Customer care desk: Bill Dispute Investigation, beside the care agents of area 3.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
