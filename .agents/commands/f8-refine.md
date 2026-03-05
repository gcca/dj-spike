---
description: Explore any F-enabled project — overview, feature history, recent activity
allowed-tools: Task, Read, Glob, Grep
---

# Explore Project

Build a rapid snapshot of the project by dispatching parallel subagents to gather context from three distinct angles.

## Procedure

### 1. Dispatch parallel subagents

Launch all three subagents **in a single message** (one Task call each):

#### Agent 1 — Project Overview

Examine the project root to determine what the project does and how it is structured:

1. Read foundational docs (`AGENTS.md`, `README.md`, and any top-level guides).
2. Glob for top-level files and key subdirectories to map the directory layout.
3. Identify the tech stack from config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, etc.).
4. Note any warnings, constraints, or non-obvious conventions from `AGENTS.md`.

Return: project name, purpose, tech stack, directory layout, notable constraints.

#### Agent 2 — Feature History

Survey the F system to understand past and planned work:

1. Read `docs/features/FEATURE_INDEX.md`.
2. Read every active (non-Complete) F file.
3. List files under `docs/features/archive/` to gauge completed work.
4. Search the git log for commits matching the `F-` pattern (last 20).

Return: active features table, archived feature count, recent F commit summary.

#### Agent 3 — Recent Activity

Assess current development momentum:

1. Retrieve the last 15 commits with messages.
2. Identify files changed in the last 5 commits.
3. Report the current branch name and its offset from main.
4. Check `git status` for any staged or unstaged changes.

Return: recent commit summary, files in flux, branch status, uncommitted work.

### 2. Synthesize results

Merge the three agent outputs into a single briefing:

**Project Overview**
- Name, purpose, and tech stack (Agent 1)
- Key constraints or gotchas

**Feature Status**
- Active features table (Agent 2)
- Archived count and noteworthy completions

**Recent Activity**
- Development momentum summary (Agent 3)
- Current branch and any open work

**Quick Reference**
- **Project:** {name}
- **Branch:** {current branch}
- **Active Fs:** {count}
- **Recent focus:** {summary of last few commits}

## Working Directory

Use the current working directory as the project root.
