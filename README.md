# sw2-skills-collection

Copilot CLI-first repository for reusable agent skills.

Current model: all skills live under `skills/general/`.  
When the collection grows, skills can be reorganized into more specific categories.


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
│   └── general/
│       ├── git-commit-message-skill/
│       ├── obsidian-week-review-skill/
│       ├── seven-day-commit-overview-skill/
│       └── template-skill/
├── LICENSE
└── README.md
```

### Major folders

- `skills/`: skill content. Each skill lives in `skills/general/<skill-name>/` and must include `SKILL.md`.
- `registry/`: machine-readable index for discovery (`registry/skills-index.yaml`).
- `docs/`: contributor guidance (`adding-a-skill.md`, `taxonomy.md`).
- `.github/`: pull request checklist and contribution process.

## Add a skill (quick start)

1. Copy `skills/general/template-skill/` to a new skill folder.
2. Update `SKILL.md` frontmatter:
   - required: `name`, `description`
   - optional: `license`, `compatibility`, `metadata`, `allowed-tools`
3. Ensure folder name matches `name` in frontmatter.
4. Add optional folders when needed: `references/`, `scripts/`, `assets/`.
5. Register the skill in `registry/skills-index.yaml`.
6. Open a PR and complete `.github/pull_request_template.md`.

For detailed rules, see `docs/adding-a-skill.md` and `docs/taxonomy.md`.

## Included skills

- `skills/general/template-skill/`: starter template for new skills.
- `skills/general/git-commit-message-skill/`: generates high-quality Conventional Commit messages with quality checks.
- `skills/general/seven-day-commit-overview-skill/`: generates a 7-day commit overview grouped by branch with branch-level summaries.
- `skills/general/obsidian-week-review-skill/`: generates and can save weekly Obsidian diary summary notes from `Journal/01-daily` week folders.
