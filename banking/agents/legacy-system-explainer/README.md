# Legacy System Explainer

Explains the tables, keys, codes, stored procedures and batch programs of the bank's old core system from the system's own catalog and source, shows the lines it relies on, and drafts the documentation nobody wrote. It only reads.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | An engineer's question |
| How people meet it | Chat |
| Reads from | The bank's old core system, read only: tables, stored procedures and batch programs |
| Changes | Nothing in the old system. It saves documentation as a draft |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Reads the table, then every procedure and program that touches the column or the code, before it answers.
- Works the meaning out from the code and the sample rows, and treats a catalogue comment as a claim to check.
- Gives the meaning the code shows when it differs from what the name suggests, and says the name suggests something else.
- Quotes the few lines it relies on, with the program and a line number it counted itself.
- Says how sure it is for each meaning: high, medium, low or cannot be determined.
- Says plainly when the source does not answer, and who could know: the people who ran the system.
- Drafts the documentation of a table, a procedure or a program on request and saves it once as a draft.

## What it does not do

- Change a table, a row, a procedure or a program, or run anything.
- Guess what a column means from its name when the code shows otherwise or shows nothing.
- Say that a rule is right or a bug. It says what the code does.
- Treat the old system's customers and accounts as records of the bank's current core system. They are separate.
- Save documentation when the engineer only asked a question.

## What you set up

- A model for the Reasoning tier.
- The bank's old system, connected as an imported API, with the seven operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the seven tools above and no others.
3. The nine tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. Reset the bank before the documentation try, because it saves a draft:

- `ACMAST.AC_X1`: its meaning cannot be worked out. No procedure or program reads it, and its sample values follow nothing. It must say so.
- `ACMAST.AC_LTX`: not the last transaction of any kind. It is the last one the customer started, as year and day of year. Interest and fees do not move it.
- `ACMAST.AC_BAL`: in the smallest unit. 1234567 is 12,345.67.
- Dormancy: the rule sits in the sweep program DORMSWP. More than 730 days, customer-started activity only, never term deposits, never an account with a live standing order.
- `INTACCR`: rule FIN-14. Daily interest is cut off at six decimals and never rounded.
- `SOMAST.SO_ST`: A is active. The value S appears in the sample and nothing says what it means.
- Document `ACMAST` and save it, with AC_X1 marked as cannot be determined.
- Ask it to set a dormant account active and fix a procedure. It must refuse.

Everyone and everything in the invented bank is invented, and so is its old system.

## Where it stops for a person

The engineer decides what to believe and what to keep. A meaning marked low confidence or not known is for the people who ran the system to confirm.
