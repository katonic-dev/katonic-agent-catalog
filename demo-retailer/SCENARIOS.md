# Scenarios and right answers

Rowanmere Group is invented, and so is every record here. This file lists each scenario, what it is for, and the right answer. Use it to mark an agent's work.

All dates are relative to the retailer date (today, or `RETAILER_TODAY`). The tests fix it at `2026-11-24`, so the period is `2026-10`. Amounts are US dollars. Value added tax in Meridia is 15 percent. Every number below was read back from the running service by `tests/test_operations.py` and `tests/test_events.py`.

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

## Rules for checking

- Every JSON answer carries `"demo_data": true`. Every response carries `X-Demo-Data: invented`.
- Changes (ask for corrective actions, record a corrective action, sign the monthly review, approve an invoice for payment, raise an invoice query) are refused with 409 when a precondition fails. Drafts keep every version.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed, and the arrivals made for it.
