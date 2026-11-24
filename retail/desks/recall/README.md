# Recall desk

The settings folder that turns the Katonic case desk into a desk for a retailer's Quality team when a supplier recalls a batch. The agent prepares the recall pack in three parts: where the batch went, the instruction to the stores, and the notice to customers. A quality lead decides.

Rowanmere Group (an invented company in the invented country Meridia), its suppliers, its customers, its colleagues and every batch, store and order are invented.

## The one kind of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| Recalled batch | [Product Recall Preparation](../../agents/product-recall-preparation/README.md) | Lists every store the batch was delivered to and every online order it was picked for, from the batch record and from nothing else. Drafts one instruction for the stores and one notice for the customers, to the recall procedure. Says what it left out and why | Issue the notices as drafted, edit them and then issue, add a store or an order the agent missed, or ask the agent again |

The desk sends the agent one message: the drafting instruction, then the recall with its records. The agent works from that message. It reads nothing from the retailer's systems and saves nothing.

**The desk records the decision and does nothing else.** It issues no notice, sends nothing to a store or a customer, and calls no operation of the retailer. "Issue the notices" records that a named person decided to issue that version of the two texts. The Quality team sends them.

## What a recall text never says

- What caused the fault. The supplier's words about the fault are given as the supplier wrote them.
- That anyone was or was not harmed.
- Medical advice. A customer who feels unwell is told to speak to a doctor, and nothing more.
- A customer's name. The notice is one text, and the list of orders says who it goes to.

## What the desk holds about a customer

A name, an order number and an address for messages, which ends in `.invalid`. Nothing else: no customer id, no card, no device and no delivery address. The register and its export hold no customer at all.

## A recall is urgent

The queue shows, on each open recall, the day the recall was raised and a clock: "Due today" on that day, and "Overdue since" with the day from the next day on. The oldest recall is first. The clock counts days, from the desk's own setting `due`: a pack is decided on the day the recall is raised. Set it to the company's own turnaround. A decided recall carries no clock.

## What the person sees

- **A queue of recalls**, each with the batch, the product, how many stores and orders it reached, the day it was raised and the clock.
- **The records beside the pack.** What the stock, orders and stores systems hold is on one side. The agent's pack is on the other.
- **One row for each store and each order on the batch record**, under two headings. A store's row gives the units delivered, sold and on hand, the town and the area manager. An order's row gives the units picked, the line they went out as, and the customer's name and address.
- **Three cards under the rows**: the store instruction, the customer notice, and what was left out of the recall and why. "Edit the text" changes the wording of a card before the decision, and the edit is kept as a new version by the person.
- **The agent's proposal**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version, and with which agent.

### The marks

| Mark | Meaning |
|---|---|
| On the batch record | The batch record names this store or this order |
| Added by the quality lead | The batch record does not name it. A quality lead added it, with a note |
| Not checked | The record needed was not with the recall |

The agent's Summary carries no count of stores or orders. The desk counts the rows.

## The decisions

| Decision | What it records |
|---|---|
| Issue the notices | The decision to issue that version of the store instruction and the customer notice, in the person's name. One click when every row is on the batch record. Needs a reason when a row is not. After "Edit the text" it records the edited version |
| Add a store or an order | A note that names the store or the order and the record that shows it. The agent sees the note and drafts the pack again, with the addition marked as the quality lead's |
| Ask the agent again | A note that the agent sees. The agent drafts again |

The person who entered a recall cannot issue it.

## The three demo recalls

| Recall | What the agent should find |
|---|---|
| BT-44031 Pasta sauce, six jars | Four stores: S-101 (240 units), S-104 (180), S-105 (60) and S-107 (200). Seven online orders, of five customers: two customers have two orders each and get one notice. Left out: BT-44032, a later batch of the same line that is on sale and went to S-102 and S-106, and the orders RM-58188 and RM-58198, which hold a Weekly grocery box that has not been packed. The supplier's words: "The supplier has reported that pieces of glass may be present in jars of this batch." |
| BT-90001 Olive oil, 1 litre bottle | Two stores, S-103 (60) and S-108 (48), and two orders, RM-58147 and RM-58158. The supplier reports that the bottles may not be sealed |
| BT-90002 Chilled ready meals, pack of four | Three stores, S-101 (36), S-102 (24) and S-105 (12), and two orders, RM-58136 and RM-58160. The supplier reports that milk is not named on the label |

These are the records the invented retailer holds when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each.

The retailer's starting data holds one recalled batch, BT-44031. The two others are the first two recalls the retailer makes when a recall arrives (`POST /admin/simulate/recalled-batch`, twice). The cases script makes them the same way, from the same seed, so the queue is not one case. The seed holds no other recalled batch.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). Each recall carries the recall in the supplier's words, the batch record, the stores, the orders, what is not on the batch record (another batch of the same line, and orders that hold the line and were not picked from this batch) and the recall procedure. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_recall_desk_cases.py`, fails when `cases.json` differs from what the script would write, when a case differs from what the service returns once the two recalls have arrived, when the first recall is not the batch record's four stores and seven orders, or when a case holds more of a customer than a name, an order number and a `.invalid` address.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions for a kind, `due`, `draft.sections`, `draft.groupHeadings`, `draft.summaryAboveRows`, lines in a cell of a row, `intake.fields[].shownAs`, `case.foldOnPhone` and `intake.fields[].options`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/recall/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
RECALL_PREPARATION_AGENT_ID=<id of Product Recall Preparation> \
KATONIC_AGENT_ID=<the same id, for a case of an unknown kind> \
LOCAL_USER=sigrun.aldersey-keane@rowanmere.invalid \
LOCAL_USER_NAME="Sigrun Aldersey-Keane" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `RECALL_PREPARATION_AGENT_ID` | The agent for a recalled batch. If it is empty, drafting a recall fails and says which setting to fill |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is not Recalled batch. The desk asks it only to say that the kind is not recognised, and such a case offers only "Ask the agent again" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented quality lead |
| `SEED_DEMO` | `true` loads the three demo recalls on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each recall carries its records and the recall procedure |

Build the agent from its folder. The agent's own instructions tell it to read the retailer's systems and to save the pack on the batch. The desk asks for another shape, so the agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds it. The section and the drafting instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agent with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for the two agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the three demo recalls, following the right answers above. Every stand-in reply says on its first line that it is canned. A recall you enter by hand gets one row saying the stand-in read none of the records. When a pack is sent back, the stand-in gives the same pack again and says which note it was sent: it does not add the store the note names.

The stand-in shows how the desk works. It does not test the agent.

## How it was tested

On 24 and 25 November 2026 the desk was run against the stand-in through twenty scenarios in a headless browser. All twenty pass.

- The queue shows the three recalls, each with its reach, the day it was raised and the clock.
- The records were read again from the text of each case and set against the retailer's scenario list: the stores with their units, the orders with their customers, what is not on the batch record, the supplier's words.
- Each pack comes from the agent the setting names. Every message to the agent is under 10,000 characters.
- What is shown for all three recalls matches the scenario list: every store and every order on the batch record and no other, the two customers with two orders, the later batch and the unpacked orders left out. The store instruction names only the stores of the recall. The customer notice gives the supplier's words, names no customer and carries no customer's address. Neither text speaks of cause, harm or medicine beyond one sentence about a doctor. Each text is within 130 words.
- Every decision: issue with one click, edit the notice and then issue, add a store with a note, ask the agent again, and issue with a reason while a row is not on the batch record.
- A decision the desk does not have is refused, and a decided recall cannot be drafted or decided again. With the agent setting empty the page says which setting to fill. A kind the desk does not know offers only asking again.
- The register and its export, which hold no customer; a question to the agent; the form for a new recall; search by batch, product, supplier, store, order and customer; the filters; and a reload.
- Four eyes: the person who entered a recall cannot issue it, on the page or by calling the desk directly. A second quality lead can.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after each of two rounds. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the real agent on a platform, the desk section added to the agent's folder, the platform's sign-in in front of the desk, and the desk deployed as an app. The clock counts days, not hours.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, the clock, and the `routing` setting with the drafting instruction |
| `cases.json` | The three demo recalls, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section the agent needs before the desk is pointed at it |
