# Sanctions Alert Review

Compares a customer's record with a watchlist entry field by field and recommends whether a screening alert should be cleared or escalated, with the reason beside each field.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A screening alert arriving at the bank. The bank's screening system can announce one through its event for new screening alerts |
| How people meet it | An application: the Sanctions desk |
| Reads from | The bank's screening system: the alert, the customer's fields and the list entry's fields side by side (place of birth and address included), the list entry and the earlier alerts. The core system: the customer's contact history |
| Changes | Saves a draft recommendation. The draft closes no alert |
| State | Built on a development cluster on 24 November 2026. All ten tests pass five runs in a row. Not on the Catalog shelf |
| Website page | [katonic.ai/use-cases/banking-sanctions-alert-review-agent](https://www.katonic.ai/use-cases/banking-sanctions-alert-review-agent) |

## What it does

- Reads the alert, the list entry and the system's own field by field comparison, which now includes place of birth and address.
- Writes one row for each field: name, aliases, date of birth, place of birth, nationality, identity number, address, related persons where the entry lists any, and the earlier alerts on the same pair.
- Marks each row matches, partly matches, differs, not on the entry or noted, with the reason and the ids of both records.
- Where the entry holds too little to rule a match out, says so and does not clear the alert.
- Saves the recommendation and the comparison as a draft, each row's result in one of the five words the system takes (matches, partly_matches, differs, not_on_entry, noted), and says it was saved only if the system's reply says so. If the system refuses the save, it says what the system said and that nothing was saved.
- Writes the summary in plain statements, with no count of marks (the desk counts them from the table) and no first person, and writes every date as day, short month and year, for example 21 Jul 1990.
- Ends with one recommendation line: clear or escalate, and why.

## What it does not do

- Close an alert, mark it a true match or a false positive as a decision, or say that the customer is sanctioned or cleared. The compliance officer decides.
- Contact the customer, freeze or block anything, or file a report.
- Fill a gap: a field the entry does not hold is marked not on the entry. An entry may leave out its address or its place of birth on purpose, and that is not a finding.
- Treat the match score as evidence.
- Guarantee the same marks on every run. The draft is for the compliance officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's screening system and its core system, connected as imported APIs, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Sanctions desk](../../desks/sanctions/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads `DESK_CONFIG`. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft review. For the compliance officer. Not decided.", a seven-column table, and a last line that starts "Recommendation:" followed by clear or escalate. In the earlier-alerts row the two value columns hold the same text. Change the instructions and the desk's `draft.instruction` together.
4. The tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `SCR-2001`: a false positive. Wynne Castellane against WL-9001, Wynn Castellano. Date of birth (21 Jul 1990 against 2 Feb 1962), place of birth, nationality and address differ. An earlier alert on the same pair, SCR-1990, was closed as a false positive. Clear.
- `SCR-2002`: a false positive. Oskar Brindlemoor against WL-9002, Oscar Brindlemore. Date of birth (3 Nov 1978 against 17 May 1955), place of birth, nationality and address differ and no identity number matches. Clear.
- `SCR-2003`: Valdis Orrenmoor against WL-9003. Name, date of birth, place of birth, nationality, identity number and address all agree. Escalate, for a person to confirm a true match.
- `SCR-2004`: uncertain. Katrin Elsdottir-Vance against WL-9004, which holds a birth year and a country of birth only, and no address. The country agrees with her place of birth, which is not enough to identify anyone. Escalate.
- `SCR-2005`: uncertain. Anselm Drozdowich against WL-9005, a spelling variant the entry lists as an alias. Date of birth, place of birth and nationality agree. The entry has no identity number, and its address differs from hers, which could be a move. Escalate.
- `SCR-2006`: Perdita Vanhollow against WL-9006, a politically exposed person who lists her as spouse. An earlier alert, SCR-1991, was closed as a true match with enhanced due diligence. Her place of birth differs from his, and the address is the same, as a shared home would be. Escalate for enhanced due diligence.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The compliance officer reads the review and decides every true or uncertain match, and closes the alert in the screening system under their own name. Nothing is closed, frozen or reported by the agent.
