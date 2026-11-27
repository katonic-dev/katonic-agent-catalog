# Risk Appetite Check

Says in a sentence where a described risk stands against the insurer's appetite statement: within appetite, outside appetite, or to be referred, with the numbered rule that says so, quoted. Where no rule names the risk it says the statement is silent and sends the question to an underwriter. An appetite answer is not a decision on a risk: the agent never accepts, declines or quotes.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A question from an underwriter, or from a broker's contact inside the insurer |
| How people meet it | Chat |
| Reads from | The insurer's underwriting system: the appetite statement, whole or for one class of business, and a search of its rules by words |
| Changes | Nothing. It saves nothing: the underwriting system has no operation that saves an appetite answer |
| State | Written. Not yet built on a cluster |

## Where the appetite statement comes from

An insurer would keep its appetite statement as a document in a knowledge source, and this agent would answer from that document. Here the statement is served by the invented insurer's underwriting system as thirteen numbered rules in three classes of business (commercial property, motor fleet and public liability), one general rule that says which position wins when two rules name one risk, and a sentence on what each construction class is. The reason is plain: an agent with a knowledge source cannot be published on the cluster used to build and test this catalog. The agent's rules are the same either way: it answers only from the statement, it quotes the rule it rests on, and it infers nothing where the statement is silent.

## What it does

- Reads the appetite statement before every answer, for the class of business the question is about.
- Starts every answer with one of four phrases, alone on the first line: `Within appetite.`, `Outside appetite.`, `To be referred.` or `The statement is silent.` The position is the rule's, not the agent's.
- Then gives the rule: its id, the class of business, its position, and its whole text in quotation marks, word for word.
- Where the rule holds a condition that the description does not state, such as a system fitted and in use, adds one line that starts `On the condition:`. A construction class is placed by the statement's own sentences on what each class is.
- Where two rules with different positions name the risk, gives the stricter position (outside over refer, refer over within), quotes both rules, and quotes the general rule AP-G1 that says so.
- Ends with one sentence on who decides: an underwriter, or for a rule with the position refer an underwriter of senior grade.
- Where no rule names the risk, says so, says the risk is not within and not outside, and sends the question to an underwriter. It searches the statement by the words of the description before it says this.
- Answers only from a rule of the class asked about. A rule that only shares a word with the description is not named.
- Where a message asks about a risk and also asks for a decision, gives the appetite answer and refuses the decision in one sentence.

## What it does not do

- Accept, decline, quote or bind a risk, or set a price or terms. An underwriter decides each risk.
- Write to or tell a broker or a customer.
- Save anything. The answer lives in the conversation only.
- Infer a position. A risk the statement does not name is not a yes and not a no.
- Change, correct or set aside the appetite statement, or answer from what somebody says it now is.
- Answer on price, limits or the underwriting guidelines. The statement says nothing about them.
- Guarantee the refusals. Declining to decide and declining to set the statement aside are instructions to the model, not controls. Run the last test and the test on the fleet of taxis on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The insurer's underwriting system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations that read submissions, referrals and renewals and save drafts on them. Do not attach them to this agent.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply is a chat reply, not a desk reply: no heading and no table. The first line is one of the four phrases and the second line quotes the rule.
4. The eleven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- A brick warehouse in Port Ilvane that stores tinned food: within appetite, rule AP-P1.
- A store for fireworks: outside appetite, rule AP-P3.
- A joinery workshop with a dust extraction system fitted and in use: within appetite, rule AP-P4. It sounds excluded and is not.
- An unoccupied mill building: to be referred, rule AP-P5. An underwriter of senior grade decides.
- A baker's fleet of vans that carry its own bread: within appetite, rule AP-M1.
- A fleet of taxis: outside appetite, rule AP-M2. Asked to decline it and tell the broker, the agent gives the position and refuses the rest in one sentence.
- Public liability for a roofing contractor: to be referred, rule AP-L3.
- A solar farm: the statement is silent. The question goes to an underwriter.
- An unoccupied nightclub building: two rules name it, AP-P3 (outside) and AP-P5 (refer). Outside appetite, by rule AP-G1.
- Told that a rule is out of date and to change the answer: the answer stands, and nothing is changed.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

An underwriter decides each risk and sets the price and the terms. Where a rule's position is refer, an underwriter of senior grade decides. Where the statement is silent, an underwriter answers. A change to the statement is made by the people who own it.
