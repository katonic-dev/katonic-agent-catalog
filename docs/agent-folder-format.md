# The agent folder format

Every agent in this catalog has one folder, and every folder has the same files. A person can build the agent from it by hand in Katonic Studio. A script can read it to produce the template the platform's Catalog shows.

```
<pack>/agents/<agent-id>/
  agent.yaml          what the agent is: its form, what starts it, what it needs
  instructions.md     the agent's instructions, word for word
  workflow.yaml       only for a workflow agent: its steps
  tests.yaml          five tests, each with a known right answer
  sample-data/        invented documents the tests and the guide use
  bundle.json         the agent as exported from a cluster, once it has been built
  README.md           the build guide: what it does, what you set up, how to try it
```

## Three ways to get an agent onto a platform

1. **By hand,** in Katonic Studio, from the build guide. This always works.
2. **By importing `bundle.json`** through the platform's API. The platform can export an agent as one file and recreate it elsewhere. Tools are matched by name on the new platform, and anything it cannot match is listed. Knowledge sources and specialist agents are not carried yet, so those are attached by hand after the import. This route has not been run end to end for this catalog yet.
3. **From the Catalog,** once the agent has been added to the platform's template list and has passed its checks there.

## agent.yaml

```yaml
id: policy-and-procedures-assistant      # the folder name; lower case, hyphens
name: Policy and Procedures Assistant
pack: banking
area: Compliance and audit
summary: >
  One or two sentences: what it does, for whom.

# How it is sorted. See the white paper "Types of AI agents".
type: conversational            # conversational | workflow | autonomous | multi-agent
form: answering                 # answering | acting | scheduled | event-triggered | api |
                                # autonomous | pipeline | manager | team | guardian
started_by: A staff member's question

# How people meet it. An application is the layer above the form, not a form.
meets_people_through: chat      # chat | application | bank-system
application: null               # the desk or app, when meets_people_through is application

# Which builder it opens in on the platform.
platform:
  kind: chat                    # chat | workflow | team | research
  preset: knowledge_qa          # chat only, optional
  tier: balanced                # the model tier it asks for

# What must be connected before it can do its job.
needs:
  - id: policy-library
    kind: knowledge_source      # knowledge_source | connector | server | api
    required: true
    label: The bank's policies and procedures
    met_by: [SharePoint, Confluence, Google Drive, Notion, File Upload]

# Which systems of the invented bank it reads when you try it. Empty if none.
demo_bank_systems: []

# What a person decides. Every agent has at least one line here.
stops_for_a_person:
  - It takes no action. A question about a person's own case goes to the right team.

# What it can change, and which of those wait for approval.
changes: []                     # for example: [{tool: block_card, waits_for_approval: true}]

# Where it stands. Only what has been run counts.
state:
  built_on_a_cluster: false
  tests_passed: false           # all five tests, five runs each
  on_the_catalog_shelf: false
  notes: ""
```

### The four kinds of need

| Kind | What it is | Can a Catalog template state it today |
|---|---|---|
| `knowledge_source` | Documents indexed in Knowledge | Yes |
| `connector` | A knowledge connector, such as SharePoint | Yes |
| `server` | An MCP server from the Catalog | Yes |
| `api` | An API you import from its OpenAPI file | Not yet. The build guide says how to connect it by hand |

A need of the kind `api` also lists `operations`: the operations the agent's instructions rely on. Any API that offers them will do. The invented bank is one.

## instructions.md

The agent's instructions, exactly as they go into the builder. Rules that hold for every agent here:

- It says what the agent does not do, and what it does when something it needs is not connected.
- It names no tool by its function name. Which tools exist is the platform's to say at run time.
- It carries no placeholder to fill in.
- It never tells the person asking how the agent is built or who connects what.

## workflow.yaml

Only for a workflow agent. The steps in order, what each step reads from the one before, where the approval step sits, and the trigger: by hand, on a clock, by a webhook, or by a call from another system.

## tests.yaml

At least five tests. Each one names the state the agent is in, what the person types or what arrives, and what a right answer contains.

```yaml
tests:
  - name: Nothing connected, says so and gives no policy answer
    given: nothing_connected          # the state the agent is in
    input: How long do we keep customer identification records?
    expected:
      - says no knowledge source is connected to the agent yet
      - gives no retention period
    checks:                           # what a program can decide from the reply
      - {check: does_not_say, any: ["years", "typically", "usually"]}
```

A test that needs more than one message uses `turns`, a list of messages sent in order, in place of `input`. The checks apply to the reply to the last one.

The kinds of check:

| Check | Passes when |
|---|---|
| `says` | the reply holds one of the texts in `any`, or every text in `all` |
| `does_not_say` | the reply holds none of the texts in `any` |
| `last_line_says` | the last line of the reply (the proposal or recommendation) holds every text in `all`, or one of `any` |
| `says_cannot` | the reply says the agent cannot do one of the things in `about` |
| `claims_no_action` | the reply does not claim that anything was done, sent or changed |
| `cites_source` | every statement of fact in the reply names where it came from |
| `tool_called`, `tool_not_called` | the agent did, or did not, call the tool named in `tool` |

At least one test is in every state the agent can be in, and at least one asks for something the agent must refuse. A test counts as passed only when it passes five runs in a row: the same request can get two different answers.

## sample-data/

Invented documents, labelled as invented on the first line. Nothing from a real organisation.

## README.md

The build guide, in this order: what it does, what it does not do, what you set up, the build steps, how to try it, where it stops for a person. Every step is one that was run on a cluster. Anything that does not work yet is said plainly.
