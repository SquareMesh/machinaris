# What to Customize

When starting a new project from this template, these are the specific sections that need to be filled in or adapted. Each section is marked with `<!-- TEMPLATE NOTE -->` comments in the source files.

---

## 1. CLAUDE.md — Required Changes

### Section 1: Who You Are
**What to change:** Update the project description from generic to your specific project.

**Before:**
```
You are the primary development agent for this project.
```

**After (example):**
```
You are the primary development agent for a Rust web API serving a recipe management platform.
```

### Section 3: Design Document Hierarchy
**What to change:** Define your actual design documents and their priority order.

**Before:**
```
└── [project-specific design docs] ← Add as project grows
```

**After (example):**
```
├── OVERVIEW.md               ← Project identity, goals, constraints
├── API_DESIGN.md             ← Endpoints, auth, error handling
├── DATA_MODEL.md             ← Database schema, entities, relationships
└── DEPLOYMENT.md             ← Infrastructure, CI/CD, environments
```

### Section 4.2: Hard Rules
**What to change:** Define your project's non-negotiable rules. These are rules the agent will refuse to break.

**Before:**
```
RULE-1  [Define your first hard rule]
RULE-2  [Define your second hard rule]
```

**After (example):**
```
RULE-1  No secrets in source code. Use environment variables via dotenvy.
RULE-2  All external input validated at the handler boundary. Never trust raw input in service layer.
RULE-3  Database access only through the repository layer. No raw SQL in handlers or services.
RULE-4  All API endpoints return typed error responses, never raw strings or panics.
RULE-5  No unwrap() in library code. Use ? with typed errors. unwrap() only in tests and main.rs.
```

### Section 9: Code Quality Standards
**What to change:** Replace the generic standards with your language and framework conventions.

**Before:**
```
### General Standards
- Every public type/function must have a doc comment
```

**After (example):**
```
### Rust-Specific
- Every public type must have a doc comment
- Public functions state their invariants with `# Panics` and `# Errors` sections
- Errors are typed via thiserror, never raw strings
- No unwrap() in library code — only in tests and main.rs bootstrap
- Use ? with typed errors throughout
```

---

## 2. `.claude/settings.json` — Add Build Permissions

**What to change:** Add permissions for your project's build tools, test runners, and other CLI commands.

**Before:**
```json
{
  "permissions": {
    "allow": [
      "Skill(*)",
      "Edit",
      "Write",
      "Bash(git status*)",
      ...
      "Bash(mkdir *)"
    ]
  }
}
```

**Add for Rust:**
```json
"Bash(cargo build*)",
"Bash(cargo test*)",
"Bash(cargo check*)",
"Bash(cargo clippy*)",
"Bash(cargo run*)",
"Bash(cargo fmt*)"
```

**Add for Node.js:**
```json
"Bash(npm run*)",
"Bash(npm test*)",
"Bash(npm install*)",
"Bash(npx *)"
```

**Add for Python:**
```json
"Bash(python *)",
"Bash(pytest*)",
"Bash(pip install*)",
"Bash(uv *)"
```

---

## 3. `.gitignore` — Uncomment Your Language

**What to change:** Uncomment the relevant sections for your tech stack.

For a Rust project, uncomment:
```
/target/
```

For a Node.js project, uncomment:
```
node_modules/
/dist/
```

Add any project-specific ignores (e.g., database files, generated code).

---

## 4. `docs/design/CLAUDE.md` — Add Your Design Docs

**What to change:** Replace the placeholder with your actual design document listing.

As you create design documents, register them here so the agent knows where to find information about each topic.

---

## 5. `docs/knowledge/` — Rename Subfolders (Optional)

The default subfolders are generic:
```
knowledge/
├── research/      ← Domain-specific research
├── patterns/      ← Code patterns, architecture
├── algorithms/    ← Algorithm comparisons
└── tools/         ← Tooling notes
```

You may want to rename these to match your domain. For example, a web project might use:
```
knowledge/
├── api/           ← API design patterns, REST/GraphQL research
├── database/      ← Schema design, query optimization, migration strategies
├── security/      ← Auth patterns, OWASP findings, encryption
└── infrastructure/← Deployment, CI/CD, monitoring
```

If you rename, update the subfolder list in:
- `CLAUDE.md` Section 8 (Knowledge Curation Protocol)
- `.claude/commands/capture-knowledge.md` (Step 1 subfolder list)

---

## 6. Optional: Add Project-Specific Slash Commands

The template includes 14 general-purpose commands. You may want to add project-specific ones:

| Example Command | Purpose |
|---|---|
| `/scaffold-module [name]` | Create a new module following project conventions |
| `/add-endpoint [path]` | Walk through adding a new API endpoint |
| `/add-migration [name]` | Create a database migration |
| `/run-checks` | Run the full lint + test + build pipeline |

Create these as `.md` files in `.claude/commands/` following the existing command format:

```markdown
---
description: Short description shown in command list
allowed-tools: Read, Write, Edit, Bash
argument-hint: [args]
---

# Command Title

Instructions for the agent...
```

Register new commands in CLAUDE.md Section 5.1 (Slash Commands table).
