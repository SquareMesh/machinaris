# TODO

> Lightweight items identified but not yet explored.
> Promote to OPEN_ISSUES when analyzed. Dismiss with reason if not needed.
> Format defined in CLAUDE.md Section 5.1.
> Next TODO number: TODO-010

---

## TODO-001 — DISMISSED
~~Audit deprecated blockchain forks for removal~~
Dismissed: 2026-03-21 — All non-Chia forks removed from Dockerfile entirely. Chia-only focus locked in.

## TODO-002 — Review hardcoded secret key in web/__init__.py
Discovered during: Initial codebase review (2026-03-21)
Flask session secret key appears hardcoded. Evaluate security implications for Docker-isolated deployment.

## TODO-003 — Assess CSRF protection gaps
Discovered during: Initial codebase review (2026-03-21)
No visible CSRF token implementation in web forms. Forms use POST but rely on network isolation for security.

## TODO-004 — Review test coverage
Discovered during: Initial codebase review (2026-03-21)
Only 15 unit tests exist (test_converters.py). Assess need for expanded test coverage for critical paths.

## TODO-005 — DISMISSED
~~Update CI/CD for new fork repository~~
Dismissed: 2026-03-21 — All 6 workflows updated to GHCR-only with github.repository_owner. DockerHub removed.

## TODO-006 — Evaluate Python version upgrade path
Discovered during: Initial codebase review (2026-03-21)
pyproject.toml targets Python 3.10, CI runs 3.9, Chia 2.6.0 supports Python 3.13. Assess upgrade path.

## TODO-007 — DISMISSED
~~Review entrypoint.sh for dead fork code paths~~
Dismissed: 2026-03-22 — Reviewed and cleaned up. Removed: random sleep, forktools, fd-cli calls. Simplified worker_port_warning.sh and start_machinaris.sh.

## TODO-008 — Clean up blockchains.json for Chia-only
Discovered during: Chia-only lockdown (2026-03-21)
common/config/blockchains.json still contains metadata for 50+ forks. Consider trimming to Chia-only to reduce confusion.

## TODO-009 — Monitor Chia v3.0 for V2 plot format impact
Discovered during: Chia version research (2026-03-21)
Chia v3.0 introduces a new Proof of Space format with activation at block height ~9,562,000 (~6 months after release). Will likely require plot migration and Machinaris updates. Track beta releases.
