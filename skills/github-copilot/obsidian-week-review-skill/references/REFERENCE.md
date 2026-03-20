# Reference

## Vault defaults

- Vault root: `/mnt/d/obsidian/sync_valut/terry-vault-v1`
- Daily note location pattern: `Journal/01-daily/yyyy/mm/Www`
- Example week path: `Journal/01-daily/2026/03/W12`

## Current diary structure assumptions

- Each week folder contains daily markdown notes.
- Daily note content commonly uses:
  - `# NOTE`
  - `# TODO`
  - level-2 topic headings such as `AT&T`, `TPE POC`, and `Others`
  - level-3 issue or solution-style subsections
- Task extraction comes from `# TODO`.
- Focus areas come from level-2 headings under the note content.
- Blockers come from issue-like level-3 headings.
- Actions come from `Solution` sections and action-oriented lines such as `Ask ...`, `Enable ...`, `Record ...`, `Prioritize ...`.

## Summary note layout

Generated notes should follow this shape:

1. YAML frontmatter with `weekly-summary` tagging and source metadata
2. Obsidian Automatic Table Of Content block:

   ````
   ```table-of-contents
   ```
   ````

3. `# Wxx Summary`
4. `## Weekly overview`
5. `## Focus areas` with `###` subsections such as:
   - `### AT&T`
   - `### TPE POC`
   - `### Others`
6. `## Open tasks`
7. `## Completed this week`
8. `## Key actions`
9. `## Key blockers`

## Suggested validation command

From this skill folder:

```bash
python3 -m unittest scripts.test_obsidian_week_review_skill
```

## Example execution

Preview only:

```bash
python3 scripts/obsidian_week_review_skill.py Journal/01-daily/2026/03/W12
```

Preview and write the summary note:

```bash
python3 scripts/obsidian_week_review_skill.py Journal/01-daily/2026/03/W12 --write-note
```
