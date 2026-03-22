---
name: seven-day-commit-overview-skill
description: Generate a 7-day commit overview with commits grouped by branch and branch-level change summaries.
compatibility: Designed for GitHub Copilot CLI workflows.
metadata:
  author: sw2-skills-collection
  version: "0.4.0"
---

# Seven-Day Commit Overview Skill

Use this skill when the user asks for a recent commit overview across branches, optionally with the result saved as a Markdown report.

## When to use

- The user wants a recent commit overview for a repository.
- The user wants commits grouped by branch for the last 7 days.
- The user wants a Markdown report generated and optionally saved to a file.

## Output format (mandatory)
Return exactly these two sections in order:

1. `## New commits by branch (last 7 days)`
2. `## Branch change summary (last 7 days)`

- Always produce those two sections in chat unless the user explicitly asks for file output only.
- If the user asks to save the report to a file, keep the same section headings and content structure in the saved file.

## Scope rules
- Time window: rolling last 7 days from execution time.
- Branch scope: include only branches that have commits in the last 7 days.
- Repository scope: if the repository identifier is ambiguous, clarify it before collecting data.
- If no branches have commits in the window, still return both sections and state that no new commits were found.

## Workflow
1. Identify repository owner/name and execution time reference.
2. If the repository name is ambiguous, confirm the intended repository before continuing.
3. List branches in the repository.
4. Collect commits per branch and keep only commits authored in the last 7 days.
5. Remove duplicate commits across branches (for example, merged commits appearing in multiple refs) while keeping branch context where they are new.
6. Build section 1 by listing commits grouped under each branch, including SHA, author, date, and subject.
7. Build section 2 by summarizing branch-level change themes from collected commits, focusing on what changed rather than raw commit counts.
8. If the user asked only for a review/overview, return the report in chat and do not write a file.
9. If file output is requested, determine the target path:
   - If the user provided a path, use that exact path candidate.
   - If no path is provided, propose `<repo-name>_<week-count>_report.md` in the current working directory.
   - For this skill, `week-count` is the current ISO week-of-year based on the execution date, unless the user explicitly requests a different week numbering scheme.
10. Always ask for explicit confirmation of the final output path before writing, even when the user already provided a concrete path.
11. Write the report only after confirmation.
12. After writing, acknowledge the exact saved file path.

## Quality gate
- Both required sections exist and are in the required order.
- Commit listings are grouped by branch and only include the last 7 days.
- Summaries are branch-specific and grounded in observed commit data.
- If the repository identifier was ambiguous, it was clarified before data collection.
- If the user asked only for a review/overview, no file was written.
- If file output was requested, path confirmation was obtained before writing.
- If no path was provided, the default filename pattern `<repo-name>_<week-count>_report.md` was used as the proposed path.
- If a default filename was proposed, `week-count` was derived from the current ISO week-of-year at execution time unless the user requested another scheme.
- Final response includes the exact output path that was written.
