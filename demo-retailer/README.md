# Rowanmere Group (invented)

Rowanmere Group is invented, and so is every person, company, store, restaurant, supplier and record in this service. Nothing here describes a real retailer or a real customer.

This is one small service that plays the back-office systems of a retailer, so that AI agents have something realistic to read from and act on. Rowanmere Group has two arms: Rowanmere Market (supermarkets and convenience stores, with an online shop) and Rowanmere Kitchen (quick-service restaurants, some of them franchised). The service holds fourteen systems with invented data. Each system has its own OpenAPI document, its own docs page and its own MCP address, the way a real retailer keeps separate systems. It is a sibling of the demo bank in `../demo-bank` and is built the same way.

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`.

Licence: Apache-2.0.

## The fourteen systems

| System | Path | What it holds | Operations |
|---|---|---|---|
| stores | `/stores` | the group's eight stores and twelve restaurants: town, street, area, area manager, franchisee. Also the area managers' visits: the checklist with scores, the notes, and the reports saved on them. Also yesterday's shift log of six sites with the handover notes saved on them, and six colleagues' accounts of accidents and incidents with the report forms saved on them | 11 |
| foodsafety | `/foodsafety` | the food safety plan (version 5.0), each restaurant's monthly temperature, cleaning and delivery records, and the monthly review | 8 |
| care | `/care` | guest feedback: 260 comments for the last full month, and the analyses saved on them. Also the online shop's customer care: twenty customer tickets, twelve help articles, ten past cases, eight complaints with their contact history and the complaints procedure (version 2.1), and twelve public reviews, with the drafts saved on them | 20 |
| purchasing | `/purchasing` | suppliers, purchase orders, goods received, supplier invoices and the matches saved on them. Also eight delivery notes with the claims drafted on them, ten supplier payments made and scheduled, and six supplier questions with the replies drafted on them | 20 |
| property | `/property` | nine store and restaurant leases, each with its full text in numbered clauses, and the summaries saved on them | 3 |
| performance | `/performance` | each restaurant's sales, labour cost, labour hours and food waste for three months, with plan and peer group, and the reviews saved on them | 4 |
| tills | `/tills` | 180 refunds, voids and discounts for the last full month, the company's four till rules, and the audits saved on the month | 4 |
| orders | `/orders` | the online shop's 43 orders with their deliveries and carrier scans, ten return requests and the returns policy (version 3.0), and four orders flagged for a fraud review, with each customer's earlier orders | 14 |
| catalogue | `/catalogue` | the online shop's sixty product listings in eight categories, the supplier's specification for each, the style guide for descriptions (version 1.3), twelve new products with their image descriptions as text, and a month of the shop's search log. It holds no images | 12 |
| stock | `/stock` | stock on hand and thirteen weeks of sales for sixty lines in the eight stores, each line's supplier, lead time and open orders, the replenishment rules (version 2.1), eight stock counts with loss and the stock loss tolerance (version 1.4), and four batches with the stores and online orders that received them | 15 |
| pricing | `/pricing` | the price file with costs, two competitors' published prices for thirty lines, the pricing rules (version 2.0), six finished promotions with plan and result, range review data with the thresholds (version 3.0), sales history by line, and the buying office's market notes | 16 |
| loyalty | `/loyalty` | thirty members of the loyalty programme with consent flags, purchases and browsing, the personalisation rules (version 1.1), six past campaigns with results, and the campaign brief template (version 1.0) | 10 |
| people | `/people` | next week's draft rosters of four restaurants and two stores, with colleagues by id and role, the working time and staffing rules (version 1.2), and the checks saved on each roster | 5 |
| franchise | `/franchise` | the three franchisees with their restaurants, and seventeen questions franchisees have asked, for trying an agent that answers from the franchise operations manual. It only reads | 4 |

In all, 146 operations:

- stores: `list_sites`, `get_site`, `list_site_visits`, `get_site_visit`, `save_visit_report`, `get_shift_log`, `save_handover_note`, `list_incident_accounts`, `get_incident_account`, `save_incident_report`, `submit_incident_report`
- foodsafety: `get_food_safety_plan`, `list_record_periods`, `get_food_safety_records`, `get_record_review`, `save_record_check`, `request_corrective_actions`, `record_corrective_action`, `sign_monthly_review`
- care: `list_guest_feedback`, `get_guest_feedback`, `get_feedback_analysis`, `save_feedback_analysis`, `list_customer_tickets`, `get_customer_ticket`, `search_help_articles`, `search_past_cases`, `save_ticket_reply`, `send_ticket_reply`, `list_complaints`, `get_complaint`, `get_complaints_procedure`, `save_complaint_classification`, `save_complaint_response`, `send_complaint_response`, `list_public_reviews`, `get_public_review`, `save_review_reply`, `publish_review_reply`
- purchasing: `list_suppliers`, `get_supplier`, `list_purchase_orders`, `get_purchase_order`, `list_goods_receipts`, `list_supplier_invoices`, `get_supplier_invoice`, `save_invoice_match`, `approve_invoice_for_payment`, `raise_invoice_query`, `list_delivery_notes`, `get_delivery_note`, `save_discrepancy_claim`, `send_discrepancy_claim`, `list_supplier_payments`, `get_supplier_payment`, `list_supplier_questions`, `get_supplier_question`, `save_supplier_reply`, `send_supplier_reply`
- property: `list_leases`, `get_lease`, `save_lease_summary`
- performance: `list_performance_periods`, `get_restaurant_performance`, `get_peer_group_performance`, `save_performance_review`
- tills: `get_till_rules`, `list_till_entries`, `get_till_audit`, `save_till_audit`
- orders: `search_orders`, `get_order`, `get_delivery_scans`, `get_returns_policy`, `list_return_requests`, `get_return_request`, `save_return_assessment`, `approve_return`, `refuse_return`, `list_flagged_orders`, `get_customer_order_history`, `save_fraud_review`, `release_flagged_order`, `hold_flagged_order`
- catalogue: `list_product_listings`, `get_product_listing`, `get_supplier_specification`, `get_product_style_guide`, `list_new_products`, `save_product_description`, `publish_product_description`, `get_product_data_checks`, `save_product_data_check`, `get_search_log`, `get_search_terms_analysis`, `save_search_terms_analysis`
- stock: `list_stock_levels`, `get_line_stock_history`, `get_replenishment_rules`, `list_supply_terms`, `get_replenishment_plan`, `save_replenishment_plan`, `approve_replenishment_plan`, `list_stock_counts`, `get_shrink_tolerance`, `get_shrink_analysis`, `save_shrink_analysis`, `list_batches`, `get_batch_trace`, `save_recall_pack`, `issue_recall_notice`
- pricing: `list_prices`, `list_competitor_prices`, `get_pricing_rules`, `get_price_recommendations`, `save_price_recommendations`, `approve_price_changes`, `list_promotions`, `get_promotion`, `save_promotion_review`, `get_range_review_thresholds`, `get_range_review_data`, `save_range_review_pack`, `list_line_sales_history`, `get_market_notes`, `get_demand_plan_notes`, `save_demand_plan_note`
- loyalty: `list_members`, `get_member`, `get_personalisation_rules`, `save_product_suggestions`, `get_loyalty_programme_summary`, `list_past_campaigns`, `get_past_campaign`, `get_campaign_brief_template`, `list_campaign_briefs`, `save_campaign_brief`
- people: `list_draft_rosters`, `get_draft_roster`, `get_working_time_rules`, `save_roster_check`, `publish_roster`
- franchise: `list_franchisees`, `get_franchisee`, `list_franchisee_questions`, `get_franchisee_question`

For each system `<path>`:

- `<path>/openapi.json` is its OpenAPI 3.0.3 document. Every operation has a snake_case `operationId` (verb first, unique across the whole service), a summary and a description written for a language model.
- `<path>/docs` is its docs page. It loads nothing from the internet.
- `<path>/mcp` is its MCP address over streamable HTTP. `<path>/sse` is the same tools over SSE. The tool names and descriptions are the `operationId`s and descriptions of the OpenAPI document, built from it, never kept twice.

The landing page `/` lists all of this with counts. `/health` and `/healthz` answer without a key.

Operations that only read are plain reads. Operations that write come in two kinds:

- A draft (a saved check of a month's records, a feedback analysis, an invoice match, a visit report, a lease summary, a performance review, a refund and discount audit, a ticket reply, a complaint classification and response, a review reply, a return assessment, a fraud review, a discrepancy claim, a supplier reply, a product description, a product data check, a search terms analysis, a replenishment plan, a shrink analysis, a recall pack, price recommendations, a promotion review, a range review pack, a demand plan note, product suggestions, a campaign brief, a roster check, a handover note, an incident report form) is stored with who wrote it (a free-text field, default `agent`), a time and a version number. Earlier versions are kept. A draft changes no status.
- A change (ask for corrective actions, record a corrective action, sign the monthly review, approve an invoice for payment, raise an invoice query, send a ticket reply, send a complaint response, publish a review reply, approve or refuse a return, release or hold a flagged order, send a discrepancy claim, send a supplier reply, publish a product description, approve a replenishment plan, issue a recall notice, approve price changes, publish a roster, submit an incident report) changes a record. The summary of a change ends in "(change)". Where the person who decides is named (`requested_by`, `signed_by`, `approved_by`, `raised_by`, `sent_by`, `published_by`, `refused_by`, `released_by`, `held_by`, `issued_by`, `submitted_by`) the call needs the name. Each of the nine changes of version 1.2, the four of version 1.3 and the two of version 1.4 is refused with 409 until the draft it rests on has been saved. A change is refused with 409 and a readable message when a precondition fails, for example the review is already signed.

A request the service cannot read answers 422 with a message that says which field to correct and which values are accepted. A draft that does not fit the record it is saved on is refused the same way: a lease summary that cites a clause the lease does not have, a visit finding tied to a standard its checklist item does not rest on. A month that has not ended answers 409 in the performance and tills systems and for the search log. Some drafts of version 1.3 are checked against the company's own rules as they are saved: a price that breaks the floor margin, the price endings or the maximum weekly move, a suggestion that a personalisation rule blocks, a description outside the style guide, and a recall pack that leaves a store or an order out are refused with 422 and the rule. The drafts of version 1.4 are checked against the record they rest on: a roster check that names a colleague or a shift the roster does not hold, a handover note with a line that rests on no entry of the log, and an incident report that leaves out a clause the procedure sets are refused with 422.

This is a simulator with its own state. A write really changes it, and the answer says `"applied": true`. One rule holds for every agent that uses it: an agent prepares the work, and a person decides. Nothing here pays an invoice or a refund, decides whether food was safe, ends a lease, says that a colleague did anything wrong or says that a customer is a fraudster. Nothing here changes a price, places an order with a supplier, publishes a listing, tells a store or a customer about a recall, or shows a shopper a suggestion, until a named person has done it. Nothing here changes a shift or gives one to a colleague, and nothing here decides a safety matter.

Dates are relative to the retailer date (today, or `RETAILER_TODAY`). The period is the last full calendar month before the retailer date, written `YYYY-MM`. With the retailer date 2026-11-24 the period is `2026-10`. Amounts are US dollars. Value added tax in Meridia is 15 percent. Towns are Port Ilvane, Marlow Reach and Tallowby.

The scenarios and their right answers are in [SCENARIOS.md](SCENARIOS.md).

## Quick start

```
pip install -r requirements.txt
python -m uvicorn main:app --port 8461
```

The first start prints a key, because `RETAILER_API_KEY` was not set. Use it:

```
curl -H "X-API-Key: <key>" http://localhost:8461/stores/sites?kind=restaurant
curl -H "Authorization: Bearer <key>" http://localhost:8461/purchasing/invoices?status=received
```

For play on your own laptop only, `RETAILER_AUTH=off` turns the key check off. The landing page then shows a warning.

With Docker:

```
docker build -t rowanmere-demo-retailer .
docker run --rm -p 8080:8080 -e RETAILER_API_KEY=choose-a-key rowanmere-demo-retailer
```

Behind a prefix (the application gateway removes the prefix before the request arrives, links keep it):

```
cd demo-retailer && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8080 --root-path /apps/demo-retailer
```

Tests: `pip install -r requirements-dev.txt` then `pytest`. One test file, `tests/test_agent_folders.py`, checks every agent folder in `../retail/agents` against the retailer: each operation an agent names must exist in a system it lists (field `demo_retailer_systems`), each operation that writes must be listed under the agent's `changes`, and each `tests.yaml` must be readable, with a known state and something expected for every test. It is skipped when the folder is missing.

Behind a gateway, absolute addresses on the landing page use the scheme in `X-Forwarded-Proto` when it is present, otherwise the request's own scheme.

## Sign-in

Data operations, the MCP addresses and the admin routes need the key, as the header `X-API-Key: <key>` or as `Authorization: Bearer <key>`. Open without a key: `/`, `/health`, `/healthz`, the docs pages and the OpenAPI documents. Each OpenAPI document declares the header key as its security scheme.

## Environment variables

| Variable | Meaning |
|---|---|
| `RETAILER_API_KEY` | The key. If not set, a random key is made at start and printed once in the log. It is never shown on a page. |
| `RETAILER_AUTH` | `off` turns the key check off (laptop only). |
| `RETAILER_TODAY` | The retailer date, `YYYY-MM-DD`. Default is today. Dates in the data are relative to it. With the same retailer date the data is identical on every start. |
| `DATA_DIR` | A writable folder. State is written there as one JSON file. |
| `KATONIC_DATASET_PATH` | If `DATA_DIR` is not set and this is, state goes to `<KATONIC_DATASET_PATH>/demo-retailer-state`. |
| `RETAILER_WEBHOOKS` | A JSON list of subscriptions, each `{"event_kind": "...", "url": "...", "header_name": "...", "secret_value": "..."}`. |
| `RETAILER_PUBLIC_SCHEME` | `https` or `http`. Forces the scheme in every address the service prints. Set it to `https` when the service sits behind a gateway that ends the secure connection early, and the landing page shows `http://` addresses. |

With none of `DATA_DIR` and `KATONIC_DATASET_PATH`, the service writes no file at all. It never writes inside its own folder, so a read-only root filesystem is fine. State lives in memory. Subscriptions added through the API live in memory only and are never written to the state file, because they hold a secret.

## Events

These routes need the key.

- `POST /admin/reset` puts the data back to the start.
- `POST /admin/reset/<system>` puts back only what that one system has changed since the start or the last full reset: the records its operations wrote and the items made to arrive for it. The rest of the retailer stays as it is, so several people can test different agents against one retailer without wiping each other's records. The answer lists what was put back.
- `GET /admin/state` gives counts, and under `changed_by` which system has changed what.
- `GET /admin/events` shows what was sent and the outcome.
- `GET`, `POST` and `DELETE /admin/subscriptions` manage subscriptions: an event kind (`supplier-invoice`, `food-safety-records`, `site-visit`, `customer-ticket`, `return-request`, `complaint`, `public-review`, `flagged-order`, `delivery-note`, `supplier-question`, `new-product`, `promotion-ended`, `recalled-batch`, `stock-count`, `shift-end`, `incident-account`, or `*`), a URL, a header name and a secret value.
- `POST /admin/simulate/<kind>` makes one new item arrive, from a pool of four templates that rotate. `supplier-invoice` makes a purchase order, a goods receipt and a new supplier invoice in the purchasing system (templates in turn: the invoice agrees, the price differs, the quantity differs, a line is not on the order). `food-safety-records` makes a month of records, and its review, for one more restaurant in the foodsafety system (templates in turn: nothing outside the plan, a chiller above its limit three times, a chilled delivery that is too warm and a missing cleaning sign-off, hot holding and chicken core readings below their limits). `site-visit` makes one more area manager visit in the stores system, dated the retailer date (templates in turn: nothing to report, two findings on the checklist, one finding on the checklist with one in the notes and one vague sentence, a clean checklist with one vague sentence in the notes). Version 1.2 adds seven kinds, each with four templates: `customer-ticket` (three that a help article answers and one that none does), `return-request` (inside the window, outside it, an excluded category, an opened item), `complaint` (one of each class), `public-review` (praise, criticism, both, and one that describes a safety matter), `flagged-order` (two that depart from the customer's pattern and two that the history explains), `delivery-note` (agrees, short delivery, wrong item, damaged) and `supplier-question` (paid, scheduled, short-paid, and one the records cannot answer). Version 1.3 adds four kinds, each with four templates: `new-product` (a plain grocery line, one with allergens, an age-restricted line, and one whose picture and specification disagree), `promotion-ended` (on plan and in profit, sold well and lost money, displaced a neighbouring line, undersold), `recalled-batch` (stores and orders, three stores and two orders, one store and no order, orders and no store) and `stock-count` (within tolerance, beyond it with three lines beyond, just within, beyond it with all the loss in one line). Version 1.4 adds two kinds, each with four templates, both in the stores system: `shift-end` (the day's shift log of one more site: nothing open, two entries open, one open with no time given, three open) and `incident-account` (a small cut, a customer's fall, a near miss, a guest who reports being ill). [SCENARIOS.md](SCENARIOS.md) gives the right answer for each.

For each matching subscription the service POSTs `{"message": "...", "event_type": "...", "item_id": "...", "system": "...", "demo_data": true}` with the secret header and a 10 second timeout. A failed delivery never fails the caller. The outcome is recorded in the events log. The message is plain sentences that say what arrived, its id and which system holds it.

## Connecting it to a platform

These steps follow the demo bank's. They have not been run for this service yet.

1. Deploy it. In App Studio, start a new app from the public repository, branch `main`, with the main file `demo-retailer/main.py`. Set the health check path to `/health`.
2. Choose the app's access. Every access level except Public puts a person's sign-in page in front of the app, and the platform's own services cannot pass it. So the app is set to Public, and the service's own key protects it: set `RETAILER_API_KEY` as a secret setting. If a test key may not be entered, run it with `RETAILER_AUTH=off`, on a development cluster only.
3. Import a system as tools. In Control Room, Tools, Import OpenAPI, import from the URL of one system's document, for example `<the app's address>/foodsafety/openapi.json`. Choose the API key sign-in with the header `X-API-Key`, and an access group. Each operation becomes a tool. Import one system at a time, so that an agent gets only the tools of the systems it needs.
4. Attach the tools to an agent in Studio and ask it something. A call to a tool reaches the service and comes back with `"demo_data": true`.

## Notes for people who build on it

- All names, places, identifiers and country codes are invented. The home country is Meridia (`XM`) and the towns are Port Ilvane, Marlow Reach and Tallowby. Email addresses of suppliers and of the company end in `.example`, and a customer's ends in `.invalid`.
- Version 1.4 holds fourteen systems. It adds the people system (draft rosters and the rules they are checked against) and the franchise system (franchisees and their questions), and it adds shift logs and incident accounts to the stores system: 15 operations and two kinds of arrival. It changed no path, no name and no answer shape of an earlier operation, and it added no record to an earlier record set.
- A colleague appears in a roster, a shift log and an incident account by id and role only. A guest is never named. The roster gives an age band, adult or young worker, never a date of birth.
- The working time rules are the company's statement of the rules of Meridia, an invented country. They are not the rules of any real country. The service serves them, and the same text is a document in `../retail/policy-library/`: a test keeps them equal.
- The service holds no wording of the store procedures manual, the franchise operations manual or the brand standards. An incident account names the procedure its report form follows, and a franchisee names the two documents a question is answered from. The documents are in `../retail/policy-library/`, to be attached as knowledge sources. The franchise agreement is in no system and in no document, on purpose: a question about it goes to the franchise team.
- What a careful reader should find in version 1.4 is never served: which shifts break a rule, which log entries are still open and which comes first, what an incident report form should hold, and where a franchisee's question is answered. The seed works the breaches of each roster out from its shifts every time it builds the data, and stops when they are not the planted ones.
- Version 1.3 held twelve systems. It added Rowanmere Market's side of the business: the catalogue, stock, pricing and loyalty systems, 53 operations and four kinds of arrival. It changed no path, no name and no answer shape of an earlier operation, and it added no record to an earlier system: the purchasing system still holds four suppliers and eight purchase orders.
- The four systems of version 1.3 share sixty lines. Seven of them are the grocery, chilled, frozen and personal care items the online orders already name, with the same ids and prices. The stock and pricing systems serve the same thirteen weeks of sales.
- Ten suppliers supply the Market's lines. Three of them also supply the restaurants and are in the purchasing system. The other seven are held in the stock system's supply terms only, and `list_supply_terms` says which is which. The Market's open orders are in the supply terms as well, with references that start `MO-`. Approving a replenishment plan writes no purchase order to the purchasing system.
- The catalogue holds no images. An image of a new product is a description in words, and an agent that reads it has seen no picture.
- The loyalty system returns no suggestions of its own, on purpose: an agent works them out from the member, the rules and the catalogue, and saves them. A member is an invented name, a member number and an address that ends in `.invalid`. The age check is a flag, never a date of birth.
- The figures of a promotion stand on their own. They are not worked into the weekly sales the stock system serves.
- What a careful reader should find in version 1.3 is never served either: which listings differ from their specification, which lines run out, which stores and lines are beyond tolerance, what the pricing rules allow, what a promotion added up to, which lines are below a threshold, and what a member should be shown. The service serves the records and the company's rules, and `SCENARIOS.md` gives the answers. The seed checks its own planted cases every time it builds the data.
- The product style guide and the campaign brief template are served by the service and are also documents in `../retail/policy-library/`, with the same text: a test keeps them equal.
- Version 1.2 held eight systems. Version 1.1 added leases, restaurant performance, till rows and area manager visits to version 1. Version 1.2 adds the orders system, the rest of customer care (tickets, complaints, public reviews) and the rest of purchasing (delivery notes, supplier payments, supplier questions). Operation names already in use will not change, and version 1.2 changed no path and no answer shape of an earlier operation. It added two purchase orders, PO-450161 and PO-450164, each with a goods receipt, so the lists of orders and receipts hold eight rows where they held six.
- The tills system holds refunds, voids and discounts only. It holds no sales rows yet.
- What a careful reader should find is never served: which till rows were planted, which sentences of a visit's notes are findings, and the last day for a lease's break notice. Nor is which help article answers a ticket, how a complaint should be classified, which public reviews go to a person, what a return assessment or a fraud review should propose, or what a delivery note should claim. They are in `SCENARIOS.md`. The lease gives the months of notice, and `get_lease` gives the retailer date, so the last day and how far away it is can be worked out.
- The wording of the brand standards is not in the service. A visit's checklist carries the number of the standard each item rests on, and the document is in `../retail/policy-library/brand-standards-v2.0.md`, to be attached as a knowledge source.
- The returns policy, the complaints procedure and the help articles are served by the service and are also documents in `../retail/policy-library/`, with the same text: a test keeps them equal. The brand voice guide is a document there only.
- A customer appears by an invented name, an id and an address ending in `.invalid`. A delivery address, a device and a payment card appear as a reference such as `ADDR-1`, never as the thing itself.
- The purchasing system holds no delivery slots and no dock rules, on purpose: one supplier question asks about a slot, and the right answer is that the records do not say.
- Colleagues appear in the tills system by id only. No operation serves a colleague's name there.
- The theme a guest comment was made from is kept in the seed and no operation serves it. An analysis has to find the themes itself.
- The food safety plan's limits are served as data with the log columns they apply to, so a check can be written from the plan without hard-coded numbers.
- If the `fastapi-offline` package is not installed, the docs pages are switched off. The OpenAPI documents are still served.
- Do not change a record set's shape without changing the seed and the tests together: `tests/test_operations.py`, `tests/test_version_1_1.py`, `tests/test_version_1_2.py`, `tests/test_version_1_3.py` and `tests/test_version_1_4.py` read the planted cases back through the API and compare them with the tables in `SCENARIOS.md`.
