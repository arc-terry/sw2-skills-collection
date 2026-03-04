# Taxonomy

## Platform layers

- `github-copilot` (primary): skills optimized for Copilot CLI workflows.
- `claude-code` (secondary): skills specific to Claude Code behavior.
- `multi-agent` (secondary): skills or references intended to be shared across agent ecosystems.

## Naming rules

- Skill folder path: `skills/<platform>/<skill-name>/`
- `<skill-name>` must match `name` in `SKILL.md` frontmatter.
- Use lowercase letters, numbers, and hyphens.

## Category tagging

Within each platform, classify skills in `registry/skills-index.yaml` using tags such as:

- `development`
- `automation`
- `research`
- `docs`
- `productivity`
