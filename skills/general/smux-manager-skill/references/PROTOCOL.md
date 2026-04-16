# Smux Manager Protocol

This protocol assumes a **manager pane** talking to one or more **worker panes** over `tmux-bridge`.

## Design goals

- Human-readable in a pane
- Machine-friendly enough for helper scripts
- Single-line envelopes for control traffic
- Long outputs moved to artifact files

## Required message types

- `HELLO`
- `TASK_ASSIGN`
- `TASK_ACCEPT`
- `HEARTBEAT`
- `STATUS`
- `ASK`
- `RESULT`
- `FAIL`

## Envelope format

Keep the control line on one line:

```text
[role type:VERB task:task-123 worker:codex seq:45 reply:%0 context_seq:110 lease_token:lease-task-123]
```

Optional payload may follow on the same line after the bracket:

```text
[mgr type:TASK_ASSIGN task:task-123 worker:codex seq:45 reply:%0 context_seq:110 lease_token:lease-task-123] goal="Investigate failing auth tests" input="tests/ src/auth.ts" artifact_dir="/tmp/smux/artifacts"
```

## Field meanings

| Field | Meaning |
| --- | --- |
| `role` | `mgr` or `wrk` |
| `type` | Protocol verb |
| `task` | Stable task identifier |
| `worker` | Logical worker identifier |
| `seq` | Monotonic sequence number from the sender |
| `reply` | Manager pane target to reply to |
| `context_seq` | Latest shared context sequence the sender expects |
| `lease_token` | Assignment token echoed back by the worker |

## Manager rules

1. Only the manager sends `TASK_ASSIGN`.
2. Only the manager decides reassignment, retry, or cancellation.
3. The manager must rotate `lease_token` when reassigning a task.
4. The manager should mirror meaningful worker replies into the shared context files.

## Worker rules

1. Reply to the manager pane using `tmux-bridge`, not only inside the local pane.
2. Echo the latest `lease_token` exactly.
3. Use `ASK` when context is insufficient instead of silently guessing.
4. Use `RESULT` or `FAIL` as the terminal message for an assignment.
5. If `tmux-bridge` is missing from `PATH`, use an absolute path or set `TMUX_BRIDGE_BIN`.

## Verb guidance

### `HELLO`

Used when a worker pane first joins the pool or when the manager probes capabilities.

```text
[wrk type:HELLO task:none worker:codex seq:1 reply:%0 context_seq:0 lease_token:none] caps="code,search,edit"
```

### `TASK_ASSIGN`

Manager sends work to a worker pane.

```text
[mgr type:TASK_ASSIGN task:task-123 worker:codex seq:45 reply:%0 context_seq:110 lease_token:lease-task-123] goal="Investigate failing auth tests" input="tests/ src/auth.ts" artifact_dir="/tmp/smux/artifacts"
```

### `TASK_ACCEPT`

Worker acknowledges ownership of the task.

```text
[wrk type:TASK_ACCEPT task:task-123 worker:codex seq:46 reply:%0 context_seq:110 lease_token:lease-task-123] note="Accepted and starting inspection"
```

### `HEARTBEAT`

Worker indicates continued liveness on a long-running task.

```text
[wrk type:HEARTBEAT task:task-123 worker:codex seq:47 reply:%0 context_seq:111 lease_token:lease-task-123] note="Still running"
```

### `STATUS`

Short progress or blocked-but-not-terminal update.

```text
[wrk type:STATUS task:task-123 worker:codex seq:48 reply:%0 context_seq:112 lease_token:lease-task-123] note="Narrowed failure to refresh-token branch"
```

### `ASK`

Worker asks for more context or a manager decision.

```text
[wrk type:ASK task:task-123 worker:codex seq:49 reply:%0 context_seq:112 lease_token:lease-task-123] question="Should I inspect only tests, or patch code too?"
```

### `RESULT`

Successful terminal reply. Prefer an artifact path for anything long.

```text
[wrk type:RESULT task:task-123 worker:codex seq:50 reply:%0 context_seq:113 lease_token:lease-task-123] artifact="/tmp/smux/artifacts/task-123.md" note="Root cause identified"
```

### `FAIL`

Terminal failure or refusal.

```text
[wrk type:FAIL task:task-123 worker:codex seq:51 reply:%0 context_seq:113 lease_token:lease-task-123] note="Missing repository access"
```

## Suggested state flow

```text
queued -> assigned -> running -> blocked/retry_wait -> done|failed|cancelled
```

For the smux-native MVP, this state flow may be tracked manually or with very light helper scripts.

## Practical friction seen in live validation

The first multi-pane validation surfaced two common mistakes:

1. Worker panes may not inherit the same `PATH`, so `tmux-bridge` lookup can fail.
2. After `type`, workers still need another `read` before `keys Enter`; otherwise read guard rejects the send.

That is why this skill ships `send-reply.sh` in addition to `send-task.sh`.
