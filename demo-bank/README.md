# Meridian Trust Bank (invented)

Meridian Trust Bank is invented, and so is every person, company, account and record in this service. Nothing here describes a real bank or a real customer.

This is one small service that plays the back-office systems of a bank, so that AI agents have something realistic to read from and act on. It holds six systems with invented data. Each system has its own OpenAPI document, its own docs page and its own MCP address, the way a real bank keeps separate systems.

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`.

Licence: Apache-2.0.

## The six systems

| System | Path | What it holds | Operations |
|---|---|---|---|
| core | `/core` | customers, accounts, transactions, contacts, credit exposure | 8 |
| cards | `/cards` | cards, card payments, blocks, replacements, disputes | 7 |
| screening | `/screening` | sanctions and politically-exposed-person alerts, the watchlist | 6 |
| aml | `/aml` | transaction monitoring alerts, rules, counterparties, cases | 8 |
| payments | `/payments` | payments, investigations, the repair queue, rules, bank directory | 13 |
| lending | `/lending` | loan applications, documents, credit policy, approved loans | 11 |

For each system `<path>`:

- `<path>/openapi.json` is its OpenAPI 3.0.3 document. Every operation has a snake_case `operationId` (verb first, unique across the whole service), a summary and a description written for a language model.
- `<path>/docs` is its docs page. It loads nothing from the internet.
- `<path>/mcp` is its MCP address over streamable HTTP. `<path>/sse` is the same tools over SSE. The tool names and descriptions are the `operationId`s and descriptions of the OpenAPI document, built from it, never kept twice.

The landing page `/` lists all of this with the counts of open items. `/health` and `/healthz` answer without a key.

Operations that only read are plain reads. Operations that write come in two kinds:

- A draft (a recommendation, a narrative, a reply, a proposal, missing items, a memo, document differences, a contact note) is stored with who wrote it (a free-text field, default `agent`), a time and a version number. Earlier versions are kept.
- A change (close an alert, release a repair, block a card, request a replacement, open a dispute, recall a payment) changes a status. Where the person who decides is listed (`decided_by`, `approved_by`) the call needs the name. A change is refused with 409 and a readable message when a precondition fails, for example the alert is already closed.

This is a simulator with its own state. A write really changes it, and the answer says `"applied": true`. There is deliberately no operation that files a report.

The scenarios and their right answers are in [SCENARIOS.md](SCENARIOS.md).

## Quick start

```
pip install -r requirements.txt
python -m uvicorn main:app --port 8080
```

The first start prints a key, because `BANK_API_KEY` was not set. Use it:

```
curl -H "X-API-Key: <key>" http://localhost:8080/core/customers?name=Marrowick
curl -H "Authorization: Bearer <key>" http://localhost:8080/aml/alerts?status=open
```

For play on your own laptop only, `BANK_AUTH=off` turns the key check off. The landing page then shows a warning.

With Docker:

```
docker build -t meridian-demo-bank .
docker run --rm -p 8080:8080 -e BANK_API_KEY=choose-a-key meridian-demo-bank
```

Behind a prefix (the application gateway removes the prefix before the request arrives, links keep it):

```
cd demo-bank && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8080 --root-path /apps/demo-bank
```

Tests: `pip install -r requirements-dev.txt` then `pytest`.

## Sign-in

Data operations, the MCP addresses and the admin routes need the key, as the header `X-API-Key: <key>` or as `Authorization: Bearer <key>`. Open without a key: `/`, `/health`, `/healthz`, the docs pages and the OpenAPI documents. Each OpenAPI document declares the header key as its security scheme.

## Environment variables

| Variable | Meaning |
|---|---|
| `BANK_API_KEY` | The key. If not set, a random key is made at start and printed once in the log. It is never shown on a page. |
| `BANK_AUTH` | `off` turns the key check off (laptop only). |
| `BANK_TODAY` | The bank date, `YYYY-MM-DD`. Default is today. Dates in the data are relative to it. With the same bank date the data is identical on every start. |
| `DATA_DIR` | A writable folder. State is written there as one JSON file. |
| `KATONIC_DATASET_PATH` | If `DATA_DIR` is not set and this is, state goes to `<KATONIC_DATASET_PATH>/demo-bank-state`. |
| `BANK_WEBHOOKS` | A JSON list of subscriptions, each `{"event_kind": "...", "url": "...", "header_name": "...", "secret_value": "..."}`. |

With none of `DATA_DIR` and `KATONIC_DATASET_PATH`, the service writes no file at all. It never writes inside its own folder, so a read-only root filesystem is fine. State lives in memory. Subscriptions added through the API live in memory only and are never written to the state file, because they hold a secret.

## Events

These routes need the key.

- `POST /admin/reset` puts the data back to the start.
- `GET /admin/state` gives counts.
- `GET /admin/events` shows what was sent and the outcome.
- `GET`, `POST` and `DELETE /admin/subscriptions` manage subscriptions: an event kind (`screening-alert`, `payment-repair`, `payment-investigation`, `loan-application`, or `*`), a URL, a header name and a secret value.
- `POST /admin/simulate/<kind>` creates one new item from a pool of four templates per kind, rotating.

For each matching subscription the service POSTs `{"message": "...", "event_type": "...", "item_id": "...", "system": "...", "demo_data": true}` with the secret header and a 10 second timeout. A failed delivery never fails the caller. The outcome is recorded in the events log. The message is plain sentences that say what arrived, its id and which system holds it.

## Connecting it to a platform

The steps are being proven on a cluster and will be added.

## Notes for people who build on it

- All names, places, bank codes, identifiers and country codes are invented. Countries use codes that no real country has (`XM` is Meridia, the bank's home). The watchlist is the "Meridia Consolidated Demonstration List (invented)".
- Account numbers are IBAN-shaped with correct check digits, except where a scenario needs a wrong one. Card numbers appear only masked.
- If the `fastapi-offline` package is not installed, the docs pages are switched off. The OpenAPI documents are still served.
