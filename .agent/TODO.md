# TODO

> Lightweight items identified but not yet explored.
> Promote to OPEN_ISSUES when analyzed. Dismiss with reason if not needed.
> Format defined in CLAUDE.md Section 5.1.
> Next TODO number: TODO-022

---

## TODO-001 — DISMISSED
~~Audit deprecated blockchain forks for removal~~
Dismissed: 2026-03-21 — All non-Chia forks removed from Dockerfile entirely. Chia-only focus locked in.

## TODO-002 — DONE
~~Move hardcoded secret key to environment variable~~
Done: 2026-03-22 — Replaced hardcoded key with file-based auto-generated key at `/root/.chia/machinaris/config/secret_key`. Generated once on first boot, persisted across restarts.

## TODO-003 — DISMISSED
~~Assess CSRF protection gaps~~
Dismissed: 2026-03-22 — CSRF protection implemented via Flask-WTF CSRFProtect. 41 csrf_token fields added across 18 templates.

## TODO-004 — Review test coverage
Discovered during: Initial codebase review (2026-03-21)
Only 15 unit tests exist (test_converters.py). Assess need for expanded test coverage for critical paths.

## TODO-005 — DISMISSED
~~Update CI/CD for new fork repository~~
Dismissed: 2026-03-21 — All 6 workflows updated to GHCR-only with github.repository_owner. DockerHub removed.

## TODO-006 — DONE
~~Evaluate Python version upgrade path~~
Done: 2026-03-23 — Aligned all Python version references to 3.12 (matching Ubuntu Noble runtime). CI bumped from 3.9 → 3.12, pyproject.toml updated with requires-python >= 3.12 and Black py312 target, ARCHITECTURE.md updated, GitHub Actions bumped to latest versions.

## TODO-007 — DISMISSED
~~Review entrypoint.sh for dead fork code paths~~
Dismissed: 2026-03-22 — Reviewed and cleaned up. Removed: random sleep, forktools, fd-cli calls. Simplified worker_port_warning.sh and start_machinaris.sh.

## TODO-008 — DONE
~~Clean up blockchains.json for Chia-only~~
Done: 2026-03-23 — Trimmed from 34 entries to Chia-only. Also deleted forktools files, removed tools nav/route/template, simplified hardcoded fork lists (POOLABLE, PLOTTABLE, PEER_CMD), removed legacy_blockchain/gather_mmx_reward dead code, cleaned globals.py.

## TODO-009 — Monitor Chia v3.0 for V2 plot format impact
Discovered during: Chia version research (2026-03-21)
Chia v3.0 introduces a new Proof of Space format with activation at block height ~9,562,000 (~6 months after release). Will likely require plot migration and Machinaris updates. Track beta releases.

## TODO-010 — DISMISSED
~~Add notification history/log to web UI~~
Dismissed: 2026-03-22 — Telegram notifications confirmed working in production (test + automated wallet change). Logging via app.logger is sufficient for now.

## TODO-011 — DISMISSED
~~Improve chat ID retrieval UX in setup guide~~
Dismissed: 2026-03-22 — Telegram setup confirmed working end-to-end. Current guide is sufficient.

## TODO-012 — DONE
~~Refactor flash messages to remove |safe XSS risk~~
Done: 2026-03-22 — All `|safe` filters removed from templates. Flash messages use category suffixes (`_pre`) for preformatted content with template-side rendering via `_flash_messages.html` macro. Intentional HTML in non-flash contexts uses `markupsafe.Markup()`. Zero `|safe` occurrences remain.

## TODO-013 — DONE
~~Add basic authentication to web UI~~
Done: 2026-03-22 — Implemented TOTP-based two-factor authentication. Single-user, authenticator-app-only login. 7-day sessions. Web UI only (port 8926), internal API (port 8927) unaffected. Optional — app runs unauthenticated until user sets up TOTP. User guide at docs/TOTP_AUTHENTICATION.md.

## TODO-014 — Switch certificate downloads to HTTPS
Discovered during: Security audit (2026-03-22)
All 50+ fork launch scripts fetch SSL certificates via `curl http://...` (not HTTPS). MITM attack can intercept and replace certificates. Harvester would then trust attacker's fake farmer. Security audit Priority 7. Fix: change `http://` to `https://` in `scripts/forks/chia_launch.sh:125` and equivalent lines in other launch scripts. May require Gunicorn HTTPS config or a note that users should use a reverse proxy.

## TODO-016 — Remove mmx_cli.py and MMX code paths
Discovered during: Chia-only cleanup (2026-03-23)
`api/commands/mmx_cli.py` and `api/models/mmx.py` are dead code (MMX not in blockchains.json or Dockerfile), but deeply integrated — imported by 8 scheduler files. Removing requires updating all 8 importers plus ~27 files with `if blockchain == 'mmx'` checks. Deferred as lower priority than the config/forktools cleanup done today.

## TODO-017 — DONE
~~Add database indexes for query performance~~
Done: 2026-03-23 — Added `index=True` to hostname, blockchain, created_at columns across all 17 stat tables + alerts, challenges, partials, plots models. Created Alembic migration `b1a2c3d4e5f6` for existing databases.

## TODO-018 — DONE
~~Replace bare except clauses (~50+ locations)~~
Done: 2026-03-23 — Replaced 147 bare `except:` with `except Exception:` across 50 Python files. 1 commented-out occurrence left as-is, 1 `# noqa` in migrations left as-is.

## TODO-019 — DONE
~~Audit entrypoint.sh and chia_launch.sh for set -e~~
Done: 2026-03-23 — Added `set -eo pipefail` to 12 shell scripts: entrypoint.sh, chia_launch.sh, setup_databases.sh, stop_machinaris.sh, mount_remote_shares.sh, worker_port_warning.sh, gpu_drivers_setup.sh, plotman_setup.sh, chiadog_setup.sh, bladebit_setup.sh, madmax_setup.sh, plotman_autoplot.sh. Fixed `grep -q` + `$?` anti-patterns, added `|| true` guards to pidof/kill/chmod.

## TODO-020 — DONE
~~Add gunicorn max_requests for worker recycling~~
Done: 2026-03-23 — Added `max_requests = 1000` and `max_requests_jitter = 50` to api/gunicorn.conf.py.

## TODO-021 — DONE
~~Replace marshmallow-toplevel (unmaintained since 2020)~~
Done: 2026-03-23 — Created inline `TopLevelSchema` class in `api/extensions/api/__init__.py`. Updated all 21 schema files to import from there. Removed `marshmallow-toplevel` from requirements.txt and unpinned marshmallow `<4.0` constraint.

## TODO-015 — DISMISSED
~~Encrypt or protect sensitive config files~~
Dismissed: 2026-03-22 — Encryption at rest is security theater here: the app must read configs in plaintext to use them, so the decryption key must also be accessible, putting us back at square one. Docker secrets not supported by Unraid's Docker UI. The real vulnerability is unauthenticated API access (GET /configs/notifications/chia serves bot token) — TODO-013 (authentication) is the correct fix. See CHANGE_HISTORY [2026-03-22] — Dismiss Config File Encryption.
