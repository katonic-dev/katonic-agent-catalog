# Customer care desk

The settings folder that turns the Katonic case desk into a desk for a retailer's customer care team. Four kinds of case sit in one queue. A customer ticket is answered from the help articles. A return request is checked against the returns policy. A complaint is given its class and its due date, and a response is drafted. A public review is checked for a safety or legal matter and, when there is none, answered in the brand's voice. Each kind goes to its own agent. A person decides.

Rowanmere Group (an invented company in the invented country Meridia), its customers and every ticket, return request, complaint, review and order are invented.

## The four kinds of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| Customer ticket | [Customer Service](../../agents/customer-service/README.md) | Finds the help article that answers the question, cites it, and drafts the reply | Send the reply, pass to a colleague, or ask the agent again |
| Return request | [Returns Processing](../../agents/returns-processing/README.md) | Checks the request against the Returns Policy, names the condition that decides, works out the refund and drafts the message to the customer | Approve the return, refuse it, or pass it to a colleague |
| Complaint | [Complaint Handling](../../agents/complaint-handling/README.md) | Gives the complaint its class, works out the date the response is due, sets what the customer says beside what the records show, and drafts the response | Send the response, with any goodwill as the person's own decision, or pass it to the Customer Relations Lead |
| Public review | [Review Reply](../../agents/review-reply/README.md) | Checks the review for a safety or legal matter. If there is none, drafts a reply to the Brand Voice Guide. If there is one, drafts nothing | Publish the reply, or mark the review for a person with no reply |

The desk sends the agent one message: the drafting instruction for the kind, then the case with its records. The agent works from that message. It reads nothing from the care or orders system and saves nothing.

**The desk records the decision and does nothing else.** It sends nothing to a customer, posts nothing on a review site, pays no refund and no goodwill, and calls no operation of the care or orders system. "Approve the return" records that a named person approved it. The person approves it in the orders system.

## What the person sees

- **A queue of cases**, each with its number, who it is from, its kind and its status. A short chip marks a case to see first: a safety or legal complaint, a response that is overdue, a repeat contact, a review for a person, a ticket no article answers, a return the policy does not decide.
- **The records beside the draft.** What the care and orders systems hold is on one side, with the policy the case is judged by. The agent's draft is on the other.
- **One row for each thing checked**: each question in a ticket, each condition of the Returns Policy that applies, each thing a complaint says, each rule of the Brand Voice Guide.
- **The text for the customer on a card of its own**, under the rows. "Edit the text" changes its wording before the decision, and the edit is kept as a new version.
- **The agent's proposal**, one line, and the button it points to. For a complaint the line carries the class and the due date.
- **The register** afterwards: who decided what, when, on which version, with which note and with which agent.

### The marks

| Mark | Kind | Meaning |
|---|---|---|
| Answered | Ticket | A help article states what the customer asked |
| No article answers | Ticket | None of the twelve help articles states it. A colleague answers |
| Met | Return | The request meets this condition of the Returns Policy |
| Not met | Return | The request does not meet it. The first condition that is not met decides a refusal |
| Policy does not decide | Return | The policy says it does not decide the case. The Customer Care Team Leader does |
| In the records | Complaint | The order, its scans or the contact history show what the customer describes |
| Not in the records | Complaint | The records do not show it. That is not a statement that the customer is mistaken |
| For a person | Complaint, review | An injury, an illness, a hazard or a legal threat. The agent decides nothing about it |
| Follows the guide | Review | The draft reply follows this rule of the Brand Voice Guide |
| Not checked | All | The record needed was not with the case |

The agent's Summary carries no count of marks. The desk counts them from the table.

## The decisions

| Decision | Kind | What it records |
|---|---|---|
| Send the reply | Ticket | That the reply goes out, who sends it, and the reply as it reads |
| Approve the return | Return | The approval, in the person's name. One click when every condition is met. Needs a reason when a condition is not met |
| Refuse the return | Return | The refusal and its reason |
| Send the response | Complaint | That the response goes out, who sends it, and any goodwill the person has decided, as that person's own decision |
| Pass to the Customer Relations Lead | Complaint | Why the complaint goes to the Lead. This is what the agent proposes for a safety or legal complaint |
| Publish the reply | Review | That the reply is posted, who posts it and where, and the reply as it reads |
| Mark for a person, no reply | Review | Why a person reads the review first. No reply is posted |
| Pass to a colleague | Ticket, return | Who it goes to and why, when no article answers a ticket or the policy does not decide a return |
| Ask the agent again | All | A note that the agent sees. The agent drafts again |

A case offers only the decisions of its kind, and the desk refuses any other. The person who entered a case cannot decide it.

## The thirty demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| CT-2611-001, Delivery cost | Customer ticket | HA-01 answers it. Send the reply |
| CT-2611-004, Refund timing | Customer ticket | HA-05 answers it. Send the reply |
| CT-2611-011, Left with a neighbour | Customer ticket | HA-12 answers it. Send the reply |
| CT-2611-020, Kettle lid cracked | Customer ticket | HA-09 answers it. Send the reply |
| CT-2611-014, Price match | Customer ticket | No article answers it. To a colleague |
| CT-2611-016, Nut allergy | Customer ticket | No article answers it, and no view on whether the food is safe. To a colleague |
| RR-2611-01, Cast-iron casserole | Return request | Approve under 1.1, day 8. Refund USD 64.00 |
| RR-2611-02, Rain jacket | Return request | Refuse under 1.2, day 38 |
| RR-2611-03, Chilled ready meals | Return request | Refuse under 3.1, chilled food |
| RR-2611-04, Hand blender | Return request | Refuse under 2.2, opened and used |
| RR-2611-05, Kettle | Return request | Approve under 5.2, faulty on day 6. Refund USD 34.50 |
| RR-2611-06, Olive oil | Return request | Approve under 5.1, damaged, day 2, photograph. Refund USD 11.50 for one bottle of two |
| RR-2611-07, Ceramic dinner set | Return request | The policy does not decide: 5.3, damage reported on day 15. To the Customer Care Team Leader |
| RR-2611-08, School shoes | Return request | Approve under 2.3, tried on indoors with the labels. Refund USD 31.00 for one pair of two |
| RR-2611-09, Gift card | Return request | Refuse under 3.3, gift cards |
| RR-2611-10, Wool jumper | Return request | Approve under 1.1, day 30. Refund USD 46.00 |
| CM-2611-01, Order is late | Complaint | Class C, service failure, 2.3. Due 2026-12-02. The scans explain the delay |
| CM-2611-02, Still no refund | Complaint | Class B, repeat contact, 2.2. Due 2026-11-26. A refund of USD 28.00 approved and not paid |
| CM-2611-03, Glass in a jar | Complaint | Class A, safety or legal, 2.1. Due 2026-11-25. An acknowledgement only. To the Customer Relations Lead |
| CM-2611-04, Charged for delivery | Complaint | Class D, policy disagreement, 2.4. Due 2026-12-02. The charge follows the rule |
| CM-2611-05, Parcel left with a neighbour | Complaint | Class C, service failure, 2.3. Due 2026-12-03. One earlier contact |
| CM-2611-06, Charged twice | Complaint | Class A, safety or legal, 2.1. Due 2026-11-24. The order shows one charge. To the Customer Relations Lead |
| CM-2611-07, Fish missing | Complaint | Class C, service failure, 2.3. Due 2026-12-03. One earlier contact |
| CM-2611-08, Wrong item | Complaint | Class B, repeat contact, 2.2. Due 2026-11-22, which has passed |
| PR-2611-01, 5 stars | Public review | Praise. Reply |
| PR-2611-02, 2 stars | Public review | Criticism. Reply |
| PR-2611-03, 1 star | Public review | Something found in food. For a person, no reply |
| PR-2611-05, 3 stars | Public review | Praise and criticism. Reply |
| PR-2611-06, 1 star | Public review | A fall, an injury and a solicitor. For a person, no reply |
| PR-2611-10, 1 star | Public review | A colleague's manner. Not a safety or legal matter. Reply |

These are records the invented retailer holds when its date is 24 November 2026: six of its twenty tickets, all ten return requests, all eight complaints and six of its twelve reviews. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). Each case carries the records its agent needs: the ticket with the twelve help articles; the return request with its order and the Returns Policy; the complaint with its contact history, its order, the charges, refunds and carrier scans, and the Complaints Procedure; the review with the [Brand Voice Guide](../../policy-library/brand-voice-guide.md). The script never reads the retailer's answer sets. It starts no server.

A case shows a customer by an invented name, an order number and an address that ends in `.invalid`. It carries no customer id and no card, address or device reference. A review carries the display name only.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_customer_care_desk_cases.py`, fails when `cases.json` differs from what the script would write, or when a case differs from what the service returns for that record.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions and its own wording for each kind, `draft.sections` for the text to the customer, `draft.markIcons`, `draft.summaryAboveRows`, `case.flags`, `case.foldOnPhone` and `intake.fields[].options`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/customer-care/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
CUSTOMER_SERVICE_AGENT_ID=<id of Customer Service> \
RETURNS_PROCESSING_AGENT_ID=<id of Returns Processing> \
COMPLAINT_HANDLING_AGENT_ID=<id of Complaint Handling> \
REVIEW_REPLY_AGENT_ID=<id of Review Reply> \
KATONIC_AGENT_ID=<any one of the four, for a case of an unknown kind> \
LOCAL_USER=ottoline.verrowby-shaw@rowanmere.invalid \
LOCAL_USER_NAME="Ottoline Verrowby-Shaw" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `CUSTOMER_SERVICE_AGENT_ID` | The agent for cases of the kind Customer ticket. If it is empty, drafting such a case fails and says which setting to fill |
| `RETURNS_PROCESSING_AGENT_ID` | The same, for Return request |
| `COMPLAINT_HANDLING_AGENT_ID` | The same, for Complaint |
| `REVIEW_REPLY_AGENT_ID` | The same, for Public review |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the four. The desk asks it only to say that the kind is not recognised, and such a case offers only "Ask the agent again" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented care lead |
| `SEED_DEMO` | `true` loads the thirty demo cases on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each case carries its records and its policy |

The kind of a case is the value of its "Kind of work" field, matched without regard to case.

Build the four agents from their folders. Each agent's own instructions tell it to read the care or orders system and to save a draft there. The desk asks for another shape, so each agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds the four. The section and the drafting instruction for the kind in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agents with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for each of the five agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the thirty demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned text. A case you enter by hand gets one row saying the stand-in read none of the records.

The stand-in shows how the desk works. It does not test the agents.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty-four scenarios in a headless browser. All twenty-four pass.

- The queue shows the thirty cases, each with its kind.
- The right answer for each case was worked out again from the text of the case, by the rules: the return's deciding condition, day and refund, the complaint's class, section and due date, and which reviews go to a person. They are the ones the retailer's scenario list gives.
- Each kind's draft comes from the agent its setting names, with its own instruction. Every message to an agent is under 10,000 characters.
- What is shown for all thirty cases matches the scenario list: the article cited, the condition and the refund, the class and the due date, the two reviews marked for a person with no reply drafted. The agent's proposal sits on the right button.
- Every decision: send a reply as drafted and after editing its wording, pass a ticket to a colleague, approve a return with one click, approve with a reason while a condition is not met, refuse a return, pass a return to a colleague, send a complaint response with and without a goodwill payment in the person's note, pass a complaint to the Customer Relations Lead, publish a review reply, mark a review for a person, and ask the agent again.
- A decision of another kind is refused. A kind whose agent setting is empty says which setting to fill. A kind the desk does not know offers only asking again.
- The register and its export, a question to the agent, the form for a new case, search by kind, by customer, by order number and by case number, the filters, and a reload.
- Four eyes: the person who entered a case cannot decide it, on the page or by calling the desk directly, for each of the four kinds. A second care lead can.
- No screen, document or export shows a customer by more than a name, an order number and an address ending in `.invalid`.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after the first round. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the four real agents on a platform, the desk section added to the four agent folders, the platform's sign-in in front of the desk, and the desk deployed as an app. The desk offers "Send the response" on every complaint, also on a safety or legal one, where the agent proposes the Customer Relations Lead: the page says when a decision differs from the proposal, and does not stop it. The queue has no filter by kind: a search for the kind's name lists its cases.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, chip, decision, status and register label, and the `routing` setting with the four drafting instructions |
| `cases.json` | The thirty demo cases, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section each of the four agents needs before the desk is pointed at it |
