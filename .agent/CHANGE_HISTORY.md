# Change History

> Append-only log of all functional decisions made during development.
> Never delete entries. Reference by date + title.
> Format defined in CLAUDE.md Section 6.

---
## [2026-03-21] — Project Fork and Initial Setup

**Type:** Architecture
**Affects:** Entire project
**Design doc ref:** ARCHITECTURE.md

### Context
The original Machinaris project (guydavis/machinaris) was closed as the author no longer has interest in continuing. The project has been forked to SquareMesh/machinaris to continue development with a key focus on maintaining alignment with the latest versions of Chia from chia.net.

### Options Considered
- **Option A:** Start fresh — Pro: Clean slate Con: Lose all existing work and community
- **Option B:** Fork and continue — Pro: Preserve all existing functionality, community, and Docker infrastructure Con: Inherit technical debt

### Decision
Fork the SquareMesh/machinaris repository and continue development. The primary goal is to keep Machinaris aligned with the latest Chia blockchain versions while maintaining the existing multi-fork farming management capabilities.

### Technical Rationale
The existing codebase is mature (v2.6.0) with comprehensive Docker-based deployment, 34+ blockchain fork support, and a well-structured Flask API/WebUI architecture. Forking preserves all of this while allowing independent development direction.

### Impact
- All future development targets the SquareMesh fork
- Priority is Chia version alignment
- Comprehensive design documentation created to enable ongoing development

### Follow-up Required
- [x] Review and update all blockchain fork versions
- [x] Assess which deprecated forks to remove
- [x] Update CI/CD pipelines for the new repository
- [ ] Review and update Docker base images

---
## [2026-03-21] — Chia-Only Focus and v2.6.1 Upgrade

**Type:** Architecture
**Affects:** docker/dockerfile, .github/workflows/*, VERSION, CHANGELOG.md
**Design doc ref:** ARCHITECTURE.md, DOCKER-DEPLOYMENT.md, BLOCKCHAIN-INTEGRATION.md

### Context
User confirmed they only care about Chia blockchain. The codebase supported 34+ forks which added enormous build time, image size, and maintenance burden. Latest stable Chia is v2.6.1 (released 2026-03-18).

### Options Considered
- **Option A:** Keep all forks, only update Chia — Pro: Maximum compatibility Con: Huge build time, massive image, maintenance burden for abandoned forks
- **Option B:** Remove all non-Chia forks from Dockerfile — Pro: Fast builds, smaller image, focused maintenance Con: Can't support other forks without re-adding

### Decision
Remove all 33 non-Chia blockchain forks from the Dockerfile. Upgrade Chia to v2.6.1. The fork install scripts remain in the repo for reference but are not executed during build.

### Technical Rationale
Most forks are abandoned or have negligible user bases. The original author listed many as deprecated. Building 34 forks takes 1-3 hours; Chia-only builds in a fraction of that time. The install scripts are kept in `scripts/forks/` so they can be re-enabled if needed — this is a build-level change, not a code deletion.

### Impact
- Docker image is Chia-only — much smaller and faster to build
- CI/CD workflows simplified: single job (no Gigahorse), GHCR only (no DockerHub)
- Dropped Jammy base image — Noble (24.04) only
- VERSION bumped to 2.7.0 to reflect the breaking change
- Chia upgraded from 2.6.0 to 2.6.1
- Removed: forktools, fd-cli build args (Chia-only, not needed)

### Follow-up Required
- [ ] Verify entrypoint.sh handles Chia-only gracefully (no fork-specific code paths break)
- [ ] Test Docker build end-to-end
- [ ] Clean up blockchains.json to remove non-Chia entries (optional, app-level)
- [ ] Review common/config/globals.py for dead fork references
