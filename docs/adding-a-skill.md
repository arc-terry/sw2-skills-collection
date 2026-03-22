# Adding a Skill

1. Create a new folder under `skills/general/<skill-name>/`.
2. Add `SKILL.md` with YAML frontmatter:
   - required: `name`, `description`
   - optional: `license`, `compatibility`, `metadata`, `allowed-tools`
3. Add optional folders only if needed:
   - `references/`
   - `scripts/`
   - `assets/`
4. Register your skill in `registry/skills-index.yaml`.
5. Submit a PR and complete the checklist.

Notes:
- For now, all skills are stored in `general` to keep the structure simple.
- Keep categorization intent in `tags`; folders can be split by type later.
