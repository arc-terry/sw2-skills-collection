---
name: seven-day-commit-overview-skill
description: Generate a 7-day commit overview with commits grouped by branch and branch-level change summaries.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.1.0"
---

# Seven-Day Commit Overview Skill

Use this skill when the user asks for a recent commit overview across branches.

## Output format (mandatory)
Return exactly these two sections in order:

1. `## New commits by branch (last 7 days)`
2. `## Branch change summary (last 7 days)`

## Scope rules
- Time window: rolling last 7 days from execution time.
- Branch scope: include only branches that have commits in the last 7 days.
- If no branches have commits in the window, still return both sections and state that no new commits were found.

## Workflow
1. Identify repository owner/name and execution time reference.
2. List branches in the repository.
3. Collect commits per branch and keep only commits authored in the last 7 days.
4. Remove duplicate commits across branches (for example, merged commits appearing in multiple refs) while keeping branch context where they are new.
5. Build section 1 by listing commits grouped under each branch, including SHA, author, date, and subject.
6. Build section 2 by summarizing branch-level change themes from collected commits (and diffs when available), focusing on what changed rather than raw commit counts.

## Quality gate
- Both required sections exist and are in the required order.
- Commit listings are grouped by branch and only include the last 7 days.
- Summaries are branch-specific and grounded in observed commit data.
