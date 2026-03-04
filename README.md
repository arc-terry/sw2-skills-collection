# sw2-skills-collection

Copilot CLI-first repository for collecting reusable agent skills, with an extensible structure for Claude Code and multi-agent skills.

## Structure

- `skills/github-copilot/`: primary skill collection target.
- `skills/claude-code/`: reserved for future expansion.
- `skills/multi-agent/`: reserved for future expansion.
- `registry/skills-index.yaml`: machine-readable index of all skills.
- `docs/`: taxonomy and contribution guidance.

## Quickstart

1. Copy `skills/github-copilot/template-skill/` to a new skill folder.
2. Update `SKILL.md` frontmatter (`name`, `description`) and instructions.
3. Add the skill entry to `registry/skills-index.yaml`.
4. Open a PR using `.github/pull_request_template.md` checklist.

## How to add a new skill

1. Create a folder under `skills/<platform>/<skill-name>/` (prefer `skills/github-copilot/` for now).
2. Add `SKILL.md` with YAML frontmatter:
   - required: `name`, `description`
   - optional: `license`, `compatibility`, `metadata`, `allowed-tools`
3. Ensure folder name matches frontmatter `name`.
4. Optionally add `references/`, `scripts/`, and `assets/`.
5. Add the skill entry to `registry/skills-index.yaml`.
6. Submit a PR and complete `.github/pull_request_template.md` checklist.

Tip: Copy `skills/github-copilot/template-skill/` as your starting point.
