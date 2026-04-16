#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 8 || $# -gt 10 ]]; then
  echo "Usage: $0 <target-pane> <type> <task-id> <worker-id> <seq> <context-seq> <lease-token> <note> [reply-pane] [artifact-path]" >&2
  exit 1
fi

tmux_bridge_bin="${TMUX_BRIDGE_BIN:-}"

if [[ -z "$tmux_bridge_bin" ]]; then
  if command -v tmux-bridge >/dev/null 2>&1; then
    tmux_bridge_bin="$(command -v tmux-bridge)"
  elif [[ -x "$HOME/.smux/bin/tmux-bridge" ]]; then
    tmux_bridge_bin="$HOME/.smux/bin/tmux-bridge"
  else
    echo "tmux-bridge not found; set TMUX_BRIDGE_BIN or install it under PATH/~/.smux/bin" >&2
    exit 1
  fi
fi

target="$1"
event_type="$2"
task_id="$3"
worker_id="$4"
seq="$5"
context_seq="$6"
lease_token="$7"
note="$8"
reply_pane="${9:-$("$tmux_bridge_bin" id)}"
artifact_path="${10:-}"

message="[wrk type:${event_type} task:${task_id} worker:${worker_id} seq:${seq} reply:${reply_pane} context_seq:${context_seq} lease_token:${lease_token}] note=\"${note}\""

if [[ -n "$artifact_path" ]]; then
  message+=" artifact=\"${artifact_path}\""
fi

"$tmux_bridge_bin" read "$target" 20 >/dev/null
"$tmux_bridge_bin" type "$target" "$message"
"$tmux_bridge_bin" read "$target" 20 >/dev/null
"$tmux_bridge_bin" keys "$target" Enter >/dev/null

printf '%s\n' "$message"
