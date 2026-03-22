# Commit Message Policy

## Required format
Use Conventional Commits header format:

`<type>(optional-scope): <subject>`

Examples:
- `feat(parser): add array literal support`
- `fix(auth): handle expired refresh token`
- `docs(readme): clarify setup steps`

## Allowed types
- `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`, `style`

## Quality checklist
- Subject describes the change clearly and specifically.
- Subject uses imperative mood (e.g., "add", "fix", "remove").
- Subject is concise (target ~50 chars, avoid trailing period).
- Add body when context is needed; explain what changed and why.
- Mark breaking changes with `!` in header and/or `BREAKING CHANGE:` footer.

## Body and footer guidance
- Keep a blank line between header and body.
- Wrap long body lines around ~72 chars when practical.
- Use footers for references, e.g. `Refs: #123`.
