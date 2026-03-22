# Example: Rust Web App Project

This walkthrough shows how to customize the template for a Rust web application — an API server built with Axum, SQLx, and PostgreSQL. The project is a recipe management platform called "Pantry".

---

## Step 1: Copy and Initialize

```bash
cp -r blank-project/ PantryAPI
cd PantryAPI
git init
cargo init --name pantry-api
```

---

## Step 2: CLAUDE.md Customization

### Section 1 — Project Identity

```markdown
## 1. Who You Are In This Project

You are the **primary development agent** for Pantry — a Rust web API for recipe
management built with Axum, SQLx (PostgreSQL), and Tower middleware. You are not
just a code generator — you are an active design participant, a standards enforcer,
a knowledge curator, and a quality gatekeeper.
```

### Section 3 — Design Document Hierarchy

```markdown
## 3. Design Document Hierarchy

docs/design/
├── CLAUDE.md                      ← Master navigation guide — start here
├── OVERVIEW.md                    ← Project identity, goals, target users, MVP scope
├── DESIGN_REVIEW.md               ← Gap analysis, inconsistencies, action order
├── api/                           ← API design
│   ├── CLAUDE.md                  ← Section map
│   ├── 01-endpoints.md            ← Route definitions, request/response shapes
│   ├── 02-authentication.md       ← JWT auth, refresh tokens, middleware
│   ├── 03-authorization.md        ← Role-based access, resource ownership
│   └── 04-error-handling.md       ← Error types, HTTP status mapping, error responses
├── data-model/                    ← Data layer
│   ├── CLAUDE.md
│   ├── 01-entities.md             ← Core entities (User, Recipe, Ingredient, Tag)
│   ├── 02-relationships.md        ← Foreign keys, junction tables, cascades
│   └── 03-migrations.md           ← Migration strategy, seed data
└── architecture/                  ← System architecture
    ├── CLAUDE.md
    ├── 01-layer-boundaries.md     ← Handler → Service → Repository pattern
    ├── 02-configuration.md        ← Environment config, feature flags
    └── 03-observability.md        ← Logging, tracing, health checks

Priority order when documents conflict:
1. OVERVIEW.md — defines what/why
2. DESIGN_REVIEW.md — supersedes anything flagged as incorrect
3. api/ — endpoint contracts are authoritative for HTTP behavior
4. data-model/ — entity definitions are authoritative for persistence
5. architecture/ — structural decisions
```

### Section 4.2 — Hard Rules

```markdown
### 4.2 Hard Rules — Never Violate

RULE-1   No secrets in source code. All credentials via environment variables (dotenvy).
RULE-2   All external input validated at the handler boundary using axum extractors
         with custom rejection types. Service layer receives only validated types.
RULE-3   Database access only through the repository layer (src/repo/). No raw SQL
         in handlers or services. All queries in repository functions.
RULE-4   All API endpoints return AppError (implements IntoResponse). Never return
         raw strings, StatusCode alone, or panic in request handling.
RULE-5   No unwrap() in library code. Use ? with typed errors (thiserror).
         unwrap() only in tests and main.rs bootstrap.
RULE-6   Handler functions are thin — extract, validate, call service, map response.
         No business logic in handlers.
RULE-7   All database queries use parameterized inputs. Never interpolate user data
         into SQL strings.
RULE-8   Every endpoint requires authentication unless explicitly listed in the
         public routes allowlist in 02-authentication.md.
RULE-9   Migrations are append-only. Never modify a committed migration file.
         Create a new migration to alter schema.
RULE-10  All timestamps stored as UTC. Display timezone conversion is a client concern.
```

### Section 9 — Code Quality Standards

```markdown
## 9. Code Quality Standards

### Rust-Specific

/// Every public type must have a doc comment.
/// A recipe with its metadata and ingredient list.
pub struct Recipe { ... }

/// Every public function states its error conditions.
/// # Errors
/// Returns `AppError::NotFound` if no recipe exists with the given ID.
/// Returns `AppError::Forbidden` if the user does not own the recipe.
pub async fn get_recipe(id: RecipeId, user: &AuthUser) -> Result<Recipe, AppError> { ... }

// Errors are typed, never strings
#[derive(thiserror::Error, Debug)]
pub enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("forbidden")]
    Forbidden,
    #[error("validation: {0}")]
    Validation(String),
    #[error("internal")]
    Internal(#[from] anyhow::Error),
}

// No unwrap() in library code
// Use ? with typed errors throughout

### Layer Conventions

- **Handlers** (`src/handlers/`): Extract → validate → call service → map response
- **Services** (`src/services/`): Business logic, orchestration, authorization checks
- **Repositories** (`src/repo/`): Database queries, entity mapping, connection management
- **Models** (`src/models/`): Domain types, DTOs, request/response shapes

### Testing Standards

- Unit tests for services (mock the repository)
- Integration tests for handlers (use a test database)
- Repository tests against a real PostgreSQL instance (sqlx test fixtures)
- Tests prefixed by concern: `test_auth_*`, `test_recipe_*`, `test_validation_*`

### Commit Message Format

[scope] short imperative description

- references ISSUE-NNN if applicable
- scope is one of: api, auth, db, model, config, test, docs, ci
```

---

## Step 3: settings.json

```json
{
  "permissions": {
    "allow": [
      "Skill(*)",
      "Edit",
      "Write",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git branch*)",
      "Bash(git add *)",
      "Bash(git commit*)",
      "Bash(git stash*)",
      "Bash(git show*)",
      "Bash(cargo build*)",
      "Bash(cargo test*)",
      "Bash(cargo check*)",
      "Bash(cargo clippy*)",
      "Bash(cargo run*)",
      "Bash(cargo fmt*)",
      "Bash(sqlx *)",
      "Bash(ls *)",
      "Bash(mkdir *)"
    ]
  }
}
```

---

## Step 4: .gitignore

```gitignore
# Rust
/target/
**/*.rs.bk
Cargo.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Environment
.env
.env.*

# Database
*.sqlite
*.db
```

---

## Step 5: Knowledge Subfolders

Rename `docs/knowledge/` subfolders for the web domain:

```
docs/knowledge/
├── api/              ← REST design, middleware patterns, auth strategies
├── database/         ← Schema design, query optimization, SQLx patterns
├── rust/             ← Rust crate evaluations, patterns, gotchas
└── tools/            ← Cargo, Docker, CI/CD, deployment tooling
```

Update the subfolder list in:
- `CLAUDE.md` Section 8
- `.claude/commands/capture-knowledge.md` Step 1

---

## Step 6: Design Docs Navigation

Update `docs/design/CLAUDE.md`:

```markdown
# Design Documents — Navigation Guide

## Documents

| Document | Description | Status |
|---|---|---|
| OVERVIEW.md | Project identity, MVP scope, target users | READY |
| DESIGN_REVIEW.md | Gap analysis, open questions | LIVING |
| api/CLAUDE.md | API endpoints, auth, errors | Section map |
| data-model/CLAUDE.md | Entities, relationships, migrations | Section map |
| architecture/CLAUDE.md | Layers, config, observability | Section map |

## Quick Lookup

| Topic | Go to |
|---|---|
| "How do I add an endpoint?" | api/01-endpoints.md |
| "What does the User entity look like?" | data-model/01-entities.md |
| "How does auth work?" | api/02-authentication.md |
| "Where does business logic go?" | architecture/01-layer-boundaries.md |
| "How do I add a migration?" | data-model/03-migrations.md |
```

---

## Step 7: Add Project-Specific Commands (Optional)

### `/scaffold-module [name]` — `.claude/commands/scaffold-module.md`

```markdown
---
description: Create a new module following the handler/service/repo pattern
allowed-tools: Read, Write, Edit, Bash
argument-hint: [module-name]
---

# Scaffold Module

Create a new module: $ARGUMENTS

## Steps

1. Confirm the module name (singular, snake_case).
2. Create the following files:
   - `src/handlers/{name}.rs` — handler functions with Axum extractors
   - `src/services/{name}.rs` — business logic
   - `src/repo/{name}.rs` — database queries
   - `src/models/{name}.rs` — domain types and DTOs
3. Add `pub mod {name};` to each layer's `mod.rs`.
4. Create a basic test file at `tests/{name}_test.rs`.
5. Update `.agent/DESIGN_INDEX.md` with the new module.
6. Confirm the files created and suggest next steps.
```

### `/add-migration [name]` — `.claude/commands/add-migration.md`

```markdown
---
description: Create a new database migration
allowed-tools: Read, Write, Bash
argument-hint: [migration-name]
---

# Add Migration

Create a migration: $ARGUMENTS

## Steps

1. Run `sqlx migrate add $ARGUMENTS` to create the migration file.
2. Open the generated `.sql` file for editing.
3. Remind: migrations are append-only (RULE-9). Never modify committed migrations.
4. After writing the SQL, suggest running `sqlx migrate run` to apply.
```

---

## Example Session Flow

Here's what a typical session looks like with the customized template:

```
User: /session-start

Agent: SESSION START
Read: CLAUDE.md ✓ | DESIGN_REVIEW ✓ | CHANGE_HISTORY ✓ | OPEN_ISSUES ✓
Design index: 12 tracked | 0 DRIFT | 1 BLOCKED (auth middleware)
Open issues: 2 — ISSUE-003 (HIGH: JWT refresh token rotation)
Open TODOs: 3
Ready for task.

User: Add a PATCH /recipes/:id endpoint for updating recipes

Agent: [Checks api/01-endpoints.md for existing route patterns]
       [Checks data-model/01-entities.md for Recipe fields]
       [Checks architecture/01-layer-boundaries.md for layer rules]
       [Implements handler → service → repo following RULE-3, RULE-6]
       [Writes tests]
       [Updates CHANGE_HISTORY with the decision]
       Task complete.

User: /commit

Agent: COMMITTED a1b2c3d
Scope: [api] add PATCH /recipes/:id endpoint
Tracking synced: CHANGE_HISTORY [+1] | ISSUES [0 resolved, 0 new] | TODOs [+0]
Working tree: clean
```

---

## Resulting Project Structure

After setup and initial development, the project looks like:

```
PantryAPI/
├── CLAUDE.md                          ← Customized working framework
├── Cargo.toml
├── .env.example
├── .gitignore
├── .agent/                            ← Agent tracking (committed)
│   ├── CHANGE_HISTORY.md
│   ├── OPEN_ISSUES.md
│   ├── RESOLVED_ISSUES.md
│   ├── TODO.md
│   ├── DESIGN_INDEX.md
│   └── stack/
├── .claude/
│   ├── settings.json
│   └── commands/                      ← 14 standard + 2 project-specific
├── docs/
│   ├── design/
│   │   ├── CLAUDE.md
│   │   ├── OVERVIEW.md
│   │   ├── DESIGN_REVIEW.md
│   │   ├── api/
│   │   ├── data-model/
│   │   └── architecture/
│   ├── reviews/
│   ├── scenarios/
│   ├── knowledge/
│   │   ├── api/
│   │   ├── database/
│   │   ├── rust/
│   │   └── tools/
│   └── reference/
├── migrations/
├── src/
│   ├── main.rs
│   ├── config.rs
│   ├── error.rs
│   ├── handlers/
│   ├── services/
│   ├── repo/
│   └── models/
└── tests/
```
