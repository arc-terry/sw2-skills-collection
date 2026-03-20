# sw2-skills-collection

Copilot CLI-first repository for collecting reusable agent skills, with an extensible structure for Claude Code and multi-agent skills.


## Repository layout

```text
.
├── .github/
│   └── pull_request_template.md
├── docs/
│   ├── adding-a-skill.md
│   └── taxonomy.md
├── registry/
│   └── skills-index.yaml
├── skills/
│   ├── github-copilot/
│   │   ├── git-commit-message-skill/
│   │   │   ├── SKILL.md
│   │   │   ├── assets/
│   │   │   └── references/
│   │   ├── obsidian-week-review-skill/
│   │   │   ├── SKILL.md
│   │   │   ├── references/
│   │   │   └── scripts/
│   │   ├── seven-day-commit-overview-skill/
│   │   │   └── SKILL.md
│   │   └── template-skill/
│   │       ├── SKILL.md
│   │       ├── assets/
│   │       ├── references/
│   │       └── scripts/
│   ├── claude-code/
│   └── multi-agent/
├── LICENSE
└── README.md
```

### Major folders

- `skills/`: core content area; each skill lives in `skills/<platform>/<skill-name>/` with a required `SKILL.md`.
- `registry/`: central machine-readable index (`skills-index.yaml`) used to track and discover skills.
- `docs/`: contributor-facing documentation for taxonomy rules and skill authoring workflow.
- `.github/`: pull request process/checklist to keep submissions consistent.

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


## Included skills

- `skills/github-copilot/template-skill/`: starter template for new skills.
- `skills/github-copilot/git-commit-message-skill/`: generates high-quality Conventional Commit messages with quality checks.
- `skills/github-copilot/seven-day-commit-overview-skill/`: generates a 7-day commit overview grouped by branch with branch-level summaries.
- `skills/github-copilot/obsidian-week-review-skill/`: generates and can save weekly Obsidian diary summary notes from `Journal/01-daily` week folders.
