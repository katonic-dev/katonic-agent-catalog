# Policy library of an invented bank

Meridian Trust Bank does not exist. These policies were written so that agents in this pack have something to read, cite and compare against. Each one says on its first line that the bank is invented.

| File | Policy |
|---|---|
| `MTB-POL-014-ai-and-model-risk-policy.md` | Artificial intelligence and model risk |
| `MTB-POL-021-customer-information-and-data-sharing-policy.md` | Customer information and data sharing |
| `MTB-POL-033-technology-risk-and-outsourcing-policy.md` | Technology risk and outsourcing |
| `MTB-STD-041-third-party-security-and-resilience-standard.md` | Third-party security and resilience: what the bank requires of a supplier |

The three policies also ship with the regulatory change desk in [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk). The standard is what the Third-Party Risk Assessment agent marks a supplier against.

## How to use them

In Knowledge, choose Connect Source, then File Upload, and add the files. Indexing needs an embedding model.

One thing is left out on purpose, so that an agent can be tested on what it does when the documents are silent: the retention schedule that policy MTB-POL-021 points to in clause 6.2 is not in the library.
