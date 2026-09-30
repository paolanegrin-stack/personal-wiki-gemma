# Chat tests

Date: 2026-09-29T17:29:41-07:00

Command: `wiki chat --script tests/chat-script.txt`
Model: gemma4:e2b-it-qat; local Ollama only; think=False.
History limit: 6 complete user/assistant turns. Search answers use ask v2; answer temperature=0.2 and seed=42.
Routing and rewriting use temperature=0, seed=42, and token limits of 8 and 96 respectively.
Retrieval remains top_k=4 with keyword/semantic weights of 0.5/0.5.

Model decisions and outputs are recorded as observed, without correctness judgments or post-generation edits.

| Turn | Message | Raw routing output | Enforced decision | Rewritten query | Citations | Total time |
|---|---|---|---|---|---|---:|
| 1 | Hi, what can you help me with? | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 20.745 s |
| 2 | What is scope creep? | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 2.635 s |
| 3 | How can a team prevent it? | `I don't have enough evidence in` | SEARCH | How can a team prevent scope creep? | [1] | 43.935 s |
| 4 | Thanks, that helps. | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 8.195 s |

## Stage timings

| Turn | Routing | Rewrite | Search | Generation | Total |
|---|---:|---:|---:|---:|---:|
| 1 | 16.430 s | 0.000 s | 0.000 s | 4.314 s | 20.745 s |
| 2 | 0.974 s | 0.000 s | 0.000 s | 1.660 s | 2.635 s |
| 3 | 1.451 s | 3.579 s | 5.803 s | 33.101 s | 43.935 s |
| 4 | 1.311 s | 0.000 s | 0.000 s | 6.883 s | 8.195 s |

Timings include any model loading. Total excludes transcript saving and final output printing.

## Citation checks and run warnings

- Citation warnings: none on all four turns.
- Turn 3 returned an invalid routing label (`I don't have enough evidence in`); the parser fell back to SEARCH as configured.
- Turn 3 citation [1] maps to vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md, section 3: Statement of work: detailed boundaries.
- Turns 1, 2, and 4 used no retrieval and had no cited sources.
- Runtime errors: none.
- History supplied to turns 1–4: 0, 1, 2, and 3 prior complete turns.

## Transcript and verification

Full answers, retrieved passages, routing output, and citation checks: [Session transcript](chat/20260929-172941-757280.md).

All 20 unit tests passed, including routing parsing, history limits, command handling, and retrieval branching.
Hash checks confirmed search code, ask code, prompt files, the vault, retrieval data, the test plan, and existing ask run files are unchanged. All pre-existing configuration values are unchanged.
