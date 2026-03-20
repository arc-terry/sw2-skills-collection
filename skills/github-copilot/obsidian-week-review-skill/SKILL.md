---
name: obsidian-week-review-skill
description: Generate and optionally save weekly Obsidian diary summaries for terry-vault-v1 from Journal/01-daily week folders.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.1.0"
---

# Obsidian Week Review Skill

Use this skill when the user wants a weekly diary summary from `terry-vault-v1`, especially for a week folder under `Journal/01-daily/yyyy/mm/Www`.

## Defaults

- Vault root: `/mnt/d/obsidian/sync_valut/terry-vault-v1`
- Week input: explicit week path such as `Journal/01-daily/2026/03/W12`
- Default summary-note location: next to the week folder, for example `Journal/01-daily/2026/03/W12/2026-03-W12-summary.md`

## Workflow

1. Resolve the target week path.
2. Run the helper:
   `python3 scripts/obsidian_week_review_skill.py <week-path>`
3. If the user wants the summary saved as a note, rerun with:
   `python3 scripts/obsidian_week_review_skill.py <week-path> --write-note`
4. If needed, override the output path with `--note-path`.

## Output policy

- Always show the generated summary note content in the terminal.
- When writing the note, report the saved path.
- Keep the summary note layout aligned with the Obsidian vault conventions documented in `references/REFERENCE.md`.

## Quality gate

- Input week path resolves correctly under the vault root.
- Summary note contains the `table-of-contents` block near the top.
- `## Focus areas` uses `###` subsections for each detected area.
- Open tasks, completed tasks, key actions, and key blockers stay grounded in the parsed notes.

## Reference

- See `references/REFERENCE.md` for vault conventions, parser rules, and note-layout details.
