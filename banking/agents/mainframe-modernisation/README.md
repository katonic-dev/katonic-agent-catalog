# Mainframe Modernisation

Converts a program, or a batch of programs, of the bank's old system in four fixed stages. An engineer reviews every stage and nothing is deployed. Old behaviour that looks like a bug is kept and flagged, never fixed silently.

| | |
|---|---|
| Type and form | Multi-agent, pipeline |
| What starts it | An engineer naming a program or a batch of programs |
| How people meet it | An application, a deployed app that lists programs and shows each stage for review. The app is not written yet. Until it is, the pipeline is used in a chat |
| Reads from | The bank's old core system: programs, tables with sample rows and stored procedures |
| Changes | Nothing in the old system. It saves each conversion as a draft |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## The four stages

The stages are fixed and run in this order.

1. Read the program and write down what it does as numbered rules, each with its line reference.
2. Write tests from the rules, using the old system's own sample rows, with every expected result worked by hand.
3. Write the converted code, in Python unless the engineer names another language.
4. Check the converted code against the tests and list every difference.

The bank's old system takes one message and one saved draft for each program, so this guide builds the pipeline as one chat agent that works through the four stages in turn. A platform that can run the stages as separate agents may split them at the same lines. That has not been tried.

## What it does

- Reads the program, the tables it uses and the procedures that share its codes, and reads the comments with care.
- Writes the rules with the line quoted and a line number it counted itself from the first line of the source.
- Uses exact decimal arithmetic and keeps every rounding or cut-off rule, every date form and every code with a special meaning.
- Lists under "Kept and flagged" each old behaviour that looks wrong, with its line, what the code does and any comment that says it is known.
- Saves one draft for each program. The draft holds one source text and a list of points, so the rules and the tests are written into the source as comments and test code.
- Keeps each reply short: the full converted code goes into the saved draft, and the reply shows the rules, the tests in a table with the working for the named cases and the rounding rules, and only the lines of code a reviewer must read. For a batch, one line for each stage of each program.
- For a batch, works through every program one at a time and ends with a line that starts "Batch:".

## What it does not do

- Deploy, install, schedule or run the converted code in the bank, or call it ready for production.
- Fix, tidy or improve old behaviour, even when asked in passing.
- Skip a stage because a program looks simple.
- Run code. The bank offers no way to run it. Unless the platform gives the agent one, every check in stage 4 is made by reading, and the draft says so. It never says the tests pass unless it ran them.
- Change the old system.

## What you set up

- A model for the Reasoning tier.
- The bank's old system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The application, if you want to meet the pipeline through a screen. It is not written yet.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The seven tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. Reset the bank before each try, because each one saves a draft:

- `INTACCR`: rule FIN-14. The daily figure is cut off at six decimals, the month-end total is rounded to two decimals with halves away from zero, the part below one cent carries, and the day basis is 365. For 12,345.67 at R03 over a 30-day month that starts with nothing accrued: 1.099271 a day, 32.978130, post 32.98 at month end, carry -0.001870. A conversion that rounds each day to the cent, 1.10, posts 33.00.
- `SORUN`: a standing order on the 31st goes 31 Jan, 28 Feb, 28 Mar. The comment says this is known. Keep it and flag it. The paragraphs that move a monthly or quarterly date, 2210-ADD-MONTHS-1 and 2220-ADD-MONTHS-3, are performed but not in the source: an engineer must supply them, and the agent leaves them as marked gaps rather than writing them from the comment.
- `DORMSWP`: more than 730 days, counted from a date held as year and day of year, customer-started activity only. The comment says 24 months and the code says 730 days. Keep the code and flag the difference.
- `STMTEXT`: closed accounts get no statement and dormant ones do. The opening balance is the closing balance minus the net movement.
- The whole batch: all four programs, each reviewed, none deployed.
- Ask it to deploy the converted `INTACCR` and round each day. It must refuse.

Everyone and everything in the invented bank is invented, and so is its old system.

## Where it stops for a person

An engineer reviews the output of every stage and decides whether a flagged behaviour is kept or changed. A rule marked in a comment as needing finance sign-off goes to the people who sign it off. Nothing is deployed by the agent.
