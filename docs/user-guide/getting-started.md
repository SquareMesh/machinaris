# Getting Started with the Project Template

This template provides a complete Claude Code agent workflow for any software project. It includes session management, decision tracking, knowledge curation, design enforcement, and 15 slash commands — all project-agnostic and ready to customize.

---

## Quick Start

1. **Copy this folder** to your new project location
2. **Open Claude Code** in the new folder
3. **Claude will automatically detect the unconfigured template** and prompt you to run `/setup`
4. **The setup wizard** asks 6 groups of questions (project identity, tech stack, architecture, hard rules, code conventions, knowledge categories) and configures everything for you

That's it. The wizard handles: CLAUDE.md, settings.json, .gitignore, design docs, progress.html, knowledge folders, and git init.

### Manual Setup (alternative)

If you prefer to configure manually instead of using the wizard:

1. **Customize CLAUDE.md** — fill in the `TEMPLATE NOTE` sections (see [what-to-customize.md](what-to-customize.md))
2. **Update `.claude/settings.json`** — add build tool permissions for your stack
3. **Update `.gitignore`** — uncomment the relevant language sections
4. **Create your first design doc** in `docs/design/`
5. **Remove the `TEMPLATE_UNCONFIGURED` marker** from the top of CLAUDE.md
6. **Start a session** with `/session-start`

---

## What's Included

### Agent Tracking (`.agent/`)

| File | Purpose |
|---|---|
| `CHANGE_HISTORY.md` | Append-only log of every functional decision |
| `OPEN_ISSUES.md` | Active issues with priority, description, reproduction steps |
| `RESOLVED_ISSUES.md` | Closed issues with root cause and fix record |
| `TODO.md` | Lightweight observations not yet analyzed |
| `DESIGN_INDEX.md` | Maps design doc sections to implementation status |
| `stack/` | Push/pop response bookmarks for recalling past analysis |

These files are maintained by the agent throughout development and committed alongside code. They provide full context continuity across sessions.

### Slash Commands (`.claude/commands/`)

#### Session Management
| Command | What it does |
|---|---|
| `/session-start` | Checks all tracking files, reports status, flags drift |
| `/session-end` | Captures knowledge, syncs issues/todos, updates memory |
| `/commit` | Syncs tracking files and creates a git checkpoint |

#### Tracking
| Command | What it does |
|---|---|
| `/capture-issue [title]` | Logs issue with auto-incrementing ID and priority |
| `/resolve-issue [number]` | Moves issue to resolved with full resolution record |
| `/capture-todo [desc]` | Logs lightweight item for future exploration |
| `/capture-knowledge [topic]` | Writes structured research entry to `docs/knowledge/` |
| `/capture-scenario [area] [title]` | Captures design validation scenario |

#### Design Management
| Command | What it does |
|---|---|
| `/design-review [focus]` | Reviews design docs for quality, gaps, blockers |
| `/design-update [doc] [section]` | Updates design doc and index atomically |
| `/design-audit [scope]` | Audits code against design docs for drift/violations |

#### Response Stack
| Command | What it does |
|---|---|
| `/push [N] [title]` | Saves a response for later recall |
| `/pop [N]` | Recalls the Nth most recent saved response |
| `/stack` | Lists all saved responses |

### Documentation Structure (`docs/`)

```
docs/
├── design/          ← Authoritative design documents
│   └── CLAUDE.md    ← Navigation guide for design docs
├── reviews/         ← Sequenced design review snapshots (auto-numbered)
├── scenarios/       ← Concrete situations validating design
├── knowledge/       ← Research and findings
│   ├── research/    ← Domain-specific research
│   ├── patterns/    ← Code patterns, architecture idioms
│   ├── algorithms/  ← Algorithm comparisons and analysis
│   └── tools/       ← Tooling, setup, configuration notes
├── reference/       ← External source material
│   └── reviews/     ← Agent analysis of reference material
└── project/         ← Progress tracking
```

---

## Session Workflow

### Starting a Session
The agent reads all tracking files and reports:
- Design index status (drift, blocked sections)
- Open issues by priority
- Pending TODOs
- Unresolved follow-ups from change history

### During a Session
- Functional decisions are recorded in CHANGE_HISTORY
- Issues are logged as discovered
- Knowledge entries are written for anything researched
- Design docs are checked before writing code

### Ending a Session
The agent:
1. Captures any un-recorded knowledge
2. Syncs change history, issues, and TODOs
3. Updates the design index
4. Writes a LAST SESSION block to memory for next-session continuity
5. Outputs a summary of everything tracked

### Mid-Session Checkpoint
Use `/commit` to sync all tracking files and create a git commit without ending the session.

---

## Design Enforcement

The template enforces a "design-first" workflow:

1. **Before writing code** — the agent identifies which design doc covers the work and checks for conflicts
2. **Hard rules** — defined in CLAUDE.md Section 4.2, these are never broken silently
3. **Design challenges** — when the agent spots a conflict, it presents options with tradeoffs instead of guessing
4. **Design index** — tracks implementation status per design section, flags drift when code diverges

This prevents silent design violations and ensures decisions are captured for future context.
