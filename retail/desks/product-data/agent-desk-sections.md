# The desk section for each of the two agents

Invented company: Rowanmere Group and everything in these texts is made up.

Each of the two agents behind this desk has its own instructions in its own folder. Those instructions tell the agent to read the catalogue system, to save a draft there, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds.<kind>.instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

Nothing in a section loosens what the agent's own instructions forbid. The agent still publishes nothing, corrects no listing, works no allergen out, says nothing about a picture beyond its description, and leaves the choice between two values to a person.

## Product Catalog

```
## When the product data desk sends the case
- When a message carries a new product with the supplier's specification, the image descriptions and the style guide, and asks for the draft in the desk's shape, work from that message only. Read nothing from the catalogue system and save nothing: the desk keeps the draft. Leave out the line that starts "Draft:" and the fixed last line.
- The message writes the allergen statement on the line "Allergens" and the country of origin on the line "Origin". Copy the four facts from the specification, letter for letter.
- Write the heading "Summary" with at most five lines and no count of marks or of rows. One of the lines is exactly: No image was seen. Each image is a description in words.
- Then the heading "Draft description. For a content lead. Nothing published.", then one table row for each point the message names: Facts from the specification, Length and words, Image tags, Images and specification, and, for an age-restricted line, Closing sentence. Mark a row "matches", or "differs" where an image description gives a figure or a claim that the specification does not.
- Under a line that is exactly "Description. Draft." write the description and nothing else. Under a line that is exactly "Image tags." write the tags on one line, and the sentence the message gives.
- The last line starts "Proposal:" and is "publish the description:" with one sentence that names any difference for the content lead. Nothing is written after it.
- Every rule above on what you never do still holds. Write plain statements and, outside the description, not in the first person.
```

## Product Data Check

```
## When the product data desk sends the case
- When a message carries one listing with the supplier's specification, and asks for the check in the desk's shape, work from that message only. Read nothing from the catalogue system and save nothing: the desk keeps the check. Leave out the line that starts "Draft:" and the fixed last line.
- The message writes the allergen statement on the line "Allergens" and the country of origin on the line "Origin". "(nothing)" after an attribute of the listing means that the listing holds nothing for it.
- Write the heading "Summary" with at most five lines and no count of marks or of rows. When the finding is on the allergen statement, one line starts "Allergen first:".
- Then the heading "Draft check. For a content lead. No listing changed.", then one table row for each of the four attributes, in the order Net quantity, Pack size, Allergen statement, Country of origin, each with the listing's value and the specification's value as written. Mark a row "matches", "missing" or "does not match". For a finding, the note gives the style guide's rule on that attribute in its own words. Leave the note of a row that matches empty.
- The last line starts "Proposal:" and is either "correct the listing:" with the attribute, whether it is missing or does not match, and both values, or "keep the listing: every attribute matches the specification". Nothing is written after it.
- Every rule above on what you never do still holds. Give both values and leave the choice between them to the content lead. Write plain statements, not in the first person.
```

## State

These sections are written and not yet in the two agent folders. No agent has been run with them. Each of the two agents needs a run with its section before the desk is pointed at it.
