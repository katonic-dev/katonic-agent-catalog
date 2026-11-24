# Retail and restaurants pack

36 agents a retailer or a restaurant operator can build on the Katonic platform, and the desks and applications people use them through. They are written against one invented company, Rowanmere Group: a store chain with an online shop, and a restaurant chain that is partly franchised.

**Status: work in progress.** The State column says where each one stands. "Planned" means the folder is not written yet. Twenty folders are written. The State column says which have been built and tested on a platform.

Every agent follows one rule: it prepares the work, and a person makes the decision. An operation that changes a record waits for a named person.

## The agents

| # | Agent | What it does | Type and form | How people meet it | State |
|---|---|---|---|---|---|
| | **Customer care** | | | | |
| 1 | [Customer Service](agents/customer-service/README.md) | Drafts a reply to each customer ticket from the help articles and past cases, with the article cited | Workflow, event-triggered | Customer care desk | Written. Not yet built on a platform |
| 2 | [Returns Processing](agents/returns-processing/README.md) | Checks a return request against the returns policy, says which condition it meets or fails, and prepares the approval and the customer message | Workflow, event-triggered | Customer care desk | Written. Not yet built on a platform |
| 3 | [Order Enquiry](agents/order-enquiry/README.md) | Answers "where is my order" from the order and delivery record, and says when the record does not explain the delay | Conversational, answering | The shop's website | Written. Not yet built on a platform |
| 4 | [Complaint Handling](agents/complaint-handling/README.md) | Classifies a complaint, sets out what happened from the order and contact history, and drafts the response and the log entry | Workflow, event-triggered | Customer care desk | Written. Not yet built on a platform |
| | **Store operations** | | | | |
| 5 | [Store Procedures Q&A](agents/store-procedures-qa/README.md) | Answers a store colleague's question from the company's own procedures, with the procedure cited, and says when they are silent | Conversational, answering | Store website | Tested as a draft on a development cluster. Seven of eight tests pass three runs in a row. Not published |
| 6 | [Store Visit Report](agents/store-visit-report/README.md) | Turns an area manager's visit notes and checklist into the report in the company's format, with each finding tied to the standard it rests on | Workflow, event-triggered | Sent to the area manager | Written. Not yet built on a platform |
| 7 | Shift Handover | Drafts the handover note for the next shift from the day's log: what happened, what is open, what needs doing first | Workflow, scheduled | The store's log | Planned |
| 8 | Incident Report | Turns a colleague's account of an accident or an incident into the report form, and lists what the procedure says must happen next | Conversational, acting | Store website | Planned |
| | **Restaurant and franchise operations** | | | | |
| 9 | [Menu and Allergen Q&A](agents/menu-and-allergen-qa/README.md) | Answers a crew member's question about a dish from the company's own allergen matrix, cites the row, and says "not in the matrix, ask the manager" when it is missing | Conversational, answering | Store website | Tested as a draft on a development cluster. All eight tests pass three runs in a row. Not published |
| 10 | [Food Safety Record Check](agents/food-safety-record-check/README.md) | Reads a restaurant's temperature, cleaning and delivery records for a period and lists gaps and readings outside the limits the food safety plan sets | Workflow, scheduled | Food safety desk | Built and tested on a development cluster. Eight of ten tests pass three runs in a row, and the saved drafts were right |
| 11 | [Guest Feedback Analysis](agents/guest-feedback-analysis/README.md) | Groups complaints, reviews and survey comments into themes by restaurant and by period, counts them, and quotes the comments behind each theme | Workflow, scheduled | Sent to operations | Built and tested on a development cluster. The comments that describe harm are listed first, all seven, in every run. The counts by theme vary from run to run |
| 12 | Franchisee Support | Answers a franchisee's question from the operations manual and the brand standards, with the section cited, and says when they are silent | Conversational, answering | Franchisee website | Planned |
| 13 | [Restaurant Performance Review](agents/restaurant-performance-review/README.md) | Sets a restaurant's sales, labour and waste for a period against its plan and its peer group, and lists where it departs, with the figures | Workflow, scheduled | Sent to the area manager | Written. Not yet built on a platform |
| | **Merchandising and pricing** | | | | |
| 14 | Price Optimization | Recommends price changes from demand, stock and published competitor prices, with the reason for each | Workflow, scheduled | Pricing and replenishment desk | Planned |
| 15 | Demand Planning | Sets out market signals and past performance to inform which lines to develop | Autonomous | Sent to the buyer | Planned |
| 16 | Promotion Review | Reviews a finished promotion: what sold, what it displaced, what it cost, against the plan | Workflow, event-triggered | Sent to the buyer | Planned |
| 17 | Range Review Preparation | Prepares the pack for a range review: sales, margin, space and availability by line, with the lines below the company's own thresholds listed | Workflow, scheduled | Sent to the buyer | Planned |
| | **Supply chain and inventory** | | | | |
| 18 | Inventory Forecasting | Forecasts stock needs from sales trends and drafts purchase orders and replenishment plans | Workflow, scheduled | Pricing and replenishment desk | Planned |
| 19 | [Supplier Query](agents/supplier-query/README.md) | Answers a supplier's question about an order, a delivery slot or a payment from the records, and drafts the reply | Workflow, event-triggered | Accounts payable desk | Written. Not yet built on a platform |
| 20 | [Delivery Discrepancy](agents/delivery-discrepancy/README.md) | Sets a delivery note against the purchase order and the invoice, lists what does not match, and drafts the claim | Workflow, event-triggered | Accounts payable desk | Written. Not yet built on a platform |
| 21 | Product Recall Preparation | For a recalled batch, lists the stores and orders that received it and drafts the store instruction and the customer notice | Multi-agent, pipeline | Recall desk | Planned |
| | **Marketing and loyalty** | | | | |
| 22 | Personalisation | Suggests products to each shopper from browsing and purchase history, within rules the team sets | Workflow, API | The shop's website | Planned |
| 23 | Campaign Brief | Drafts a campaign brief in the company's template from the offer, the audience and last year's results | Conversational, acting | Chat | Planned |
| 24 | [Review Reply](agents/review-reply/README.md) | Drafts a reply to a public review in the brand's voice, and marks reviews that describe a safety or legal matter | Workflow, event-triggered | Customer care desk | Written. Not yet built on a platform |
| | **E-commerce and catalogue** | | | | |
| 25 | Product Catalog | Tags product images and drafts product descriptions to the style guide | Workflow, event-triggered | Product data desk | Planned |
| 26 | Product Data Check | Sets a listing against the supplier's specification and lists each attribute that is missing or does not match | Workflow, scheduled | Product data desk | Planned |
| 27 | Search Terms Analysis | Lists what shoppers searched for and did not find, grouped by what they seem to have wanted | Workflow, scheduled | Sent to the e-commerce team | Planned |
| | **Finance and loss prevention** | | | | |
| 28 | [Fraud Prevention](agents/fraud-prevention/README.md) | Flags an order that departs from the pattern and explains why in plain words | Workflow, event-triggered | Loss prevention desk | Written. Not yet built on a platform |
| 29 | [Invoice Matching](agents/invoice-matching/README.md) | Matches a supplier invoice to the order and the receipt and lists what does not agree | Workflow, event-triggered | Accounts payable desk | Built and tested on a development cluster. Every test passes three runs in a row, and each saved draft was right |
| 30 | Shrink Analysis | Sets stock loss by store and by line against the company's own tolerance and lists where it departs, with the figures | Workflow, scheduled | Loss prevention desk | Planned |
| 31 | [Refund and Discount Audit](agents/refund-and-discount-audit/README.md) | Lists refunds, voids and discounts that fall outside the company's own rules for a period | Workflow, scheduled | Loss prevention desk | Written. Not yet built on a platform |
| | **People and compliance** | | | | |
| 32 | [Staff Policy Q&A](agents/staff-policy-qa/README.md) | Answers a colleague's question about HR and workplace policy from the company's own policies, with the policy cited | Conversational, answering | Chat | Tested as a draft on a development cluster. Seven of eight tests pass three runs in a row. Not published |
| 33 | [Training Content](agents/training-content/README.md) | Drafts a short training note or quiz from a procedure, in the company's format | Conversational, answering | Chat | Written. Not yet built on a platform |
| 34 | Roster Check | Checks a draft roster against working time rules and the company's own staffing rules, and lists each breach | Workflow, API | The rostering tool | Planned |
| 35 | [Lease Summary](agents/lease-summary/README.md) | Summarises a store lease: term, rent, review and break dates, repair duties, each with the clause | Conversational, answering | Chat | Written. Not yet built on a platform |
| | **For every colleague** | | | | |
| 36 | [Colleague Assistant](agents/colleague-assistant/README.md) | The one assistant every colleague uses. It passes each request to the specialist built for it and says which one answered | Multi-agent, manager | Chat | Built and tested on a development cluster with three of its six specialists. It called the right specialist every time |

The company's documents the written agents read are in [`policy-library/`](policy-library/README.md).

## The desks

A desk is the shared case desk with a different queue. Each one shows the cases, the agent's findings and draft, approve or send back, and a register of who decided what.

| Desk | Agents behind it | State |
|---|---|---|
| [Food safety desk](desks/food-safety/README.md) | Food Safety Record Check | Written. Run against the stand-in platform on 24 November 2026: twenty scenarios in a headless browser, all pass, and a visual review at desktop and phone width. Not yet run against a real agent |
| Accounts payable desk | Supplier Query, Delivery Discrepancy, Invoice Matching | Planned |
| Customer care desk | Customer Service, Returns Processing, Complaint Handling, Review Reply | Planned |
| Loss prevention desk | Fraud Prevention, Shrink Analysis, Refund and Discount Audit | Planned |
| Pricing and replenishment desk | Price Optimization, Inventory Forecasting | Planned |
| Product data desk | Product Catalog, Product Data Check | Planned |
| Recall desk | Product Recall Preparation | Planned |

## The store website

Some agents are met inside a system the company already runs. [`apps/store-portal/`](apps/store-portal/README.md) is an example: a restaurant crew's website with a chat box that asks an agent on the platform. It runs with a stand-in when no platform is connected.

## How an agent reaches a company's systems

1. **An imported API.** The company gives the platform the OpenAPI file of an API it already runs, and each operation becomes a tool.
2. **An MCP server** from the Catalog, running inside the company's own cluster.
3. **A knowledge source.** Procedures, policies, the allergen matrix and the franchise manual, indexed with each reader's permissions kept.
4. **A file the user uploads** in the conversation.

To try an agent before your own systems are connected, run the invented retailer in [`demo-retailer/`](../demo-retailer/README.md). It offers the first two routes, and [its scenario list](../demo-retailer/SCENARIOS.md) gives the right answer for every case.
