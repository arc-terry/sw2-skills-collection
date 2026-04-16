#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <runtime-dir>" >&2
  exit 1
fi

runtime_dir="$(readlink -f "$1")"
context_dir="$runtime_dir/context"
artifacts_dir="$runtime_dir/artifacts"

mkdir -p "$context_dir" "$artifacts_dir"
touch "$context_dir/context.jsonl" "$context_dir/context.md" "$context_dir/live.log"

cat <<EOF
runtime_dir=$runtime_dir
context_jsonl=$context_dir/context.jsonl
context_md=$context_dir/context.md
live_log=$context_dir/live.log
artifacts_dir=$artifacts_dir
EOF
