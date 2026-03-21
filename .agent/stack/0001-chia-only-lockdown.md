# Chia-Only Lockdown Summary

**Pushed:** 2026-03-21
**Source:** Response in conversation — Chia-only pivot and v2.6.1 upgrade
**Context:** User confirmed they only care about Chia; requested locking in latest version

---

## Locked to Chia-only with v2.6.1

**Latest Chia:** v2.6.1 (released March 18, 2026). There's also a v2.7.0-rc1 pre-release but we're using the stable version.

### Changes made:

**`docker/dockerfile`** — Stripped down to Chia-only:
- Removed all 33 non-Chia fork `ARG` declarations and install steps
- Removed forktools, fd-cli, gigahorse, mmx env vars and PATH entries
- Set `CHIA_BRANCH=2.6.1` as default
- Single `RUN` step: chia_install + 3rd party libs + machinaris + i18n

**All 6 GitHub Actions workflows** updated:
- `main-blockchains.yaml` — Chia job only, GHCR only, `CHIA_BRANCH=2.6.1`
- `develop-blockchains.yaml` — Same, removed Gigahorse job
- `test-blockchains.yaml` — Same, removed Gigahorse job
- `main-base.yaml` — GHCR only, Noble only (dropped Jammy)
- `develop-base.yaml` — Same
- `test-base.yaml` — Same
- All workflows now use `github.repository_owner` instead of `secrets.DOCKERHUB_USERNAME`

**`VERSION`** — Bumped to `2.7.0`

**`CHANGELOG.md`** — New `[2.7.0]` entry documenting the Chia-only pivot, v2.6.1 upgrade, and all removals

### What's still in the repo but not called:
- `scripts/forks/*_install.sh` and `*_launch.sh` — kept for reference, not executed during build
- `common/config/blockchains.json` — still has all fork entries (can clean up later)
- `entrypoint.sh` — may have fork-specific code paths to review next
