# Offline run checklist

Preparation only: Codex has not run this offline test. Run these commands yourself
in PowerShell with WiFi turned off. Keep the Ollama app running locally. The
virtual environment, packages, gemma4:e2b-it-qat, and embeddinggemma are already
installed; do not run pip install or ollama pull during this test.

Ask uses prompt v2; chat uses router v2. No answers are graded by this checklist.
Run each step in order and wait for it to finish. If a command reports an error,
record it and stop before proceeding. Immediately after a wiki command,
`$LASTEXITCODE` should be 0 for a completed run; citation warnings still need review.

## 1. Open the project and activate the environment

- [ ] Run:

```powershell
cd C:\Users\pao_n\projects\personal-wiki
.\.venv\Scripts\Activate.ps1
```

Success: the prompt normally shows (.venv), and wiki is available in this terminal.
Output files: none.

If activation is blocked by PowerShell policy, you may explicitly allow scripts
for this terminal only, then retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

This is an optional action for you; Codex has not changed execution policy.

## 2. Check local Ollama and models

- [ ] Run:

```powershell
wiki status
```

Success: shows local Ollama at http://localhost:11434, its version, both installed
model names, a short generated response, and generation time. Thinking is disabled.
Output files: none; status prints to the terminal. It does not update outputs/status.txt.

## 3. Rebuild retrieval data without replacing reviewed content

- [ ] Run exactly this, without --force:

```powershell
wiki ingest
```

Success for the current project: reads the three raw files, creates 16 section
chunks, rebuilds embeddings, reports all 12 existing notes as skipped, reports
vault/index.md as skipped, and ends with Errors: 0 (none).

Outputs: data/chunks.json and data/embeddings.npy are rebuilt;
outputs/ingest-log.md is rewritten with this run's progress and timings.
The old log is preserved in the preparation Git commit, not as a separate runtime copy.

Existing notes and index.md are never modified without --force. Link checks run
only for newly generated notes, not skipped notes. If a planned note is missing,
this command generates it locally; if index.md is missing, it creates the index.
Raw source files are read-only in all cases.

## 4. Search and save results

- [ ] Run:

```powershell
wiki search "What should a project charter include?" --save
```

Success: prints four ranked sections with final, keyword, and semantic scores,
source paths, headings, previews, and search time. Only embeddinggemma is called.
Output: a new dated Markdown file under outputs/search/; its exact path is printed
as Saved:. No prior search result or search-tests.md is overwritten.

## 5. Ask the four test-plan questions using ask v2

- [ ] Question 1:

```powershell
wiki ask "What should a project charter include?"
```

- [ ] Question 2:

```powershell
wiki ask "How can a company decide which projects to fund when it has more ideas than money?"
```

- [ ] Question 3:

```powershell
wiki ask "How should a project manager balance scope, time, and cost?"
```

- [ ] Question 4:

```powershell
wiki ask "How does agile project management differ from traditional approaches?"
```

For each command, successful execution prints an answer or the exact refusal
"I don't have enough evidence in my notes to answer this.", Sources, citation
warnings (or None), and search/generation/total timings. Review the answer and
citations yourself; successful execution does not establish correctness.

Each command creates one new dated Markdown file under outputs/ask/, with its
path printed as Saved:. Each file includes Prompt version: v2, temperature 0.2,
seed 42, think=False, all four full passages, the answer, citation checks, and
timings. These commands do not update ask-tests-v1.md or ask-tests-v2.md.

## 6. Run the original chat script

- [ ] Run:

```powershell
wiki chat --script tests/chat-script.txt
```

Success: processes all four messages, prints a search decision before each answer,
prints citations/checks and timings, then saves and exits at end-of-file without
waiting for keyboard input. No runtime errors should be reported. Review the
observed routing and answers yourself.

Output: one new dated transcript under outputs/chat/, printed as Saved transcript:.
It records router v2, raw routing output, queries, full passages, answers, checks,
and timings. Existing transcripts and chat-tests reports are not overwritten.

## 7. Run the held-out chat script

- [ ] Run:

```powershell
wiki chat --script tests/chat-script-heldout.txt
```

Success: processes all three messages and exits at end-of-file, with decisions,
answers, checks, timings, and no runtime errors. Review the results yourself.

Output: another new dated transcript under outputs/chat/, with router v2 and the
same evidence fields. Its path is printed as Saved transcript:.

## Runtime network review

Codex inspected the wiki_cli modules, configuration, dependency declarations,
and the installed Ollama client's request path. All application model calls use
an explicit http://localhost:11434 host with trust_env=False (environment proxies
are ignored). The status version request also uses localhost and disables proxies.
The configured model names are local model names. No runtime model pulls,
package installs, downloads, web searches, remote API calls, or subprocess commands
exist in the application. Documentation links in README.md are not fetched by code.

Git excludes data/ and .venv/. Those local files still exist for this offline run.
The project has no Git remote, and nothing has been pushed. This static review
and mocked unit tests are preparation evidence, not a completed offline test.
