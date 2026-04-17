---
name: project-usage-assess
description: Aggregate per-project Copilot premium requests and Codex token usage from local session logs, then generate a markdown table with totals for usage/quota assessment.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.1.0"
---

# project-usage-assess

## Goal

Produce an auditable usage report by project from local session logs:
- Copilot premium requests
- Codex token usage

## Trigger

Use this skill when the user asks for:
- per-project premium requests usage
- per-project token usage
- usage summary for quota increase or capacity planning
- report generation from `~/.copilot/session-state` and `~/.codex/sessions`

## Metrics (default)

- Copilot premium requests:
  - Sum of `session.shutdown.totalPremiumRequests` in the target time window.
  - Aggregated by project (`cwd` basename).
- Codex tokens:
  - Per session file, use max value of `event_msg.payload.info.total_token_usage.total_tokens` (where `payload.type == token_count`) in the target time window.
  - Aggregated by project (`cwd` basename).

## Data sources

- Copilot: `~/.copilot/session-state/*/events.jsonl`
- Codex: `~/.codex/sessions/**/**/*.jsonl`

Project mapping uses `cwd` from session metadata:
- Copilot: `session.start.data.context.cwd`
- Codex: `session_meta.payload.cwd`

## Command

Run the packaged script from the skill directory:

```bash
python3 "$PWD/scripts/generate_project_usage_report.py" \
  --start-local 2026-03-01T00:00:00 \
  --end-local-exclusive 2026-04-15T00:00:00 \
  --timezone Asia/Taipei \
  --output-md /home/paul_chen/prj_pri/agent-stats.md
```

## Output contract

The markdown report includes:
- metadata (time window, generation timestamp, metric definition)
- per-project table rows
- `TOTAL` row with:
  - Copilot premium requests total
  - Codex tokens total

## Guardrails

- Keep parsing tolerant (`jsonl` may contain malformed lines).
- Do not read or print any secret fields.
- Use absolute paths in commands and outputs.
