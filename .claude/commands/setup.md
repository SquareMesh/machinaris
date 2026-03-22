---
description: First-time project setup wizard — configure the template for your project
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Project Setup Wizard

Walk the user through configuring this project template. Ask questions one step at a time, wait for answers, then apply changes.

**Important:** This is an interactive wizard. Ask one group of related questions at a time, wait for the user's response, then proceed to the next group. Do NOT ask all questions at once.

## Pre-Check

Verify the `TEMPLATE_UNCONFIGURED` marker exists in CLAUDE.md. If it does not, this project is already configured — inform the user and stop.

## Step 1: Project Identity

Ask the user:

```
PROJECT SETUP — Step 1/6: Identity

1. What is the project name?
2. In 1-2 sentences, what does this project do?
3. What type of project is this? (e.g., web API, CLI tool, library, desktop app, game, mobile app)
```

Wait for response before continuing.

## Step 2: Tech Stack

Based on the project type, ask:

```
PROJECT SETUP — Step 2/6: Tech Stack

1. What programming language(s)? (e.g., Rust, TypeScript, Python, Go)
2. What framework(s) if any? (e.g., Axum, Next.js, FastAPI, none)
3. What database if any? (e.g., PostgreSQL, SQLite, MongoDB, none)
4. Any other key dependencies or infrastructure? (e.g., Redis, Docker, message queue)
```

Wait for response before continuing.

## Step 3: Architecture

Ask:

```
PROJECT SETUP — Step 3/6: Architecture

1. What are the main components or layers? (e.g., "handlers → services → repositories",
   "CLI → core library", "frontend + backend API")
2. Any strict boundaries? (e.g., "core must not depend on web framework",
   "no database access outside the repo layer")
3. How should the source code be organized? (e.g., "src/ with modules",
   "monorepo with packages", "workspace with crates")
```

Wait for response before continuing.

## Step 4: Hard Rules

Explain what hard rules are, then ask:

```
PROJECT SETUP — Step 4/6: Hard Rules

Hard rules are non-negotiable constraints I will NEVER break silently.
They typically cover: security, architecture boundaries, code quality, and data integrity.

Based on what you've told me, I'd suggest these hard rules:
[List 4-6 suggested rules based on the tech stack and architecture from Steps 2-3.
For example, for a web API:
  - No secrets in source code
  - All input validated at the boundary
  - Database access only through repository layer
  - No unwrap()/panic in library code
  - Typed errors, never raw strings]

Would you like to use these, modify them, or define your own?
```

Wait for response before continuing.

## Step 5: Code Conventions

Ask:

```
PROJECT SETUP — Step 5/6: Code Conventions

1. What build command(s) should I use? (e.g., "cargo build", "npm run build", "go build ./...")
2. What test command(s)? (e.g., "cargo test", "npm test", "pytest")
3. What linter/formatter? (e.g., "cargo clippy + cargo fmt", "eslint + prettier", "ruff")
4. Any naming conventions? (e.g., "snake_case for files", "PascalCase for components")
5. Commit message style? (e.g., "[scope] description", "conventional commits", "free form")
```

Wait for response before continuing.

## Step 6: Knowledge Categories

Ask:

```
PROJECT SETUP — Step 6/6: Knowledge Organization

The docs/knowledge/ folder stores research and findings. Default subfolders are:
  - research/    — domain-specific research
  - patterns/    — code patterns, architecture decisions
  - algorithms/  — algorithm comparisons
  - tools/       — tooling, setup, configuration

Would you like to keep these, or rename them for your domain?
(e.g., for a web app: api/, database/, security/, infrastructure/)
```

Wait for response before continuing.

## Apply Configuration

Once all answers are collected, apply changes to these files. **Make all edits, then show a summary.**

### 1. Update CLAUDE.md

**Section 1 — Project Identity:** Replace the generic description with the project name, type, and tech stack from Steps 1-2.

**Section 3 — Design Document Hierarchy:** Create an initial structure based on the project type. Create placeholder design docs if it makes sense (at minimum an OVERVIEW.md in docs/design/).

**Section 4.2 — Hard Rules:** Replace the placeholder rules with the confirmed rules from Step 4.

**Section 9 — Code Quality Standards:** Replace the generic standards with language-specific conventions from Step 5. Include the build, test, and lint commands. Update the commit message format.

**Remove the `TEMPLATE_UNCONFIGURED` marker** — delete the two HTML comment lines at the top of CLAUDE.md.

### 2. Update .claude/settings.json

Add build tool permissions based on the tech stack:
- Rust: `cargo build*`, `cargo test*`, `cargo check*`, `cargo clippy*`, `cargo run*`, `cargo fmt*`
- Node.js: `npm run*`, `npm test*`, `npm install*`, `npx *`
- Python: `python *`, `pytest*`, `pip install*`, `uv *`
- Go: `go build*`, `go test*`, `go run*`, `go vet*`
- Add any other relevant commands from Step 5.

### 3. Update .gitignore

Uncomment or add the relevant language-specific ignore patterns.

### 4. Update docs/design/CLAUDE.md

Replace the placeholder with the initial design document listing.

### 5. Create docs/design/OVERVIEW.md

Write an initial project overview document based on Steps 1-3:

```markdown
# [Project Name] — Overview

## What This Is
[Description from Step 1]

## Project Type
[From Step 1]

## Tech Stack
[From Step 2]

## Architecture
[From Step 3]

## Key Constraints
[Hard rules from Step 4, in prose form]
```

### 6. Update docs/knowledge/ subfolders

If the user chose custom subfolder names in Step 6:
- Rename the existing subfolders
- Update the subfolder list in CLAUDE.md Section 8
- Update `.claude/commands/capture-knowledge.md` Step 1

### 7. Update docs/project/progress.html

Update the `<h1>` tag with the project name and set an appropriate phase badge.

### 8. Update .claude/commands/capture-knowledge.md

Update the subfolder list in Step 1 to match any renamed knowledge folders.

### 9. Initialize git (if not already a repo)

Check if `.git/` exists. If not, run `git init`.

## Summary Output

After all changes are applied:

```
SETUP COMPLETE

Project: [name]
Type: [type]
Stack: [language + framework + database]
Hard rules: [count] defined
Build: [command]
Test: [command]

Files updated:
  - CLAUDE.md (identity, rules, standards)
  - .claude/settings.json (build permissions)
  - .gitignore (language patterns)
  - docs/design/CLAUDE.md (doc listing)
  - docs/design/OVERVIEW.md (created)
  - docs/project/progress.html (project name)
  [- docs/knowledge/ subfolders (renamed) — if applicable]

You're ready to go. Start working or run /session-start to begin a tracked session.
```
