#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 7 || $# -gt 9 ]]; then
  echo "Usage: $0 <target-pane> <task-id> <worker-id> <seq> <context-seq> <lease-token> <goal> [input-ref] [artifact-dir]" >&2
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
task_id="$2"
worker_id="$3"
seq="$4"
context_seq="$5"
lease_token="$6"
goal="$7"
input_ref="${8:-}"
artifact_dir="${9:-}"
reply_pane="$("$tmux_bridge_bin" id)"

message="[mgr type:TASK_ASSIGN task:${task_id} worker:${worker_id} seq:${seq} reply:${reply_pane} context_seq:${context_seq} lease_token:${lease_token}] goal=\"${goal}\""

if [[ -n "$input_ref" ]]; then
  message+=" input=\"${input_ref}\""
fi

if [[ -n "$artifact_dir" ]]; then
  message+=" artifact_dir=\"${artifact_dir}\""
fi

"$tmux_bridge_bin" read "$target" 20 >/dev/null
"$tmux_bridge_bin" type "$target" "$message"
"$tmux_bridge_bin" read "$target" 20 >/dev/null
"$tmux_bridge_bin" keys "$target" Enter >/dev/null

printf '%s\n' "$message"
