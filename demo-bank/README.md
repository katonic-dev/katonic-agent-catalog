# Meridian Trust Bank (invented)

Meridian Trust Bank is invented, and so is every person, company, account and record in this service. Nothing here describes a real bank or a real customer.

This is one small service that plays the back-office systems of a bank, so that AI agents have something realistic to read from and act on. It holds nineteen systems with invented data. Each system has its own OpenAPI document, its own docs page and its own MCP address, the way a real bank keeps separate systems. Next to them it serves the public website of an invented regulator, which is not one of the bank's systems.

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`.

Licence: Apache-2.0.

## The nineteen systems

| System | Path | What it holds | Operations |
|---|---|---|---|
| core | `/core` | customers, accounts, transactions, contacts, credit exposure | 8 |
| cards | `/cards` | cards, card payments, blocks, replacements, disputes | 7 |
| screening | `/screening` | sanctions and politically-exposed-person alerts, the watchlist | 6 |
| aml | `/aml` | transaction monitoring alerts and the investigations saved on them, rules, counterparties, cases | 9 |
| payments | `/payments` | payments, investigations, the repair queue, rules, bank directory | 13 |
| lending | `/lending` | loan applications, documents, credit policy, approved loans | 11 |
| fraud | `/fraud` | fraud cases on card payments and payments, the rules that raise them, decisions | 5 |
| recon | `/recon` | reconciliation breaks between the ledger and bank statements, the ledger and statement entries (each readable and searchable), matching rules, proposals, postings | 9 |
| news | `/news` | an invented press archive from two invented outlets, for adverse media screening | 3 |
| onboarding | `/onboarding` | account opening applications and their documents, the bank's requirements, periodic reviews of existing customers | 12 |
| complaints | `/complaints` | customer complaints, the complaints procedure, classifications, responses and redress | 6 |
| collections | `/collections` | transcripts of collections calls, the conduct rules, call reviews | 5 |
| audit | `/audit` | control tests of policy MTB-POL-033, tickets, change records, access reviews, recovery tests | 11 |
| itops | `/itops` | incidents, monitoring metrics, dashboards, recent changes, runbooks | 8 |
| legacy | `/legacy` | an old core system, read only: tables with cryptic names, stored procedures, batch programs | 8 |
| funds | `/funds` | a pension scheme: funds and fact sheets, members, holdings, contribution batches, transfer forms | 10 |
| crm | `/crm` | relationship managers' meetings, what a client holds across the bank, earlier contact | 5 |
| finance | `/finance` | a finance warehouse (general ledger and management accounts for 24 months) that answers one read-only SQL query at a time | 4 |
| research | `/research` | invented listed companies on an invented exchange: filings, prices, consensus estimates | 6 |

For each system `<path>`:

- `<path>/openapi.json` is its OpenAPI 3.0.3 document. Every operation has a snake_case `operationId` (verb first, unique across the whole service), a summary and a description written for a language model.
- `<path>/docs` is its docs page. It loads nothing from the internet.
- `<path>/mcp` is its MCP address over streamable HTTP. `<path>/sse` is the same tools over SSE. The tool names and descriptions are the `operationId`s and descriptions of the OpenAPI document, built from it, never kept twice.

The landing page `/` lists all of this with the counts of open items. `/health` and `/healthz` answer without a key.

Operations that only read are plain reads. Operations that write come in two kinds:

- A draft (a recommendation, a narrative, a reply, a proposal, missing items, a memo, document differences, a contact note) is stored with who wrote it (a free-text field, default `agent`), a time and a version number. Earlier versions are kept.
- A change (close an alert, release a repair, block a card, request a replacement, open a dispute, recall a payment) changes a status. Where the person who decides is listed (`decided_by`, `approved_by`) the call needs the name. A change is refused with 409 and a readable message when a precondition fails, for example the alert is already closed.

This is a simulator with its own state. A write really changes it, and the answer says `"applied": true`. There is deliberately no operation that files a report.

In all, 146 operations. Changes in the newer systems: `decide_fraud_case`, `post_break_resolution`, `decide_onboarding_application`, `complete_kyc_review`, `send_complaint_response`, `mark_call_reviewed` and `post_contribution_batch`. Drafts: the fraud case summary, the break proposal, the media screening summary, the onboarding file, the refreshed profile, the complaint classification, the complaint response, the call review and the evidence pack. The evidence pack gives no conclusion: the auditor concludes. The monitoring system has a draft for the work on an alert before a person opens a case (`save_alert_investigation`): the findings with their evidence ids, the narrative and a recommendation. When a person opens a case from that alert, the latest narrative becomes the first narrative version of the case. The reconciliation system lets an agent read and search the ledger and statement entries behind a break (`get_ledger_entry`, `get_statement_entry`, `search_ledger_entries`, `search_statement_entries`), so it can show what it searched for. The six newest systems add these drafts: an incident assessment, a post-incident review, legacy documentation, a converted program, a batch result, a meeting brief, finance commentary and a research report.

Three things to know about the newest systems:

- `itops` and `legacy` change nothing. There is no operation that runs a runbook step or changes a service, and none that changes the old system. An incident assessment needs an open incident and a post-incident review needs a closed one, or the call is refused with 409.
- `funds` has one change, `post_contribution_batch`. It needs a saved result and `approved_by`, posts only the rows that passed, and is refused with 409 if the saved result passes a row that breaks a rule.
- `finance` runs ONE read-only SQL statement on an in-memory SQLite database that is built at start from the seed. Anything that is not a single SELECT (or a WITH query that ends in a SELECT) is refused with 400: no insert, update, delete, drop, attach, pragma, comment or second statement. Each query runs on a private copy of the database with `query_only` on and an authorizer that allows reads only. At most 200 rows come back, and a query that runs too long is stopped. The warehouse is created in memory and never written to disk.

The `legacy` estate is separate from the core system: its customers and account numbers are its own and are not the records of `core`. The `crm` holdings are not stored: they are read from `core`, `lending` and `funds` on every call, so the totals agree with those systems.

The audit tests are tied to clauses 2.2, 3.1, 6.1 and 6.2 of `banking/policy-library/MTB-POL-033`. Complaint dates use working days (Monday to Friday).

The news system also serves each article as a plain web page at `/news/pages/<article id>`. It needs no key, so a link in a summary can be opened. It is not in the OpenAPI document. The `page_url` in an article carries the address.

The scenarios and their right answers are in [SCENARIOS.md](SCENARIOS.md).

## The regulator's public website (invented)

The "Meridia Financial Conduct Authority (invented)" is not one of the bank's systems. It stands for a regulator's public website, so it needs no key and has no MCP address and no OpenAPI document. It starts with six publications dated over the last 60 days.

| Address | What it gives |
|---|---|
| `/regulator/feed.xml` | An RSS 2.0 feed, newest first: title, link, pubDate, guid, description. |
| `/regulator/publications.json` | The same list as JSON. |
| `/regulator/publications/<id>` | One publication as a web page, with the full text in numbered paragraphs. |

Publication ids look like `MFCA-2026-045`. They are written to be compared with the policy library in `banking/policy-library`; the right verdicts are in [SCENARIOS.md](SCENARIOS.md). `POST /admin/simulate/regulator-publication` adds one more.

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

Tests: `pip install -r requirements-dev.txt` then `pytest`. One test file, `tests/test_agent_folders.py`, checks every agent folder in `../banking/agents` against the bank: each operation an agent names must exist in a system it lists, and each operation that writes must be listed under the agent's `changes`.

Behind a gateway, absolute addresses (landing page, news `page_url`, the regulator's feed) use the scheme in `X-Forwarded-Proto` when it is present, otherwise the request's own scheme.

## Sign-in

Data operations, the MCP addresses and the admin routes need the key, as the header `X-API-Key: <key>` or as `Authorization: Bearer <key>`. Open without a key: `/`, `/health`, `/healthz`, the docs pages, the OpenAPI documents, the news article pages (`/news/pages/<id>`) and the regulator's website (`/regulator/...`). Each OpenAPI document declares the header key as its security scheme.

## Environment variables

| Variable | Meaning |
|---|---|
| `BANK_API_KEY` | The key. If not set, a random key is made at start and printed once in the log. It is never shown on a page. |
| `BANK_AUTH` | `off` turns the key check off (laptop only). |
| `BANK_TODAY` | The bank date, `YYYY-MM-DD`. Default is today. Dates in the data are relative to it. With the same bank date the data is identical on every start. |
| `DATA_DIR` | A writable folder. State is written there as one JSON file. |
| `KATONIC_DATASET_PATH` | If `DATA_DIR` is not set and this is, state goes to `<KATONIC_DATASET_PATH>/demo-bank-state`. |
| `BANK_WEBHOOKS` | A JSON list of subscriptions, each `{"event_kind": "...", "url": "...", "header_name": "...", "secret_value": "..."}`. |
| `BANK_PUBLIC_SCHEME` | `https` or `http`. Forces the scheme in every address the bank prints. Set it to `https` when the bank sits behind a gateway that ends the secure connection early, and the landing page shows `http://` addresses. |

With none of `DATA_DIR` and `KATONIC_DATASET_PATH`, the service writes no file at all. It never writes inside its own folder, so a read-only root filesystem is fine. State lives in memory. Subscriptions added through the API live in memory only and are never written to the state file, because they hold a secret.

## Events

These routes need the key.

- `POST /admin/reset` puts the data back to the start.
- `POST /admin/reset/<system>` puts back only what that one system has changed since the start or the last full reset: the records its operations wrote and the items made to arrive for it. The rest of the bank stays as it is, so several people can test different agents against one bank without wiping each other's records. The answer lists what was put back.
- `GET /admin/state` gives counts, and under `changed_by` which system has changed what.
- `GET /admin/events` shows what was sent and the outcome.
- `GET`, `POST` and `DELETE /admin/subscriptions` manage subscriptions: an event kind (`screening-alert`, `payment-repair`, `payment-investigation`, `loan-application`, `fraud-case`, `reconciliation-break`, `regulator-publication`, `onboarding-application`, `kyc-review`, `complaint`, `collections-call`, `incident`, `contribution-batch`, `client-meeting`, `monitoring-alert`, or `*`), a URL, a header name and a secret value.
- `POST /admin/simulate/<kind>` creates one new item from a pool of four templates per kind, rotating. The new kinds make a fraud case in the fraud system, a break in the recon system, a publication on the regulator's website, an application or a periodic review in the onboarding system, a complaint in the complaints system and a call in the collections system. The three newest kinds make an incident in the itops system, a contribution batch in the funds system and a client meeting for tomorrow in the crm system. The kind `monitoring-alert` makes an alert, with its transactions, in the aml system.

For each matching subscription the service POSTs `{"message": "...", "event_type": "...", "item_id": "...", "system": "...", "demo_data": true}` with the secret header and a 10 second timeout. A failed delivery never fails the caller. The outcome is recorded in the events log. The message is plain sentences that say what arrived, its id and which system holds it.

## Connecting it to a platform

The same steps with screenshots: [docs/install-on-katonic.md](docs/install-on-katonic.md)

These steps were run on a development cluster of the Katonic platform on 24 November 2026.

1. Deploy it. In App Studio, start a new app from this repository, branch `main`, with the main file `demo-bank/main.py`. The platform finds the framework by itself, installs `requirements.txt` from that folder and starts the service under the app's own address. Set the health check path to `/health`.
2. Choose the app's access. Every access level except Public puts a person's sign-in page in front of the app, and the platform's own services cannot pass it. So the app is set to Public, and the service's own key protects it: set `BANK_API_KEY` as a secret setting. On a cluster that the internet can reach, the service is then reachable from outside with that key.
3. Import a system as tools. In Control Room, Tools, Import OpenAPI, import from the URL of one system's document, for example `<the app's address>/cards/openapi.json`. Choose the API key sign-in with the header `X-API-Key`, and an access group. Each operation becomes a tool. Import one system at a time, so that an agent gets only the tools of the systems it needs.
4. Attach the tools to an agent in Studio and ask it something. A call to a tool reaches the service and comes back with `"demo_data": true`.

What was proven: the deployment, the import, and agents calling the tools. In that run the key check was off (`BANK_AUTH=off`) and the import used no sign-in, because the run was a first proof on a development cluster.

What was not proven: registering a system's MCP address with the platform. The registration was accepted and then did not appear in the list of servers. The service itself answers MCP requests correctly.

## Notes for people who build on it

- All names, places, bank codes, identifiers and country codes are invented. Countries use codes that no real country has (`XM` is Meridia, the bank's home). The watchlist is the "Meridia Consolidated Demonstration List (invented)".
- Account numbers are IBAN-shaped with correct check digits, except where a scenario needs a wrong one. Card numbers appear only masked.
- If the `fastapi-offline` package is not installed, the docs pages are switched off. The OpenAPI documents are still served.
