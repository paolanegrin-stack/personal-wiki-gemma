# Chat routing iteration: v1 to v2

This is one routing-only improvement round. Answers are unedited and are not graded here.

## Preserved v1 turn-2 answer

I don't have enough evidence in my notes.

Original transcript: [V1](chat/20260929-172941-757280.md). The original summary was renamed to chat-tests-v1.md without changing its bytes.

## What changed and why

- Router instructions are versioned as prompts/router-v1.md (exact original text) and prompts/router-v2.md. ROUTER_PROMPT_VERSION selects v2 and is recorded in new transcripts.
- V2 routing receives only the new user message and previous user message. Assistant answers and older user messages are excluded to avoid influencing routing with prior assistant replies. V1 received recent user/assistant history.
- V2 adds six short examples of social/capability messages and content/follow-up questions. None uses an exact message from either test script.
- V2 explicitly requires exactly SEARCH or NO_SEARCH, with no explanation. The existing parser and fallback to SEARCH are unchanged.
- These changes target the observed v1 turn-2 NO_SEARCH decision and turn-3 invalid output. This documents the motivation, not an answer-correctness grade.
- Rewrite prompts, rewrite inputs, answer prompts, answer inputs, citation checks, model settings, search, and the history limit were not changed. Different routing/answers can naturally change subsequent conversation history.

## Original script: routing comparison

| Turn | Message | V1 raw output | V1 decision | V2 raw output | V2 decision |
|---|---|---|---|---|---|
| 1 | Hi, what can you help me with? | `NO_SEARCH` | NO_SEARCH | `NO_SEARCH` | NO_SEARCH |
| 2 | What is scope creep? | `NO_SEARCH` | NO_SEARCH | `SEARCH` | SEARCH |
| 3 | How can a team prevent it? | `I don't have enough evidence in` | SEARCH | `SEARCH` | SEARCH |
| 4 | Thanks, that helps. | `NO_SEARCH` | NO_SEARCH | `NO_SEARCH` | NO_SEARCH |

V1 turn 3 used the parser fallback; v2 turn 3 returned SEARCH directly.

## Held-out script: v2 routing

There was no v1 run of this held-out script; no v1 comparison is implied.

| Turn | Message | V2 raw output | V2 decision |
|---|---|---|---|
| 1 | Good morning! | `NO_SEARCH` | NO_SEARCH |
| 2 | What does a responsibility matrix show? | `SEARCH` | SEARCH |
| 3 | Who should be on it? | `SEARCH` | SEARCH |

Transcripts: [V2 original script](chat/20260929-173859-359124.md), [V2 held-out script](chat/20260929-174055-698358.md).
Full timings, queries, and citation checks: [chat-tests-v2.md](chat-tests-v2.md).

## Preservation

All 21 unit tests passed, including assistant-exclusion, routing-parser fallback, and history-limit tests. Protected files passed hash checks; rewrite and answer branch text matched the pre-change snapshot exactly.
