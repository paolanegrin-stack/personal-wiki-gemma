# Review edits after Gemma generation

Gemma generated the notes; Codex applied these corrections after comparing them against the raw sources; Paola verified each correction against the sources.

## Provenance

Codex edited 10 of the 12 notes after generation. These were editorial decisions made by Codex, applied using a one-off Python script outside the ingest pipeline. Gemma did not make those revisions, and no additional generation calls were made. The earlier description should have made that distinction explicit.

This report records the before/after explanation given in the preceding conversation. Quoted fragments show the complete replaced text; surrounding text and citations stayed unchanged. Saving this report does not modify any notes.

## 1. Concepts/Project Success Criteria.md

In the second key point:

**Before:** “not just administrative details like delivery date and cost.”

**After:** “alongside delivery date and cost, which are part of the result.”

## 2. Concepts/Project Life Cycle.md

In the summary:

**Before:** “mentions standards such as”

**After:** “mentions standards and organizations such as”

## 3. Concepts/Projects Programs and Portfolios.md

In the summary:

**Before:** “portfolios group projects, programs, and operations”

**After:** “portfolios group projects, programs, and sometimes operations”

## 4. Concepts/Project Complexity.md

Replaced the five-sentence summary with three sentences.

**Before:**

> Project complexity is mapped across three forms: structural, sociopolitical, and emergent. Structural complexity relates to size, team, tasks, and dependencies. Sociopolitical complexity involves stakeholder interests, organizational relationships, and conflict. Emergent complexity involves new technology, changing methods, and uncertainty. Understanding these complexities helps in planning resources, anticipating risks, and selecting a management approach.

**After:**

> Project complexity has structural, sociopolitical, and emergent forms. These cover size, teams, tasks, and dependencies; stakeholder interests, organizational relationships, and conflict; and new technology, changing methods, and uncertainty, respectively. Mapping these forms helps teams plan resources, anticipate risks, and choose a management approach.

## 5. Selection/Project Selection Methods.md

Three replacements:

| Before | After |
|---|---|
| “early screening screens” | “early yes/no screens” |
| “Net Present Value (NPV), which discounts future cash flows to today's value.” | “Net Present Value (NPV), which discounts future net cash flows to today's value and subtracts the investment.” |
| “Nonfinancial methods use a weighted scoring model” | “Nonfinancial methods can use a weighted scoring model” |

## 6. Selection/Financial Evaluation.md

Two summary replacements:

| Before | After |
|---|---|
| “net present value (NPV), which discounts future cash flows to today's value.” | “net present value (NPV), which discounts future net cash flows to today's value and subtracts the investment.” |
| “often using a weighted scoring model” | “and can use a weighted scoring model” |

## 7. Selection/Weighted Scoring Model.md

Removed the second occurrence of `[[Project Selection Methods]]` from Related notes.

**Before:**

```markdown
- [[Project Selection Methods]]
- [[Project Definition]]
- [[Project Selection Methods]]
```

**After:**

```markdown
- [[Project Selection Methods]]
- [[Project Definition]]
```

## 8. Initiation/Project Charter.md

Removed the note's self-link.

**Before:**

```markdown
- [[Project Definition]]
- [[Project Charter]]
- [[Project Selection Methods]]
```

**After:**

```markdown
- [[Project Definition]]
- [[Project Selection Methods]]
```

## 9. Initiation/Statement of Work.md

In the summary:

**Before:** “also known as the project scope statement”

**After:** “called the project scope statement in these slides”

Codex also deleted this summary sentence, reducing the summary from four sentences to three:

> A scope checklist can be used to cover objectives, deliverables, milestones, technical requirements, acceptance criteria, limits, exclusions, and customer review.

The key point covering that checklist remained.

## 10. Initiation/Stakeholder Management.md

In the summary:

**Before:**

> Success is measured by stakeholder satisfaction, which requires understanding their needs and matching communication levels to their impact.

**After:**

> Stakeholder satisfaction is one measure of success; teams should understand stakeholder needs and match communication levels to their impact.

## What the ingest pipeline changed during the original run

It rendered Gemma's JSON into Markdown, added frontmatter and citation formatting, and converted the unapproved link in Statement of Work:

```text
Before: - [[Project Scope Statement]]
After:  - Project Scope Statement
```

That link removal was automatic. The ten note edits listed above were Codex's subsequent interventions.

At the time of the preceding report, Codex had also updated the pipeline for future runs to deduplicate related links and request summaries as two or three sentence strings. Those updates did not retroactively edit the running generation. At that time, the pipeline did not contain Codex's specific wording corrections or automatically remove self-links. The separately requested pipeline update accompanying this saved report now removes and logs self-links and duplicates on future runs; it has not been applied to existing notes.

## Unchanged content and audit limitations

Project Definition and Pan Europa Foods had no content edits. The cleanup script rewrote all 12 files, but those two retained identical text. Raw source files were unchanged. The ingest log records the review categories and final counts, but it does not contain these exact before-and-after replacements; they are preserved in this report.
