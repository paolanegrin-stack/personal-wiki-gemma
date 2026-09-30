# Offline evidence report

Paola reports running these commands with WiFi off, airplane mode enabled, no phone hotspot, and a fresh CLI process per command on 2026-09-29, approximately 22:10–22:30 (local time, UTC−07:00). Saved run timestamps and matching screenshots identify the evidence below. This report reviews those existing runs; it does not rerun them or independently measure network traffic.

The supplied screenshot window was described as 22:12–22:29; the status screenshot clock shows 22:11. Both fall within the approximate run window. `help.png` was captured online afterward and is excluded from offline evidence.

## Status, ingest, and search

| Command | Evidence | Timing | Citations / result | Screenshots |
|---|---|---|---|---|
| `wiki status` | Screenshot only for the offline run | 15.23 s generation, including loading if needed | Ollama 0.34.4; both models installed; “The local wiki is ready.”; no citations | [offline-01-status](../screenshots/offline-01-status.png) |
| `wiki ingest` | [Log](ingest-log.md), 22:12:52 | 13.66 s total | 16 chunks and embeddings rebuilt; 12 existing notes and index skipped; no generated citations; 0 errors | [offline-02-ingest](../screenshots/offline-02-ingest.png) |
| `wiki search "What should a project charter include?" --save` | [Results](search/20260929-221404-264046-what-should-a-project-charter-include.md), 22:14:04 | 3.742 s search | Ranked sections: 03 §2; 01 §4; 03 §3; 01 §1. Result IDs are not generated answer citations. | [offline-03-search-a](../screenshots/offline-03-search-a.png), [offline-03-search-b](../screenshots/offline-03-search-b.png) |

Source key: [01](../vault/raw/01_Project_Management_Introduction_Summary.md); [02](../vault/raw/02_Project_Selection_Methods_Summary.md); [03](../vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md).

## Ask runs

All use ask v2, gemma4:e2b-it-qat, embeddinggemma, think=False, temperature 0.2, seed 42, top_k=4, and unchanged 0.5/0.5 weights. Citation warnings, run warnings, and errors are None in all four files.

### Q1

Command: `wiki ask "What should a project charter include?"`

Record: [20260929-221632-664236-what-should-a-project-charter-include.md](ask/20260929-221632-664236-what-should-a-project-charter-include.md). Started: 2026-09-29T22:15:40-07:00.

Search: 2.333 s; Generation: 49.330 s; Total: 51.913 s

Citations used: [1]

- [1] -> vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md, section 2: 2. Project charter: authority and direction

Screenshots: [offline-04-ask-q1](../screenshots/offline-04-ask-q1.png).

### Q2

Command: `wiki ask "How can a company decide which projects to fund when it has more ideas than money?"`

Record: [20260929-221827-001385-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md](ask/20260929-221827-001385-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md). Started: 2026-09-29T22:17:26-07:00.

Search: 2.522 s; Generation: 57.535 s; Total: 60.355 s

Citations used: [2], [1], [3], [4]

- [2] -> vault/raw/02_Project_Selection_Methods_Summary.md, section 1: 1. The selection problem
- [1] -> vault/raw/02_Project_Selection_Methods_Summary.md, section 5: 5. A practical portfolio process
- [3] -> vault/raw/02_Project_Selection_Methods_Summary.md, section 2: 2. Classify projects before comparing them
- [4] -> vault/raw/02_Project_Selection_Methods_Summary.md, section 4: 4. Pan Europa Foods: a portfolio decision

Screenshots: [offline-05-ask-q2-a](../screenshots/offline-05-ask-q2-a.png), [offline-05-ask-q2-b](../screenshots/offline-05-ask-q2-b.png).

### Q3

Command: `wiki ask "How should a project manager balance scope, time, and cost?"`

Record: [20260929-222017-030884-how-should-a-project-manager-balance-scope-time-and-cost.md](ask/20260929-222017-030884-how-should-a-project-manager-balance-scope-time-and-cost.md). Started: 2026-09-29T22:19:46-07:00.

Search: 2.482 s; Generation: 28.005 s; Total: 30.754 s

Citations used: [2], [1]

- [2] -> vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md, section 4: 4. Responsibilities, priorities, and complexity
- [1] -> vault/raw/01_Project_Management_Introduction_Summary.md, section 3: 3. How to judge success

Screenshots: [offline-06-ask-q3](../screenshots/offline-06-ask-q3.png).

### Q4

Command: `wiki ask "How does agile project management differ from traditional approaches?"`

Record: [20260929-222130-739645-how-does-agile-project-management-differ-from-traditional-approaches.md](ask/20260929-222130-739645-how-does-agile-project-management-differ-from-traditional-approaches.md). Started: 2026-09-29T22:21:03-07:00.

Search: 2.307 s; Generation: 24.753 s; Total: 27.347 s

Citations used: None

- None

Screenshots: [offline-07-ask-q4](../screenshots/offline-07-ask-q4.png).

## Chat runs

Both use router v2 and ask-v2 search answers. Citation warnings, run warnings, and errors are None on all seven turns.

### Original script

Command: `wiki chat --script tests/chat-script.txt`

Record: [20260929-222301-926620.md](chat/20260929-222301-926620.md). Started: 2026-09-29T22:23:01-07:00.

Screenshots: [offline-08-chat-a](../screenshots/offline-08-chat-a.png), [offline-08-chat-b](../screenshots/offline-08-chat-b.png).

| Turn / message | Raw route / decision | Rewritten query | Citations | Routing / rewrite / search / generation / total (s) |
|---|---|---|---|---|
| 1. Hi, what can you help me with? | "NO_SEARCH" / NO_SEARCH | Not applicable | None | 6.774 / 0.000 / 0.000 / 4.147 / 10.921 |
| 2. What is scope creep? | "SEARCH" / SEARCH | What is scope creep in project management? | [1] | 4.623 / 2.639 / 2.478 / 26.647 / 36.389 |
| 3. How can a team prevent it? | "SEARCH" / SEARCH | How can a team prevent scope creep? | [1] | 4.670 / 1.550 / 2.428 / 28.772 / 37.421 |
| 4. Thanks, that helps. | "NO_SEARCH" / NO_SEARCH | Not applicable | None | 4.827 / 0.000 / 0.000 / 6.035 / 10.863 |

Cited [1] on turns 2–3 maps to 03 §3: Statement of work: detailed boundaries. Social turns have no citations. Full retrieved passages and source filenames are in the transcript.

### Held-out script

Command: `wiki chat --script tests/chat-script-heldout.txt`

Record: [20260929-222733-700496.md](chat/20260929-222733-700496.md). Started: 2026-09-29T22:27:33-07:00.

Screenshots: [offline-09-chat-heldout-a](../screenshots/offline-09-chat-heldout-a.png), [offline-09-chat-heldout-b](../screenshots/offline-09-chat-heldout-b.png).

| Turn / message | Raw route / decision | Rewritten query | Citations | Routing / rewrite / search / generation / total (s) |
|---|---|---|---|---|
| 1. Good morning! | "NO_SEARCH" / NO_SEARCH | Not applicable | None | 6.678 / 0.000 / 0.000 / 3.561 / 10.240 |
| 2. What does a responsibility matrix show? | "SEARCH" / SEARCH | responsibility matrix meaning in project management | [1] | 4.627 / 2.296 / 2.437 / 28.719 / 38.081 |
| 3. Who should be on it? | "SEARCH" / SEARCH | Who should be on the responsibility matrix? | [1] | 4.633 / 2.960 / 2.427 / 30.933 / 40.955 |

Cited [1] on turns 2–3 maps to 03 §4: Responsibilities, priorities, and complexity. Social turns have no citations. Full retrieved passages and source filenames are in the transcript.

## Exact answer-text comparisons

Ask baseline: [ask-tests-v2.md](ask-tests-v2.md). Chat baseline: transcripts linked from [chat-tests-v2.md](chat-tests-v2.md), which is a routing/timing summary rather than an answer listing. Comparisons extract the Answer blocks, normalize file line endings, and remove only surrounding Markdown separator whitespace; wording, punctuation, citations, and internal whitespace are compared exactly. Whole files differ in timestamps and timings.

| Answer | Identical to v2? | Baseline | Offline |
|---|---|---|---|
| Ask Q1 | Yes | [V2](ask/20260929-171254-119566-what-should-a-project-charter-include.md) | [Offline](ask/20260929-221632-664236-what-should-a-project-charter-include.md) |
| Ask Q2 | Yes | [V2](ask/20260929-171356-520531-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md) | [Offline](ask/20260929-221827-001385-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md) |
| Ask Q3 | Yes | [V2](ask/20260929-171434-605304-how-should-a-project-manager-balance-scope-time-and-cost.md) | [Offline](ask/20260929-222017-030884-how-should-a-project-manager-balance-scope-time-and-cost.md) |
| Ask Q4 | Yes | [V2](ask/20260929-171505-908648-how-does-agile-project-management-differ-from-traditional-approaches.md) | [Offline](ask/20260929-222130-739645-how-does-agile-project-management-differ-from-traditional-approaches.md) |
| Chat original, turn 1 | Yes | [V2](chat/20260929-173859-359124.md) | [Offline](chat/20260929-222301-926620.md) |
| Chat original, turn 2 | Yes | [V2](chat/20260929-173859-359124.md) | [Offline](chat/20260929-222301-926620.md) |
| Chat original, turn 3 | Yes | [V2](chat/20260929-173859-359124.md) | [Offline](chat/20260929-222301-926620.md) |
| Chat original, turn 4 | Yes | [V2](chat/20260929-173859-359124.md) | [Offline](chat/20260929-222301-926620.md) |
| Chat held-out, turn 1 | Yes | [V2](chat/20260929-174055-698358.md) | [Offline](chat/20260929-222733-700496.md) |
| Chat held-out, turn 2 | No | [V2](chat/20260929-174055-698358.md) | [Offline](chat/20260929-222733-700496.md) |
| Chat held-out, turn 3 | Yes | [V2](chat/20260929-174055-698358.md) | [Offline](chat/20260929-222733-700496.md) |

### Chat held-out, turn 2: full differing answers

**V2**

A responsibility matrix lists activities against the people involved and clarifies who does the work, who supports it, where teams must coordinate, and what authority each person has [1]. The illustrated market-research matrix marks "R = responsible" and "S = supports/assists" [1].

**Offline**

A responsibility matrix lists activities against the people involved and clarifies who does the work, who supports it, where teams must coordinate, and what authority each person has [1]. The illustrated market-research matrix marks "R = responsible" and "S = supports/assists" [1]. A RACI matrix is another way to clarify roles, but the detailed example in the slides uses R and S rather than all four RACI labels [1].

All four ask answers and six of seven chat answers are identical. The held-out turn-2 offline answer adds a sentence about RACI. This is a text comparison, not an answer-correctness assessment.

## Timing and preservation notes

Search timing excludes startup and saving. Ask totals include retrieval, prompt assembly, generation, and citation checks, excluding saving/printing. Chat totals include routing, rewriting, retrieval, and answering, excluding transcript saving/printing. Model timings may include loading. A pure first-load duration was not recorded: [TODO: separate model-load measurement, if required].

No existing evidence, code, prompts, tests, or vault files were edited to produce this report. The initial ingest record is preserved separately in [ingest-log-initial.md](ingest-log-initial.md); the offline run had already replaced the current ingest log.
