---
name: git-commit-message-skill
description: Draft high-quality git commit messages using a mandatory Conventional Commits format and a concise quality checklist.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.1.0"
---

# Git Commit Message Skill

Use this skill when the user asks to write, improve, or validate git commit messages.

## Output policy (mandatory)
All generated commit messages must follow Conventional Commits:

`<type>(optional-scope): <subject>`

## Workflow
1. Inspect staged changes and infer the primary intent.
2. Select the best commit type (`feat`, `fix`, `docs`, etc.).
3. Add scope only if it adds useful clarity.
4. Write an imperative subject line.
5. Add body text only when needed to explain what/why.
6. Add footer lines for issue references or breaking changes.

## Quality gate
Before finalizing, check:
- Header is valid Conventional Commits syntax.
- Subject is specific, imperative, and concise.
- No trailing period in subject.
- Body (if present) explains context, not implementation noise.
- Breaking changes are explicitly marked.

## Examples
- `fix(api): prevent nil pointer on empty payload`
- `feat(cli): add --dry-run option for sync command`
- `docs(contributing): add commit message examples`

## Reference
- See `references/COMMIT_POLICY.md` for policy details.
