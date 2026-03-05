# DjSpike — Agent Guidelines

## Tech Stack

- **Python**
- **Django**
- **Django REST Framework**
- **Django Filter**
- **Gunicorn** (WSGI server)
- **PostgreSQL**

**Always consult `pyproject.toml`** for dependency names, versions, and constraints.

## Python Environment

- A Python virtual environment **must** be active throughout the session.
- If none is detected, **notify the user** and wait for them to activate one before proceeding.
- **Do not continue** until a virtual environment is confirmed.

## Pre-commit

### Scoped Execution

Development runs **multiple coding workers** in parallel. Each worker executes pre-commit **only against the files it touched**:

```bash
pre-commit run --files path/to/file1 path/to/file2 ...
```

Feature documents specify which files belong to each worker. Every worker runs the command above after making changes.

### Auto-correction Policy

- **Auto-correct** formatting issues only (e.g., black, ruff formatting, trailing whitespace).
- **Do not auto-correct** any of the following:
  - Security findings (e.g., bandit)
  - Linting errors requiring design decisions
  - Type errors
  - Test failures
- For non-formatting issues, **ask the user** for context or explicit guidance before making changes.

## Feature (F) Management

Features are tracked in `docs/features/`. Each feature has a dedicated file (`F-XXX_TITLE.md`) and is registered in `FEATURE_INDEX.md`.

### Lifecycle

| Stage | Description |
|-------|-------------|
| **Planned** | Identified but not yet designed |
| **Design** | Actively being designed (code exploration, plan drafting) |
| **Open** | Design complete; ready for implementation |
| **In Progress** | Implementation underway |
| **Pending Verification** | Code complete; awaiting verification |
| **Complete** | Verified and ready to archive |
| **Deferred** | Postponed (low priority or blocked) |
| **Closed** | Will not be implemented (superseded or unnecessary) |

### Conventions

- **File path**: `docs/features/F-XXX_TITLE.md` (XXX = zero-padded number)
- **Commit message**: `F-XXX: Brief description`
- **Numbering**: next number = highest across all index sections + 1
- **Source of truth**: the F file's status takes precedence over the index
- **Archiving**: completed features move to `docs/features/archive/`

### Index Structure

`FEATURE_INDEX.md` contains four sections:

1. **Active Features** — all non-complete features, sorted by F number
2. **Completed** — finished features, newest first
3. **Deferred / Closed** — features that will not proceed
4. **Backlog** — low-priority or blocked items parked for later

### Httpie Examples

Every feature document **must** include an **Httpie examples** section with annotated commands suitable for both manual testing and agentic end-to-end verification.

Use `http` (httpie) against `localhost:8000`. Document each endpoint with the exact command and expected outcome:

```bash
# List (empty)
http :8000/api/v1/resources/

# Create
http POST :8000/api/v1/resources/ name="Example"

# Retrieve
http :8000/api/v1/resources/1/
```

### Inline Annotations (`%%`)

Lines beginning with `%%` are **direct instructions from the user** embedded in any file. When encountered:

- Treat each `%%` line as an actionable directive — answer questions, expand content, provide feedback, or apply changes as requested.
- Address **every** `%%` annotation in the file; never skip one.
- Remove each `%%` line after acting on it.
- If an annotation is ambiguous, ask for clarification before proceeding.

This mechanism enables a precise review workflow: the engineer annotates files inline, then asks the agent to resolve all annotations — more targeted than conversational back-and-forth for complex designs.

### Changelog

- **Format**: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- **Trigger**: `/f8-close` (complete disposition only) appends entries under `[Unreleased]`
- **Traceability**: each entry ends with `(F-XXX)`
- **Subsections**: Added, Changed, Fixed, Removed
- **Releasing**: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and insert a fresh `[Unreleased]` header
