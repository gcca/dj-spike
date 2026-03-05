---
description: Close a feature — mark complete, update index, archive, commit
allowed-tools: Read, Glob, Grep, Write, Shell
---

# Close Feature

Mark a feature as complete (or closed/deferred), update the index, archive the file, and commit.

## Input

Parse `$ARGUMENTS` for:

- **F number** (required unless inferable): e.g. `1` or `F-001`.
- **Disposition** (optional): `complete` (default), `closed`, or `deferred`.
- **Notes** (optional): additional context.

Examples:
- `/f8-close 1` — complete F-001
- `/f8-close 2 deferred blocked on X` — defer F-002
- `/f8-close 3 closed superseded by F-005` — close F-003
- `/f8-close` (no args) — infer from conversation context

When no F number is provided, identify the feature most recently discussed or worked on. If only one candidate is clear, use it and state which. If ambiguous, ask the user.

## Procedure

### 1. Locate and validate the F file

- Glob for `docs/features/F-{number}_*.md`.
- Read it to obtain the title and current status.
- If the file is already archived or cannot be found, report the issue and stop.

### 2. Update the F file

- Set `**Status:**` to `Complete`, `Closed`, or `Deferred`.
- For **Complete**: append `**Completed:** {YYYY-MM-DD}` after the status line.
- For **Closed / Deferred**: append `**Closed:** {YYYY-MM-DD}` if not already present.

### 3. Update FEATURE_INDEX.md

- Read `docs/features/FEATURE_INDEX.md`.
- Remove the F's row from **Active Features**.
- Insert it at the top of the appropriate section:
  - Complete -> **Completed** table (include date and notes).
  - Closed / Deferred -> **Deferred / Closed** table (include status and notes).

### 4. Update CHANGELOG.md (complete disposition only)

Skip this step for closed or deferred dispositions.

- Read `CHANGELOG.md`. If it does not exist, skip.
- Add an entry under `## [Unreleased]` in the matching subsection:
  - New functionality -> `### Added`
  - Behavioural change -> `### Changed`
  - Bug fix -> `### Fixed`
  - Removal -> `### Removed`
- Create the subsection if it does not yet exist under `[Unreleased]`.
- Format: `- Brief description (F-XXX)`

### 5. Archive the file

- Move the F file to `docs/features/archive/`.

### 6. Commit

Stage all related changes in a single atomic commit:
- Archived F file, deleted original path, `FEATURE_INDEX.md`, and `CHANGELOG.md` (when updated).
- Include any implementation files modified during this session.
- Commit message: `F-{number}: {title}`

## Output

Report:
- F number and title
- Disposition applied (Complete / Closed / Deferred)
- Index section updated
- Changelog entry added (if applicable)
- Archive destination
- Commit short hash
