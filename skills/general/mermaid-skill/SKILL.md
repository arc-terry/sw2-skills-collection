---
name: mermaid-skill
description: Generate Mermaid diagrams from natural language, partial/invalid Mermaid, or embedded Mermaid blocks. Use when the user asks to draw or produce diagrams in Mermaid.
---

# Mermaid Agent

Follow this workflow when producing Mermaid diagrams.

## Core workflow

1. Read `references/mermaid-skill.md` before generating Mermaid.
2. If syntax policy or source provenance is relevant, read `references/mermaid-syntax-sync.md`.
3. Extract Mermaid intent and normalize input.
4. Infer diagram type and direction using the reference matrix.
5. Apply strict syntax rules and project conventions from the reference.
6. Apply visual styling rules and interaction rules from the reference.
7. Output:
   - Mermaid code block
   - Change log (concise list of key fixes)

## Output constraints

- Keep node labels short; avoid brackets or long strings inside labels.
- Quote labels with special characters.
- Do not mix C4 DSL with flowchart DSL in the same block.
- Apply `style` with both `fill` and `stroke`.

## References

- `references/mermaid-skill.md`
- `references/mermaid-syntax-sync.md`
