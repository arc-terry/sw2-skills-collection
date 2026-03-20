#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_VAULT_ROOT = Path("/mnt/d/obsidian/sync_valut/terry-vault-v1")
TASK_SECTION_ALIASES = {"tasks", "todo"}
IGNORED_FOCUS_HEADINGS = TASK_SECTION_ALIASES | {"note", "notes"}
BLOCKER_HEADING_KEYWORDS = (
    "issue",
    "cannot",
    "timeout",
    "failed",
    "blocker",
    "problem",
    "lacking",
    "sympton",
)
ACTION_LINE_PREFIXES = (
    "ask ",
    "enable ",
    "set ",
    "record ",
    "prioritize ",
    "plan ",
    "think about ",
)

HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*$")
CHECKBOX_PATTERN = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*?)\s*$")
BULLET_PATTERN = re.compile(r"^\s*[-*+]\s+(.*?)\s*$")


@dataclass(frozen=True)
class HeadingBlock:
    level: int
    heading: str
    lines: list[str]


@dataclass(frozen=True)
class TaskItem:
    text: str
    source: str
    status: str


@dataclass(frozen=True)
class HighlightItem:
    text: str
    source: str


@dataclass(frozen=True)
class FocusArea:
    name: str
    count: int
    sources: tuple[str, ...]


@dataclass(frozen=True)
class WeeklyReview:
    week_path: Path
    notes: list[Path]
    focus_areas: list[FocusArea]
    tasks: list[TaskItem]
    actions: list[HighlightItem]
    blockers: list[HighlightItem]

    @property
    def open_tasks(self) -> list[TaskItem]:
        return [item for item in self.tasks if item.status == "open"]

    @property
    def completed_tasks(self) -> list[TaskItem]:
        return [item for item in self.tasks if item.status == "done"]

    @property
    def other_task_items(self) -> list[TaskItem]:
        return [item for item in self.tasks if item.status == "unspecified"]


def normalize_heading(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text.strip().strip("#")).strip()
    return collapsed.lower()


def resolve_week_path(week_path_input: str, vault_root: Path = DEFAULT_VAULT_ROOT) -> Path:
    path = Path(week_path_input)
    if path.is_absolute():
        return path
    return vault_root / path


def build_default_note_path(week_path: Path) -> Path:
    parts = week_path.parts
    if len(parts) >= 3:
        year = parts[-3]
        month = parts[-2]
        week = parts[-1]
        if re.fullmatch(r"\d{4}", year) and re.fullmatch(r"\d{2}", month) and re.fullmatch(r"W\d{1,2}", week):
            return week_path / f"{year}-{month}-{week}-summary.md"
    return week_path / f"{week_path.name}-summary.md"


def build_week_label(week_path: Path) -> str:
    parts = week_path.parts
    if len(parts) >= 3:
        year = parts[-3]
        month = parts[-2]
        week = parts[-1]
        if re.fullmatch(r"\d{4}", year) and re.fullmatch(r"\d{2}", month) and re.fullmatch(r"W\d{1,2}", week):
            return f"{year}-{month}-{week}"
    return week_path.name


def discover_daily_notes(week_path: Path) -> list[Path]:
    if not week_path.exists():
        raise FileNotFoundError(f"Week folder does not exist: {week_path}")
    if not week_path.is_dir():
        raise NotADirectoryError(f"Week path is not a directory: {week_path}")

    notes = sorted(
        (
            path
            for path in week_path.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".md"
            and not path.name.endswith("-summary.md")
        ),
        key=lambda path: path.name,
    )
    if not notes:
        raise ValueError(f"No markdown notes found in week folder: {week_path}")
    return notes


def parse_heading_blocks(markdown_text: str) -> list[HeadingBlock]:
    blocks: list[HeadingBlock] = []
    current_heading: str | None = None
    current_level = 0
    current_lines: list[str] = []
    in_code_block = False

    def flush_current() -> None:
        nonlocal current_heading, current_level, current_lines
        if current_heading is not None:
            blocks.append(HeadingBlock(level=current_level, heading=current_heading, lines=current_lines))
        current_heading = None
        current_level = 0
        current_lines = []

    for raw_line in markdown_text.splitlines():
        if raw_line.strip().startswith("```"):
            in_code_block = not in_code_block
            if current_heading is not None:
                current_lines.append(raw_line)
            continue

        if in_code_block:
            if current_heading is not None:
                current_lines.append(raw_line)
            continue

        heading_match = HEADING_PATTERN.match(raw_line)
        if heading_match:
            flush_current()
            current_level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip().rstrip("#").strip()
            continue

        if current_heading is not None:
            current_lines.append(raw_line)

    flush_current()
    return blocks


def iter_meaningful_lines(lines: Iterable[str]) -> Iterable[str]:
    in_code_block = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped or stripped.startswith("![[") or stripped == "---":
            continue
        yield stripped


def extract_tasks(lines: Iterable[str], source: str) -> list[TaskItem]:
    tasks: list[TaskItem] = []

    for raw_line in iter_meaningful_lines(lines):
        checkbox_match = CHECKBOX_PATTERN.match(raw_line)
        if checkbox_match:
            status = "done" if checkbox_match.group(1).lower() == "x" else "open"
            text = checkbox_match.group(2).strip()
            if text:
                tasks.append(TaskItem(text=text, source=source, status=status))
            continue

        bullet_match = BULLET_PATTERN.match(raw_line)
        if bullet_match and not bullet_match.group(1).startswith("["):
            text = bullet_match.group(1).strip()
            if text:
                tasks.append(TaskItem(text=text, source=source, status="unspecified"))

    return tasks


def extract_points(lines: Iterable[str], source: str) -> list[HighlightItem]:
    points: list[HighlightItem] = []
    buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        text = " ".join(buffer).strip()
        if text:
            points.append(HighlightItem(text=text, source=source))
        buffer = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            flush_buffer()
            continue
        if stripped.startswith("![[") or stripped == "---":
            continue
        if not stripped:
            flush_buffer()
            continue

        checkbox_match = CHECKBOX_PATTERN.match(raw_line)
        if checkbox_match:
            flush_buffer()
            text = checkbox_match.group(2).strip()
            if text:
                points.append(HighlightItem(text=text, source=source))
            continue

        bullet_match = BULLET_PATTERN.match(raw_line)
        if bullet_match and not bullet_match.group(1).startswith("["):
            flush_buffer()
            text = bullet_match.group(1).strip()
            if text:
                points.append(HighlightItem(text=text, source=source))
            continue

        buffer.append(stripped)

    flush_buffer()
    return points


def dedupe_items(items: Iterable[HighlightItem]) -> list[HighlightItem]:
    seen: set[tuple[str, str]] = set()
    deduped: list[HighlightItem] = []
    for item in items:
        key = (item.text, item.source)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def canonicalize_focus_area_name(name: str) -> str:
    normalized = normalize_heading(name)
    if normalized in {"att", "at&t"}:
        return "AT&T"
    if normalized.startswith("tpe poc"):
        return "TPE POC"
    return name.strip()


def extract_focus_area_names(blocks: Iterable[HeadingBlock]) -> list[str]:
    names: list[str] = []
    for block in blocks:
        normalized = normalize_heading(block.heading)
        if block.level != 2 or normalized in IGNORED_FOCUS_HEADINGS:
            continue
        names.append(canonicalize_focus_area_name(block.heading))
    return names


def extract_blockers(blocks: Iterable[HeadingBlock], source: str) -> list[HighlightItem]:
    blockers: list[HighlightItem] = []
    for block in blocks:
        if block.level > 3:
            continue
        normalized = normalize_heading(block.heading)
        if any(keyword in normalized for keyword in BLOCKER_HEADING_KEYWORDS):
            blockers.append(HighlightItem(text=block.heading, source=source))
    return dedupe_items(blockers)


def extract_actions(blocks: Iterable[HeadingBlock], source: str) -> list[HighlightItem]:
    actions: list[HighlightItem] = []

    for block in blocks:
        normalized = normalize_heading(block.heading)
        if normalized == "solution":
            actions.extend(extract_points(block.lines, source))

        for line in iter_meaningful_lines(block.lines):
            if any(line.lower().startswith(prefix) for prefix in ACTION_LINE_PREFIXES):
                actions.append(HighlightItem(text=line, source=source))

    return dedupe_items(actions)


def build_weekly_review(week_path: Path) -> WeeklyReview:
    notes = discover_daily_notes(week_path)
    focus_area_counter: Counter[str] = Counter()
    focus_area_sources: dict[str, set[str]] = defaultdict(set)
    tasks: list[TaskItem] = []
    actions: list[HighlightItem] = []
    blockers: list[HighlightItem] = []

    for note_path in notes:
        blocks = parse_heading_blocks(note_path.read_text(encoding="utf-8"))
        source = note_path.name

        for block in blocks:
            if normalize_heading(block.heading) in TASK_SECTION_ALIASES:
                tasks.extend(extract_tasks(block.lines, source))

        focus_names = extract_focus_area_names(blocks)
        focus_area_counter.update(focus_names)
        for name in focus_names:
            focus_area_sources[name].add(source)

        actions.extend(extract_actions(blocks, source))
        blockers.extend(extract_blockers(blocks, source))

    focus_areas = [
        FocusArea(name=name, count=count, sources=tuple(sorted(focus_area_sources[name])))
        for name, count in focus_area_counter.most_common()
    ]

    return WeeklyReview(
        week_path=week_path,
        notes=notes,
        focus_areas=focus_areas,
        tasks=tasks,
        actions=dedupe_items(actions),
        blockers=dedupe_items(blockers),
    )


def stringify_items(items: Iterable[TaskItem | HighlightItem]) -> list[str]:
    return [f"- [{item.source}] {item.text}" for item in items]


def render_summary_note(review: WeeklyReview, note_path: Path, vault_root: Path = DEFAULT_VAULT_ROOT) -> str:
    week_name = build_week_label(review.week_path)
    try:
        source_week = review.week_path.relative_to(vault_root).as_posix()
    except ValueError:
        source_week = str(review.week_path)

    first_note = review.notes[0].name if review.notes else "n/a"
    last_note = review.notes[-1].name if review.notes else "n/a"
    focus_names = ", ".join(f"`{area.name}`" for area in review.focus_areas) or "none"

    lines = [
        "---",
        "tags:",
        "  - weekly-summary",
        f"source-week: {source_week}",
        "generated-by: obsidian-week-review-skill",
        "---",
        "",
        "```table-of-contents",
        "```",
        "",
        f"# {week_name} Summary",
        "",
        "## Weekly overview",
        "",
        f"- Reviewed {len(review.notes)} daily notes from `{first_note}` to `{last_note}`.",
        f"- Main focus areas this week were {focus_names}.",
        f"- Open tasks: {len(review.open_tasks)}. Completed tasks: {len(review.completed_tasks)}.",
        "",
        "## Focus areas",
        "",
    ]

    if review.focus_areas:
        for area in review.focus_areas:
            note_label = "note" if area.count == 1 else "notes"
            lines.extend(
                [
                    f"### {area.name}",
                    "",
                    f"- Appeared across {area.count} {note_label}.",
                    f"- Source notes: {', '.join(f'`{source}`' for source in area.sources)}.",
                    "",
                ]
            )
    else:
        lines.extend(["- No recurring focus areas detected.", ""])

    lines.extend(["## Open tasks", ""])
    lines.extend(stringify_items(review.open_tasks) or ["- No open tasks captured."])
    lines.extend(["", "## Completed this week", ""])
    lines.extend(stringify_items(review.completed_tasks) or ["- No completed tasks captured."])
    lines.extend(["", "## Key actions", ""])
    lines.extend(stringify_items(review.actions) or ["- No action-oriented lines captured."])
    lines.extend(["", "## Key blockers", ""])
    lines.extend(stringify_items(review.blockers) or ["- No blocker-like headings captured."])

    if review.other_task_items:
        lines.extend(["", "## Other task items", ""])
        lines.extend(stringify_items(review.other_task_items))

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a weekly Obsidian summary note from a Journal/01-daily week folder."
        )
    )
    parser.add_argument(
        "week_path",
        help="Week folder path to review, absolute or relative to the vault root.",
    )
    parser.add_argument(
        "--vault-root",
        default=str(DEFAULT_VAULT_ROOT),
        help="Vault root used when week_path is relative.",
    )
    parser.add_argument(
        "--write-note",
        action="store_true",
        help="Write the rendered summary note to disk in addition to printing it.",
    )
    parser.add_argument(
        "--note-path",
        help="Optional explicit output note path. Defaults to a summary note beside the week folder.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    vault_root = Path(args.vault_root)
    week_path = resolve_week_path(args.week_path, vault_root)

    try:
        review = build_weekly_review(week_path)
    except (FileNotFoundError, NotADirectoryError, ValueError, UnicodeDecodeError) as error:
        parser.exit(1, f"Error: {error}\n")

    note_path = Path(args.note_path) if args.note_path else build_default_note_path(week_path)
    note_content = render_summary_note(review, note_path, vault_root)
    print(note_content, end="")

    if args.write_note:
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(note_content, encoding="utf-8")
        print(f"Saved summary note: {note_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
