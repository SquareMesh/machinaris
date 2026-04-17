# Resolved Issues

> Closed issues with full resolution record.
> Format defined in CLAUDE.md Section 7.

---
## ISSUE-001 — Scheduled POSTs silently return 500, freezing 20+ tables for 25 days

**Priority:** CRITICAL
**Status:** RESOLVED
**Opened:** 2026-04-17
**Affects:** api/extensions/api/__init__.py (TopLevelSchema), 21 schema files, 23 scheduler POST sites
**Discovered during:** Investigating stale /pools page reported by user

### Description
Every APScheduler POST into any endpoint whose input schema inherits `TopLevelSchema` was returning HTTP 500 with `TypeError: TopLevelSchema._deserialize() got an unexpected keyword argument 'error_store'`. The scheduler's outer `try/except` only catches Python exceptions (not HTTP status codes), so APScheduler kept logging "executed successfully" while nothing was written. Tables affected: pools, alerts, challenges, drives, partials, plotnfts, plots, plottings, transfers, warnings, plus 11 `stat_*` tables.

### Reproduction
1. Deploy any image built after 2026-03-23 (date TODO-021 shipped).
2. Wait 2 minutes for the first `status_pools` cycle.
3. `docker exec machinaris sqlite3 /root/.chia/machinaris/dbs/pools.db 'SELECT updated_at FROM pools;'` → timestamp is static from the last build with marshmallow 3.
4. `docker exec machinaris grep -A 40 'Exception on /pools/ \[POST\]' /root/.chia/machinaris/logs/apisrv.log | tail -80` → TypeError stack.

### Impact
- /pools page frozen (latest observable symptom for user).
- Alerts, Partials, Farm Summary, Plots, and stat charts all served stale data.
- Pool login-link URLs expired (pool auth tokens time-sensitive; stored URL 25 days old).
- Was silent: scheduler "healthy" by APScheduler's own reporting. Not caught by tests because TODO-021's verification was unit-only, no scheduler→API integration test exists.

### Resolution
**Resolved:** 2026-04-17
**Root cause:** TODO-021 (2026-03-23) replaced `marshmallow-toplevel` with an inline `TopLevelSchema` that overrode `_deserialize`/`_serialize` with a narrow signature, AND simultaneously removed the `marshmallow<4.0` pin. Marshmallow 4's `Schema._do_load` passes `error_store=...` into `_deserialize`, which the override rejected.
**Fix:** Rewrote `TopLevelSchema` (`api/extensions/api/__init__.py`) to wrap input as `{"_toplevel": data}` and delegate to `super().load/dump`, unwrapping on return. Goes through the public marshmallow API so internal kwargs are handled by the parent class; version-agnostic across marshmallow 3 and 4. Also added `response.status_code >= 400` logging to `api/utils.py:send_post` and `send_worker_post` so any future scheduler-POST regression surfaces immediately in `apisrv.log`.
**Verified by:** (post-deploy) `pools.updated_at` advances within 2 min of container restart; `POST /pools/` returns 201; multiple frozen tables show current data; no TypeError in log.
**Change history ref:** [2026-04-17] — Fix TopLevelSchema marshmallow-4 regression

