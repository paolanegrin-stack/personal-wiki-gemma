# Personal Wiki CLI — Fundamentals of AI, Assignment 4

## 1. Overview

A personal study wiki for Project Management classes 1–3.<br>
A simple Python harness uses local Ollama for ingestion, hybrid search, cited answers, and conversation.<br>
Installed models run offline: no cloud API, hosted embeddings, LangChain, or LlamaIndex.

**Evidence at a glance:** [Ask cards](#7-evidence--ask-mode) · [Search checks](outputs/search-tests.md) · [Chat checks](outputs/chat-tests-v2.md) · [Offline report](outputs/offline-tests.md) · Obsidian [note](screenshots/obsidian-note.png), [index](screenshots/obsidian-index.png), [graph](screenshots/obsidian-graph.png).

## 2. Purpose and sources

The wiki turns my own English class notes into 12 connected study pages. Retrieval always searches raw-source sections, not generated wiki notes or the test plan. Source IDs 01, 02, and 03 below mean these exact files.

| ID / raw file | Topics and numbered sections |
|---|---|
| 01: [01_Project_Management_Introduction_Summary.md](vault/raw/01_Project_Management_Introduction_Summary.md) | 6 sections: 1. What is a project?; 2. Why project management matters; 3. How to judge success; 4. The project life cycle and core tools; 5. Link projects to strategy; 6. Practical principles |
| 02: [02_Project_Selection_Methods_Summary.md](vault/raw/02_Project_Selection_Methods_Summary.md) | 5 sections: 1. The selection problem; 2. Classify projects before comparing them; 3. Selection methods; 4. Pan Europa Foods: a portfolio decision; 5. A practical portfolio process |
| 03: [03_Project_Initiation_and_Stakeholders_Summary.md](vault/raw/03_Project_Initiation_and_Stakeholders_Summary.md) | 5 sections: 1. Start with a clear definition; 2. Project charter: authority and direction; 3. Statement of work: detailed boundaries; 4. Responsibilities, priorities, and complexity; 5. Stakeholder management is continuous |

The explicit [wiki plan](wiki_cli/wiki_plan.py) maps each note to selected raw sections. Gemma receives only those sections and [wiki instructions](prompts/wiki-instructions.md); Python renders validated source IDs as YAML frontmatter and a source reference after each key point. Approved wikilinks connect the notes.

Trace: open [Project Success Criteria](vault/wiki/Concepts/Project%20Success%20Criteria.md), follow its related [[Project Definition]] to [Project Definition](vault/wiki/Concepts/Project%20Definition.md), then return to Success Criteria and follow its source reference to [01, section 3: How to judge success](vault/raw/01_Project_Management_Introduction_Summary.md#3-how-to-judge-success). Project Definition itself cites sections 1–2; the section-3 provenance belongs to Success Criteria.

## 3. Setup and device

| Item | Recorded setup |
|---|---|
| OS / CPU | Windows 11 Pro; Intel Core i5-1335U, 13th generation, 1.30 GHz |
| RAM / graphics | 16 GB DDR4 3200 MT/s, 15.7 GB usable; Intel Iris Xe integrated GPU, 128 MB dedicated, no discrete VRAM |
| Normal-app RAM / disk | 10.0 GB in use, 5.6 GB available ([Task Manager](screenshots/device-memory.png)); 477 GB disk, approximately 319 GB free |
| Runtime | Python 3.13; Git 2.55; Ollama 0.34.4 at `http://localhost:11434` |
| Dependencies | [requirements.txt](requirements.txt): `ollama>=0.6.0,<1`, `rank-bm25==0.2.2`, `numpy>=2.2,<3` |

Device details come from Windows Settings > System > About and Task Manager; the memory screenshot corroborates RAM use/capacity/speed. It shows normal apps, not an isolated model-memory benchmark.

Generation uses [Gemma 4](https://ollama.com/library/gemma4), specifically [gemma4:e2b-it-qat](https://ollama.com/library/gemma4:e2b-it-qat): E2B instruction-tuned, quantization-aware trained 4-bit, 4.3 GB, ID `07ea59a47401`. Embeddings use [embeddinggemma](https://ollama.com/library/embeddinggemma), 621 MB. Weights are installed separately.

Choice at setup: E2B is the smallest effective-size Gemma 4 option; I selected the lightest E2B QAT build (4.3 GB versus the default Q4_K_M build at 7.2 GB) to leave room for Windows, apps, and retrieval within 16 GB. The saved runs demonstrate CPU execution. E4B was expected to be slower on this CPU, but was not benchmarked. `think=False` reduces CPU work spent on thinking.

**One-time online installation (PowerShell):** replace the placeholder before running the clone command; no remote is currently configured.

```powershell
git clone "[TODO: repository clone URL]" C:\Users\pao_n\projects\personal-wiki
cd C:\Users\pao_n\projects\personal-wiki
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
ollama pull gemma4:e2b-it-qat
ollama pull embeddinggemma
.\.venv\Scripts\Activate.ps1
```

Start the local Ollama app (or `ollama serve` in another terminal). If activation is blocked, optionally allow scripts for this terminal only with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then activate again. Alternatively use `.\.venv\Scripts\wiki.exe` in place of `wiki`, with no policy change.

**Launch after installation; these commands work offline:**

```powershell
wiki --help
wiki status
wiki ingest
wiki search "What should a project charter include?" --save
wiki ask "What should a project charter include?"
wiki chat
wiki chat --script tests/chat-script.txt
wiki chat --script tests/chat-script-heldout.txt
```

Exit interactive chat with `/quit` before running the scripts. The [offline checklist](tests/offline-run.md) includes all four ask questions.

**Measured performance** (seconds unless stated; individual observations, not a benchmark):

| Operation | Recorded result | Evidence |
|---|---|---|
| Loaded model memory | Gemma 4.0 GB; EmbeddingGemma 680 MB; both 100% CPU | [ollama ps](outputs/memory.txt) |
| Initial ingest / offline re-ingest | 733.23 / 13.66; 12 notes generated initially, all skipped offline | [Initial](outputs/ingest-log-initial.md), [offline](outputs/ingest-log.md) |
| Search Q1–Q4 / offline Q1 | 2.404, 2.394, 2.381, 2.368 / 3.742 | [Search tests](outputs/search-tests.md), [offline report](outputs/offline-tests.md) |
| Ask generation Q1–Q4, v2 | 60.594, 57.881, 33.725, 26.944 | [Ask v2](outputs/ask-tests-v2.md) |
| Ask generation Q1–Q4, offline | 49.330, 57.535, 28.005, 24.753 | [Offline report](outputs/offline-tests.md) |
| Status test, initial / offline | 17.22 / 15.23; includes model loading if needed | [Initial](outputs/status.txt), [offline screenshot](screenshots/offline-01-status.png) |

Status measures a short generation plus any loading.

| Chat turn | V2 routing / total | Offline routing / total |
|---|---:|---:|
| Original 1 | 20.723 / 25.265 | 6.774 / 10.921 |
| Original 2 | 4.909 / 45.882 | 4.623 / 36.389 |
| Original 3 | 4.919 / 32.119 | 4.670 / 37.421 |
| Original 4 | 4.927 / 11.410 | 4.827 / 10.863 |
| Held-out 1 | 6.847 / 10.609 | 6.678 / 10.240 |
| Held-out 2 | 5.693 / 43.067 | 4.627 / 38.081 |
| Held-out 3 | 4.709 / 44.734 | 4.633 / 40.955 |

Chat timing sources: [v2 stage timings](outputs/chat-tests-v2.md), [offline stage timings](outputs/offline-tests.md). Totals exclude saving/printing; model timings can include loading.

## 4. Architecture

| Term | Role here |
|---|---|
| Model | Gemma generates text; EmbeddingGemma converts text to vectors. |
| Retrieval tool | Local BM25 and cosine ranking return raw-source passages. |
| RAG workflow | Retrieve evidence, add it to the prompt, generate a cited answer. |
| Harness | My Python control code manages commands, prompts, routing, context, checks, errors, and evidence files. |
| CLI | The `wiki` terminal entry point installed by [pyproject.toml](pyproject.toml). |

An ask request follows this path:

1. [cli.py](wiki_cli/cli.py) `main()` parses `wiki ask "..."` and dispatches to [ask.py](wiki_cli/ask.py) `ask()` → `run_ask()`.
2. [search.py](wiki_cli/search.py) `retrieve()` loads chunks/embeddings and ranks BM25 plus query-vector cosine scores.
3. `ask.build_prompt()` combines [persona](prompts/persona.md), [ask-v2 rules](prompts/ask-v2.md), four numbered passages with source headings, and the question.
4. `run_ask()` calls local `ollama.Client.generate()`; `check_citations()` maps numbers to passages and flags invalid numbers or an uncited non-refusal.
5. `save_run()` writes a full evidence card, then `print_report()` prints answer, sources, warnings, timing, and saved path. Saving precedes printing in the implementation.

Ask is stateless and never uses chat history. [chat.py](wiki_cli/chat.py) retains six complete turns for rewriting/answering. Router v2 receives only the current and previous user messages. SEARCH rewrites a standalone query and calls the same retriever and ask-v2 rules; NO_SEARCH handles greetings, thanks, or conversation questions briefly. Invalid routing output falls back to SEARCH. `/sources`, `/reset`, `/help`, and `/quit` manage the session; transcripts preserve all recorded turns.

CLI error handling reports local Ollama connection/model failures, missing retrieval data/prompts/scripts, and file errors without an ordinary stack trace. Ask and chat retain error records when outputs are writable. Status explicitly checks both installed models. Calls use localhost with proxy environment settings disabled; there are no runtime downloads or remote inference calls.

## 5. Design choices

- One `##` section per chunk gives 16 passages and keeps readable source boundaries. Embedding documents use `title: ... | text: ...`; queries use `task: search result | query: ...`.
- Lowercase alphanumeric BM25 tokens and cosine similarity are independently min-max normalized; constant scores become zero. Final score is `0.5 * keyword + 0.5 * semantic`, with `top_k=4`. Scores are rankings, not confidence.
- Research/answer rules in [ask-v2.md](prompts/ask-v2.md) are separate from [persona.md](prompts/persona.md). [config.py](wiki_cli/config.py) sets context 8192, six chat turns, answer temperature 0.2, seed 42, and thinking off; router temperature is 0.
- Descriptive note names live in Concepts, Selection, Initiation, and Cases. Frontmatter identifies sources; inline `(source: file, section)` references lead back to readable raw pages. Only approved note names become wikilinks.
- Without `--force`, ingest reads raw files, rebuilds chunks/embeddings in `data/`, skips existing notes completely (including link cleanup), preserves existing `vault/index.md`, and rewrites the ingest log. Missing notes/index can be created. Link checks apply to newly generated notes; unknown, self, and duplicate related links are removed and logged. `--force` replaces reviewed notes/index. The offline run shows all 12 notes and index skipped.

## 6. Wiki review process

Gemma generated 12 notes. Codex proposed and applied corrections across **10 notes**, and I verified each against the raw sources; the [before/after report](outputs/review-edits.md) records multiple edits within those notes. These were editorial corrections outside the ingest pipeline. I then made one manual Obsidian edit: removing the off-topic complexity bullet from Project Success Criteria, because it belonged in Project Complexity.

One unapproved `[[Project Scope Statement]]` link was removed automatically. Observed overgeneralization included NPV missing “subtract the investment,” portfolios using “and operations” instead of “sometimes operations,” and stakeholder satisfaction presented as “the” measure rather than “one” measure. The report preserves the exact corrections.

Obsidian evidence: [note](screenshots/obsidian-note.png), [index](screenshots/obsidian-index.png), [graph](screenshots/obsidian-graph.png). The graph uses `-path:raw` to hide raw-source pages. My observation: Project Definition and Project Selection Methods are link hubs because Gemma often links to general notes.

In Obsidian, index and related-note links resolve to existing notes (see obsidian-index.png and obsidian-note.png); no unresolved links remain after the link check.

## 7. Evidence — ask mode

Expected evidence comes from the unchanged [test plan](tests/test-plan.md). Retrieval lists below are ranked; IDs refer to the source catalog. The following grades are **my evaluation of the saved v2 answers**, not the automatic citation checker. All four offline ask answers are identical to v2.

### Q1. What should a project charter include?

**Type:** Direct, one source. **Expected evidence:** 03 §2.<br>
**Retrieved (file ID + section):** 03 §2; 01 §4; 03 §3; 01 §1.<br>
**Actual v2 answer and full passages:** [evidence card](outputs/ask/20260929-171254-119566-what-should-a-project-charter-include.md). **Citations:** [1]. Citation warnings: None.

Q1 — Correct. All six items match class 3 section 2 and the citation is right. Minor: it still merges "milestones and timeline" with "effects on existing systems or teams" using "including"; it does not mention SMART objectives.

### Q2. How can a company decide which projects to fund when it has more ideas than money?

**Type:** Different wording from the source. **Expected evidence:** 02 §§1, 3, 5.<br>
**Retrieved (file ID + section):** 02 §5; 02 §1; 02 §2; 02 §4.<br>
**Actual v2 answer and full passages:** [evidence card](outputs/ask/20260929-171356-520531-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md). **Citations:** [2], [1], [3], [4]. Citation warnings: None.

Q2 — Partial. Every claim is supported and correctly cited, and v2 uses all four retrieved passages. Missing: the weighted scoring model and the NPV definition, because retrieval never returned class 2 section 3 (predicted in the test plan). It also presents the Pan Europa Foods committee lesson as a general rule without naming the case.

### Q3. How should a project manager balance scope, time, and cost?

**Type:** Connects two sources. **Expected evidence:** 01 §3 and 03 §4.<br>
**Retrieved (file ID + section):** 01 §3; 03 §4; 03 §1; 01 §6.<br>
**Actual v2 answer and full passages:** [evidence card](outputs/ask/20260929-171434-605304-how-should-a-project-manager-balance-scope-time-and-cost.md). **Citations:** [2], [1]. Citation warnings: None.

Q3 — Correct (v2). Combines class 3 section 4 (priority matrix: constrain/enhance/accept) with class 1 section 3 (adding features needs more time or money). In v1 it used only class 3.

### Q4. How does agile project management differ from traditional approaches?

**Type:** Unsupported. **Expected evidence:** None; the notes do not mention agile.<br>
**Retrieved (file ID + section):** 01 §2; 03 §4; 01 §5; 03 §1.<br>
**Actual v2 answer and full passages:** [evidence card](outputs/ask/20260929-171505-908648-how-does-agile-project-management-differ-from-traditional-approaches.md). **Citations:** None. Citation warnings: None.

Q4 — Correct. Returned exactly "I don't have enough evidence in my notes to answer this." although the model has general knowledge of agile. No retrieved passage mentions agile.

**Instruction-only iteration:** [full v1/v2 comparison](outputs/ask-iteration.md). Retrieval and generation settings stayed fixed. Effects and aggregate grades below are my review.

| Added rule | Target v1 failure | Observed v2 effect |
|---|---|---|
| Read all passages; combine relevant evidence | Q3 used only 03 §4 despite retrieving 01 §3 | Worked for Q3; improved Q2 coverage |
| Preserve case/example scope | Q2 generalized the Pan Europa Foods committee lesson | No visible effect |
| Keep source items separate | Q1 merged charter items using “including” | Fixed 1 of 2 merges |

My grades changed from **v1: 2 correct / 2 partial** to **v2: 3 correct / 1 partial**. Q2/Q3 became longer; generation was slower for all four in these runs: v1 53.041 / 47.360 / 27.124 / 26.748 s → v2 60.594 / 57.881 / 33.725 / 26.944 s. There was one run per version, so timing differences are not a controlled benchmark.

## 8. Evidence — search and chat checks

[Search test record](outputs/search-tests.md), with unchanged weights and expected evidence:

| Question | Top four source sections, ranked | All expected evidence? | Seconds |
|---|---|---|---:|
| Q1 | 03 §2; 01 §4; 03 §3; 01 §1 | Yes | 2.404 |
| Q2 | 02 §5; 02 §1; 02 §2; 02 §4 | No | 2.394 |
| Q3 | 01 §3; 03 §4; 03 §1; 01 §6 | Yes | 2.381 |
| Q4 | 01 §2; 03 §4; 01 §5; 03 §1 | No | 2.368 |

Q2 missed 02 §3. Q4 still returns four sections; search ranks passages, while ask must decide that evidence is insufficient.

[Router v1](outputs/chat-tests-v1.md) incorrectly chose NO_SEARCH for “What is scope creep?” Its exact answer was:

> I don't have enough evidence in my notes.

Turn 3 returned the invalid label `I don't have enough evidence in`; code searched only through the fallback. Assistant-history contamination was the suspected cause: v1 saw assistant answers. [Router v2](prompts/router-v2.md) uses only current/previous user messages and adds few-shot examples. Both changed together, so this does not isolate the cause experimentally.

Under my expected routing labels, [v2 achieved 7/7 correct routes](outputs/chat-tests-v2.md), including the three-message held-out script. Follow-up rewriting resolved “prevent it” to “prevent scope creep” and “on it” to “responsibility matrix.” Excluding first-turn loading, original-script routing rose from 0.974–1.451 s in v1 to 4.909–4.927 s in v2 (roughly 1 → 5 s). See the [routing iteration](outputs/chat-iteration.md).

## 9. Offline demonstration

I ran the [checklist](tests/offline-run.md) with airplane mode on, WiFi off, no phone hotspot, and a fresh CLI process per command on September 29, approximately 22:10–22:30. Screenshots show airplane mode on; saved files record each run.

The [offline report](outputs/offline-tests.md) links every run, stage timing, citation, and exact answer comparison. All four ask answers match v2; six of seven chat answers match. Held-out turn 2 adds a RACI sentence; both full versions are shown without grading.

| Offline command | Screenshots |
|---|---|
| `wiki status` | [offline-01-status](screenshots/offline-01-status.png) |
| `wiki ingest` | [offline-02-ingest](screenshots/offline-02-ingest.png) |
| `wiki search "What should a project charter include?" --save` | [offline-03-search-a](screenshots/offline-03-search-a.png), [offline-03-search-b](screenshots/offline-03-search-b.png) |
| `wiki ask "What should a project charter include?"` | [offline-04-ask-q1](screenshots/offline-04-ask-q1.png) |
| `wiki ask "How can a company decide which projects to fund when it has more ideas than money?"` | [offline-05-ask-q2-a](screenshots/offline-05-ask-q2-a.png), [offline-05-ask-q2-b](screenshots/offline-05-ask-q2-b.png) |
| `wiki ask "How should a project manager balance scope, time, and cost?"` | [offline-06-ask-q3](screenshots/offline-06-ask-q3.png) |
| `wiki ask "How does agile project management differ from traditional approaches?"` | [offline-07-ask-q4](screenshots/offline-07-ask-q4.png) |
| `wiki chat --script tests/chat-script.txt` | [offline-08-chat-a](screenshots/offline-08-chat-a.png), [offline-08-chat-b](screenshots/offline-08-chat-b.png) |
| `wiki chat --script tests/chat-script-heldout.txt` | [offline-09-chat-heldout-a](screenshots/offline-09-chat-heldout-a.png), [offline-09-chat-heldout-b](screenshots/offline-09-chat-heldout-b.png) |

[help.png](screenshots/help.png) was captured **online afterward** and is not offline evidence. The status screenshot clock shows 22:11; the other reported screenshots span approximately 22:12–22:29.

## 10. Reflection

The main limitation is Q2 retrieval: 02 §3 never reached the top four for a question without “selection” or “methods.” A possible cause is its long section mixing several methods, diluting keyword and embedding relevance; this is a hypothesis. Next I would split long sections by paragraph or method and rerun all four tests with the same weights.

The small model can overgeneralize, and valid citation numbers do not prove supported claims. There is only one run per prompt version and a small held-out chat set. Offline ingest rebuilt retrieval data from existing sources and skipped reviewed notes; it did not demonstrate new note generation offline. Fixed seeds did not make every repeated chat answer identical.

## 11. AI assistance disclosure

Code written with OpenAI Codex under my direction; planning and review guided with Claude; all results, grades, and verification by me (Paola). Codex helped organize this evidence and compare saved text; my grades are explicitly attributed above.

## 12. Repository structure

```text
personal-wiki/
├── wiki_cli/          # CLI, config, ingest/plan, search, ask, chat
├── prompts/           # Wiki/persona rules; ask v1/v2; router v1/v2
├── vault/
│   ├── raw/           # 3 unchanged source notes
│   ├── wiki/          # Concepts, Selection, Initiation, Cases
│   └── index.md
├── tests/             # Test plan, unit tests, scripts, offline checklist
├── outputs/           # Runs, comparisons, review and offline evidence
├── screenshots/       # Device, Obsidian, terminal evidence
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

**Not included:** model weights, `.venv/`, and `data/` (rebuilt by `wiki ingest` outside the vault). [Git ignore rules](.gitignore) exclude them. Prior local milestones are `87e555b` (CLI and versioned prompts) and `ece0d09` (safe ingest and offline checklist).
