# sw2-skills-collection

Copilot CLI-first repository for reusable agent skills.

Current model: all skills live under `skills/general/`.  
When the collection grows, skills can be reorganized into more specific categories.


- [sw2-skills-collection](#sw2-skills-collection)
  - [Usage](#usage)
    - [User](#user)
    - [Developer](#developer)
    - [Maintainer](#maintainer)
  - [Introduction](#introduction)
    - [Repository layout](#repository-layout)
    - [Major folders](#major-folders)
    - [Add a skill (quick start)](#add-a-skill-quick-start)



## Usage

### User

Download the `sw2-skills-collection` repository first:

```bash
# Example local path (customize for your environment)
SKILL_RESOURCE_DIR="$HOME/ai/skill-resource"
SKILL_REPO_DIR="$SKILL_RESOURCE_DIR/sw2-skills-collection"

mkdir -p "$SKILL_RESOURCE_DIR"
cd "$SKILL_RESOURCE_DIR"
git clone https://github.com/arc-terry/sw2-skills-collection.git
```

Use Copilot CLI step by step:

```bash
# Create a daily workspace
WORKSPACE_DIR="$HOME/ai/workspace-$(date +'%Y%m%d')"
mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

# Launch Copilot CLI
copilot

# In Copilot CLI, load and verify skills
# (run these after Copilot starts)
/skills add $SKILL_REPO_DIR
/skills list

# Examples

```

### Developer

todo: to be completed

### Maintainer

todo: to be completed

## Introduction

### Repository layout

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

### Add a skill (quick start)

1. Copy `skills/general/template-skill/` to a new skill folder.
2. Update `SKILL.md` frontmatter:
   - required: `name`, `description`
   - optional: `license`, `compatibility`, `metadata`, `allowed-tools`
3. Ensure folder name matches `name` in frontmatter.
4. Add optional folders when needed: `references/`, `scripts/`, `assets/`.
5. Register the skill in `registry/skills-index.yaml`.
6. Open a PR and complete `.github/pull_request_template.md`.

For detailed rules, see `docs/adding-a-skill.md` and `docs/taxonomy.md`.
