# Personal Wiki CLI

Assignment 4 — Fundamentals of AI. Step 4: local wiki ingestion, hybrid search, and cited answers.

Uses local Ollama at `http://localhost:11434`, with `gemma4:e2b-it-qat`
for generation and `embeddinggemma` for future retrieval. Help, status, ingest, search, and ask are implemented. Chat supports interactive and scripted conversations.
Runtime model calls stay on this laptop. No cloud API, hosted embeddings,
LangChain, or LlamaIndex is used. Installing Python packages initially may
require internet access; running the installed CLI with installed models does not.

## PowerShell quick start

```powershell
.\.venv\Scripts\Activate.ps1
wiki --help
wiki status
```

If PowerShell blocks activation, you may allow scripts for just this terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Alternatively, run without activation or any execution-policy change:

```powershell
.\.venv\Scripts\wiki.exe --help
.\.venv\Scripts\wiki.exe status
```

To recreate the environment with Python 3.13 available on PATH:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

`vault/raw/` holds unchanged source notes; `vault/wiki/` will hold generated
wiki notes. `data/` holds future machine files outside the vault and is ignored
by Git. The prompts describe source-grounded wiki writing and the future study assistant. `outputs/` is for saved evidence.
`tests/test-plan.md` contains the original test plan for later implementation.

All editable settings are in `wiki_cli/config.py`. Status checks both models
and generates at most 32 tokens with `think=False`; the reported time includes
any cold model load. It does not download models or test embeddings.

## Build the wiki

```powershell
wiki ingest
wiki ingest --force
python -m unittest discover -s tests -v
```

Ingest reads every Markdown file under `vault/raw/`, making one chunk for each
`## ` section. Text before the first section is not a chunk. Numbered headings
keep their explicit numbers; otherwise, the section position supplies the number.
Raw files are never written. The explicit twelve-note mapping is in
`wiki_cli/wiki_plan.py`.

`data/chunks.json` holds model metadata and a `chunks` list; item i corresponds
to row i in `data/embeddings.npy` (float32). Embeddings are rebuilt on each run.
The embedding model is unloaded before Gemma generates notes to reduce memory use.
Each new note uses one Gemma call with `think=False` and only its mapped evidence.
Gemma returns JSON; Python validates source IDs and renders YAML and citations.
Formatting checks do not prove every model claim is correct; review the notes
against their cited sections.

Existing notes are skipped unless `--force` is supplied. That flag replaces
manual edits. The index and ingest log are regenerated on each run. A failed
note is logged and not saved; later notes are still attempted. Rerun normally
to resume after resolving errors. Unknown wikilinks are converted to plain text
and recorded in `outputs/ingest-log.md`. The index lists only notes that exist.
No new dependencies or external services are used.

## Search raw-source sections

```powershell
wiki ingest --embeddings-only
wiki search "What should a project charter include?"
wiki search "What should a project charter include?" --save
```

Embeddings-only updates `data/chunks.json` and `data/embeddings.npy`, never the
vault, notes, index, prompts, or original ingest log. It does not call the
text-generation model. Normal ingest uses the same document formatting.

Following Google's [EmbeddingGemma prompt instructions](https://ai.google.dev/gemma/docs/embeddinggemma/model_card#prompt-instructions),
documents use `title: {section heading} | text: {section text}` and queries use
`task: search result | query: {query}`. Search checks the saved model and format
metadata so old, unformatted embeddings cannot silently be mixed with new ones.
This documentation lookup was a development step; the application runs offline.

BM25 tokenizes section headings and text into lowercase letter/number runs,
splitting at punctuation and underscores. It uses rank-bm25's defaults, without
stemming or stop-word filtering. Semantic scores are cosine similarities.
Each score array is independently min-max scaled over all chunks; constant
arrays become zeros. The final score is 0.5 keyword + 0.5 semantic, with weights
in config.py. Ties retain chunk order. Scores are relative rankings, not evidence
sufficiency or confidence probabilities; unsupported questions still get results.

Search prints four sections (or fewer if the corpus is smaller), normalized and
raw scores, source paths, headings, and 200-character text previews. `--save`
creates dated Markdown in `outputs/search/`. Search timing covers data loading,
BM25, the local query embedding, and ranking, excluding output formatting/saving.
Only embeddinggemma is called; Gemma generation is not used.

## Ask a question

```powershell
wiki ask "What should a project charter include?"
```

Ask reuses the same top-four hybrid search without changing ranking or weights.
It sends persona.md, explicit answer rules, the four full numbered passages,
and the question to local Gemma with think=False, temperature 0.2, and seed 42.
Generation settings are in config.py. The required insufficient-evidence reply
is exactly: "I don't have enough evidence in my notes to answer this."

Every attempted run is saved in outputs/ask/ with the question, full passages,
model settings, unedited answer, citation references, warnings, and timings.
Generation failures are saved too when the output directory is writable.
The citation checker lists every numeric reference and maps valid numbers to
sources. It flags nonexistent passage numbers and uncited non-refusal answers.
It does not grade correctness or prove that every claim has supporting evidence.
No automatic answer correction or retry occurs. Total time includes retrieval,
prompt building, generation, and citation checks, excluding saving and printing.

## Chat

```powershell
wiki chat
wiki chat --script tests/chat-script.txt
```

Session commands are `/help`, `/sources`, `/reset`, and `/quit`. End-of-file
also saves and exits. Blank lines are ignored. Reset clears model history and
last-answer sources, while preserving the transcript for evidence.

A turn means one user message and one assistant answer. The last six complete
turns (CHAT_HISTORY_TURNS in config.py) are sent to local Gemma for routing,
query rewriting, and answering. The full transcript is saved after each turn.
A short routing call returns SEARCH or NO_SEARCH; any other output defaults to
SEARCH. Only SEARCH can call the existing hybrid retriever. It first rewrites
the message with history, then uses ask-v2 rules and the existing citation check.
History helps interpret the question; only current passages are factual evidence.
Citation numbers restart each turn. NO_SEARCH uses persona.md for brief social
or conversation-related replies, with no retrieval or course-content teaching.
Unexpected citations on NO_SEARCH turns are flagged, not silently removed.

The transcript in outputs/chat/ records every message and answer, routing output,
rewritten query, full retrieved passages, citations, warnings, and stage timings.
Routing and rewriting use temperature 0, seed 42, think=False, and short token
limits; answers use the existing ask generation settings. Model outputs are not
automatically graded. The model may still route or rewrite incorrectly; raw
routing output and warnings are retained for review.
