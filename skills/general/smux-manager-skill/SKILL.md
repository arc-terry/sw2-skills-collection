---
name: smux-manager-skill
description: Run a smux-native manager/worker workflow over tmux panes with task envelopes, sanitized context mirrors, and optional thin helper scripts.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.1.0"
---

# Smux Manager Skill

Use this skill when one pane should act as a **manager agent** and coordinate one or more **worker agent panes** through `tmux-bridge`, without first building a separate orchestration runtime.

## When to use

- You already have tmux panes running agents such as Copilot CLI or Codex.
- You want **1-to-many task dispatch** from one manager pane to multiple worker panes.
- You want worker panes to see a **shared, sanitized manager context**.
- You want to stay **smux-native first** and add helpers only if pain appears.

## When not to use

- You need unattended execution, durable replay, or restart recovery.
- You need queue semantics that survive process or tmux restarts.
- You need device/UART brokering or policy enforcement beyond pane orchestration.

## Core model

1. **Manager is just another pane**
   - The first version should not assume a daemon or server.
   - The manager agent uses `tmux-bridge` directly.

2. **Pane transport is for control signals**
   - Use pane messages for task assignment and short status.
   - Put long outputs in artifact files and send paths back.

3. **Workers should read a context mirror, not scrape the manager pane**
   - Keep a sanitized `context.jsonl` / `context.md` / `live.log`.
   - Workers consume snapshot + delta using `context_seq`.

4. **Manager is the only task authority**
   - Only the manager may assign, requeue, cancel, or rotate leases.
   - Workers may ask for context, report progress, succeed, or fail.

## Roles

### Manager pane

- Discovers worker panes
- Writes the shared context mirror
- Sends `TASK_ASSIGN`
- Collects `TASK_ACCEPT`, `STATUS`, `RESULT`, `FAIL`
- Decides requeue / retry / cancel

### Worker panes

- Receive `TASK_ASSIGN`
- Read the current context snapshot and deltas
- Reply through `tmux-bridge` using protocol verbs
- Write long outputs to artifact files

### Optional bus pane

- Runs `tail -f runtime/context/live.log`
- Gives humans and agents a passive shared view of manager↔worker traffic

## Recommended workflow

1. Initialize a runtime directory:

   ```bash
   skills/general/smux-manager-skill/scripts/init-runtime.sh /tmp/smux-manager-demo
   ```

2. Label panes early:

   ```bash
   tmux-bridge name "$(tmux-bridge id)" manager
   tmux-bridge name %1 codex
   ```

3. Append sanitized context entries as the manager clarifies or narrows work:

   ```bash
   skills/general/smux-manager-skill/scripts/append-context.sh \
     /tmp/smux-manager-demo 110 manager codex CONTEXT task-123 \
     "Investigate failing auth tests under tests/ and src/auth.ts"
   ```

4. Dispatch a task:

   ```bash
   skills/general/smux-manager-skill/scripts/send-task.sh \
     codex task-123 codex 45 110 lease-task-123 \
     "Investigate failing auth tests" "tests/ src/auth.ts" \
     "/tmp/smux-manager-demo/artifacts"
   ```

5. Track short replies in the manager pane and mirror meaningful ones back into `context.jsonl` / `context.md` / `live.log`.

6. Let workers send protocol replies with the helper when PATH or read-guard friction appears:

   ```bash
   TMUX_BRIDGE_BIN="$HOME/.smux/bin/tmux-bridge" \
   skills/general/smux-manager-skill/scripts/send-reply.sh \
     manager TASK_ACCEPT task-123 codex 46 110 lease-task-123 \
     "Accepted and starting inspection"
   ```

## Installing smux when `tmux-bridge` is missing

- If a pane cannot find `tmux-bridge`, **ask the user whether they want to install `smux` before running any installer command**.
- If the user approves installation, use the upstream installer:

  ```bash
  curl -fsSL https://shawnpana.com/smux/install.sh | bash
  ```

- Per the upstream `ShawnPana/smux` README, this installs `tmux` when needed, the `smux` setup, and `tmux-bridge` under `~/.smux/`.
- The helper scripts in this skill already fall back to `~/.smux/bin/tmux-bridge`, so `TMUX_BRIDGE_BIN` is optional rather than required.
- If direct `tmux-bridge ...` commands still fail because `PATH` has not been refreshed in the current pane, use the absolute path until the shell environment is updated:

  ```bash
  "$HOME/.smux/bin/tmux-bridge" list
  ```

## Protocol summary

Required verbs:

- `HELLO`
- `TASK_ASSIGN`
- `TASK_ACCEPT`
- `HEARTBEAT`
- `STATUS`
- `ASK`
- `RESULT`
- `FAIL`

Required fields on every task-bound message:

- `task`
- `worker`
- `seq`
- `lease_token`
- `context_seq`

See `references/PROTOCOL.md` for the wire format and examples.

## Context mirror policy

- Mirror **only manager↔worker sanitized context**
- Do **not** mirror user↔manager conversation by default
- Use `context_seq` so workers can read snapshot + delta instead of scraping manager scrollback

See `references/CONTEXT_MIRROR.md` for file layout and update rules.

## Thin helper scripts

- `scripts/init-runtime.sh` — create runtime folders and mirror files
- `scripts/append-context.sh` — append a sanitized context event to JSONL / Markdown / live log
- `scripts/send-task.sh` — send a `TASK_ASSIGN` envelope using the required read-act-read cycle
- `scripts/send-reply.sh` — send worker replies with tmux-bridge path fallback and read-act-read handling

## Observed thin-helper thresholds

The smux-native MVP worked, but the first live validations exposed two real sources of friction:

1. **Pane-local PATH drift**
   - Fresh worker panes did not always have `tmux-bridge` on `PATH`.
   - The pragmatic fix is to support `TMUX_BRIDGE_BIN` or fall back to `~/.smux/bin/tmux-bridge`.

2. **Read guard recovery**
   - Workers can accidentally `type` a reply and then forget the extra `read` required before `keys Enter`.
   - A helper script is worth keeping once more than one worker pane is active.

## Escalate beyond smux when

- You need durable queues or replay after restart
- Many worker panes make manual status tracking too noisy
- Lease / retry / artifact tracking becomes too tedious by hand
- The manager needs to run unattended

At that point, keep the same protocol and context mirror, then add a thin helper layer or a real runtime on top.
