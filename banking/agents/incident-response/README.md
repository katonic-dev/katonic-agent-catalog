# Incident Response

For an open incident, it gathers the dashboards and metrics, the recent changes and the incident's own tickets, and drafts the first assessment for the engineer on call. Every statement carries the record it came from. The engineer on call decides what to do.

| | |
|---|---|
| Type and form | Multi-agent, manager agent: a manager and three specialists |
| What starts it | An incident being opened. The bank's IT operations system can announce a new incident through its event for incidents. Otherwise a person names the incident |
| How people meet it | Through the bank's own system: the assessment is a draft note on the incident |
| Reads from | The bank's IT operations system: incidents, metrics, dashboards, changes and runbooks |
| Changes | Nothing in the bank. One specialist saves the assessment as a draft note |
| State | Built on a development cluster on 24 November 2026 as one chat agent. On its fourth version three of six tests passed five runs in a row; the three long assessments passed four, two and one of five. Every safety check passed in every run. This folder now describes the manager and three specialists. That form is written and not yet built. Not on the Catalog shelf |

## The manager and its three specialists

Four agents. The manager is the one people and the bank's system talk to. It holds no tool of its own: an agent that coordinates a team is given only the specialists attached to it, and its instructions go in the team's router prompt. So it reads no record itself. A message that asks only for an action gets a short refusal and no specialist is sent. For anything else it sends Incident Evidence first; if that specialist returns that the incident is closed or not held, the manager stops there and sends no one else. Otherwise it sends Change History, checks every id and figure the two return, writes the one reply, and sends the finished text to the one specialist that can save it.

| Agent | Instructions | Its one job | Tools |
|---|---|---|---|
| Incident Response (manager) | [`instructions.md`](instructions.md) | Sends the specialists, checks each part, writes the nine-part reply and the Saved line | none |
| Incident Evidence | [`specialists/incident-evidence/instructions.md`](specialists/incident-evidence/instructions.md) | The incident, its timeline, the measures of each service affected, every gap, the dashboards and certificates. The alert's minutes without data and the gap's minutes come back in one sentence as two readings of one event. A closed incident comes back as closed, with nothing else read | get_incident, get_service_metrics, get_dashboard_snapshot |
| Change History | [`specialists/change-history/instructions.md`](specialists/change-history/instructions.md) | A fixed set of change searches, each one listed with the period the system gave back; every change by its id on its own line, in its record's words; the runbook of the alert's service, every step | list_recent_changes, get_runbook |
| Draft Keeper | [`specialists/draft-keeper/instructions.md`](specialists/draft-keeper/instructions.md) | Saves the manager's finished text once as a draft note, each part exactly as given with its heading, and returns one line with what the system said | save_incident_assessment |

Only Draft Keeper can write, and it writes only a draft note. The manager calls it once, after the reply is written, and never for a closed incident or a message that only asks for an action.

### Why it is split this way

The fourth version, built as one chat agent with one long instruction, failed in four places, and each specialist holds one of them:

- **The change search.** It had to run four searches before writing, and in some runs it left one out: the 168-hour search was not stated, or the older change ITC-8104 was not looked up, or a search was described that had not been run. Change History runs every search in a fixed order and lists each one with the period the bank gave back, and the manager checks the list before it writes.
- **Two readings of one gap.** The alert says "no data for 36 minutes" at 09:36; the measure's gap is 50 minutes at 09:50. In four of five runs the agent set them against each other under evidence against or what is not known. Incident Evidence returns them as one sentence, two readings of one event, pairing the two lengths of time and never a sample's value, and the manager copies that sentence unchanged into part 2 only. (Until 25 November 2026 the bank's alert said 35 minutes, which did not agree with its own times, 09:00 to 09:36; the bank's data now says 36.)
- **The save.** One run saved twice and one three times; one wrote the whole assessment into the note and a four-line summary into the reply. Draft Keeper saves once, from the manager's finished text, word for word.
- **The runbook steps.** One run left out the steps that need the incident manager and the change manager. Change History returns every step word for word, and the manager gives every step that needs an approval.

There is no specialist for severity: the bank holds no rule that sets it. Severity is a field of the incident, which the agent reports and does not change.

## What it does

- Writes the assessment in a fixed order: what is failing, since when, what changed just before, the likely cause, the evidence for, the evidence against, what is not known, what to check next.
- Gives every figure exactly as the record gives it, with its time and its source.
- Says when a measure has a gap in its samples, and does not treat the gap as normal or abnormal.
- Says what the runbook says for each step and who may run it. It does not say a step should be run.
- Saves the assessment once as a draft note, and says it was saved only if the system says it was applied.

## What it does not do

- Restart a service, roll back a release, switch a flag, install a certificate, or change anything in the bank.
- Close the incident, change its severity or add to its timeline.
- Say that a cause is certain, or judge a person.
- Assess a closed incident. That is for a post-incident review.
- Search tickets beyond the incident's own timeline and linked changes. The bank's IT operations system holds no others.
- Send anything to anyone. The note is read on the incident.
- Guarantee the same wording on every run. The note is a draft for the engineer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's IT operations system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml), each attached only to the specialist that holds it. The system offers two more, which list incidents and save a post-incident review; attach them to none of the four agents.
- If you want it to start by itself, a subscription to the incident event that calls the manager with the incident id. Without it, a person names the incident.

## Build it

These steps follow the way the connection was built on 24 November 2026 and the manager form was built on 25 November 2026.

1. In Tools, import the IT operations system from its OpenAPI file (`<bank>/itops/openapi.json`), with no authentication, for the owner team.
2. Build the three specialists first. For each, create a new chat agent on the Reasoning tier, give it the name in the table above (the slug the same as its id: `incident-evidence`, `change-history`, `draft-keeper`), paste its instructions word for word, and attach only the tools in its row. Attach no skill and no knowledge source. Publish each.
3. Check the tags on Draft Keeper's one tool. The builder tagged it READ in the one-agent build, although it saves a draft.
4. Create the manager as a new agent of the kind that coordinates a team. Name it Incident Response, set the Reasoning tier, attach the three specialists, and paste [`instructions.md`](instructions.md) word for word into the router prompt of its routing settings. The team builder has no place for tools: the manager holds none. Publish it.
5. Test. Run test 1 on the manager with no specialist attached. Run tests 7, 8 and 9 on each specialist alone. Then run tests 2 to 6 on the manager with the team attached. Put the IT operations system back before each run that saves (`POST /admin/reset/itops` on the bank).

The tests are in [`tests.yaml`](tests.yaml). A tool check counts a call made by any of the specialists in the run; the manager makes none.

## What is unchanged from the one-agent version

- The six tests and their right answers. One line was added to tests 2, 3 and 4 (save once, the same text as the reply) and one to test 6 (send Incident Evidence only). Three tests were added, one for each specialist.
- The reply: the same nine parts in the same order, the same two short replies (nothing connected; asked only for an action), and the same "Saved:" line.
- The one draft it saves, and where it stops for a person. The operations are six: the list of incidents is no longer needed, because the manager holds no tool and asks which incident when a message names none.
- No desk uses this agent. It meets people through the bank's own system.

## Try it

Against the invented bank at its starting data (bank date 2026-11-24, service clock 10:00). Put the IT operations system back before each try, because each one saves a draft:

- `INC-7001`: payments slow down 20 minutes after release 4.18.0 of payment-service (change ITC-8101). The payments database CPU went from 34 to 95 percent. The other changes of the day do not touch the payment path.
- `INC-7002`: card purchases declined. The client certificate cardproc-mtls-client expired at 04:58, with no recent change. The last change, ITC-8104, was 12 days earlier.
- `INC-7003`: a false alarm. The collector sent no volume samples from 09:10 to 09:40. The service's own measures are normal.
- `INC-7004`: closed. It gets no assessment, only a post-incident review.
- Ask it to switch the flag off, roll back the release and close `INC-7001`. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The engineer on call decides every action. A runbook step that needs the incident manager or the change manager is run by a person. The agent only says what the runbook says.
