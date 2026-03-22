# Taxonomy

## Current storage model

- For now, all skills are stored under `skills/general/`.
- Current folder path pattern: `skills/general/<skill-name>/`.
- This keeps contribution simple while the skill count is still small.

## Future categorization model

- When the collection grows, skills can be moved into type-based folders:
  `skills/<type>/<skill-name>/`.
- Suggested future types include:
  - `development`
  - `automation`
  - `research`
  - `docs`
  - `productivity`
  - additional types as needed

## Naming rules

- Skill folder path (current): `skills/general/<skill-name>/`
- `<skill-name>` must match `name` in `SKILL.md` frontmatter.
- Use lowercase letters, numbers, and hyphens.

## Category tagging

Even when stored in `general`, each skill should still carry meaningful tags in
`registry/skills-index.yaml`, such as:

- `development`
- `automation`
- `research`
- `docs`
- `productivity`
