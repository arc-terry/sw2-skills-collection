#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 7 || $# -gt 8 ]]; then
  echo "Usage: $0 <runtime-dir> <seq> <from> <to> <type> <task-id> <summary> [artifact-path]" >&2
  exit 1
fi

runtime_dir="$(readlink -f "$1")"
seq="$2"
from="$3"
to="$4"
event_type="$5"
task_id="$6"
summary="$7"
artifact_path="${8:-}"

context_dir="$runtime_dir/context"
jsonl_path="$context_dir/context.jsonl"
md_path="$context_dir/context.md"
log_path="$context_dir/live.log"

mkdir -p "$context_dir"
touch "$jsonl_path" "$md_path" "$log_path"

ts="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

if python3 - "$jsonl_path" "$seq" "$task_id" <<'PY'
import json
import sys

path, seq, task_id = sys.argv[1:]

try:
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if str(payload.get("seq")) == seq and payload.get("task_id") == task_id:
                raise SystemExit(0)
except FileNotFoundError:
    pass

raise SystemExit(1)
PY
then
  echo "context entry already exists for task=$task_id seq=$seq; skipping" >&2
  exit 0
fi

python3 - "$ts" "$seq" "$from" "$to" "$event_type" "$task_id" "$summary" "$artifact_path" >>"$jsonl_path" <<'PY'
import json
import sys

ts, seq, src, dst, event_type, task_id, summary, artifact_path = sys.argv[1:]
payload = {
    "seq": int(seq),
    "ts": ts,
    "task_id": task_id,
    "from": src,
    "to": dst,
    "type": event_type,
    "summary": summary,
    "artifact_path": artifact_path or None,
}
print(json.dumps(payload, ensure_ascii=True))
PY

artifact_note=""
if [[ -n "$artifact_path" ]]; then
  artifact_note=" artifact=$artifact_path"
fi

printf -- "- seq=%s task=%s %s -> %s %s%s\n" \
  "$seq" "$task_id" "$from" "$to" "$summary" "$artifact_note" >>"$md_path"

printf -- "[%s] seq=%s task=%s %s -> %s type=%s%s summary=%s\n" \
  "$ts" "$seq" "$task_id" "$from" "$to" "$event_type" "$artifact_note" "$summary" >>"$log_path"
