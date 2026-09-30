# Chat tests

Router prompt version: v2.
Model: gemma4:e2b-it-qat; local Ollama only; think=False.
Router input: new user message and previous user message only; no assistant answers.
History limit for rewrite/answers: 6 complete turns. Search answers use ask v2; temperature=0.2 and seed=42.
Routing and rewriting use temperature=0, seed=42, and token limits of 8 and 96 respectively.
Retrieval remains top_k=4 with keyword/semantic weights of 0.5/0.5.

Decisions and outputs are recorded as observed, without answer-correctness judgments or post-generation edits.

## Original script

Date: 2026-09-29T17:38:59-07:00
Command: `wiki chat --script tests/chat-script.txt`

| Turn | Message | Raw routing output | Enforced decision | Rewritten query | Citations | Total time |
|---|---|---|---|---|---|---:|
| 1 | Hi, what can you help me with? | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 25.265 s |
| 2 | What is scope creep? | `SEARCH` | SEARCH | What is scope creep in project management? | [1] | 45.882 s |
| 3 | How can a team prevent it? | `SEARCH` | SEARCH | How can a team prevent scope creep? | [1] | 32.119 s |
| 4 | Thanks, that helps. | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 11.410 s |

### Stage timings

| Turn | Routing | Rewrite | Search | Generation | Total |
|---|---:|---:|---:|---:|---:|
| 1 | 20.723 s | 0.000 s | 0.000 s | 4.540 s | 25.265 s |
| 2 | 4.909 s | 2.732 s | 4.877 s | 33.363 s | 45.882 s |
| 3 | 4.919 s | 1.636 s | 2.475 s | 23.087 s | 32.119 s |
| 4 | 4.927 s | 0.000 s | 0.000 s | 6.483 s | 11.410 s |

Full session transcript: [Original script](chat/20260929-173859-359124.md).

## Held-out script

Date: 2026-09-29T17:40:55-07:00
Command: `wiki chat --script tests/chat-script-heldout.txt`

| Turn | Message | Raw routing output | Enforced decision | Rewritten query | Citations | Total time |
|---|---|---|---|---|---|---:|
| 1 | Good morning! | `NO_SEARCH` | NO_SEARCH | Not applicable | None | 10.609 s |
| 2 | What does a responsibility matrix show? | `SEARCH` | SEARCH | responsibility matrix meaning in project management | [1] | 43.067 s |
| 3 | Who should be on it? | `SEARCH` | SEARCH | Who should be on the responsibility matrix? | [1] | 44.734 s |

### Stage timings

| Turn | Routing | Rewrite | Search | Generation | Total |
|---|---:|---:|---:|---:|---:|
| 1 | 6.847 s | 0.000 s | 0.000 s | 3.761 s | 10.609 s |
| 2 | 5.693 s | 2.570 s | 2.495 s | 32.307 s | 43.067 s |
| 3 | 4.709 s | 2.293 s | 2.717 s | 35.013 s | 44.734 s |

Full session transcript: [Held-out script](chat/20260929-174055-698358.md).

## Citation checks and run warnings

- Citation warnings: none on all seven turns.
- Run warnings and runtime errors: none.
- Original-script turns 2 and 3 cite [1]: vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md, section 3: Statement of work: detailed boundaries.
- Held-out turns 2 and 3 cite [1]: vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md, section 4: Responsibilities, priorities, and complexity.
- Other turns used no retrieval and had no cited sources.

Timings include any model loading. Total excludes transcript saving and final output printing.

## Verification

All 21 unit tests passed. V1 router prompt, summary, and transcript are preserved unchanged.
Hash checks confirmed search, ask v2, existing prompts, the vault, data, test plan, and original test script are unchanged. Rewrite and answer-generation code and every pre-existing configuration value are unchanged.
