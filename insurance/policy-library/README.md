# Policy library (invented)

The policy wordings of Thornmere Mutual Insurance, an invented insurer, as documents. Nothing here is a contract of insurance.

| Wording | Files |
|---|---|
| TMI-MOT-01, Private Motor Policy Wording, version 3 | [Markdown](TMI-MOT-01-private-motor-policy-wording.md), [PDF](TMI-MOT-01-private-motor-policy-wording.pdf) |
| TMI-HOM-02, Home Buildings and Contents Policy Wording, version 2 | [Markdown](TMI-HOM-02-home-buildings-and-contents-policy-wording.md), [PDF](TMI-HOM-02-home-buildings-and-contents-policy-wording.pdf) |

## Why they are here

The invented insurer serves each wording as numbered clauses through its policy system, so that an agent can be tried before any document store is connected. A real insurer keeps its wordings as documents. These files are the same wordings as documents, for trying an agent with the wording in a knowledge source.

The files are written from the insurer's own data by [`demo-insurer/tools/make_wording_documents.py`](../../demo-insurer/tools/make_wording_documents.py), and a test keeps the Markdown in step with the data. Do not edit them by hand.

Both wordings go into one knowledge source on purpose. A question about a motor claim must then be answered from the motor wording and not from the home wording, although the two share clause numbers.
