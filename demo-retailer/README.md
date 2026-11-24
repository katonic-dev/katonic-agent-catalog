# Rowanmere Group (invented)

Rowanmere Group is invented, and so is every person, company, store, restaurant, supplier and record in this service. Nothing here describes a real retailer or a real customer.

This is one small service that plays the back-office systems of a retailer, so that AI agents have something realistic to read from and act on. Rowanmere Group has two arms: Rowanmere Market (supermarkets and convenience stores, with an online shop) and Rowanmere Kitchen (quick-service restaurants, some of them franchised). The service holds seven systems with invented data. Each system has its own OpenAPI document, its own docs page and its own MCP address, the way a real retailer keeps separate systems. It is a sibling of the demo bank in `../demo-bank` and is built the same way.

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`.

Licence: Apache-2.0.

## The seven systems

| System | Path | What it holds | Operations |
|---|---|---|---|
| stores | `/stores` | the group's eight stores and twelve restaurants: town, street, area, area manager, franchisee. Also the area managers' visits: the checklist with scores, the notes, and the reports saved on them | 5 |
| foodsafety | `/foodsafety` | the food safety plan (version 5.0), each restaurant's monthly temperature, cleaning and delivery records, and the monthly review | 8 |
| care | `/care` | guest feedback: 260 comments for the last full month, and the analyses saved on them | 4 |
| purchasing | `/purchasing` | suppliers, purchase orders, goods received, supplier invoices and the matches saved on them | 10 |
| property | `/property` | nine store and restaurant leases, each with its full text in numbered clauses, and the summaries saved on them | 3 |
| performance | `/performance` | each restaurant's sales, labour cost, labour hours and food waste for three months, with plan and peer group, and the reviews saved on them | 4 |
| tills | `/tills` | 180 refunds, voids and discounts for the last full month, the company's four till rules, and the audits saved on the month | 4 |

In all, 38 operations:

- stores: `list_sites`, `get_site`, `list_site_visits`, `get_site_visit`, `save_visit_report`
- foodsafety: `get_food_safety_plan`, `list_record_periods`, `get_food_safety_records`, `get_record_review`, `save_record_check`, `request_corrective_actions`, `record_corrective_action`, `sign_monthly_review`
- care: `list_guest_feedback`, `get_guest_feedback`, `get_feedback_analysis`, `save_feedback_analysis`
- purchasing: `list_suppliers`, `get_supplier`, `list_purchase_orders`, `get_purchase_order`, `list_goods_receipts`, `list_supplier_invoices`, `get_supplier_invoice`, `save_invoice_match`, `approve_invoice_for_payment`, `raise_invoice_query`
- property: `list_leases`, `get_lease`, `save_lease_summary`
- performance: `list_performance_periods`, `get_restaurant_performance`, `get_peer_group_performance`, `save_performance_review`
- tills: `get_till_rules`, `list_till_entries`, `get_till_audit`, `save_till_audit`

For each system `<path>`:

- `<path>/openapi.json` is its OpenAPI 3.0.3 document. Every operation has a snake_case `operationId` (verb first, unique across the whole service), a summary and a description written for a language model.
- `<path>/docs` is its docs page. It loads nothing from the internet.
- `<path>/mcp` is its MCP address over streamable HTTP. `<path>/sse` is the same tools over SSE. The tool names and descriptions are the `operationId`s and descriptions of the OpenAPI document, built from it, never kept twice.

The landing page `/` lists all of this with counts. `/health` and `/healthz` answer without a key.

Operations that only read are plain reads. Operations that write come in two kinds:

- A draft (a saved check of a month's records, a feedback analysis, an invoice match, a visit report, a lease summary, a performance review, a refund and discount audit) is stored with who wrote it (a free-text field, default `agent`), a time and a version number. Earlier versions are kept. A draft changes no status.
- A change (ask for corrective actions, record a corrective action, sign the monthly review, approve an invoice for payment, raise an invoice query) changes a record. The summary of a change ends in "(change)". Where the person who decides is named (`requested_by`, `signed_by`, `approved_by`, `raised_by`) the call needs the name. A change is refused with 409 and a readable message when a precondition fails, for example the review is already signed.

A request the service cannot read answers 422 with a message that says which field to correct and which values are accepted. A draft that does not fit the record it is saved on is refused the same way: a lease summary that cites a clause the lease does not have, a visit finding tied to a standard its checklist item does not rest on. A month that has not ended answers 409 in the performance and tills systems.

This is a simulator with its own state. A write really changes it, and the answer says `"applied": true`. One rule holds for every agent that uses it: an agent prepares the work, and a person decides. Nothing here pays an invoice, decides whether food was safe, ends a lease or says that a colleague did anything wrong.

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
- `GET`, `POST` and `DELETE /admin/subscriptions` manage subscriptions: an event kind (`supplier-invoice`, `food-safety-records`, `site-visit`, or `*`), a URL, a header name and a secret value.
- `POST /admin/simulate/<kind>` makes one new item arrive, from a pool of four templates that rotate. `supplier-invoice` makes a purchase order, a goods receipt and a new supplier invoice in the purchasing system (templates in turn: the invoice agrees, the price differs, the quantity differs, a line is not on the order). `food-safety-records` makes a month of records, and its review, for one more restaurant in the foodsafety system (templates in turn: nothing outside the plan, a chiller above its limit three times, a chilled delivery that is too warm and a missing cleaning sign-off, hot holding and chicken core readings below their limits). `site-visit` makes one more area manager visit in the stores system, dated the retailer date (templates in turn: nothing to report, two findings on the checklist, one finding on the checklist with one in the notes and one vague sentence, a clean checklist with one vague sentence in the notes).

For each matching subscription the service POSTs `{"message": "...", "event_type": "...", "item_id": "...", "system": "...", "demo_data": true}` with the secret header and a 10 second timeout. A failed delivery never fails the caller. The outcome is recorded in the events log. The message is plain sentences that say what arrived, its id and which system holds it.

## Connecting it to a platform

These steps follow the demo bank's. They have not been run for this service yet.

1. Deploy it. In App Studio, start a new app from the public repository, branch `main`, with the main file `demo-retailer/main.py`. Set the health check path to `/health`.
2. Choose the app's access. Every access level except Public puts a person's sign-in page in front of the app, and the platform's own services cannot pass it. So the app is set to Public, and the service's own key protects it: set `RETAILER_API_KEY` as a secret setting. If a test key may not be entered, run it with `RETAILER_AUTH=off`, on a development cluster only.
3. Import a system as tools. In Control Room, Tools, Import OpenAPI, import from the URL of one system's document, for example `<the app's address>/foodsafety/openapi.json`. Choose the API key sign-in with the header `X-API-Key`, and an access group. Each operation becomes a tool. Import one system at a time, so that an agent gets only the tools of the systems it needs.
4. Attach the tools to an agent in Studio and ask it something. A call to a tool reaches the service and comes back with `"demo_data": true`.

## Notes for people who build on it

- All names, places, identifiers and country codes are invented. The home country is Meridia (`XM`) and the towns are Port Ilvane, Marlow Reach and Tallowby. Email addresses end in `.example`.
- Version 1.1 holds seven systems. It added leases, restaurant performance, till rows and area manager visits to version 1. Later versions add orders, stock, pricing, catalogue, loyalty and people. Operation names already in use will not change.
- The tills system holds refunds, voids and discounts only. It holds no sales rows yet.
- What a careful reader should find is never served: which till rows were planted, which sentences of a visit's notes are findings, and the last day for a lease's break notice. They are in `SCENARIOS.md`. The lease gives the months of notice, and `get_lease` gives the retailer date, so the last day and how far away it is can be worked out.
- The wording of the brand standards is not in the service. A visit's checklist carries the number of the standard each item rests on, and the document is in `../retail/policy-library/brand-standards-v2.0.md`, to be attached as a knowledge source.
- Colleagues appear in the tills system by id only. No operation serves a colleague's name there.
- The theme a guest comment was made from is kept in the seed and no operation serves it. An analysis has to find the themes itself.
- The food safety plan's limits are served as data with the log columns they apply to, so a check can be written from the plan without hard-coded numbers.
- If the `fastapi-offline` package is not installed, the docs pages are switched off. The OpenAPI documents are still served.
- Do not change a record set's shape without changing the seed and the tests together: `tests/test_operations.py` and `tests/test_version_1_1.py` read the planted cases back through the API and compare them with the tables in `SCENARIOS.md`.
