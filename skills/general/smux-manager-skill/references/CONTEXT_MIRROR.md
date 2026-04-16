# Context Mirror

The context mirror gives worker panes a **shared, sanitized view** of manager↔worker traffic without forcing them to scrape the manager pane.

## Scope

Mirror:

- manager↔worker task context
- manager decisions
- worker questions that matter to the task
- artifact paths and short summaries

Do not mirror by default:

- raw user↔manager conversation
- secrets
- irrelevant side chatter

## Recommended layout

```text
runtime/
  context/
    context.jsonl
    context.md
    live.log
  artifacts/
```

## File roles

### `context.jsonl`

Machine-readable append-only event stream.

Suggested fields:

```json
{
  "seq": 110,
  "ts": "2026-04-06T10:15:00Z",
  "task_id": "task-123",
  "from": "manager",
  "to": "codex",
  "type": "CONTEXT",
  "summary": "Investigate failing auth tests under tests/ and src/auth.ts",
  "artifact_path": null
}
```

### `context.md`

Readable rolling snapshot for agents or humans that want a quick summary.

Suggested style:

```md
# Shared context

- seq=110 task=task-123 manager -> codex: Investigate failing auth tests under tests/ and src/auth.ts
- seq=111 task=task-123 codex -> manager: Accepted and starting inspection
```

### `live.log`

Human-friendly append-only tail target for a bus pane:

```bash
tail -f runtime/context/live.log
```

## Consumption model

1. Worker reads the current snapshot (`context.md`) for fast orientation.
2. Worker reads deltas from `context.jsonl` using the last seen `context_seq`.
3. Manager includes the expected `context_seq` inside every `TASK_ASSIGN`.

This gives a simple **snapshot + delta** model without requiring a full runtime.

## Update policy

Manager should mirror:

- every `TASK_ASSIGN`
- every manager clarification that changes task scope
- every worker `ASK` that changes understanding
- every `RESULT` / `FAIL`

Manager may skip:

- duplicate heartbeats
- low-value chatter
- private reasoning that workers should not inherit

## Bootstrap and debug

Pane scraping is still acceptable for:

- initial bootstrap
- debugging a broken interaction
- manual post-mortem after an agent crash

But the mirror files, not pane scrollback, should be the main shared source of truth.
