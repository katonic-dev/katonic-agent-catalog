# Install Meridian Trust Bank on the Katonic platform

Meridian Trust Bank is an invented bank, kept as one small service. This guide puts it inside your own Katonic platform and turns its back-office systems into tools that agents can call.

What you get when you finish:

- The bank running as an app in App Studio, on an address of your platform.
- Its systems (the guide imports two, `cards` and `core`) available as tools in Control Room.
- An agent in Studio that has those tools and can read from the bank and act on it.

What you need:

- An administrator account on the platform, with access to App Studio, Control Room and Studio.
- The repository address: `https://github.com/katonic-dev/katonic-agent-catalog`. It is public, so no access token is needed.
- A key of your own for the bank. Make a long random value, for example with `python -c "import secrets; print(secrets.token_urlsafe(32))"`, and keep it. You use the same value twice.

It takes about 15 minutes. The first build of the app takes about two minutes.

The screenshots show the platform with demonstration data. Names of people, teams and organisations in them belong to that demonstration. Your platform will show your own.

## 1. Start a new app from the repository

Open App Studio (Studio, Develop, App Studio) and choose **New app**. Choose the source **GitHub repo**, type the repository address and the branch, and press **Continue**.

| Field | Value |
|---|---|
| Source | GitHub repo |
| Repository URL | `https://github.com/katonic-dev/katonic-agent-catalog` |
| Branch | `main` |
| Access token | leave empty |

![App Studio before the first app, with the New app button](images/01-app-studio-new-app.png)

![The Source step, filled in](images/02-new-app-source.png)

The platform reads the repository. It detects FastAPI and finds `demo-bank/main.py` and the `requirements.txt` next to it. Leave the main file and the start command as they are. It also says it found a Dockerfile and that App Studio does not build Dockerfiles. That is right: App Studio runs the code on its own FastAPI image and installs `requirements.txt` itself.

![The Framework step: FastAPI detected, main file demo-bank/main.py](images/03-new-app-framework.png)

## 2. Name it, give it its settings, and make it Public

On the Runtime step, give the app a name and a size, set the health check path, and add the three settings. Then choose the access on the Network step.

| Field | Value |
|---|---|
| App name | `meridian-demo-bank` |
| Compute tier | the smallest one. Nano, with 0.2 of a core and 512 Mi of memory, was enough |
| Replicas | 1 minimum, 1 maximum |
| Health check path | `/health` |
| Setting `BANK_API_KEY` | your key, with **Secret** ticked |
| Setting `BANK_TODAY` | `2026-11-24` |
| Setting `BANK_PUBLIC_SCHEME` | `https` |
| Access | Public |

![The Runtime step: name and compute tier](images/04-runtime-name-and-size.png)

Tick **Secret** on `BANK_API_KEY`. The value is then hidden and is stored as a secret, not as plain text.

![The Runtime step: health check path and the three settings, the key hidden](images/05-runtime-health-and-settings.png)

Choose **Public**. Every other access level puts a sign-in page for a person in front of the app, and the platform's own services cannot get past that page. The bank protects itself with the key you set, so Public is safe here: every data call needs the key.

`BANK_PUBLIC_SCHEME` makes the addresses on the bank's landing page start with `https://`. Without it they can show `http://` when the platform ends the secure connection before the app.

![The Network step: Public chosen](images/06-network-public.png)

Press **Continue**, check the summary, and press **Ship app**.

![The Review step, with the Ship app button](images/07-review-and-ship.png)

## 3. Wait until the app runs

The build page shows the steps: the platform starts a pod, clones the repository, pulls the image, installs the requirements and starts the app. It goes live when `/health` answers. The first time takes about two minutes.

![The build page while the dependencies install](images/08-build-running.png)

When it is live, the app has its own page with the tabs Preview, Deploys, Logs, Metrics and Settings. Under the name is the address of the app. It looks like this, with six characters that the platform adds to the name:

```
https://<your platform>/apps/meridian-demo-bank-<six characters>/
```

Write this address down. It is `<the app's address>` in the rest of this guide. The Preview tab shows the bank's landing page.

![The app page with Preview, Deploys, Logs, Metrics and Settings, and the address](images/09-app-running.png)

The Settings tab, under Environment, lists the settings again. The value of `BANK_API_KEY` is never shown. You can change a setting there, and the app restarts when you save.

![Settings, Environment: the key stays hidden](images/10-app-settings-environment.png)

## 4. Import the systems as tools

Open Control Room, Tools, and choose **Import OpenAPI**. Import one system at a time, so that an agent gets only the tools of the systems it needs. Start with `cards`.

On the first page choose **From URL** and type the address of the system's OpenAPI document:

```
<the app's address>/cards/openapi.json
```

![Import OpenAPI, the first page: From URL](images/11-tools-import-source.png)

Press **Next: Configure**. The platform reads the document and says "Spec validated successfully". The document itself needs no key; only the data calls do. The platform fills in the name, the description and the base URL. Change the name, and check that the base URL starts with `https://` and ends with `/cards`.

| Field | Value |
|---|---|
| Name | `Meridian demo bank: cards` |
| Base URL | filled in by the platform: `<the app's address>` followed by `cards`, with no slash at the end |
| Authentication | API Key (Header) |
| Header name | `X-API-Key` |
| Header value | your key |
| Access groups | at least one team; only people in those teams see the connection |

![Configure: name, description and base URL, then the authentication](images/12-tools-import-configure-top.png)

![Configure: the key as a hidden header value, and the access group](images/13-tools-import-configure-auth.png)

Press **Import API**. The connection appears with seven tools.

![Tools: the cards connection, ready, with seven tools](images/14-tools-cards-imported.png)

Do the same for `core`, with `<the app's address>/core/openapi.json` and the name `Meridian demo bank: core`. It has eight tools.

![Tools: both connections](images/15-tools-both-imported.png)

Open a connection to see its operations. Each operation is one tool, named after its `operationId` in the bank's document.

![The cards connection: its seven operations](images/16-tools-cards-operations.png)

The **All tools** tab lists every tool with its source and a read or write kind taken from the HTTP method.

![All tools: the 15 tools of the two connections](images/17-tools-all-tools.png)

The tools are:

| Connection | Tool | Method and path |
|---|---|---|
| cards | `list_customer_cards` | GET `/cards` |
| cards | `get_card` | GET `/cards/{card_id}` |
| cards | `list_card_transactions` | GET `/cards/{card_id}/transactions` |
| cards | `list_card_disputes` | GET `/cards/{card_id}/disputes` |
| cards | `open_card_dispute` | POST `/cards/{card_id}/disputes` |
| cards | `block_card` | POST `/cards/{card_id}/block` |
| cards | `request_card_replacement` | POST `/cards/{card_id}/replacement` |
| core | `search_customers` | GET `/customers` |
| core | `get_customer` | GET `/customers/{customer_id}` |
| core | `list_customer_accounts` | GET `/customers/{customer_id}/accounts` |
| core | `get_account` | GET `/accounts/{account_id}` |
| core | `list_account_transactions` | GET `/accounts/{account_id}/transactions` |
| core | `list_customer_contacts` | GET `/customers/{customer_id}/contacts` |
| core | `add_contact_note` | POST `/customers/{customer_id}/contacts` |
| core | `get_customer_exposure` | GET `/customers/{customer_id}/exposure` |

The other seventeen systems work the same way. Import each one at `<the app's address>/<system>/openapi.json`. The names of the systems are in the table at the top of the [README](../README.md).

## 5. Attach the tools to an agent

Open Studio and choose **New agent**, then **Answer & assist**, then **Answer questions**, then **Start blank**. Give the agent a name, such as `Card Servicing`, and open the **Tools** section.

The section lists the connections you imported, each with `0 / N tools`.

![The Tools section of the agent: the two connections, no tools yet](images/18-agent-tools-section.png)

Press **Browse & attach**. Choose a connection at the top of the dialog and press **Select all** to take every tool of it, or tick single tools. Do this for both connections, then press **Done**.

![The picker: tools of the core connection ticked](images/19-agent-pick-tools.png)

The section now says that 15 tools are attached. The agent can call them.

![The Tools section with 15 tools attached](images/20-agent-tools-attached.png)

Four of the fifteen tools change data: `open_card_dispute`, `block_card`, `request_card_replacement` and `add_contact_note`. To have a person approve such a call before it runs, set an approval rule for each of those tools in Control Room, Policies. The page of the [Card Servicing agent](../../banking/agents/card-servicing/README.md) says how, and what was seen when a call was held.

## Check it works

1. Open the landing page. Open `<the app's address>` in a browser. It is titled "Meridian Trust Bank (invented)" and lists the nineteen systems with links to their OpenAPI documents and docs pages.

   ![The bank's landing page: the nineteen systems](images/23-bank-landing-page.png)

2. Check the health path. It needs no key:

   ```
   curl <the app's address>/health
   ```

   The answer is `{"demo_data":true,"status":"ok","bank":"Meridian Trust Bank","bank_date":"2026-11-24"}`.

3. Make one call with the key. Without the key the call is refused with 401:

   ```
   curl -H "X-API-Key: <your key>" <the app's address>/cards/cards/CRD-2001
   ```

   The answer is one card, masked, and starts with `{"demo_data":true,"card_id":"CRD-2001","customer_id":"CUS-1002",`. Every answer of the bank carries `"demo_data": true`. The docs page of a system lets you try its operations in the browser:

   ![The docs page of the cards system](images/24-bank-cards-docs.png)

4. Ask the agent. Open the Test tab of the agent and write: `I have customer CUS-1002 on the line. He lost his debit card two days ago and says some payments are not his. What do we have?` The agent calls tools such as `search_customers`, `get_card` and `list_card_transactions`, and the answer is built from what the bank returns. Open the trace of the run to see the tool calls.

## Update it later

When you push a change to the repository, or when you want the app to start again, use the Apps list. In App Studio, press the three dots at the end of the app's row and choose **Redeploy**.

![The row menu in the Apps list, with Redeploy](images/21-apps-list-redeploy-menu.png)

The platform says that the running app keeps serving until the new pod is ready.

![The Apps list after Redeploy](images/22-apps-list-redeploying.png)

The Deploys tab of the app lists every deploy with its commit and which one is current. Saving a changed setting under Settings restarts the app in the same way.

## Settings

Set these under Settings, Environment, or in the Runtime step when you create the app.

| Setting | Meaning | In this guide |
|---|---|---|
| `BANK_API_KEY` | The key. If it is not set, a random key is made at start and printed once in the log. It is never shown on a page. | Set, as a secret |
| `BANK_AUTH` | `off` turns the key check off. For a laptop only. | Not set |
| `BANK_TODAY` | The bank date, `YYYY-MM-DD`. The default is today. Dates in the data are relative to it. With the same bank date the data is identical on every start. | `2026-11-24` |
| `DATA_DIR` | A writable folder. State is written there as one JSON file. | Not set |
| `KATONIC_DATASET_PATH` | If `DATA_DIR` is not set and this is, state goes to `<KATONIC_DATASET_PATH>/demo-bank-state`. | Not set |
| `BANK_WEBHOOKS` | A JSON list of subscriptions, each `{"event_kind": "...", "url": "...", "header_name": "...", "secret_value": "..."}`. | Not set |
| `BANK_PUBLIC_SCHEME` | `https` or `http`. Forces the scheme in every address the bank prints. Set it to `https` when the bank sits behind a gateway that ends the secure connection early and the landing page shows `http://` addresses. | `https` |

With none of `DATA_DIR` and `KATONIC_DATASET_PATH` set, the bank keeps its state in memory only, so a restart puts the data back to the start.

## What is not covered

Registering a system's MCP address (`<the app's address>/<system>/mcp`) with the platform is not covered, because it was not proven: on the development cluster the registration was accepted and the server then did not appear in the list. The bank itself answers MCP requests correctly. Use the OpenAPI import above. A packaged, one-step install is planned.

## What was proven

On 24 November 2026, on a development cluster of the platform, the deployment, the import of the `cards` and `core` documents, and agents calling the tools were run, and the bank answered. In that run the bank's key check was switched off (`BANK_AUTH=off`) and the import used no sign-in.

The set-up shown in this guide, with the key switched on, the key as a secret setting and the import signing in with the `X-API-Key` header, is the one to use. It had not been run end to end on a cluster when this was written.

The bank's side of that set-up was run on a laptop on the same day, with the key switched on: the health path, the landing page and the OpenAPI documents of `cards` and `core` answered without a key, a data call without the key was refused with 401, and the same call with the key in the `X-API-Key` header was answered.
