# Adverse Media Screening

Searches the bank's press archive for a named subject and reports what it finds, each point with its article id and the address of the article's page.

| | |
|---|---|
| Type and form | Autonomous agent |
| What starts it | A request from a person, or from another agent |
| How people meet it | An application: the Investigations desk |
| Reads from | The bank's press archive, and the core system and monitoring system for the subject's own record |
| Changes | Saves a draft screening summary. Nothing else changes |
| State | Built on a development cluster on 24 November 2026. All nine tests pass five runs in a row. Not on the Catalog shelf |
| Website page | [katonic.ai/use-cases/banking-adverse-media-screening-agent](https://www.katonic.ai/use-cases/banking-adverse-media-screening-agent) |

## What it does

- Searches the archive for the subject's name and, when that finds nothing, for the parts of it.
- Reads every article in full, and sets the facts in it (age, town, country, trade) beside the same facts in the bank's record, including a person's place of birth.
- Says for each article whether it is adverse and about the subject, about someone else with the same name (or a relative), or neutral, with the facts that tie it or separate it. The marks it uses are supports concern, neutral, someone else, unclear and missing. The Summary holds no count of marks.
- Gives each article's id and its page address exactly as the archive returned it.
- Says when an article reports an allegation or an inquiry and not a finding.
- Saves the findings as a draft, and ends with one recommendation line.

## What it does not do

- Treat a person with the same name as the subject unless a detail ties them together, and it never merges two people.
- Treat a relative's coverage as the subject's.
- Decide that a subject is a risk or is cleared, close an alert or open a case. The compliance analyst decides.
- Fill a gap or guess an age, a place or a trade.
- Guarantee the same marks on every run. The draft is for the compliance analyst. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's press archive, core system and monitoring system, connected as imported APIs, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Investigations desk](../../desks/investigations/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting, and the agent's id in `MEDIA_AGENT_ID`. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft media screening. For the compliance analyst. Not decided.", a seven-column table, and a last line that starts "Recommendation:". Change the instructions and the desk's `routing` setting for "Media screening" together.
4. The tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- Valdis Orrenmoor (`CUS-1007`): adverse and about him. ART-6001 and ART-6002: an asset freezing order for arms brokering, upheld by a court. Born 30 September 1971, a Quenmark national who lives on Cinder Quay in Port Ilvane.
- Karn Harbour Freight Agency (`CPY-4005`): adverse and about the agency. ART-6003, a customs inquiry, and ART-6004, an accusation of moving goods for listed buyers.
- Perdita Vanhollow (`CUS-1010`): no article names her. ART-6005 and ART-6006 are about her spouse, Leopold Vanhollow, and are not about her.
- Wynne Castellane (`CUS-1005`): a namesake. ART-6008 is about a 54-year-old machinery dealer in Brandymoor, Tessaly. The customer was born in 1990, in Marlow Reach, Meridia.
- Harrowgate Bakery Supplies Ltd (`CUS-1017`): a company namesake. ART-6011 is about a flour mill in Hartsfell, Quenmark, with no link to Meridia.
- Pinecrest Tooling Works Ltd (`CUS-1018`): nothing adverse. ART-6012 reports an export award and names 24 staff, the same as the loan application LAP-8003.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The compliance analyst reads the findings, judges what is relevant and decides what to do. The agent decides nothing.
