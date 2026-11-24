# Onboarding and review desk

The settings folder that turns the Katonic case desk into a desk for a bank's onboarding officers. Three kinds of case sit in one queue. An application from an individual is checked against the documents the applicant sent and the bank's screening. An application from a company is checked the same way, and its ownership chain is drawn down to the people behind it. A customer due a periodic review has the profile the bank holds compared with fresh documents and a fresh screening. Each kind goes to its own agent. A person decides.

Meridian Trust Bank (an invented bank in the invented country Meridia), its applicants, its customers, their companies and all their documents are invented. Nothing here is a real account decision.

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Individual onboarding | [Customer Onboarding](../../agents/customer-onboarding/README.md) | Reads the applicant's documents, extracts the details, checks them against the form and the screening service, prepares the account opening file | The file. A member of staff approves or declines the account |
| Business onboarding | [Business Onboarding](../../agents/business-onboarding/README.md) | Reads the registry extract and the constitutional documents, draws the ownership chain, lists directors and owners for screening, prepares the file. A gap in the chain is listed and never filled in | The file, with every gap. A member of staff approves or declines the account |
| Periodic review | [Periodic Review](../../agents/periodic-review/README.md) | Compares the held profile with the fresh documents and a fresh screening, and drafts the refreshed profile with every change marked | The profile. The reviewer signs off. A change of risk rating waits for a named approver |

The desk sends the agent one message: the drafting instruction for the kind, then the case. The case names the application or the review. The agent reads the documents themselves from the bank's onboarding system.

## What the person sees

- **A queue of files**, each titled with who it concerns and the id, for example `Odalys Merrowby (ONB-1001)`. The kind is its own field, shown beside the date the case reached the bank.
- **The case beside the review.** The desk's short summary of the case is on one side: what is on the form or in the held profile, the documents received with their ids, and what the bank requires. The agent's file is on the other.
- **One table for every kind**, one row for each item checked. Each row shows what it was checked against, what the file shows, its source (the document or record id, with the line or clause), a mark and a note.
- **The agent's proposal**, one line, and the decision it points at.
- **The register** afterwards: who decided what, when, on which version of the file, and with which agent run and tool calls.

### The marks

| Mark | Meaning |
|---|---|
| agrees | The documents or records say what the form, the requirement or the held profile says |
| differs | A document disagrees with the form, or is out of date. Both values are shown and neither is chosen |
| missing | Not on file, or a gap in the ownership chain. Nothing is filled in |
| changed | A fresh document shows something other than what the bank holds (periodic review only) |
| needs a person | A watchlist match (strong or weak), an owner in a higher-risk country, or a change of risk rating. Not a failed check: only a person can decide it. Shown in the brand colour with a diamond, not in red |

The two onboarding kinds use agrees, differs, missing and needs a person. The periodic review uses agrees, changed, missing and needs a person. The desk shows each kind only its own marks, and counts them from the table. A row about a gap in the ownership chain starts with GAP: and is marked missing.

## What the person decides

| Decision | What it records |
|---|---|
| Approve | The person approves version N of the file. It opens no account, completes no review and changes no rating. That is done in the bank's own onboarding system |
| Ask for more | What to ask for, one item to a line. A letter is written. The case waits until the reply is added, then the agent reads the case again |
| Refer to Compliance | The watchlist entry and why. No letter is written. Nothing is said to the applicant about the reason |
| Send the rating change for approval | Who approves the change, and the reason. The review is completed in the bank's system only when a named person has approved the new rating |
| Decline | The reason the bank can state. The agent never proposes this |
| Ask the agent to redo the file | A note that the agent sees |

Each kind offers only the decisions that fit it. An application offers Approve, Ask for more, Refer to Compliance and Decline. A periodic review offers Approve, Ask for more, Refer to Compliance and Send the rating change for approval, and has no Decline. The server refuses any other decision (409). Approving a file in which a row is not marked agrees needs a reason: for a weak watchlist match it is how the person cleared it. The agent never proposes Decline.

The agent's proposal line marks one of these. The person who entered a case cannot decide it. The letter for Ask for more names the application or review id and nothing about a risk rating, and its dates are written as 8 Dec 2026.

No identity number is shown in full anywhere: the cases, the agent's rows and the register show only its last four characters, as in ending 2045. Dates are written as 18 Nov 2026.

## The nine demo cases

| Case | Kind | What the agent should find | What it should propose |
|---|---|---|---|
| ONB-1001, Odalys Merrowby | Individual onboarding | Name, date of birth, nationality, identity number and address agree. The bill is 26 days old, the card is valid, screening finds no hit | Approve |
| ONB-1002, Isadora Fenimore | Individual onboarding | Form says Fenimore, identity card says Fennimore. The water bill is 150 days old | Ask the applicant |
| ONB-1003, Wynn Castellano | Individual onboarding | Documents agree. Screening returns WL-9001, score 100, with the same identity number | Refer to Compliance |
| ONB-1004, Cobblegate Print Supplies Ltd | Business onboarding | One owner and director at 100 percent. All three documents agree. A weak surname hit, WL-9007 with score 79, for the officer to clear | Approve |
| ONB-1005, Larkfield Marine Services Ltd | Business onboarding | 60 percent held by Vardane Holdings Ltd, and no document shows who owns it. The gap is listed and not filled in | Ask the applicant |
| ONB-1006, Thistlewick Bakehouse Ltd | Business onboarding | Registry lists directors Nerys Hallowfield and Garrick Oldacre. The form lists only Nerys Hallowfield | Ask the applicant |
| KYR-1001, Cassius Dunmore | Periodic review | Nothing changed. The rating stays standard | Approve (sign-off only) |
| KYR-1002, Leopold Fenwick-Aral | Periodic review | Two changes: the address and the occupation. The rating stays standard | Approve (sign-off only) |
| KYR-1003, Orchard Lane Dental Group | Periodic review | Ownership changed. A new 30 percent owner lives in Kharnovia, a higher-risk country | Send the rating change for approval: high, from standard |

The dates and the ages in days in the cases are as at the bank date 2026-11-24. Start the invented bank with `BANK_TODAY=2026-11-24` so that the documents the agent reads match the cases.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, the `routing` setting with `decisions` and `marks` for each kind, `draft.markTones` with the `person` tone, `draft.rowLabels.check`, `draft.plainSource`, `draft.passMark`, `rules.reasonToApproveUnmet`, `letters.<outcome>.dateStyle`, `intake.fields[].options`, and the `case.queryFields` and `decisions[].proposalPrefix` settings.

**That version is in `main` of katonic-case-desk** since 24 November 2026 ([pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2)). A copy of the engine cloned before that date will not run this folder. An earlier engine ignores `routing`, and every case would go to one agent with one instruction.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/onboarding-and-review/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
INDIVIDUAL_ONBOARDING_AGENT_ID=<id of Customer Onboarding> \
BUSINESS_ONBOARDING_AGENT_ID=<id of Business Onboarding> \
PERIODIC_REVIEW_AGENT_ID=<id of Periodic Review> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `INDIVIDUAL_ONBOARDING_AGENT_ID` | The agent for cases of the kind Individual onboarding. If it is empty, drafting such a case fails and says which variable to set |
| `BUSINESS_ONBOARDING_AGENT_ID` | The same, for Business onboarding |
| `PERIODIC_REVIEW_AGENT_ID` | The same, for Periodic review |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. It can be any one of the three agents. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the nine demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `PORT` | The port the desk listens on |
| `INTAKE_TOKEN` | Turns on intake by webhook. The bank's system sends it as `X-Intake-Token` |
| `TRUST_SIGN_IN_HEADERS`, `LOCAL_USER`, `LOCAL_USER_NAME` | Who the desk believes is signed in. Without the headers it uses the local user, and every register row says which it was |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the bank's onboarding system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Individual onboarding`, `Business onboarding` or `Periodic review`.

Build the three agents from [`customer-onboarding`](../../agents/customer-onboarding/README.md), [`business-onboarding`](../../agents/business-onboarding/README.md) and [`periodic-review`](../../agents/periodic-review/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case's id in its title. Each follows the right answers in the invented bank's scenario list. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/onboarding-and-review/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the four agent ids. The stand-in does not read them. A case you enter by hand gets a plain line saying the stand-in has nothing for it. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the onboarding team enters it, or the bank's onboarding system sends it to `POST /api/intake` with the intake token. The bank's own events for new onboarding applications and for reviews that fall due carry a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through thirteen scenarios in a headless browser, on ports 8423 (stand-in), 8433 (recording proxy) and 3428 (desk): the nine demo cases with their rows, marks and proposals against the right answers in the invented bank's scenarios, which agent and which instruction each kind used, a question to the agent, a redo with a note and an edit of the text, every decision on a case it fits (approve with and without a reason, ask for more with its letter and the reply, refer to Compliance, decline, send the rating change for approval), the server refusing a decline on a review and a rating change on an application, the register and its export, filters and search by kind, id and name, a case entered by hand for each kind and one with a kind the desk does not know, the three themes, a phone-width window at 390 and 360, and a reload. It also checked that no identity number appears in full and no date appears as 2026-11-24 anywhere a person reads. All thirteen passed (319 checks) after two rounds of fixes. It was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three drafting instructions |
| `cases.json` | The nine demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case |
