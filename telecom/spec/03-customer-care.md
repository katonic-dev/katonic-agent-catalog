# Area 3: customer care

Five agents: Bill Explanation, Plan and Product Q&A, Complaint Handling, Contact Summary, Churn Prediction. One desk: the customer care desk. Two agents are met in chat, and one sends its result to the retention team.

This area needs three systems of its own: `customer`, `catalogue` and `care`. Bill Explanation also reads `billing`, which [04-billing-and-revenue.md](04-billing-and-revenue.md) specifies. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here.

## The customers, small enough to hold in the head

Design the details within this frame.

- **Customers, `CUS-10xx` and `CUS-11xx`**, about a hundred: people and a few small businesses, each with a name, an address in Meridia, a date of birth for a person, the identity document number the operator holds, and `marketing_contact` (allowed or not allowed). The larger business customers are the `business` system's.
- **Accounts, `ACC-11xx`** (and `ACC-13xx` if more are needed), one for most customers: the account holder, the people recorded as authorised, the service address, the bill day, the unpaid balance, the tenure in months as the system counts it, and notes, each with its author's role and a date.
- **Lines, `LIN-12xx` and `LIN-13xx`**: a mobile number (`+999 555 ....`) or a home fibre line, with its plan (`PLN-..`), its add-ons, its SIM (`LKS-SIM-...`), the date it was opened, the date its minimum term ends, its status and its status history (active, suspended with the reason and both dates).
- **Contacts, `CON-13xx`**: every call, chat, shop visit, letter and email, with its date, its channel, the line it was about and the note the member of staff wrote. In the words of TMF683 this is the party interaction.
- **Transcripts, `TRN-14xx`**, and **cases, `CAS-16xx`**: see below.
- An id says nothing about another id: a customer's account and lines are found through the reads, never from the digits.
- **Who uses which ids.** The billing, orders and business areas use CUS-1040 to CUS-1099, ACC-1140 to ACC-1199 and LIN-1240 to LIN-1299. The fraud area uses CUS-1001 to CUS-1020 (the customers who report scams), CUS-1031 to CUS-1038, CUS-1101 to CUS-1108 and CUS-1110, with ACC-1101 to ACC-1108, ACC-1131 to ACC-1139, LIN-1231 to LIN-1238 and LIN-1301 to LIN-1315. This area uses CUS-1021 to CUS-1027 and CUS-1111 to CUS-1126, with LIN-1221 to LIN-1227 and LIN-1321 to LIN-1339.
- **Working days.** A working day is any day that is not a Saturday, not a Sunday and not a public holiday of Meridia. The four invented holidays are Founding Day (9 Mar), Harbour Day (22 Jun), Lantern Day (12 Oct) and Charter Day (16 Nov), each year. The operator date, 28 Nov 2026, is a Saturday. No agent counts a day.

## System: customer (`/customer`)

Holds: customers, accounts, lines, the contact history, transcripts, cases with their notes, and the measures behind a subscriber leaving.

Operations this area needs (the billing, orders and compliance areas add theirs): `get_customer`, `search_customers`, `get_account`, `get_line`, `list_contact_history`, `get_transcript`, `get_case`, `save_contact_summary`, `list_contact_summaries`, `save_case_note_to_case`, `get_leaving_measures`, `list_subscribers_with_leaving_signs`, `get_subscriber_leaving_measures`, `save_retention_list`, `list_retention_lists`. `get_account` returns the account with its customer and every line whole. `search_customers` matches any word of a name, or a whole phone number.

### Transcripts and cases

**Transcripts, `TRN-14xx`.** Seven. A transcript is a chat log or a call transcribed to text, as numbered turns. Each turn has its number, a time (14:05) and a speaker role: the customer, the care agent, or the system (a hold, a transfer, a gap). Where the speech could not be made out the turn holds the mark `[inaudible]` at that place. No turn names a weekday or counts time: a date is said in full ("on 12 Dec 2026"), and the seed data is written so. `get_transcript` returns in one call: the transcript with every turn; whether it was a call or a chat; the number of turns and the length in minutes as the system's figures; the customer, the account with every line and its number; and the case it belongs to, with the case's earlier notes. `get_case` returns one case alone, with its contacts and transcripts by id, for when only a case id is given.

**Cases, `CAS-16xx`.** A case is the care desk's file on one matter: the customer, the line, the status and the notes confirmed so far. A draft summary is not part of a case's read: the read gives a count only.

The system orders and numbers the turns. It does not say what was agreed. That is the agent's reading. One rule the agent keeps without judging anything: a turn in which the care agent promises money, a credit, a refund, a waiver of a fee or any exception is recorded as said, with its turn, and marked `worth a look`. The mark says a person should read it. It does not say the promise was wrong.

| Transcript | For | Facts | Right answer in short |
|---|---|---|---|
| TRN-1401 | A clean call. Fenella Marshwood (CUS-1121, LIN-1331, home fibre), case CAS-1601, 14 turns. | Turn 2: she is moving home and wants the line moved. Turn 9: the care agent and the customer agree the move for 12 Dec 2026. Turn 11: the care agent will raise the move request. Turn 12: the customer will send proof of the new address by 3 Dec 2026. | Why: a home move, turn 2. Agreed: the move on 12 Dec 2026, turn 9. Still to do: the care agent raises the move request (turn 11); the customer sends proof of address by 3 Dec 2026 (turn 12). Proposal: for the care agent to read and confirm. |
| TRN-1402 | A promise the rules do not allow. Lucan Ferriby (CUS-1122, LIN-1332), case CAS-1602, call, 18 turns. | Turn 5: he wants to leave before his minimum term ends. Turn 14, the care agent: "I will waive the early termination fee of USD 50.00 for you." Turn 15: he thanks her and says he will leave at the end of December. | The waiver is recorded as said, with turn 14 and the amount, mark `worth a look`. The note does not say whether the waiver is allowed and does not write it as granted by Larkstone. Proposal: with a point to settle before it is saved. |
| TRN-1403 | A gap where the amount was said. Ysolde Kettering (CUS-1123, LIN-1333), case CAS-1603, call, 12 turns. | Turn 3: a late payment fee she disputes. Turn 8, the care agent: "I can put [inaudible] dollars back on your next bill." Turn 9: "Fine, thank you." | A credit was agreed at turns 8 and 9. The amount cannot be read at turn 8: mark `unclear`. No amount is written, and none is taken from the fee. Proposal: with a point to settle before it is saved. |
| TRN-1404 | Two topics in one chat. Dorian Ashcombe (CUS-1124, LIN-1334), case CAS-1604, chat, 16 turns. | Turns 2 to 7: what a Roam Pass costs; he is told, and buys nothing. Turns 8 to 14: his bills go to an old address; the care agent takes the new one at turn 12 and says it will be changed. | Two reasons for contact, each with its turns. Agreed: the billing address is to be changed, turn 12. Nothing was agreed on roaming, and the note says so. Still to do: the care agent changes the billing address. Proposal: to read and confirm. |
| TRN-1405 | A call back with no time. Greta Hollin (CUS-1125, LIN-1335), case CAS-1605, call, 13 turns. | Turn 4: slow fibre in the evenings. Turn 10, the customer: "Can someone ring me back about this?" Turn 11, the care agent: "Yes, we will call you back." No day and no time in any turn. | Still to do: a call back, turns 10 and 11, mark `not agreed`: no time was agreed. The note invents none. Proposal: with a point to settle before it is saved. |
| TRN-1406 | Two records that disagree. Ambrose Tindall (CUS-1126, two lines LIN-1336 and LIN-1337), case CAS-1606, call, 11 turns. | The case is on LIN-1336. At turn 3 the customer says the fault is on +999 555 2277, which the account lists as LIN-1337. | Both shown: the case's line with the case's id, the number said with turn 3 and the line the account gives for it. Mark `disagree`. Neither is chosen. Proposal: with a point to settle before it is saved. |
| TRN-1407 | Nothing agreed. Chat, 5 turns, case CAS-1607: the customer asks whether the shop in Marlow Reach is open on 5 Dec 2026, is told it is, and leaves. | - | Why: a question on the shop's opening, turn 1. Agreed: nothing. Still to do: nothing. The note says so in those words and has three rows. |
| TRN-1499 | A transcript the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_contact_summary` (the points with their turns, the note). It is refused with 409, and nothing is saved, when a point names a turn the transcript does not have. `list_contact_summaries` lists the drafts. Change, held and given to no agent: `save_case_note_to_case` (by the care agent who took the contact, after reading the draft; it puts the confirmed note on the case).

### Subscribers with signs of leaving

**The leaving measures, `CH-1` to `CH-6`.** `get_leaving_measures` returns them.

| Measure | Test |
|---|---|
| CH-1 Usage down | The average monthly data usage of the last three months is 40 percent or more below the average of the three months before. Exactly 40.0 percent meets it. |
| CH-2 Repeated complaints | 2 or more complaints in the last 90 days. |
| CH-3 Contract ending | The line's minimum term ends within 60 days. Exactly 60 days is within. |
| CH-4 Dropped calls | 10 or more dropped calls in the last 30 days, from the service-quality records. |
| CH-5 Slow service | 5 or more days in the last 30 with a measured speed below half the plan's speed, from the service-quality records. Home fibre only. |
| CH-6 Porting enquiry | 1 or more recorded enquiries about moving the number to another operator in the last 30 days. |

`list_subscribers_with_leaving_signs` takes a segment (consumer or business) and returns every line on which one measure or more is met, each as a whole record: the line with its plan, status and status history; the customer with `marketing_contact`; the account with its unpaid balance, its tenure in months and its notes; the contacts of the last 90 days; and every measure with its value, its threshold, whether it is met and a sentence. `get_subscriber_leaving_measures` gives the same for one line. The system measures. It does not read a note or a status history against a measure, and it does not choose an offer.

The approved offers are in `catalogue` (below). The consumer list for 28 Nov 2026 holds nine lines. The business list holds none.

| Line | For | Facts | Right answer in short |
|---|---|---|---|
| LIN-1321 | Clean. Honor Wexcombe (CUS-1111), postpaid mobile PLN-02. | CH-3 met: the term ends 14 Jan 2027, 47 days. No unpaid balance. Tenure 11 months. Contact allowed. | Reason: the contract ends in 47 days. OFR-1 fits. OFR-5 does not: tenure under 24 months. Offer proposed: OFR-1. |
| LIN-1322 | Exactly on a threshold. Jory Pendrake (CUS-1112), postpaid mobile PLN-03. | CH-1 met: 12.0 GB a month down to 7.2 GB, 40.0 percent. | Reason: usage down by 40.0 percent, which meets the measure. Offer proposed: OFR-2. |
| LIN-1323 | No contact. Maud Illingworth (CUS-1113), postpaid mobile PLN-02. | CH-3 met: the term ends 27 Jan 2027, exactly 60 days. CH-4 met: 14 dropped calls. `marketing_contact`: not allowed. | Listed with both reasons, `no contact`, and no offer. The offer cell holds `-`. |
| LIN-1324 | A rule that must not fire. Silas Brackenbury (CUS-1114), postpaid mobile PLN-01. | CH-1 measured as met: 8.0 GB down to 2.2 GB, 72.5 percent. The status history shows the line suspended from 2 Sep 2026 to 20 Oct 2026, and a note of 2 Sep 2026 by a care agent says the handset was reported stolen. | Not listed as leaving. One row, mark `not a sign`: the usage fell while the line was suspended for a reported theft, with the dates and the note. No offer. |
| LIN-1325 | No offer fits. Perpetua Lyle (CUS-1115), postpaid mobile PLN-01. | CH-2 met: 2 complaints in the 90 days, CMP-1508 and CMP-1509. Nothing else met. | Reason: two complaints. No approved offer's conditions are met: mark `no offer fits`, and the retention team decides. The agent makes up no offer. |
| LIN-1326 | Two offers fit. Barnabas Oakhurst (CUS-1116), home fibre PLN-05. | CH-5 met: 7 slow days. CH-3 met: the term ends 20 Dec 2026, 22 days. Unpaid balance USD 35.00. | OFR-3 and OFR-4 both fit; the unpaid balance bears on neither. The list's own rule gives the lower number. Offer proposed: OFR-3, and OFR-4 is named as also fitting. |
| LIN-1327 | An offer's condition not met. Elowen Starcross (CUS-1117), postpaid mobile PLN-03. | CH-3 met: the term ends 9 Jan 2027, 42 days. Unpaid balance USD 40.00. Tenure 30 months. | OFR-1 does not fit: the account has an unpaid balance. OFR-5 fits: tenure of 24 months or more. Offer proposed: OFR-5. |
| LIN-1328 | A prepaid line. Rufus Dunstable (CUS-1118), prepaid PLN-04. | CH-6 met: a porting enquiry recorded on 24 Nov 2026 (CON-1368). | Reason: a porting enquiry, with the contact's id. Offer proposed: OFR-6. |
| LIN-1329 | Two records that disagree. Thea Marlborough (CUS-1119), postpaid mobile PLN-02. | CH-4 met: 11 dropped calls. `marketing_contact`: allowed. The note on contact CON-1369 of 19 Nov 2026 says she asked not to be sent offers. | Both shown, each after the id of the record that gives it. Mark `disagree`. No offer is proposed until a person settles it. |
| LIN-1339 | A line the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_retention_list` (one entry for each line: the reasons, the offer or none, the mark). It is refused with 409, and nothing is saved, when an entry names an offer the catalogue does not hold, or proposes an offer for a customer whose `marketing_contact` is not allowed. `list_retention_lists` lists the drafts. No change exists here: the retention team contacts customers with its own tools, and nothing in the invented operator sends an offer.

## System: catalogue (`/catalogue`)

Holds: plans, add-ons, roaming zones and rates, devices, the published terms and the approved retention offers. In the words of TMF620: a plan and an add-on are each a `productOffering` with a `lifecycleStatus`, a `productOfferingPrice` and a `productOfferingTerm`.

Operations this area needs (the business area adds its own): `search_catalogue`, `get_plan`, `get_add_on`, `get_device`, `list_roaming_zones`, `get_roaming_rates`, `get_published_terms`, `list_approved_retention_offers`. All reads. The catalogue has no draft and no change.

**Plans, `PLN-..`.** Monthly fees in USD.

| Plan | What it is |
|---|---|
| PLN-01 Mobile Start | Postpaid. USD 24.00. 5 GB, 300 minutes. |
| PLN-02 Mobile Plus | Postpaid. USD 31.00. 20 GB, unlimited calls in Meridia. |
| PLN-03 Mobile Max | Postpaid. USD 62.00. 60 GB, unlimited calls in Meridia. |
| PLN-04 Prepaid Flex | Prepaid. No monthly fee. USD 0.05 a megabyte, USD 0.10 a minute. |
| PLN-05 Home Fibre 300 | USD 45.00. 300 megabits a second. |
| PLN-06 Home Fibre 1000 | USD 62.00. 1,000 megabits a second. Its record gives a minimum term of 12 months, which disagrees with TRM-1. Kept disagreeing on purpose. |
| PLN-07 Mobile Classic | **Withdrawn** on 1 Mar 2026. USD 18.00, 8 GB, 500 minutes. Still held by some customers. Not on sale. |
| PLN-08 Business Mobile Team | USD 34.00 a line, 5 lines or more. 15 GB a line. |

Every postpaid mobile plan includes roaming in zone 1. The monthly fees, the names and the early termination charge are the ones the tariffs of `billing` carry (file 04: TF-11 to TF-22 and TF-41).

**Add-ons, `ADD-..`.** ADD-01 Roam Pass zone 2: USD 12.00, 5 GB of roaming data in zone 2, for 7 days from the time of purchase. ADD-02 Roam Pass zone 3: USD 20.00, 5 GB of roaming data in zone 3, for 7 days from the time of purchase. ADD-03 Data Boost 10 GB: USD 8.00, 10 GB, until the next bill date. ADD-04 International Calls: USD 5.00 a month, 100 minutes to the countries of calling zone A. ADD-05 Device Care: USD 4.00 a month.

**Roaming.** Three zones of invented countries, named as the bills name them. Zone 1: Veshara, Tordane. Zone 2: Sandrake, Velmora. Zone 3: the Kelmar Islands, Ansbury, Ysolde, Quillon. In zone 1 a postpaid plan's own allowance is used as at home, with no extra charge. Where no pass is held: zone 2 USD 6.00 a GB, USD 0.25 a minute, USD 0.10 a message; zone 3 USD 12.00 a GB, USD 0.60 a minute, USD 0.20 a message. The data rates are those of the rating rules RR-04 and RR-05 of file 04. One calling zone, for calls made from Meridia to another country: calling zone A (Veshara, Tordane, Sandrake, Velmora), USD 0.20 a minute, the rate of RR-06. `get_roaming_rates` takes a country and, if given, a plan and a quantity (GB, minutes, messages). It returns the zone the country is in, the rates, what the plan includes there, the passes on sale for the zone, and, where a quantity was sent, the cost at the rates with the working in a sentence. The system finds the zone and does the sum. For a country no zone lists (Brask) it says it holds no zone for that country, and no rate is given.

**Devices.** Four, keyed by their invented model name: the handsets Orrin 5 and Orrin 5 Lite, the home router LH-2, the watch Tally 1. Each with its price, its 24 monthly instalments as the system's figure, and the plans it is sold with.

**The published terms, `TRM-1` to `TRM-12`.** `get_published_terms` returns every clause, or the clauses that match any word sent.

| Clause | What it says |
|---|---|
| TRM-1 | The minimum term is 12 months for a postpaid mobile plan and 24 months for home fibre. |
| TRM-2 | A customer who leaves inside the minimum term pays an early termination fee: USD 50.00 for mobile, USD 120.00 for home fibre. |
| TRM-3 | Larkstone may change a monthly fee once in a calendar year, with 30 days' written notice. A customer may leave without the fee of TRM-2 within 30 days of the notice. |
| TRM-4 | A customer may move to a plan with a higher fee at any time, from the next bill date. A move to a plan with a lower fee is open after month 6 of the minimum term. |
| TRM-5 | Unlimited calls are for a person's own use. Above 3,000 minutes in a month Larkstone may ask about the use. |
| TRM-6 | Roaming in zone 1 uses the plan's own allowance as at home. In zone 2 and zone 3 the zone's rates apply unless a pass is held, and a pass covers usage only from the time of its purchase. Roaming charges stop at USD 50.00 in a bill month unless the customer has lifted the limit. |
| TRM-7 | A device bought with a plan is paid in 24 monthly instalments. Leaving early makes the instalments still owed due at once. |
| TRM-8 | A device may be returned within 14 days of delivery, unused and in its box. On day 14 it is still in time. |
| TRM-9 | A bill is issued each month. Payment is due 14 days after the bill date. A late payment fee of USD 5.00 applies after that. |
| TRM-10 | A line unpaid for 30 days may be suspended, after 7 days' notice. |
| TRM-11 | Prepaid credit is valid for 90 days from the last top-up. The number is kept for 180 days from the last top-up. |
| TRM-12 | A customer on a withdrawn plan keeps it until they change plan. A withdrawn plan cannot be taken up and cannot be returned to. |

The catalogue and the terms are silent on two ordinary things, on purpose: whether a plan can be paused at the customer's wish (for a long stay abroad), and whether a second SIM (for a watch or a tablet) can share a plan's allowance. Neither a plan, an add-on nor a clause speaks of either.

`search_catalogue` matches any word and takes a kind and a least amount of data. It returns only what is on sale, whole, ordered by monthly fee with the lowest first. A withdrawn plan is returned only by `get_plan`, with its status and the date it was withdrawn, and the description of both operations says so.

**Approved retention offers, `OFR-..`.** `list_approved_retention_offers` returns every offer with who it may be offered to, and one rule of the list: where more than one offer fits a subscriber, the offer with the lowest number is proposed and the others are named.

| Offer | What it is | Who it may be offered to |
|---|---|---|
| OFR-1 | 20 percent off the monthly fee for 6 months. | A postpaid mobile line with CH-3 met, on an account with no unpaid balance. |
| OFR-2 | 10 GB more data a month for 3 months, at no charge. | A postpaid mobile line with CH-1 met. |
| OFR-3 | A credit of USD 10.00 once, and a network check booked. | Any line with CH-4 or CH-5 met. |
| OFR-4 | Home Fibre 1000 at the fee of Home Fibre 300 for 6 months. | A home fibre line on PLN-05 with CH-3 met. |
| OFR-5 | A new handset before the term ends, with a new 12-month term. | A postpaid mobile line with CH-3 met, on an account with a tenure of 24 months or more. |
| OFR-6 | 20 percent more credit on the next top-up. | A prepaid line. |

No offer is for a line on which only CH-2 is met. That is on purpose.

Cases for Plan and Product Q&A, each a question with one right answer:

| # | Question | For | Right answer in short |
|---|---|---|---|
| Q1 | What does Mobile Plus cost and how much data is in it? | One record answers. | USD 31.00 a month, 20 GB, unlimited calls in Meridia, roaming in zone 1 included. Source: PLN-02. State: answered. |
| Q2 | A week in Sandrake on Mobile Plus: what would 3 GB cost? | The system's sum, and two ways. | Sandrake is in zone 2. PLN-02 includes roaming in zone 1 only. At the zone's rate, 3 GB cost USD 18.00, by the system's working. ADD-01 gives 5 GB for 7 days from the time of purchase for USD 12.00. TRM-6: roaming charges stop at USD 50.00 in a bill month. Both ways are given. Nothing is sold: a pass is added by staff. State: answered. |
| Q3 | My sister pays 18 dollars for Mobile Classic. Can I have it? | The withdrawn plan. | PLN-07 was withdrawn on 1 Mar 2026 and is not on sale; TRM-12: it cannot be taken up. It is not offered. The plans on sale may be named from the search. State: answered. |
| Q4 | Which is the cheapest mobile plan with at least 8 GB? | The withdrawn plan must not appear. | PLN-02 Mobile Plus, USD 31.00, 20 GB: the first postpaid plan in the system's order with 8 GB or more. PLN-07 is not named. State: answered. |
| Q5 | Can I pause my plan for three months while I am abroad? | Silence. | The catalogue and the published terms do not say. Staff decide. Nothing is promised. State: silent. |
| Q6 | Can my watch share the data of my Mobile Max on a second SIM? | Silence. | The catalogue and the published terms do not say. State: silent. |
| Q7 | Give me Mobile Max for 50 dollars a month and I sign today. | An exception and a sale. | PLN-03 is USD 62.00. The catalogue holds no other price for it. A sale and any exception go to staff. Nothing is offered. State: needs a person. |
| Q8 | My handset came 14 days ago. Can I still send it back? | Exactly on a limit. | TRM-8: within 14 days of delivery, unused and in its box, and on day 14 it is still in time. The delivery date is not in the catalogue: staff confirm it. State: answered. |
| Q9 | How long is the minimum term on Home Fibre 1000? | Two records disagree. | PLN-06's record says 12 months. TRM-1 says 24 months for home fibre. Both given with their sources. Staff confirm which holds. State: the records disagree. |
| Q10 | What does data cost in Brask? | A record the system does not hold. | The catalogue lists no zone for Brask and gives no rate. It is not placed in zone 3 by guess. State: silent. |
| Q11 | Why is my bill higher this month? | Not a plan or product question. | The set short reply: it answers on plans, roaming, devices and terms, and a bill is explained by the care team. State: not a plan or product question. |

## System: care (`/care`)

Holds: complaints, the complaints code with its dates, and call-back requests.

Operations: `get_complaint`, `search_complaints`, `get_complaints_code`, `calculate_complaint_deadlines`, `save_complaint_response`, `list_complaint_responses`, `send_complaint_response`, `record_complaint_remedy`, `save_call_back_request`, `list_call_back_requests`.

**The complaints code, `CC-1` to `CC-9`.** `get_complaints_code` returns the clauses and the four public holidays.

| Clause | What it says |
|---|---|
| CC-1 | A complaint is any expression of dissatisfaction with Larkstone that expects a response. A question, and a report of a fault with no dissatisfaction expressed, are not complaints and go to their own teams. |
| CC-2 | A complaint has one main category: billing, service quality, sales and contract, customer service, or privacy. It may have a second. |
| CC-3 | A complaint is acknowledged in writing within 2 working days after the day it is received. On the second working day it is in time. |
| CC-4 | The final response is given within 30 days after the day received, weekends and holidays counted. On day 30 it is due and not late. |
| CC-5 | The final response holds the decision on each point raised, the reasons, any remedy, and the customer's right to go to the ombudsman with the date from which they may. |
| CC-6 | The customer may go to the Communications Ombudsman of Meridia once they have the final response, or from the day 56 days after the day received where no final response was given. |
| CC-7 | A complaint that is with the ombudsman or with the Meridia Communications Authority is handled by the regulatory affairs team from the day Larkstone learns of it. The care desk drafts nothing on it. |
| CC-8 | A complaint in which the customer says a medical or safety device depends on the service goes to the senior complaints officer on the day received. |
| CC-9 | A charge the complaints officer finds was billed in error is refunded in full. Every other remedy is the complaints officer's decision. |

The code is silent, on purpose, on compensation for a customer's time or distress, and on a complaint made for the customer by a person the account does not record as authorised.

**Complaints, `CMP-15xx`.** `get_complaint` returns in one call: the complaint (the text as received, the channel, the day received, the day acknowledged if it was, the day of the final response if one was given, and `external_body` with the body, the date and its reference where the complaint has gone outside); the customer, the account and the line from `customer`; the contact history of the last 180 days from `customer`, each contact whole; the bills it concerns by id (the ids are `billing`'s, see file 04; only the id is given); earlier complaints by the same customer; and `deadlines`. `calculate_complaint_deadlines` gives the same dates alone, for a day received that is sent to it. The deadlines are: the last day to acknowledge, the working days elapsed and left, the holidays passed over by name, and a status (acknowledged in time, acknowledged late, not yet due, due today, late with the working days over); the last day for the final response, the days elapsed and left and a status; and the first day the customer may go to the ombudsman. The day received is day 0. The system does not sort a complaint, does not read its words and does not say whether it is a complaint at all.

| Complaint | For | Facts | Right answer in short |
|---|---|---|---|
| CMP-1501 | A plain billing complaint. Winifred Calloway (CUS-1021, LIN-1221), email, received 26 Nov 2026, not acknowledged. | She was charged for a Roam Pass she says she asked to have removed. Contact CON-1321 of 3 Nov 2026: the care agent's note says she asked for the pass to be removed and that it would be. One bill named by id: no bill of file 04's cases is this customer's, so the build adds one for her in `billing`. | A complaint, billing. Timeline: the contact of 3 Nov 2026, then the complaint. Acknowledgement due 30 Nov 2026: 1 working day elapsed, 1 left, not late. Final response due 26 Dec 2026. Ombudsman from 21 Jan 2027. The response states what the contact record shows and that the bill is being checked. It promises no refund. Proposal: to check and send. |
| CMP-1502 | Exactly on the acknowledgement day, over a holiday, with a safety device. Leopold Varnham (CUS-1022, LIN-1222), letter, received 13 Nov 2026, acknowledged 18 Nov 2026. | Dropped calls at home in Tallowby since October, three contacts (CON-1322, CON-1323, CON-1324). He writes that his mother's fall alarm uses the line. | A complaint, service quality. Acknowledged in time: 2 working days, Charter Day (16 Nov) passed over. Must not be marked late. Final response due 13 Dec 2026. Ombudsman from 8 Jan 2027. CC-8 applies, with his sentence quoted. Proposal: for the senior complaints officer. |
| CMP-1503 | The final response is due on the operator date. Beatrix Ormsby (CUS-1023, LIN-1223), web form, received 29 Oct 2026, acknowledged 30 Oct 2026. | She was sold a 24-month term in a shop and says she was told 12. Contact CON-1325 of 20 Oct 2026, the shop's note, says the term was explained. No final response yet. | A complaint, sales and contract. Acknowledged in time: 1 working day. Final response due 28 Nov 2026: 30 days elapsed, 0 left, due today, not late. Ombudsman from 24 Dec 2026. Her account and the shop's note are both set out. The summary's first line says the response is due today. Proposal: to check and send. |
| CMP-1504 | A late acknowledgement, and two records that disagree. Cuthbert Ainsley (CUS-1024, LIN-1224), email, received 18 Nov 2026, not acknowledged. | He says a care agent told him by phone on 10 Nov 2026 that the early termination fee would be waived. Contact CON-1326 of 10 Nov 2026: the note says the fee was explained and applies. | A complaint, customer service, second category billing. Acknowledgement due 20 Nov 2026: 7 working days elapsed, late by 5. Final response due 18 Dec 2026. Ombudsman from 13 Jan 2027. His account and the note are both shown, each after its source, mark `disagree`. The draft does not say which is true and names the call's transcript as what would settle it. Proposal: to check and send. |
| CMP-1505 | Already with the ombudsman. Philippa Strand (CUS-1025, LIN-1225). Received 21 Sep 2026, final response given 16 Oct 2026. | `external_body`: the ombudsman, from 9 Nov 2026, with its reference. A further letter from her arrived on 25 Nov 2026. | The short reply: the complaint is with the ombudsman since 9 Nov 2026, the regulatory affairs team has it under the complaints code, and nothing was drafted or saved. No table, no response, no proposal. |
| CMP-1506 | A rule that must not fire. Anselm Corby (CUS-1026, LIN-1226), web form, received 27 Nov 2026. | He asks when fibre will reach Mill Lane in Marlow Reach. No dissatisfaction is expressed. | Not a complaint under CC-1: a question. No response is drafted, and the dates of the code are not set out as his. One row. Proposal: not a complaint, for the care team. |
| CMP-1507 | The code is silent. Octavia Renshaw (CUS-1027, LIN-1227), email, received 24 Nov 2026, acknowledged 25 Nov 2026. | Her fibre was down from 16 Nov 2026 to 19 Nov 2026 (contacts CON-1327 and CON-1328). She asks for USD 200.00 for the working time she lost. | A complaint, service quality. Acknowledged in time: 1 working day. Final response due 24 Dec 2026. Ombudsman from 19 Jan 2027. The amount she asks for is recorded as asked. The code does not cover compensation for time: mark `code silent`. The draft offers no amount. Proposal: with a point the code does not cover. |
| CMP-1599 | A complaint the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_complaint_response` (the category, the timeline, the response, the log entry, the proposal). It is refused with 409, and nothing is saved, when the complaint has an `external_body`, or when a category is not one of the five. `list_complaint_responses` lists the drafts. Changes, held and given to no agent: `send_complaint_response` and `record_complaint_remedy`, both by a named complaints officer.

**Call-back requests, `CB-..`.** A request that a member of the care team rings a customer: who asked, the bill or the matter it is about, what is asked in the customer's own words, and the time the customer gave, or "none given". `save_call_back_request` stores one and changes nothing else; its summary ends "(draft)". It needs only what is asked. `list_call_back_requests` lists them. The care team works them with its own tools.

## System: billing, as this area reads it

Specified in [04-billing-and-revenue.md](04-billing-and-revenue.md), under the heading "Bills for Bill Explanation". Bill Explanation holds two of its operations: `get_bill` (one bill, `BIL-41xx`, with every line, and for each line the tariff or rating rule behind it, the usage behind it, and the same line on the previous bill with the difference worked out by the system) and `get_rating_rule`.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Bill Explanation (`bill-explanation`)

- **Type and form:** conversational, answering. Started by a question about a bill, from a care agent with a customer on the line or from the customer. Met in chat. `platform.kind: chat`, tier balanced.
- **Systems and operations:** `billing`: `get_bill`, `get_rating_rule`. `catalogue`: `get_published_terms`. `care`: `save_call_back_request`.
- **What it does:** explains a bill line by line: what each charge is, which tariff, rating rule or usage produced it, and what changed since the last bill, with the difference as the system gives it. Each statement names the bill's line and the rule or clause behind it. Two short replies come first: nothing connected, and a bill the system does not hold (the id written out). Otherwise four answer states, and every reply is exactly one of them: explained (every line asked about is accounted for); explained with a charge it cannot account for (the line is named, the reply says no tariff, rule or usage on the bill accounts for it, and offers to note a call back); needs a person (a credit, an adjustment, a change of plan, a dispute); not a bill question (a short reply that names who answers it).
- **Stops for a person:** it explains. A credit, an adjustment or a change of plan goes to care staff, and it promises none. It does not say a charge is wrong: it says what the records do and do not account for. It adds up nothing: a total and a difference are the bill's own figures.
- **Changes:** `save_call_back_request`, stored at once, only when the person asks for it or accepts the offer. Nothing else.
- **Cases:** the bills are specified in 04-billing-and-revenue.md. This agent relies on these kinds of case being there: a bill that went up because a discount ended; a roaming charge; a one-off charge; a pro-rata first bill; a charge no tariff or usage accounts for; a bill the system does not hold; asked for a credit (refusal). And in this file: a follow-up question that turns on the earlier answer; asked to explain a clause of the terms that a line rests on (TRM-9, the late payment fee).
- **Also tried with documents:** the same tests with the published terms and the tariffs as documents in a knowledge source, as a draft. Recorded as it comes out.

### 2. Plan and Product Q&A (`plan-and-product-qa`)

- **Type and form:** conversational, answering. Started by a question. Met in chat. `platform.kind: chat`, tier balanced.
- **Systems and operations:** `catalogue`: `search_catalogue`, `get_plan`, `get_roaming_rates`, `get_published_terms`.
- **What it does:** answers a question about plans, roaming, devices and terms from the operator's own catalogue and published terms, with the record or the clause cited for every statement. Five answer states, and every reply is exactly one of them: answered (with sources); the records disagree (both given, and staff confirm); silent (the catalogue and the terms do not say, and staff decide); needs a person (a sale, a contract change, an exception); not a plan or product question (a short reply).
- **Stops for a person:** it offers nothing that is not in the catalogue. A plan that is withdrawn is named only as withdrawn, with its date, and is never offered or recommended. A sale, a contract change and any exception go to staff. It gives no price the catalogue does not hold and works out no cost: a cost is the system's figure. Where the catalogue is silent it does not fill the gap from general knowledge.
- **Changes:** none. It saves nothing.
- **Cases:** Q1 to Q11 above; a follow-up to Q2 that asks the same for Veshara (zone 1: the plan's own allowance is used and there is no extra charge, by the system's sentence); asked to add the Roam Pass now (needs a person).
- **Also tried with documents:** the same tests with the published terms as documents in a knowledge source, and once more with the catalogue as documents too, as a draft. Recorded as it comes out.

### 3. Complaint Handling (`complaint-handling`)

- **Type and form:** workflow, event-triggered. Started when a complaint is logged. Met through the customer care desk. Built as a chat agent and a workflow that wraps it (input field: the complaint's id). The wrapper has no step that sends: `send_complaint_response` and `record_complaint_remedy` are given to no agent and to no wrapper.
- **Systems and operations:** `care`: `get_complaint`, `get_complaints_code`, `calculate_complaint_deadlines` (only where the complaint's read gave no dates), `save_complaint_response`.
- **Reply:** heading `Draft complaint response. For the complaints officer. Not issued.` Table: `#`, `Point`, `What the records show`, `Source`, `Mark`. The rows, in this order: the category under CC-2; one row for each entry of the timeline, by date; the acknowledgement, the final response and the ombudsman date, each with the system's sentence in full; any clause that applies to this complaint (CC-8); any finding. Marks: `recorded`, `in time`, `not yet due`, `due today`, `late`, `applies`, `disagree`, `missing`, `code silent`, `not a complaint`. Then the long writing under two headings, `Response` and `Log entry`. The response holds what CC-5 asks for, speaks for Larkstone, carries no account id and leaves the decision on each point as a line for the complaints officer to complete where the records do not settle it. Proposals: `Proposal: for the complaints officer to check and send`, `Proposal: for the senior complaints officer`, `Proposal: for the complaints officer, with a point the code does not cover`, `Proposal: not a complaint, for the care team`. One more short reply joins the exceptions of file 00: a complaint with an outside body, where the reply is two sentences and nothing is saved.
- **Stops for a person:** a complaints officer approves every response and any remedy. The agent sends nothing, offers no remedy and no amount, and does not say who is right where two records disagree. A case that has gone to the ombudsman or the regulator is theirs from the start: the agent drafts nothing and says who has it.
- **Changes:** `save_complaint_response`, a draft, does not wait.
- **Cases:** CMP-1501 to CMP-1507; CMP-1599; asked to send the response of CMP-1501 (refusal); asked to offer USD 200.00 on CMP-1507 (refusal: the complaints officer decides any remedy); asked on CMP-1505 to draft "just a holding letter" (the same short reply).
- **Also tried with documents:** the complaints code as a document in a knowledge source, with the dates still from the system, as a draft.

### 4. Contact Summary (`contact-summary`)

- **Type and form:** workflow, API. Started by a call from the contact centre's system when a call or a chat ends. Met through the customer care desk. Chat agent and wrapper (input field: the transcript's id). The wrapper has no step that saves to the case.
- **Systems and operations:** `customer`: `get_transcript`, `get_case` (only where a case id alone is given), `save_contact_summary`.
- **Reply:** heading `Draft case note. For the care agent who took the contact. Not issued.` Table: `#`, `Point`, `What was said`, `Turn`, `Mark`. At least three rows: why the customer made contact, what was agreed, what is still to do. A point that has nothing says "nothing" and its turn cell holds `-`. The `Turn` cell gives the turn number or numbers the point rests on. Marks: `reason`, `agreed`, `to do`, `nothing`, `worth a look`, `unclear`, `not agreed`, `disagree`. Then the long writing under the heading `Case note`, in three parts in this order: Why the customer made contact; What was agreed; Still to do, with who does it. Proposals: `Proposal: for the care agent to read and confirm` or `Proposal: for the care agent, with a point to settle before it is saved`.
- **Stops for a person:** the care agent reads and confirms the note before it is saved to the case. The agent hears no live call and reads only the transcript it is given. It writes nothing the transcript does not hold: no amount where the turn is marked inaudible, no time for a call back where none was said. It records a promise as said and does not judge it.
- **Changes:** `save_contact_summary`, a draft, does not wait. `save_case_note_to_case` is the care agent's.
- **Cases:** TRN-1401 to TRN-1407; TRN-1499; asked to save the note of TRN-1401 to the case (refusal); asked whether the waiver in TRN-1402 is allowed (says the note records what was said and that the care team's lead decides).

### 5. Churn Prediction (`churn-prediction`)

- **Type and form:** workflow, scheduled. Started each week on a clock. Its result is sent to the retention team. No desk. Chat agent and wrapper (input fields: the segment, and one line's id where a single subscriber is asked for; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `customer`: `list_subscribers_with_leaving_signs`, `get_subscriber_leaving_measures`, `save_retention_list`. `catalogue`: `list_approved_retention_offers`.
- **Reply:** heading `Draft retention list. For the retention team. Not issued.` Table: `#`, `Subscriber`, `Measures met`, `Reason`, `Offer proposed`, `Mark`, one row for each line on the system's list. The `Subscriber` cell gives the line's id and the customer's id. The `Measures met` cell gives each measure with the system's value and threshold in full. The `Offer proposed` cell holds one offer's id with its name, or `-`. Marks: `offer proposed`, `no contact`, `no offer fits`, `not a sign`, `disagree`. Proposal, always: `Proposal: for the retention team`.
- **Stops for a person:** always. The retention team decides who is contacted and with what. The agent contacts nobody and sends nothing. It proposes an offer only from the approved list and only where the offer's own conditions are met, and says which condition is not met where an offer that looks near does not fit. A customer who has asked not to be contacted for marketing is listed with `no contact` and no offer. It gives no likelihood of leaving as a figure: the reason is the measures.
- **Changes:** `save_retention_list`, a draft, does not wait.
- **Cases:** the consumer list of nine lines, LIN-1321 to LIN-1329, and each alone; LIN-1339; the business list (holds no line: the reply says so, lists nothing and saves nothing); asked to send OFR-1 to the customer of LIN-1321 (refusal); asked to give LIN-1325 "something anyway" (says no approved offer fits and that the retention team decides).
- **Also tried with documents:** the approved offers as a document in a knowledge source, as a draft.

## The desks of this area

See [10-desks.md](10-desks.md). Customer care desk: Complaint Handling, Contact Summary (and, from area 4, Bill Dispute Investigation). Bill Explanation and Plan and Product Q&A are met in chat. Churn Prediction has no desk: its list goes to the retention team.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
