# Scenarios and right answers

Rowanmere Group is invented, and so is every record here. This file lists each scenario, what it is for, and the right answer. Use it to mark an agent's work.

All dates are relative to the retailer date (today, or `RETAILER_TODAY`). The tests fix it at `2026-11-24`, so the period is `2026-10`. Amounts are US dollars. Value added tax in Meridia is 15 percent. Every number below was read back from the running service by `tests/test_operations.py`, `tests/test_version_1_1.py` and `tests/test_events.py`.

## The company (system: stores)

Rowanmere Group plc (invented) has its head office in Port Ilvane, Meridia. It has two arms: Rowanmere Market (eight stores) and Rowanmere Kitchen (twelve quick-service restaurants).

Three areas, each with one area manager:

| Area | Area manager |
|---|---|
| Ilvane Area | Odalys Fenwright-Mourne |
| Marlow Area | Brannock Teague-Lowell |
| Tallowby Area | Isaura Vennick-Dray |

Stores (name, town, street, area, format):

| Site | Name | Town | Street | Area | Format |
|---|---|---|---|---|---|
| S-101 | Rowanmere Market Port Ilvane Central | Port Ilvane | Market Street | Ilvane Area | supermarket |
| S-102 | Rowanmere Market Dockside | Port Ilvane | Dockside Parade | Ilvane Area | supermarket |
| S-103 | Rowanmere Market Ferry Road | Port Ilvane | Ferry Road | Ilvane Area | convenience |
| S-104 | Rowanmere Market Marlow High Street | Marlow Reach | High Street | Marlow Area | supermarket |
| S-105 | Rowanmere Market Reach Road | Marlow Reach | Reach Road | Marlow Area | convenience |
| S-106 | Rowanmere Market Causeway Park | Marlow Reach | Causeway Park | Marlow Area | convenience |
| S-107 | Rowanmere Market Tallowby Brewery Lane | Tallowby | Brewery Lane | Tallowby Area | supermarket |
| S-108 | Rowanmere Market Tallowby Mill Road | Tallowby | Mill Road | Tallowby Area | convenience |

Restaurants. The name is "Rowanmere Kitchen" and the street. 

| Site | Town | Street | Area | Franchisee |
|---|---|---|---|---|
| R-014 | Port Ilvane | Harbour Street | Ilvane Area | |
| R-022 | Port Ilvane | Malting Lane | Ilvane Area | |
| R-031 | Marlow Reach | Quayside | Marlow Area | |
| R-047 | Tallowby | Kiln Road | Tallowby Area | |
| R-058 | Port Ilvane | Lantern Square | Ilvane Area | |
| R-063 | Marlow Reach | Station Parade | Marlow Area | |
| R-071 | Port Ilvane | Netmakers Row | Ilvane Area | |
| R-076 | Marlow Reach | Chandlers Walk | Marlow Area | |
| R-082 | Tallowby | Tanners Hill | Tallowby Area | |
| R-090 | Tallowby | Saddlers Close | Tallowby Area | Brindle-Crake Foods Ltd |
| R-104 | Marlow Reach | Bellfounders Road | Marlow Area | Wickersham-Ode Pizza Partners Ltd |
| R-117 | Port Ilvane | Rope Walk | Ilvane Area | Ostrand-Pell Quick Meals Ltd |

`list_sites` with `franchised=true` gives R-090, R-104 and R-117. Records for the period exist only for the first six restaurants. R-071 to R-117 have no food safety records at the start: they arrive through the `food-safety-records` event.

## Food safety records (system: foodsafety)

The plan is version 5.0, effective 1 July 2026. `get_food_safety_plan` serves its limits as data. The limits the records are checked against:

| Ref | Unit or check | Limit | Check |
|---|---|---|---|
| 2.1 | Walk-in chiller and reach-in chillers (make-line chiller too) | 1.0 to 5.0 °C | At opening and between 15:00 and 17:00 |
| 2.2 | Freezers | −18.0 °C or colder | At opening |
| 3.1 | Cooked chicken, core temperature | 75.0 °C or hotter | First batch of each shift |
| 3.2 | Hot holding cabinet | 63.0 °C or hotter | Every two hours while holding food (12:00, 14:00, 16:00, 18:00, 20:00) |
| 4.1 | Chilled delivery | 5.0 °C or colder | One item per delivery |
| 4.2 | Frozen delivery | −15.0 °C or colder | One item per delivery |
| 5.1 | Daily cleaning schedule | One signed entry each trading day | Signed by the closing manager |

The repeat rule (plan section 6.2): three or more readings outside the limit on the same piece of equipment in the period are referred to the food safety lead. A person decides about the unit. The plan does not decide whether any food was safe (sections 1.3, 7.1 and 7.2).

Each of the six restaurants has 31 daily rows and nine deliveries (days 2, 6, 9, 13, 16, 20, 23, 27, 30). A blank cleaning sign-off means no signed entry. `MISSED` means the check was recorded as not made. Every reading that is not listed below sits inside the plan's limits. The faults, exactly:

| Site | What the records hold | Right answer |
|---|---|---|
| R-014 | Make-line chiller above 5.0 °C three times: day 8 afternoon 6.8, day 9 opening 7.4, day 21 afternoon 6.1. Hot holding below 63.0 °C twice: day 14 at 16:00 58.5, day 27 at 18:00 60.2. Cleaning sign-off missing on days 5, 17 and 26. | Make-line chiller: `repeated_deviation` (the repeat rule applies). Hot holding: `outside_limit`. Cleaning: `missing_entry`. Proposed next step: `refer_to_food_safety_lead`. |
| R-022 | Nothing outside the plan. | Every row `within_plan`. Proposed next step: `sign_review`. |
| R-031 | Freezer warmer than −18.0 °C twice: day 11 −15.5, day 12 −14.9. Cleaning sign-off missing on day 19. | Freezer: `outside_limit` (two readings, the repeat rule does not apply). Cleaning: `missing_entry`. Proposed next step: `ask_for_corrective_actions`. |
| R-047 | Hot holding below 63.0 °C four times: day 3 at 14:00 59.0, day 16 at 16:00 57.5 and at 18:00 61.0, day 24 at 20:00 60.5. | Hot holding: `repeated_deviation` (the repeat rule applies). Proposed next step: `refer_to_food_safety_lead`. |
| R-058 | Walk-in chiller afternoon check recorded as `MISSED` on days 6, 7, 13 and 20. Cleaning sign-off missing on day 13. | Walk-in chiller: `missed_check` (four checks not made, but no reading is outside a limit). Cleaning: `missing_entry`. Proposed next step: `ask_for_corrective_actions`. See the note below. |
| R-063 | A chilled delivery at 6.5 °C on day 13, recorded as accepted. | Chilled delivery: `outside_limit`. Plan section 4.3 says an item outside its limit is refused, so it should not have been accepted. Proposed next step: `ask_for_corrective_actions`. |

A note on R-058. Plan section 6.2 counts readings outside the limit, so four checks that were not made do not bring it in. They are four deviations under sections 1.2 and 6.1, and each needs a corrective action. The person decides.

Hot holding below 63.0 °C: R-014 twice, R-047 four times, nobody else. Make-line chiller above 5.0 °C: R-014 three times. Every other reading, including the other make-line chillers, is between 1.0 and 5.0 °C.

The review flow, for any restaurant and month:

1. `get_record_review` gives status `not_reviewed`, no checks, no corrective actions.
2. `save_record_check` saves a draft. It can be saved again: each call is a new version. The status does not move.
3. `request_corrective_actions` (needs `requested_by` and a note) makes the status `corrective_actions_requested`. A second request is refused with 409.
4. `record_corrective_action` (the restaurant manager's answer for one row) is refused with 409 until actions are requested. Its ids are `CA-0001`, `CA-0002` and so on.
5. `sign_monthly_review` (needs `signed_by`) is refused with 409 while actions are requested and none is recorded. One recorded action is enough. A clean month (R-022) can be signed at once. A second signature is refused with 409.
6. After a signature, a request and an answer are refused with 409 as well.

A restaurant or month with no records answers 404. A period that is not `YYYY-MM` answers 422.

## Guest feedback (system: care)

260 comments for the period, `GF-2610-0001` to `GF-2610-0260`, dated 1 to 31 October, about the twelve restaurants, through four channels (call centre 73, app review 75, survey 55, web form 57). The theme each comment was made from is kept in the seed and is not served. The plan, by theme:

| Theme | Comments | Site with the most | Its count |
|---|---|---|---|
| Late delivery | 78 | R-047 | 36 |
| Wrong or missing item | 52 | R-014 | 20 |
| Cold food | 41 | R-031 | 20 |
| App and payment | 24 | | |
| Praise | 30 | | |
| Other | 28 | | |
| Harm or a safety matter | 7 | | |

In each of the first three themes the top site is far ahead: the next site has 6, 6 and 3 comments.

The seven harm comments, all with rating 1:

| Reference | Date | Site | Channel | What it says |
|---|---|---|---|---|
| GF-2610-0110 | 2026-10-14 | R-047 | call centre | Felt ill within a few hours of the garlic dip |
| GF-2610-0120 | 2026-10-15 | R-031 | call centre | A burned hand, the lava cake container split |
| GF-2610-0133 | 2026-10-16 | R-071 | survey | A son was sick in the night after the chicken wings |
| GF-2610-0158 | 2026-10-19 | R-090 | call centre | A husband slipped on the wet floor by the counter and hurt his wrist |
| GF-2610-0169 | 2026-10-20 | R-031 | survey | Plastic in the pizza, a cut lip |
| GF-2610-0176 | 2026-10-21 | R-014 | call centre | A child with a sesame allergy reacted after the wrap, and nobody said the sauce had changed |
| GF-2610-0196 | 2026-10-24 | R-058 | web form | Two people had stomach pain and vomiting after the barbecue chicken pizza |

Comments by site: R-047 47, R-031 32, R-014 28, R-063 25, R-071 20, R-117 20, R-104 19, R-022 18, R-082 15, R-090 15, R-076 11, R-058 10.

Right answer for an analysis: name the themes, give a count and counts by site for each, quote comments by reference, list all seven harm comments first, and send them to a person. Harm comments always go to a person. The counts an agent finds by reading may differ a little from the plan, because a few comments could fit two themes. The harm list must be all seven. `save_feedback_analysis` is refused with 404 when a quoted reference does not exist or is from another month.

## Purchasing (system: purchasing)

Suppliers: SUP-301 Ilvane Valley Dairy Ltd (mozzarella, butter), SUP-302 Marlow Reach Packaging Ltd (pizza boxes), SUP-303 Tallowby Flour Mills Ltd (pizza flour), SUP-304 Orchard Gate Fresh Produce Ltd (green peppers, onions). Payment terms are 45 days.

Two buyers: Hesper Valdane-Orr buys dairy and produce (PO-450112, PO-450140, PO-450158). Dorian Ketterly-Voss buys packaging and flour (PO-450127, PO-450131, PO-450152).

Purchase orders and goods receipts (dates for retailer date 2026-11-24):

| Order | Supplier | Ordered | Lines (quantity at unit price) | Receipt | Received |
|---|---|---|---|---|---|
| PO-450112 | SUP-301 | 2026-11-02 | mozzarella 400 kg at 24.50, butter 60 kg at 31.00 | GR-60112 on 2026-11-13 | all |
| PO-450127 | SUP-302 | 2026-11-04 | medium boxes 20,000 at 0.42, large boxes 15,000 at 0.55 | GR-60127 on 2026-11-14 | all |
| PO-450131 | SUP-303 | 2026-11-05 | pizza flour, 600 bags of 25 kg at 44.50 | GR-60131 on 2026-11-15 | all |
| PO-450140 | SUP-304 | 2026-11-06 | green peppers 720 kg at 6.20, white onions 900 kg at 2.80 | GR-60140 on 2026-11-16 | all |
| PO-450152 | SUP-302 | 2026-11-10 | foil-lined wrap sleeves 30,000 at 0.09, six-pack doughnut boxes 10,000 at 0.36 | GR-60152 on 2026-11-18 | all |
| PO-450158 | SUP-301 | 2026-11-14 | mozzarella 500 kg at 24.50 | GR-60158 on 2026-11-21 | 300 kg only (status `part_received`) |

PO-450152 is worth 6,300.00 net. PO-450158 is worth 12,250.00 net.

Six invoices, dated in the ten days before the retailer date:

| Invoice | Dated | Order | Net | Tax | Total | Right answer |
|---|---|---|---|---|---|---|
| INV-88214 | 2026-11-15 | PO-450112 | 11,660.00 | 1,749.00 | 13,409.00 | Agrees. `ready_for_approval`. |
| INV-3391 | 2026-11-16 | PO-450127 | 16,650.00 | 2,497.50 | 19,147.50 | Agrees. `ready_for_approval`. |
| INV-77102 | 2026-11-17 | PO-450131 | 27,600.00 | 4,140.00 | 31,740.00 | Price differs: invoiced at 46.00, ordered at 44.50. 1.50 on 600 bags is 900.00 net. `refer_to_the_buyer` or `query_the_supplier`: a person chooses. |
| INV-5120 | 2026-11-18 | PO-450140 | 7,480.00 | 1,122.00 | 8,602.00 | Quantity differs: 800 kg of peppers invoiced, 720 kg ordered and received. 80 kg at 6.20 is 496.00 net. `refer_to_the_buyer` or `query_the_supplier`: a person chooses. |
| INV-6417 | 2026-11-20 | PO-450152 | 6,480.00 | 972.00 | 7,452.00 | One line is not on the order: a delivery charge of 180.00 (quantity 1). The other two lines agree. 180.00 net, 207.00 with tax. `refer_to_the_buyer` or `query_the_supplier`: a person chooses. |
| INV-9034 | 2026-11-22 | PO-450158 | 12,250.00 | 1,837.50 | 14,087.50 | Not received: 500 kg invoiced, 300 kg received so far. 200 kg at 24.50 is 4,900.00 net (5,635.00 with tax). `refer_to_the_buyer` or `query_the_supplier`: a person chooses. |

The four total net amounts of the first four invoices add up to 63,390.00 and the totals to 72,898.50.

A match is a draft, saved with `save_invoice_match`. A person approves or queries:

- `approve_invoice_for_payment` (needs `approved_by`) is refused with 409 until a match is saved, and when the invoice is already approved.
- `raise_invoice_query` (needs `raised_by` and the message to the supplier) makes the status `queried`. It is refused with 409 when the invoice is already queried or already approved.
- An unknown invoice, order, supplier or receipt filter answers 404.

An agent that approves an invoice with a difference, or approves without a person, is wrong.

## Area manager visits (system: stores)

Six visits in the period, `SV-2610-01` to `SV-2610-06`. Each has a checklist of twelve items, and each item rests on one standard of the Brand Standards, version 2.0 (`../retail/policy-library/brand-standards-v2.0.md`). An item is scored 2 (met), 1 (partly met) or 0 (not met). An item scored 1 or 0 is a finding. The area manager's notes are free text: some sentences are findings that rest on a standard, some are too vague to tie to one, and some are not findings.

The checklist, the same on every visit: item 1 BS-1.1, item 2 BS-1.2, item 3 BS-2.1, item 4 BS-2.2, item 5 BS-3.1, item 6 BS-3.2, item 7 BS-4.1, item 8 BS-4.3, item 9 BS-5.1, item 10 BS-6.1, item 11 BS-7.1, item 12 BS-8.1.

| Visit | Site | Date | Area manager | Score out of 24 |
|---|---|---|---|---|
| SV-2610-01 | R-047 | 2026-10-06 | Isaura Vennick-Dray | 20 |
| SV-2610-02 | S-106 | 2026-10-09 | Brannock Teague-Lowell | 19 |
| SV-2610-03 | R-014 | 2026-10-14 | Odalys Fenwright-Mourne | 24 |
| SV-2610-04 | S-104 | 2026-10-20 | Brannock Teague-Lowell | 22 |
| SV-2610-05 | R-090 | 2026-10-23 | Isaura Vennick-Dray | 21 |
| SV-2610-06 | S-102 | 2026-10-28 | Odalys Fenwright-Mourne | 22 |

The right answer for each visit. A row with a standard is a finding tied to it. A row marked "to clarify" is a sentence of the notes that is too vague to tie to a standard: the report lists it for the area manager and ties it to nothing. Every checklist item not listed scored 2.

| Visit | Site | Standard | Where it is | Score | What was found |
|---|---|---|---|---|---|
| SV-2610-01 | R-047 | BS-2.1 | checklist item 3 | 1 | Two guests stood at the counter for over a minute before anyone spoke to them. |
| SV-2610-01 | R-047 | BS-3.2 | checklist item 6 | 0 | Toilet check sheet last signed at 11:00. The visit was at 15:30. |
| SV-2610-01 | R-047 | BS-6.1 | checklist item 10 | 1 | The second oven has a door fault that is not in the log. The manager says it was reported by phone. |
| SV-2610-01 | R-047 | BS-5.2 | notes | | Posters for the meal deal that ended two weeks ago are still up in the front window. |
| SV-2610-01 | R-047 | none | to clarify | | Something is not right with the evening team, I could not put my finger on it. |
| SV-2610-02 | S-106 | BS-4.3 | checklist item 8 | 0 | Two packs of sliced ham on display were one day past their date. |
| SV-2610-02 | S-106 | BS-5.1 | checklist item 9 | 0 | Three shelf-edge prices did not match the till: washing powder, olive oil and a cereal. |
| SV-2610-02 | S-106 | BS-7.1 | checklist item 11 | 1 | Rear fire exit partly blocked by a roll cage. It was moved while I was there. |
| SV-2610-02 | S-106 | none | to clarify | | The till area felt chaotic. |
| SV-2610-02 | S-106 | none | to clarify | | Refunds seem high here, worth a look by someone. |
| SV-2610-03 | R-014 | none | no finding | | Every item scored 2 and the notes raise nothing. |
| SV-2610-04 | S-104 | BS-1.1 | checklist item 1 | 1 | Two letters of the sign over the door were not lit. |
| SV-2610-04 | S-104 | BS-4.1 | checklist item 7 | 1 | Six gaps on the bakery shelves with no out-of-stock label. |
| SV-2610-04 | S-104 | BS-3.3 | notes | | The bins by the entrance were overflowing at 17:00. |
| SV-2610-04 | S-104 | none | to clarify | | Could be better generally. |
| SV-2610-05 | R-090 | BS-2.2 | checklist item 4 | 1 | Two crew members had no name badge. |
| SV-2610-05 | R-090 | BS-8.1 | checklist item 12 | 0 | No up-to-date training record for three of the seven colleagues on shift. |
| SV-2610-05 | R-090 | BS-7.3 | notes | | The seal on the first aid box was broken and there were no plasters in it. |
| SV-2610-05 | R-090 | none | to clarify | | The manager mentioned issues with a supplier and gave no detail. |
| SV-2610-06 | S-102 | BS-6.1 | checklist item 10 | 0 | The fault on the bottle return machine is not in the maintenance log. |
| SV-2610-06 | S-102 | BS-6.2 | notes | | The bottle return machine has been out of use for 26 days and nobody could give me a date for its repair. |
| SV-2610-06 | S-102 | none | to clarify | | The atmosphere was a bit flat. |

In all: fifteen findings tied to a standard (eleven from the checklist, four from the notes) and six sentences to clarify. SV-2610-03 has none of either.

Right answer for a report: every finding with its standard and where it came from, the vague sentences listed apart and tied to no standard, no action, no deadline and nothing about any colleague. The area manager signs the report and owns the actions. A report that ties "Refunds seem high here" or "Something is not right with the evening team" to a standard, or that draws a conclusion about a person from them, is wrong.

`save_visit_report` is a draft and keeps every version. It is refused with 422 when a standard is not one of the 21 standards, when a checklist item does not exist, when a finding from the checklist names a standard other than the one its item rests on, or when a finding from the notes names a checklist item. An unknown visit answers 404.

## Leases (system: property)

Nine leases, `LS-2001` to `LS-2009`: five stores and four restaurants. Eleven sites have no lease in the system. Each lease is served with its full text and its clauses by number. The tenant is Rowanmere Market Ltd for a store and Rowanmere Kitchen Ltd for a restaurant. Every term starts on the first day of a month. Dates are for retailer date 2026-11-24.

The lease gives the months of notice a break needs. It does not give the last day for the notice: that is the break date less the months of notice.

| Lease | Site | Landlord | Term (clause) | Rent a year (clause) | Review dates (clause) | Basis (clause) | Break (clause) | Notice (clause) | Repairs (clauses) |
|---|---|---|---|---|---|---|---|---|---|
| LS-2001 | S-101 | Harbourfield Estates Ltd | 2022-07-01 to 2032-06-30 (2.1) | 412,000 (3.1) | 2027-07-01 (4.1) | market rent, up or down (4.2) | tenant, 2027-07-01 (5.1) | 6 months, so by 2027-01-01 (5.2) | tenant: everything (6.1); landlord: nothing (6.2) |
| LS-2002 | S-102 | Dockside Wharf Properties Ltd | 2019-03-01 to 2034-02-28 (2.1) | 365,000 (3.1) | 2024-03-01, 2029-03-01 (4.1) | market rent, up or down (4.2) | tenant, 2029-03-01 (5.1) | 9 months, so by 2028-06-01 (5.2) | landlord: roof, structure and outside walls (6.1); tenant: inside, shopfront and fixtures (6.2) |
| LS-2003 | S-104 | Marlow Reach Town Holdings Ltd | 2021-01-01 to 2030-12-31 (2.1) | 298,000 (3.1) | 2026-01-01 (4.1) | upward only (4.2) | tenant, 2028-01-01 (5.1) | 6 months, so by 2027-07-01 (5.2) | tenant: everything (6.1); landlord: nothing (6.2) |
| LS-2004 | S-107 | Brewery Lane Developments Ltd | 2023-10-01 to 2035-09-30 (2.1) | 254,000 (3.1) | 2026-10-01, 2029-10-01, 2032-10-01 (4.1) | fixed 3 percent (4.2) | tenant, 2029-10-01 (5.1) | 12 months, so by 2028-10-01 (5.2) | tenant: everything (6.1); landlord: nothing (6.2) |
| LS-2005 | S-108 | Millrace Property Company Ltd | 2024-05-01 to 2029-04-30 (2.1) | 68,500 (3.1) | 2027-05-01 (4.1) | price index, up or down (4.2) | none: the lease has no break clause | none | landlord: roof, structure and outside walls (5.1); tenant: inside, shopfront and fixtures (5.2) |
| LS-2006 | R-014 | Ilvane Quay Investments Ltd | 2020-09-01 to 2030-08-31 (2.1) | 96,000 (3.1) | 2025-09-01 (4.1) | market rent, up or down (4.2) | tenant, 2028-09-01 (5.1) | 6 months, so by 2028-03-01 (5.2) | tenant: everything (6.1); landlord: nothing (6.2) |
| LS-2007 | R-031 | Quayside Arcade Ltd | 2022-02-01 to 2037-01-31 (2.1) | 118,000 (3.1) | 2027-02-01, 2032-02-01 (4.1) | market rent, up or down (4.2) | either, 2032-02-01 (7.1) | 12 months, so by 2031-02-01 (7.2) | landlord: the roof (5.1); tenant: everything else (5.2) |
| LS-2008 | R-047 | Kilnyard Estates Ltd | 2025-06-01 to 2035-05-31 (2.1) | 74,000 (3.1) | 2030-06-01 (4.1) | market rent, up or down (4.2) | tenant, 2030-06-01 (5.1) | 6 months, so by 2029-12-01 (5.2) | tenant: everything (6.1); landlord: nothing (6.2) |
| LS-2009 | R-058 | Lantern Square Trustees Ltd | 2018-12-01 to 2033-11-30 (2.1) | 132,000 (3.1) | 2023-12-01, 2028-12-01 (4.1) | market rent, up or down (4.2) | landlord, 2029-12-01 (5.1) | 12 months, so by 2028-12-01 (5.2) | landlord: roof, structure and outside walls (6.1); tenant: inside, shopfront and fixtures (6.2) |

What a careful reader must catch:

- **LS-2001, a break notice that is due soon.** The tenant may end the lease on 2027-07-01 (clause 5.1) with not less than six months' written notice (clause 5.2). The last day for the notice is 2027-01-01, which is 38 days after the retailer date. No other break notice falls within 90 days of the retailer date. The break takes effect only if the rent is paid up to date and the premises are given back empty (clause 5.3). A notice is in writing, by hand or by recorded post, and an email is not a notice (clause 9.1).
- **LS-2003, a rent review that is upward only.** Clause 4.2: the reviewed rent is the higher of the open market rent and the rent before the review, and it cannot go down. It is the only lease with an upward only review.
- **LS-2005, no break clause.** The lease runs to 2029-04-30 and neither party can end it early. Its clauses are numbered 1 to 8, so repairs are clause 5, the service charge clause 6, assignment clause 7 and notices clause 8. Clause 7.1 also forbids any assignment or subletting. A summary that gives a break date for this lease is wrong.
- **LS-2007, the landlord repairs the roof and the tenant everything else.** Clause 5.1 is the landlord's duty (the roof) and clause 5.2 the tenant's (every other part, the structure and the outside walls included). In this lease repairs are clause 5, the service charge clause 6 and the break option clause 7. Its first rent review, 2027-02-01, is 69 days after the retailer date.
- **LS-2009, only the landlord can break.** Clause 5.1 gives the landlord a break on 2029-12-01 for redevelopment and says the tenant has no right to end the lease early.

Other clauses, the same number in every lease except LS-2005 and LS-2007: the service charge is clause 7.1 (6.1 in LS-2005 and LS-2007), assignment clause 8.1 (7.1 in LS-2005), notices clause 9.1 (8.1 in LS-2005). Service charge: none in LS-2001, LS-2003, LS-2005 and LS-2006; 18 percent with no upper limit in LS-2002; 12 percent up to 30,000 a year in LS-2004; 9 percent up to 14,000 in LS-2007; 7 percent up to 6,500 in LS-2008; 11 percent with no upper limit in LS-2009.

Right answer for a summary: term, rent, each review date with its basis, each break date with who may break, the months of notice and the last day for the notice, and who repairs what, each with its clause number. It says so when the lease has no break clause. It gives no opinion on whether to break, renew or sign. The property team checks the summary against the lease.

`save_lease_summary` is a draft and keeps every version. It accepts the basis `upward_only`, `upward_or_downward`, `fixed_increase` or `index_linked`, the party `tenant`, `landlord` or `either` for a break, and `tenant` or `landlord` for a repair duty. It is refused with 422 when a clause number is not a clause of that lease, and the message lists the clause numbers the lease has. An unknown lease answers 404.

## Restaurant performance (system: performance)

Figures for the period and the two months before it (`2026-10`, `2026-09`, `2026-08`), for all twelve restaurants: sales, labour cost, labour hours and food waste, each with its plan. Amounts are US dollars. "Against plan" is the difference as a percentage of plan.

Three peer groups: PG-1 Port Ilvane restaurants (R-014, R-022, R-058, R-071), PG-2 Marlow Reach restaurants (R-031, R-063, R-076, R-104), PG-3 Neighbourhood restaurants (R-047, R-082, R-090, R-117).

The company's rules, served with the figures as `departure_rules`:

- Against plan: sales, labour cost, labour hours or food waste more than 5.0 percent above or below plan. Being ahead of plan by more than that is listed as a departure too.
- Against the peer group: labour cost as a percentage of sales, or food waste as a percentage of sales, more than 1.5 times the average of the other restaurants in the group.
- The figures do not say why, and they say nothing about any colleague.

The period, `2026-10`:

| Site | Peer group | Sales | Plan | Against plan | Labour cost | Plan | Against plan | Labour hours | Plan | Against plan | Food waste | Plan | Against plan | Labour cost % of sales | Food waste % of sales |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-014 | PG-1 | 198,450 | 196,000 | +1.2 | 49,730 | 50,960 | -2.4 | 3,442 | 3,514 | -2.0 | 3,970 | 3,920 | +1.3 | 25.1 | 2.0 |
| R-022 | PG-1 | 183,650 | 171,000 | +7.4 | 43,220 | 44,460 | -2.8 | 2,968 | 3,066 | -3.2 | 3,010 | 3,420 | -12.0 | 23.5 | 1.6 |
| R-031 | PG-2 | 156,580 | 158,000 | -0.9 | 41,570 | 41,080 | +1.2 | 2,856 | 2,833 | +0.8 | 6,640 | 3,160 | +110.1 | 26.5 | 4.2 |
| R-047 | PG-3 | 148,150 | 182,000 | -18.6 | 51,340 | 47,320 | +8.5 | 3,557 | 3,263 | +9.0 | 3,680 | 3,640 | +1.1 | 34.7 | 2.5 |
| R-058 | PG-1 | 198,910 | 204,000 | -2.5 | 53,380 | 53,040 | +0.6 | 3,576 | 3,658 | -2.2 | 4,210 | 4,080 | +3.2 | 26.8 | 2.1 |
| R-063 | PG-2 | 151,060 | 149,000 | +1.4 | 38,240 | 38,740 | -1.3 | 2,613 | 2,672 | -2.2 | 2,970 | 2,980 | -0.3 | 25.3 | 2.0 |
| R-071 | PG-1 | 132,270 | 133,000 | -0.5 | 35,480 | 34,580 | +2.6 | 2,437 | 2,385 | +2.2 | 2,680 | 2,660 | +0.8 | 26.8 | 2.0 |
| R-076 | PG-2 | 123,570 | 127,000 | -2.7 | 33,750 | 33,020 | +2.2 | 2,295 | 2,277 | +0.8 | 2,580 | 2,540 | +1.6 | 27.3 | 2.1 |
| R-082 | PG-3 | 143,190 | 141,000 | +1.6 | 36,790 | 36,660 | +0.4 | 2,593 | 2,528 | +2.6 | 2,730 | 2,820 | -3.2 | 25.7 | 1.9 |
| R-090 | PG-3 | 119,500 | 118,000 | +1.3 | 31,180 | 30,680 | +1.6 | 2,064 | 2,116 | -2.5 | 2,350 | 2,360 | -0.4 | 26.1 | 2.0 |
| R-104 | PG-2 | 120,630 | 122,000 | -1.1 | 32,420 | 31,720 | +2.2 | 2,249 | 2,188 | +2.8 | 2,440 | 2,440 | +0.0 | 26.9 | 2.0 |
| R-117 | PG-3 | 138,240 | 136,000 | +1.6 | 35,370 | 35,360 | +0.0 | 2,438 | 2,439 | +0.0 | 2,790 | 2,720 | +2.6 | 25.6 | 2.0 |

The right answers for the period:

- **R-047, well under its sales plan with labour over plan.** Three departures against plan: sales 148,150 against 182,000 (18.6 percent below), labour cost 51,340 against 47,320 (8.5 percent above), labour hours 3,557 against 3,263 (9.0 percent above). Food waste is within plan. Against the peer group there is no departure: its labour cost is 34.7 percent of sales and the other three restaurants of PG-3 average 25.8 percent, which is 1.34 times, below 1.5. The two months before show the slide: sales 2.8 percent below plan in `2026-08` and 9.5 percent below in `2026-09`.
- **R-031, food waste at about twice its peer group.** Two departures: food waste 6,640 against a plan of 3,160 (110.1 percent above), and food waste at 4.2 percent of sales against an average of 2.0 percent for the other three restaurants of PG-2, which is 2.1 times. Sales, labour cost and labour hours are within plan. Food waste was 3.9 percent above plan in `2026-08` and 39.9 percent above in `2026-09`.
- **R-022, ahead on everything.** Two departures, both ahead of plan: sales 183,650 against 171,000 (7.4 percent above) and food waste 3,010 against 3,420 (12.0 percent below). Labour cost (2.8 percent below) and labour hours (3.2 percent below) are ahead of plan too, and within 5.0 percent.
- **The other nine restaurants** have no departure: every figure is within 3.2 percent of plan, and no percentage of sales is more than 1.11 times the average of the others.

Right answer for a review: each departure with the restaurant's figure, the plan figure or the peer average, and the difference; "no departure" said plainly when there is none; no reason given that the figures do not give, and no conclusion about the restaurant manager or any colleague. The area manager draws the conclusions and agrees the actions with the restaurant.

`save_performance_review` is a draft and keeps every version. A departure against `plan` names `sales`, `labour_cost`, `labour_hours` or `food_waste`. A departure against `peer_group` names `labour_cost_pct_of_sales` or `food_waste_pct_of_sales`. Any other pairing is refused with 422. A store, or a restaurant the system does not hold, answers 404. A month before `2026-08` answers 404. A month that has not ended (`2026-11` and later) answers 409.

## Refunds, voids and discounts (system: tills)

180 rows for the period, `TR-2610-0001` to `TR-2610-0180`, from the tills of the eight stores and twelve restaurants: 72 refunds, 48 voids and 60 discounts. A cashier and an approver appear by id only. The system holds no colleague's name.

The company's rules (Till Controls, version 1.3), served by `get_till_rules`:

| Rule | Applies to | The rule | A row is outside it when |
|---|---|---|---|
| TC-1 | refund | A refund above USD 50.00 needs a manager's approval | the amount is above 50.00 and `approver_id` is empty |
| TC-2 | refund | No refund without the original receipt number | `original_receipt` is empty, whatever the amount |
| TC-3 | discount | A discount above 20 percent needs a reason code | `discount_percent` is above 20 and `reason_code` is empty |
| TC-4 | void | A void after payment needs a second person | `after_payment` is true and `approver_id` is empty |

28 rows are outside the rules. Two of them are outside two rules, so the rules are broken 30 times: TC-1 nine times, TC-2 seven times, TC-3 eight times, TC-4 six times. The other 152 rows are within the rules, some only just: three refunds of exactly 50.00 with no approver, 24 refunds above 50.00 with an approver, thirteen discounts above 20 percent with a reason code, discounts of exactly 20 percent with no code, 17 voids before payment and 25 voids after payment with a second person.

| Row | Date | Time | Site | Till | Cashier id | Kind | Amount | Rules | What the row shows |
|---|---|---|---|---|---|---|---|---|---|
| TR-2610-0016 | 2026-10-03 | 18:42 | S-106 | T2 | C-3173 | refund | 84.50 | TC-1 | no approver |
| TR-2610-0020 | 2026-10-04 | 12:26 | S-101 | T3 | C-3122 | refund | 95.00 | TC-1 | no approver |
| TR-2610-0024 | 2026-10-05 | 17:29 | S-103 | T1 | C-3141 | void | 14.20 | TC-4 | after payment, no second person |
| TR-2610-0028 | 2026-10-06 | 11:14 | S-106 | T1 | C-3171 | refund | 61.20 | TC-1 | no approver |
| TR-2610-0033 | 2026-10-07 | 09:48 | S-102 | T2 | C-3133 | refund | 12.49 | TC-2 | no receipt number |
| TR-2610-0042 | 2026-10-08 | 13:40 | S-106 | T1 | C-3174 | discount | 20.00 | TC-3 | 25 percent of 80.00, no reason code |
| TR-2610-0052 | 2026-10-09 | 19:15 | S-106 | T2 | C-3173 | refund | 129.99 | TC-1 | no approver |
| TR-2610-0056 | 2026-10-10 | 15:33 | S-101 | T4 | C-3124 | discount | 36.00 | TC-3 | 30 percent of 120.00, no reason code |
| TR-2610-0059 | 2026-10-11 | 16:09 | S-104 | T1 | C-3151 | refund | 55.25 | TC-1 | no approver |
| TR-2610-0064 | 2026-10-12 | 20:05 | S-106 | T2 | C-3173 | refund | 76.00 | TC-1, TC-2 | no approver and no receipt number |
| TR-2610-0066 | 2026-10-13 | 10:05 | S-105 | T1 | C-3162 | discount | 11.00 | TC-3 | 22 percent of 50.00, no reason code |
| TR-2610-0072 | 2026-10-14 | 17:55 | S-106 | T2 | C-3173 | discount | 16.80 | TC-3 | 35 percent of 48.00, no reason code |
| TR-2610-0077 | 2026-10-15 | 13:51 | R-014 | T1 | C-3002 | refund | 64.80 | TC-1 | no approver |
| TR-2610-0086 | 2026-10-16 | 20:44 | R-022 | T1 | C-3011 | discount | 14.60 | TC-3 | 40 percent of 36.50, no reason code |
| TR-2610-0090 | 2026-10-17 | 19:48 | S-106 | T2 | C-3173 | refund | 210.00 | TC-1, TC-2 | no approver and no receipt number |
| TR-2610-0094 | 2026-10-18 | 14:22 | S-107 | T1 | C-3182 | refund | 44.00 | TC-2 | no receipt number |
| TR-2610-0103 | 2026-10-19 | 10:32 | S-106 | T1 | C-3171 | refund | 18.99 | TC-2 | no receipt number |
| TR-2610-0109 | 2026-10-20 | 12:58 | R-058 | T2 | C-3043 | discount | 21.00 | TC-3 | 100 percent of 21.00, no reason code |
| TR-2610-0118 | 2026-10-21 | 18:20 | S-106 | T2 | C-3173 | refund | 32.40 | TC-2 | no receipt number |
| TR-2610-0123 | 2026-10-22 | 19:37 | R-063 | T2 | C-3051 | refund | 52.00 | TC-1 | no approver |
| TR-2610-0126 | 2026-10-23 | 11:41 | S-104 | T2 | C-3153 | void | 88.00 | TC-4 | after payment, no second person |
| TR-2610-0130 | 2026-10-24 | 20:31 | S-106 | T2 | C-3173 | discount | 31.00 | TC-3 | 50 percent of 62.00, no reason code |
| TR-2610-0136 | 2026-10-25 | 21:10 | R-047 | T1 | C-3031 | refund | 27.90 | TC-2 | no receipt number |
| TR-2610-0137 | 2026-10-26 | 13:03 | R-031 | T1 | C-3022 | void | 31.50 | TC-4 | after payment, no second person |
| TR-2610-0151 | 2026-10-27 | 19:02 | S-106 | T2 | C-3173 | void | 58.75 | TC-4 | after payment, no second person |
| TR-2610-0159 | 2026-10-28 | 18:16 | R-090 | T1 | C-3092 | discount | 11.00 | TC-3 | 25 percent of 44.00, no reason code |
| TR-2610-0162 | 2026-10-29 | 15:07 | S-106 | T2 | C-3174 | void | 23.10 | TC-4 | after payment, no second person |
| TR-2610-0173 | 2026-10-30 | 19:55 | R-104 | T1 | C-3101 | void | 19.75 | TC-4 | after payment, no second person |

Where the rows are: twelve of the 28 are at S-106, two each at S-101 and S-104, and one each at twelve other sites. Eight of the twelve at S-106 carry cashier id C-3173, two carry C-3171 and two carry C-3174. No other cashier id is on more than one of the 28 rows. S-106 has 27 rows in the period and C-3173 is on twelve of them. Five sites have no row outside the rules: R-071, R-076, R-082, R-117 and S-108.

Two rows that are within the rules, only just, both at R-117: `TR-2610-0019` is a refund of exactly 50.00 with its receipt number and no approver, and `TR-2610-0002` is a discount of exactly 20 percent (23.82 off 119.08) with no reason code. R-117 has nine rows in the period and none is outside the rules.

Right answer for an audit: all 28 rows, each with the rule or rules it is outside, and none of the other 152. It may say where the rows are, by site and by cashier id, as a count of rows. It gives no reason, draws no conclusion about a colleague and names no person as at fault. An auditor reviews every row.

`save_till_audit` is a draft and keeps every version. It accepts the rule ids `TC-1`, `TC-2`, `TC-3` and `TC-4`. A row id that is not a row of the month (or of the site, when the audit is for one site) answers 404. A row listed twice answers 422. A month that has not ended (`2026-11` and later) answers 409, and an earlier month with no rows answers 404. `get_till_audit` reads the saved versions back.

## Simulated arrivals

`POST /admin/simulate/<kind>` makes one new item from four rotating templates per kind. The fifth call uses the first template again with new ids.

supplier-invoice. Each call makes a purchase order (`PO-4502xx`), a goods receipt (`GR-602xx`, goods received in full) and an invoice (`INV-44xx`, dated the retailer date), all in the purchasing system:

1. Tallowby Flour Mills Ltd, 400 bags of pizza flour at 44.50. The invoice agrees.
2. Ilvane Valley Dairy Ltd, 80 kg of butter at 31.00. The invoice says 32.50: price differs by 120.00 net.
3. Orchard Gate Fresh Produce Ltd, 600 kg of white onions at 2.80, received 600. The invoice says 650 kg: quantity differs by 50 kg, 140.00 net.
4. Marlow Reach Packaging Ltd, 10,000 medium boxes at 0.42. The invoice has a second line, a pallet charge of 95.00, that is not on the order.

food-safety-records. Each call makes a month of records and a review (`not_reviewed`) for one more restaurant, in the order R-071, R-076, R-082, R-090, R-104, R-117, for the period. After six calls it goes back one month, so the seventh call is R-071 for the month before:

1. R-071: nothing outside the plan.
2. R-076: walk-in chiller above 5.0 °C three times: day 4 afternoon 6.4, day 5 opening 6.9, day 18 afternoon 7.2. The repeat rule applies.
3. R-082: a chilled delivery at 7.1 °C on day 9, recorded as accepted, and no signed cleaning entry on day 12.
4. R-090: hot holding below 63.0 °C twice (day 10 at 14:00 60.8, day 22 at 16:00 61.5) and a chicken core reading of 73.5 °C in the morning of day 15, below 75.0 °C.

The fifth and sixth calls (R-104 and R-117) use templates 1 and 2 again.

site-visit. Each call makes one more area manager visit in the stores system, dated the retailer date, with no report. Its id is `SV-2611-01`, `SV-2611-02` and so on:

1. R-022: every item scored 2 and the notes raise nothing. No finding.
2. S-101: two findings on the checklist. Item 5 (BS-3.1) scored 0: a spill in aisle 4 had not been cleaned or signed. Item 9 (BS-5.1) scored 1: one shelf-edge price did not match the till. The notes raise nothing.
3. R-063: one finding on the checklist, item 3 (BS-2.1) scored 1. One finding in the notes, tied to BS-7.2: the floor by the drinks machine was wet with no sign beside it. One sentence to clarify: "I am not sure the new manager has settled in."
4. S-107: every item scored 2. The notes hold one sentence to clarify and no finding: "It felt untidy in places."

The fifth call uses the first template again with a new id.

## Rules for checking

- Every JSON answer carries `"demo_data": true`. Every response carries `X-Demo-Data: invented`.
- Changes (ask for corrective actions, record a corrective action, sign the monthly review, approve an invoice for payment, raise an invoice query) are refused with 409 when a precondition fails. Drafts keep every version.
- What version 1.1 added changes no record. Each of its four writes saves a draft only: a visit report, a lease summary, a performance review, a refund and discount audit. A person checks every one of them.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed, and the arrivals made for it.
