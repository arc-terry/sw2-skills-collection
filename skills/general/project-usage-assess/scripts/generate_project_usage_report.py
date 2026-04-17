#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


@dataclass
class Stats:
    copilot_parse_errors: int = 0
    codex_parse_errors: int = 0
    copilot_files_scanned: int = 0
    codex_files_scanned: int = 0
    copilot_sessions_included: int = 0
    codex_sessions_included: int = 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate per-project Copilot premium and Codex token usage markdown report."
    )
    p.add_argument(
        "--start-local",
        default="2026-03-01T00:00:00",
        help="Window start in local timezone (inclusive), ISO-8601 local time.",
    )
    p.add_argument(
        "--end-local-exclusive",
        default="2026-04-15T00:00:00",
        help="Window end in local timezone (exclusive), ISO-8601 local time.",
    )
    p.add_argument("--timezone", default="Asia/Taipei", help="IANA timezone name.")
    p.add_argument(
        "--copilot-root",
        default=str(Path.home() / ".copilot" / "session-state"),
        help="Copilot session-state root.",
    )
    p.add_argument(
        "--codex-root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Codex sessions root.",
    )
    p.add_argument(
        "--output-md",
        default=str(Path.home() / "prj_pri" / "agent-stats.md"),
        help="Output markdown path.",
    )
    p.add_argument(
        "--include-zero-projects",
        action="store_true",
        help="Include projects with both copilot premium and codex tokens equal to zero.",
    )
    return p.parse_args()


def parse_local_dt(value: str, tz: ZoneInfo) -> datetime:
    text = value.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        text = f"{text}T00:00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    else:
        dt = dt.astimezone(tz)
    return dt


def parse_ts_utc(ts: str | None) -> datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    try:
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts[:-1]).replace(tzinfo=timezone.utc)
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def in_window(ts: str | None, start_utc: datetime, end_utc_excl: datetime) -> bool:
    dt = parse_ts_utc(ts)
    return bool(dt and start_utc <= dt < end_utc_excl)


def project_from_cwd(cwd: str | None) -> str:
    if not cwd:
        return "(unknown)"
    name = Path(cwd.rstrip("/")).name
    return name if name else "(unknown)"


def iter_jsonl(path: Path, stats: Stats, source: str):
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                yield json.loads(line)
            except Exception:
                if source == "copilot":
                    stats.copilot_parse_errors += 1
                else:
                    stats.codex_parse_errors += 1


def aggregate_copilot(
    root: Path,
    start_utc: datetime,
    end_utc_excl: datetime,
    stats: Stats,
) -> dict[str, dict[str, int]]:
    by_project: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "copilot_premium_requests": 0,
            "copilot_sessions": 0,
            "copilot_shutdown_events": 0,
        }
    )

    files = sorted(root.glob("*/events.jsonl"))
    stats.copilot_files_scanned = len(files)

    for fp in files:
        cwd = None
        premium_sum = 0
        shutdown_count = 0

        for rec in iter_jsonl(fp, stats, "copilot"):
            if rec.get("type") == "session.start" and cwd is None:
                data = rec.get("data") or {}
                context = data.get("context") or {}
                if isinstance(context, dict):
                    cwd = context.get("cwd")

            if not in_window(rec.get("timestamp"), start_utc, end_utc_excl):
                continue

            if rec.get("type") != "session.shutdown":
                continue
            data = rec.get("data") or {}
            premium = data.get("totalPremiumRequests")
            if isinstance(premium, int):
                premium_sum += premium
                shutdown_count += 1

        if shutdown_count == 0:
            continue

        project = project_from_cwd(cwd)
        by_project[project]["copilot_premium_requests"] += premium_sum
        by_project[project]["copilot_sessions"] += 1
        by_project[project]["copilot_shutdown_events"] += shutdown_count
        stats.copilot_sessions_included += 1

    return by_project


def aggregate_codex(
    root: Path,
    start_utc: datetime,
    end_utc_excl: datetime,
    stats: Stats,
) -> dict[str, dict[str, int]]:
    by_project: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "codex_tokens_total": 0,
            "codex_sessions": 0,
            "codex_task_started_proxy": 0,
        }
    )

    files = sorted(root.glob("**/*.jsonl"))
    stats.codex_files_scanned = len(files)

    for fp in files:
        cwd = None
        max_tokens = 0
        task_started = 0
        any_in_window = False

        for rec in iter_jsonl(fp, stats, "codex"):
            if rec.get("type") == "session_meta" and cwd is None:
                payload = rec.get("payload") or {}
                if isinstance(payload, dict):
                    cwd = payload.get("cwd")

            if not in_window(rec.get("timestamp"), start_utc, end_utc_excl):
                continue
            any_in_window = True

            if rec.get("type") != "event_msg":
                continue
            payload = rec.get("payload") or {}
            ptype = payload.get("type") if isinstance(payload, dict) else None

            if ptype == "task_started":
                task_started += 1
                continue

            if ptype != "token_count":
                continue

            info = payload.get("info")
            if not isinstance(info, dict):
                continue
            total_usage = info.get("total_token_usage")
            if not isinstance(total_usage, dict):
                continue
            total = total_usage.get("total_tokens")
            if isinstance(total, int) and total > max_tokens:
                max_tokens = total

        if not any_in_window:
            continue

        project = project_from_cwd(cwd)
        by_project[project]["codex_tokens_total"] += max_tokens
        by_project[project]["codex_sessions"] += 1
        by_project[project]["codex_task_started_proxy"] += task_started
        stats.codex_sessions_included += 1

    return by_project


def render_markdown(
    rows: list[dict[str, Any]],
    start_local: datetime,
    end_local_excl: datetime,
    tz_name: str,
    stats: Stats,
) -> str:
    generated = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S %Z")

    total_copilot = sum(int(r["copilot_premium_requests"]) for r in rows)
    total_copilot_sessions = sum(int(r["copilot_sessions"]) for r in rows)
    total_copilot_shutdown = sum(int(r["copilot_shutdown_events"]) for r in rows)
    total_codex_tokens = sum(int(r["codex_tokens_total"]) for r in rows)
    total_codex_sessions = sum(int(r["codex_sessions"]) for r in rows)
    total_codex_task = sum(int(r["codex_task_started_proxy"]) for r in rows)

    out = []
    out.append(
        f"# Agent Usage Stats ({start_local.strftime('%Y-%m-%d')} ~ {(end_local_excl - (end_local_excl - end_local_excl)).strftime('%Y-%m-%d')})"
    )
    out.append("")
    out.append(f"- Generated at: `{generated}`")
    out.append(f"- Timezone: `{tz_name}`")
    out.append(
        "- Copilot premium requests: **SUM** of `session.shutdown.totalPremiumRequests` within window"
    )
    out.append(
        "- Codex tokens: per-session **MAX** `event_msg.token_count.info.total_token_usage.total_tokens`, then SUM by project"
    )
    out.append("")
    out.append(
        "| Project | Copilot Premium Requests (SUM) | Copilot Sessions | Copilot Shutdown Events | Codex Tokens | Codex Sessions | Codex Task Started (proxy) |"
    )
    out.append("|---|---:|---:|---:|---:|---:|---:|")

    for r in rows:
        out.append(
            "| {project} | {copilot_premium_requests} | {copilot_sessions} | {copilot_shutdown_events} | "
            "{codex_tokens_total} | {codex_sessions} | {codex_task_started_proxy} |".format(**r)
        )

    out.append(
        f"| **TOTAL** | **{total_copilot}** | **{total_copilot_sessions}** | **{total_copilot_shutdown}** | "
        f"**{total_codex_tokens}** | **{total_codex_sessions}** | **{total_codex_task}** |"
    )
    out.append("")
    out.append("## Audit")
    out.append("")
    out.append(f"- Copilot files scanned: `{stats.copilot_files_scanned}`")
    out.append(f"- Copilot sessions included: `{stats.copilot_sessions_included}`")
    out.append(f"- Copilot parse errors: `{stats.copilot_parse_errors}`")
    out.append(f"- Codex files scanned: `{stats.codex_files_scanned}`")
    out.append(f"- Codex sessions included: `{stats.codex_sessions_included}`")
    out.append(f"- Codex parse errors: `{stats.codex_parse_errors}`")
    out.append("")

    return "\n".join(out) + "\n"


def main() -> int:
    args = parse_args()
    tz = ZoneInfo(args.timezone)
    start_local = parse_local_dt(args.start_local, tz)
    end_local_excl = parse_local_dt(args.end_local_exclusive, tz)

    if end_local_excl <= start_local:
        raise SystemExit("end-local-exclusive must be greater than start-local")

    start_utc = start_local.astimezone(timezone.utc)
    end_utc_excl = end_local_excl.astimezone(timezone.utc)

    stats = Stats()

    copilot = aggregate_copilot(Path(args.copilot_root), start_utc, end_utc_excl, stats)
    codex = aggregate_codex(Path(args.codex_root), start_utc, end_utc_excl, stats)

    projects = sorted(
        set(copilot.keys()) | set(codex.keys()),
        key=lambda p: (
            copilot.get(p, {}).get("copilot_premium_requests", 0),
            codex.get(p, {}).get("codex_tokens_total", 0),
            p,
        ),
        reverse=True,
    )

    rows = []
    for p in projects:
        row = {
            "project": p,
            "copilot_premium_requests": copilot.get(p, {}).get("copilot_premium_requests", 0),
            "copilot_sessions": copilot.get(p, {}).get("copilot_sessions", 0),
            "copilot_shutdown_events": copilot.get(p, {}).get("copilot_shutdown_events", 0),
            "codex_tokens_total": codex.get(p, {}).get("codex_tokens_total", 0),
            "codex_sessions": codex.get(p, {}).get("codex_sessions", 0),
            "codex_task_started_proxy": codex.get(p, {}).get("codex_task_started_proxy", 0),
        }
        if args.include_zero_projects or row["copilot_premium_requests"] > 0 or row["codex_tokens_total"] > 0:
            rows.append(row)

    report = render_markdown(rows, start_local, end_local_excl, args.timezone, stats)

    out = Path(args.output_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print(f"Report written: {out}")
    print(
        f"Totals => copilot_premium={sum(r['copilot_premium_requests'] for r in rows)}, "
        f"codex_tokens={sum(r['codex_tokens_total'] for r in rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
