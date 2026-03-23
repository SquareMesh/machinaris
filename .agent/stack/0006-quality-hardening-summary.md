# Quality Hardening Summary

**Pushed:** 2026-03-23
**Source:** Response 1 in conversation (most recent)
**Context:** User asked to tackle TODOs 18, 17, 20, 21, 19 — code quality and performance hardening

---

**Completed:**

| TODO | What was done | Scope |
|---|---|---|
| **018** | Replaced 147 bare `except:` → `except Exception:` | 50 Python files |
| **017** | Added `index=True` on hostname/blockchain/created_at + Alembic migration | 21 models, 4 operational tables |
| **020** | Added `max_requests=1000`, `max_requests_jitter=50` | gunicorn.conf.py |
| **021** | Inline `TopLevelSchema` replacement, removed dep, unpinned marshmallow | 21 schema files + requirements.txt |
| **019** | `set -eo pipefail` + fixed anti-patterns | 12 shell scripts |

All tracking files (TODO.md, CHANGE_HISTORY.md, DESIGN_INDEX.md) updated.
