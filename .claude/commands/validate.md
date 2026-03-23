---
description: Pre-flight validation checks before committing or deploying
allowed-tools: Read, Bash, Glob, Grep
---

# Validate Protocol

Run pre-flight checks on changed files to catch errors before commit/deploy.

## Steps

### 1. Identify Changed Files

```bash
git diff --name-only HEAD
git diff --name-only --cached
git ls-files --others --exclude-standard
```

Combine all lists. If no changes, check the last commit's files instead:
```bash
git diff --name-only HEAD~1..HEAD
```

### 2. Python Syntax Check

For every `.py` file in the changed set:
```bash
python -m py_compile <file>
```

Report any syntax errors. This is a BLOCKING failure — do not proceed.

### 3. Jinja2 Template Tag Balance

For every `.html` file in `web/templates/` that was changed, check for balanced template tags:

Use Grep to count opening vs closing tags in each file:
- `{% if` vs `{% endif %}`
- `{% for` vs `{% endfor %}`
- `{% block` vs `{% endblock %}`
- `{% macro` vs `{% endmacro %}`

If any file has mismatched counts, report it as a BLOCKING failure with the file path and tag counts.

Note: Tags inside `{# comments #}` should be excluded. Tags in `{% elif %}` and `{% else %}` do NOT count as separate blocks.

### 4. Code Quality Checks

Search changed `.py` files for:
- **Bare `except:`** — should be `except Exception:` (Grep pattern: `^\s*except\s*:\s*$`)
- **`|safe` in templates** — potential XSS (Grep for `|safe` in changed `.html` files)
- **Removed package imports** — check for imports of packages removed from requirements.txt (e.g., `marshmallow_toplevel`)

Report any findings as warnings (non-blocking unless it's an import of a removed package).

### 5. Shell Script Check

For any changed `.sh` files, verify:
- Has a shebang line (`#!/usr/bin/env bash`)
- Has `set -eo pipefail`
- No `grep -q` followed by `$?` check on the next line (should use `if grep -q`)

Report missing items as warnings.

### 6. Report

Output:
```
VALIDATE RESULTS
Python syntax:    [N files checked] — [PASS/FAIL]
Template balance: [N files checked] — [PASS/FAIL]
Code quality:     [N warnings]
Shell scripts:    [N files checked] — [PASS/FAIL]
Overall:          [PASS/FAIL — ready to commit/deploy]
```

If any BLOCKING failures exist, the overall result must be FAIL.
