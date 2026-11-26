# Thornmere Mutual Insurance (invented)

Thornmere Mutual Insurance is invented, and so is every person, company, policy, claim and record in this service. Nothing here describes a real insurer or a real customer.

This is one small service that plays the back-office systems of an insurer, so that AI agents have something realistic to read from and act on. Each system has its own OpenAPI document, its own docs page and its own MCP address, the way a real insurer keeps separate systems. It is built on the same skeleton as [the invented bank](../demo-bank/README.md).

Every JSON answer carries `"demo_data": true` at the top level, and every response carries the header `X-Demo-Data: invented`.

Licence: Apache-2.0.

**Status: work in progress.** Five systems are written: policy, claims, health, underwriting and investigations. The systems for servicing, complaints, reinsurance and the rest follow with their agents.

## The systems

| System | Path | What it holds | Operations |
|---|---|---|---|
| policy | `/policy` | policies with their schedules and endorsements, and two policy wordings with numbered clauses | 4 |
| claims | `/claims` | loss reports, claims with their documents, checklists by claim type, the handling guide, letter templates, settlements | 21 |
| health | `/health` | two group medical schemes with their tables of benefits, members with what they have used, medical policies, pre-authorisation requests, medical claims held for review, providers with their contracts and tariffs, provider invoices, call-back requests | 26 |
| underwriting | `/underwriting` | the underwriting guidelines as numbered rules, the appetite statement by class of business, submissions from brokers, the authority of each underwriter grade with the referral rules, referrals and precedents, the renewal rules, commercial policies and the renewals that are due | 20 |
| investigations | `/investigations` | closed claims with their payment files and the handling standards of the leakage review, new claims with the fraud indicators, claims referred to the investigations desk, the parties on them, and public notices | 21 |

For each system `<path>`:

- `<path>/openapi.json` is its OpenAPI 3.0.3 document. Every operation has a snake_case `operationId`, a summary and a description written for a language model.
- `<path>/docs` is its docs page. It loads nothing from the internet.
- `<path>/mcp` is its MCP address over streamable HTTP. `<path>/sse` is the same tools over SSE.

Operations that only read are plain reads. Operations that write come in two kinds:

- A draft (a claim file, how a claim is sorted, a pack check, a summary, a coverage check, a settlement calculation, a letter; in the health system an assessment of a pre-authorisation request, a suggested determination on a held claim, a list of invoice differences, a call-back request) is stored with who wrote it, a time and a version number. Earlier versions are kept. A draft changes no status, sends nothing and pays nothing. Its summary ends in "(draft)".
- A change (`register_claim`, `record_claim_decision`, `send_claim_letter`, `record_claim_payment`, and in the health system `decide_pre_authorisation`, `decide_medical_claim`, `record_invoice_query`) is for a named person. It is refused with 409 and a readable message when a precondition fails. Its summary ends in "(change)".

Things to know:

- **Wordings are records here.** A real insurer keeps its wordings as documents. Here each wording is a list of numbered clauses that an operation returns, so that an agent can be tried before any document store is connected. `insurance/` says which agents were also tried with the wording as a document.
- **The system does the sums.** `check_policy_cover_on_date` says whether a policy was in force on a date and counts the days. `get_claim` gives the days from the loss to the report. `calculate_settlement` applies the limits and the deductible and adds up; the agent says which lines the wording does not cover. `calculate_settlement` is sent as a POST because the lines go in the body. It saves nothing.
- **A saved draft is not part of the file.** `get_claim` and `get_loss_report` only count the drafts saved on a record. `list_claim_drafts` and `list_claim_file_drafts` read them. So one agent never reads another agent's proposal as a fact, and a second run of a test does not see the first run's answer.
- **A decline letter needs a decision.** `save_claim_letter` refuses the decline template unless an adjuster's decision to decline is recorded on the claim.
- **Two schemes, two plans.** In the health system the same question has two right answers. `get_scheme` gives one scheme's table of benefits and never two, and benefit ids differ by plan (`BEN-F..` and `BEN-E..`). Both tables are silent on a few ordinary things on purpose: then a person answers.
- **The health system does the sums too.** `get_member` gives what a member has used and has left. `calculate_member_benefit` gives what the plan pays on an amount: the part within the limit, the part over it and the member's share. `get_medical_claim` gives the same for a held claim, and sets it beside the earlier claims. `get_provider_invoice` checks an invoice against the provider's contract and tariff, line by line, and counts the days between a first consultation and a follow-up. These are reads: they save nothing.
- **The record says which medical policy to read.** A pre-authorisation request carries its medical policy only when the member's cover is in force, the plan covers the procedure and the plan needs pre-authorisation for it. Otherwise a note says why none is read. No operation declines a request for an agent: a clinician decides.
- **`/health` is two things.** `GET /health` is still the health check of the service. The health system's operations are under `/health/...`, with its documents at `/health/openapi.json` and `/health/docs`.
- **Underwriting saves drafts only.** The underwriting system has no change operation. `save_underwriting_file`, `save_referral_memo` and `save_renewal_review` each store a draft with a version number and change nothing else; nothing accepts, declines, quotes, binds or refers. The system measures: `get_submission` sets a submission against every guideline with a figure (a value exactly on a limit is within), `get_underwriting_referral` says which referral rule applies and to which grade, and `get_renewal` adds up the period's claims and works out the loss ratios. The measure of a submission uses the form's fields only: the documents are still read, and where a note contradicts a field both are shown. One renewal (RNW-6704) reads a home policy and its claim from the policy and claims systems as they stand. `tests/test_underwriting.py` checks the right answers.
- **Investigations saves drafts only.** The investigations system has no change operation. `save_leakage_finding`, `save_fraud_referral` and `save_case_file` each store a draft with a version number and change nothing else; nothing declines a claim, holds a payment, asks for money back or says that a person did wrong. The system does the sums and the matching: `calculate_what_should_have_been_paid` tests a closed claim against the handling standards LS-1 to LS-6 and gives what should have been paid; `run_fraud_indicators` measures the indicators FI-1 to FI-6 and gives each measured value beside its threshold; `get_parties_earlier_claims` counts earlier claims; `get_claim_links` finds a shared repairer, witness, phone number, address or bank account; `get_public_notices_for_party` sets a notice's date of birth and address beside the party's. Two people with one name and different dates of birth are two parties. It holds its own claims (CLM-6xxx) and reads policies and the handling guide from the policy and claims systems; policies that only its cases need (POL-27xx) are kept in this system and are not in the policy system's list. Phone numbers (`+999 555 ....`), bank accounts (`DEMO-ACCT-....`) and public notices are invented. `tests/test_investigations.py` checks the right answers.

The scenarios and their right answers are in [SCENARIOS.md](SCENARIOS.md).

## Quick start

```
pip install -r requirements.txt
python -m uvicorn main:app --port 8080
```

The first start prints a key, because `INSURER_API_KEY` was not set. Use it:

```
curl -H "X-API-Key: <key>" http://localhost:8080/claims/claims/CLM-4001
curl -H "Authorization: Bearer <key>" "http://localhost:8080/policy/policies?text=Stannaway"
```

For play on your own laptop only, `INSURER_AUTH=off` turns the key check off. The landing page then shows a warning.

Tests: `pip install -r requirements-dev.txt` then `pytest`. `tests/test_scenarios.py` and `tests/test_health.py` check the right answers of SCENARIOS.md against the data. `tests/test_agent_folders.py` checks every agent folder in `../insurance/agents` against the insurer: each operation an agent names must exist in a system it lists, and each operation that writes must be listed under the agent's `changes`.

## Sign-in

Data operations, the MCP addresses and the admin routes need the key, as the header `X-API-Key: <key>` or as `Authorization: Bearer <key>`. Open without a key: `/`, `/health`, `/healthz`, the docs pages and the OpenAPI documents.

## Environment variables

| Variable | Meaning |
|---|---|
| `INSURER_API_KEY` | The key. If not set, a random key is made at start and printed once in the log. It is never shown on a page. |
| `INSURER_AUTH` | `off` turns the key check off (laptop only). |
| `INSURER_TODAY` | The insurer date, `YYYY-MM-DD`. Default is today. Dates in the data are relative to it. With the same date the data is identical on every start. The right answers in SCENARIOS.md are written for `2026-11-26`. |
| `DATA_DIR` | A writable folder. State is written there as one JSON file. |
| `KATONIC_DATASET_PATH` | If `DATA_DIR` is not set and this is, state goes to `<KATONIC_DATASET_PATH>/demo-insurer-state`. |
| `INSURER_WEBHOOKS` | A JSON list of subscriptions, each `{"event_kind": "...", "url": "...", "header_name": "...", "secret_value": "..."}`. |
| `INSURER_PUBLIC_SCHEME` | `https` or `http`. Forces the scheme in every address the service prints. |

With none of `DATA_DIR` and `KATONIC_DATASET_PATH`, the service writes no file at all. State lives in memory.

## Events

These routes need the key.

- `POST /admin/reset` puts the data back to the start.
- `POST /admin/reset/<system>` puts back only what that one system has changed, so several people can test different agents against one insurer.
- `GET /admin/state` gives counts, and under `changed_by` which system has changed what.
- `GET`, `POST` and `DELETE /admin/subscriptions` manage subscriptions: an event kind (`loss-report`, `pre-authorisation-request` or `*`), a URL, a header name and a secret value.
- `POST /admin/simulate/loss-report` makes one new loss report arrive, from four rotating templates, and tells every subscriber: `{"message": "...", "event_type": "loss-report", "item_id": "...", "system": "claims", "demo_data": true}`.
- `POST /admin/simulate/pre-authorisation-request` makes one new pre-authorisation request arrive in the health system, from four rotating templates, and tells every subscriber in the same way.
- `GET /admin/events` shows what was sent and the outcome.

## Connecting it to a platform

The steps are the same as for the invented bank: [install guide](../demo-bank/docs/install-on-katonic.md), with the main file `demo-insurer/main.py` and the settings `INSURER_API_KEY` and `INSURER_TODAY`.
