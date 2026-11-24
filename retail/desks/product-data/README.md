# Product data desk

The settings folder that turns the Katonic case desk into a desk for the content team of a retailer's online shop. Two kinds of case sit in one queue. A new product with no description gets a draft description and image tags, written to the style guide. A listing is set against the supplier's specification, attribute by attribute. Each kind goes to its own agent. A person decides.

Rowanmere Group (an invented company in the invented country Meridia), its suppliers, its products and every listing and specification are invented.

## The two kinds of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| New product | [Product Catalog](../../agents/product-catalog/README.md) | Drafts the description and the image tags from the supplier's specification and the image descriptions, to the style guide, and marks any image description that differs from the specification | Publish the description as drafted, edit it and then publish, or ask the agent again |
| Listing check | [Product Data Check](../../agents/product-data-check/README.md) | Sets the listing's net quantity, pack size, allergen statement and country of origin against the specification, and says which is missing or does not match, with both values | Accept the correction, keep the listing as it is with a reason, or ask the supplier |

The desk sends the agent one message: the drafting instruction for the kind, then the case with its records. The agent works from that message. It reads nothing from the retailer's systems and saves nothing.

**The desk records the decision and does nothing else.** It publishes no description, changes no listing, sends a supplier nothing, and calls no operation of the retailer. "Publish the description" records that a named person decided to publish that version. The person publishes it in the catalogue system.

## What the desk does not hold or do

- **No images.** The catalogue system holds none, and neither does the desk. Each image of a new product is a description in words, written by the photo studio. A draft says what a description says, and says that no image was seen. A tag names something an image description says is in a picture.
- **No allergen is worked out.** The allergen statement is the supplier's, copied word for word. A listing check reads out the two statements. It makes no statement about whether a product is safe for anyone.
- **No choice between two values.** A listing check gives what the listing says and what the specification says. The style guide says which one a listing carries. A content lead decides, and can ask the supplier.

## What the person sees

- **A queue of cases**, each with its line id, the product's name and its kind. A listing whose allergen statement is missing or differs carries a chip, "Allergen", once its draft is in. A new product whose image description differs from the specification carries the chip "Image differs".
- **The records beside the draft.** What the catalogue system holds is on one side. The agent's draft is on the other.
- **One row for each thing compared**, with the two values side by side where they differ, and in one box where they are the same.
- **A card under the rows** for the description, and one for the image tags. "Edit the text" changes the description's wording before the decision, and the edit is kept as a new version by the person.
- **The agent's proposal**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version, and with which agent.

### The marks

| Mark | Kind | Meaning |
|---|---|---|
| In line | New product | On this point the draft is what the specification or the style guide gives |
| Image differs | New product | An image description gives a figure or a claim that the specification does not. The draft uses the specification, and the content lead asks the supplier |
| Matches | Listing check | The listing and the specification say the same, letter for letter |
| Missing in the listing | Listing check | The listing holds nothing for the attribute and the specification has a value |
| Does not match | Listing check | Both have a value and the two differ. The check does not say which is right |
| Not checked | Both | The record needed was not with the case |

The agent's Summary carries no count of marks. The desk counts them from the table.

## The decisions

| Decision | Kind | What it records |
|---|---|---|
| Publish the description | New product | The decision to publish that version, in the person's name. One click when every row is in line. Needs a reason when an image description differs from the specification. After "Edit the text" it records the edited version |
| Accept the correction | Listing check | That the listing is to carry the specification's value, and who corrects it |
| Keep the listing as it is | Listing check | Why the listing stays: every attribute matches, or the reason the specification is not followed |
| Ask the supplier | Listing check | What the supplier is asked, and who asks |
| Ask the agent again | Both | A note that the agent sees. The agent drafts again |

A case offers only the decisions of its kind, and the desk refuses any other. The person who entered a case cannot decide it.

## The nineteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| AG-4411 Oat granola, 500 g | New product | 500 g, pack size 1, "Contains: oats, almonds (nuts)", Meridia. Publish |
| BK-5706 Almond pastries, pack of two | New product | 2 x 85 g, pack size 2, "Contains: wheat, milk, egg, almonds (nuts)", Meridia. Publish |
| CH-5508 Fresh tomato soup, 600 g | New product | 600 g, pack size 1, "Contains: celery, milk", Meridia. Publish |
| DR-5906 White wine, 75 cl | New product | 75 cl, pack size 1, "Contains: sulphites", Tessaly. Age-restricted: the description ends with "For adults aged 18 or over." Publish |
| FZ-5606 Frozen berry mix, 500 g | New product | 500 g, pack size 1, "No allergens", Rovaland. The pack in the first image reads 450 g: the draft uses 500 g and marks the difference for the content lead |
| HH-6107 Dishwasher tablets, pack of 30 | New product | 540 g, pack size 30, "Not a food", Quenmark. Publish |
| AG-4401 Olive oil, 1 litre bottle | Listing check | Country of origin missing. The specification says Tessaly |
| AG-4407 Basmati rice, 1 kg | Listing check | Net quantity does not match: 1 kg in the listing, 900 g in the specification |
| AG-4412 Peanut butter, crunchy, 340 g | Listing check | Allergen statement does not match: "Contains: peanuts" against "Contains: peanuts. May contain: other nuts, sesame" |
| AG-4413 Vegetable stock cubes, pack of 12 | Listing check | Every attribute matches. Keep the listing |
| BK-5703 Butter croissants, pack of four | Listing check | Allergen statement does not match: "Contains: wheat, milk" against "Contains: wheat, milk, egg" |
| CH-5506 Natural yoghurt, 500 g | Listing check | Allergen statement missing. The specification says "Contains: milk" |
| CH-5507 Free-range eggs, box of six | Listing check | Every attribute matches. Keep the listing |
| DR-5902 Sparkling water, six bottles | Listing check | Pack size missing. The specification says 6 |
| DR-5905 Red wine, 75 cl | Listing check | Every attribute matches. Keep the listing |
| FP-5804 Bananas, bunch of five | Listing check | Country of origin does not match: Aldoria against Brevnia |
| FZ-5602 Garden peas, 900 g | Listing check | Net quantity missing. The specification says 900 g |
| HH-6104 Toilet tissue, nine rolls | Listing check | Pack size does not match: 12 against 9 |
| PC-6603 Shampoo, 400 ml | Listing check | Net quantity does not match: 400 ml against 350 ml |

These are the records the invented retailer holds when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each.

The retailer's own data check runs over all sixty listings at once. The desk takes it one listing to a case, so that a person decides each listing on its own: the ten listings with a finding, and three that are clean.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). A new product carries the supplier's specification, its two image descriptions and the style guide. A listing check carries the listing, the specification and the style guide's three rules on these attributes. The script reads none of the service's answer sets. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_product_data_desk_cases.py`, fails when `cases.json` differs from what the script would write, when a case differs from what the service returns, or when what is missing or does not match in a case is not what the service holds.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions and its own wording for each kind, `draft.sections`, `draft.sideBySide`, `draft.singleValueMarks`, `draft.stackOnPhone`, `draft.markIcons`, `draft.summaryAboveRows`, lines with labels in a row, `case.flags`, `case.foldOnPhone` and `intake.fields[].options`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/product-data/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
PRODUCT_CATALOG_AGENT_ID=<id of Product Catalog> \
PRODUCT_DATA_CHECK_AGENT_ID=<id of Product Data Check> \
KATONIC_AGENT_ID=<either of the two, for a case of an unknown kind> \
LOCAL_USER=maelys.thorncastle-wray@rowanmere.invalid \
LOCAL_USER_NAME="Maelys Thorncastle-Wray" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `PRODUCT_CATALOG_AGENT_ID` | The agent for cases of the kind New product. If it is empty, drafting such a case fails and says which setting to fill |
| `PRODUCT_DATA_CHECK_AGENT_ID` | The same, for Listing check |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither of the two. The desk asks it only to say that the kind is not recognised, and such a case offers only "Ask the agent again" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented content lead |
| `SEED_DEMO` | `true` loads the nineteen demo cases on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each case carries its records |

The kind of a case is the value of its "Kind of work" field, matched without regard to case.

Build the two agents from their folders. Each agent's own instructions tell it to read the catalogue system and to save a draft there. The desk asks for another shape, so each agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds the two. The section and the drafting instruction for the kind in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agents with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for each of the three agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the nineteen demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned. A case you enter by hand gets one row saying the stand-in read none of the records.

The stand-in shows how the desk works. It does not test the agents.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty-three scenarios in a headless browser. All twenty-three pass.

- The queue shows the nineteen cases, each with its kind.
- The right answers were worked out again from the text of each case: the four facts of each new product, the quantity an image description gives against the specification's, and for each listing the attribute that is missing or does not match. They are the ones the retailer's scenario list gives.
- Each kind's draft comes from the agent its setting names, with its own instruction. Every message to an agent is under 8,500 characters.
- What is shown for all nineteen cases matches the scenario list. Each canned description is 40 to 80 words, uses none of the words the style guide rules out and gives the net quantity as the specification gives it. The description of the age-restricted line ends with the style guide's sentence. Every tag is in an image description. The agent's proposal sits on the right button.
- Every decision: publish with one click, publish with a reason while an image description differs, edit the description and then publish, accept the correction, keep the listing as the agent proposes and against its proposal, ask the supplier, and ask the agent again.
- A decision of another kind is refused. A kind whose agent setting is empty says which setting to fill. A kind the desk does not know offers only asking again.
- The register and its export, a question to the agent, the form for a new case, search by kind, by supplier, by line, by category and by a word of the records, the filters, and a reload.
- Four eyes: the person who entered a case cannot decide it, on the page or by calling the desk directly, for each of the two kinds. A second content lead can.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after each of two rounds. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the two real agents on a platform, the desk section added to the two agent folders, the platform's sign-in in front of the desk, and the desk deployed as an app. The queue has no filter by kind: a search for the kind's name lists its cases.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two drafting instructions |
| `cases.json` | The nineteen demo cases, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section each of the two agents needs before the desk is pointed at it |
