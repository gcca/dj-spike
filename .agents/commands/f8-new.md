---
description: Create a new feature file and register it in the index
allowed-tools: Read, Glob, Grep, Write, Shell
---

# New Feature

Register a feature by generating its F file and adding an entry to the index.

## Input

Title or short description of the feature: `$ARGUMENTS`

If no argument is supplied, prompt the user for a title and a brief description.

## Procedure

### 1. Resolve the F identifier

- Read `docs/features/FEATURE_INDEX.md`.
- Scan all sections (Active, Completed, Deferred, Backlog) and find the highest existing F number.
- Assign the next sequential number (start at 1 when no features exist). Zero-pad to three digits: `F-001`, `F-002`, etc.
- Derive a filename-safe slug from `$ARGUMENTS` in `UPPER_SNAKE_CASE`.

### 2. Generate the F file

- Use `docs/features/FEATURE_TEMPLATE.md` as the base structure.
- Save to `docs/features/F-{number}_{SLUG}.md`.
- Populate the F number, title, and set Status to **Open**.
- If the user provided sufficient context, fill in the Problem and Solution sections; otherwise leave them as placeholders.

### 3. Register in the index

- Append a row to the **Active Features** table in `FEATURE_INDEX.md`.
- Include the F number, title, status (`Open`), and effort/priority when known.

## Output

Print the new F number, the file path, and which sections still need the user's input.

Do **not** commit — the user will complete the remaining details first.
