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
- [x] Verify entrypoint.sh handles Chia-only gracefully (no fork-specific code paths break)
- [x] Test Docker build end-to-end
- [ ] Clean up blockchains.json to remove non-Chia entries (optional, app-level)
- [ ] Review common/config/globals.py for dead fork references

---
## [2026-03-22] — Entrypoint Chia-Only Cleanup

**Type:** Implementation
**Affects:** docker/entrypoint.sh, scripts/worker_port_warning.sh, scripts/start_machinaris.sh
**Design doc ref:** DOCKER-DEPLOYMENT.md, BLOCKCHAIN-INTEGRATION.md

### Context
After removing all 33 non-Chia forks from the Dockerfile, the entrypoint and supporting scripts still contained dead code paths for other forks — port warnings, plotman configs, forktools/fd-cli installs, and a multi-container stagger sleep.

### Options Considered
- **Option A:** Leave dead code — Pro: No risk of regression Con: Up to 3 min wasted on startup sleep, forktools clone attempt, confusing dead code
- **Option B:** Strip fork-specific code paths — Pro: Faster startup, cleaner code, no wasted network calls Con: Harder to re-enable forks (mitigated by git history)

### Decision
Strip all dead fork code paths from the entrypoint flow.

### Technical Rationale
With `blockchains=chia` hardcoded in the Dockerfile, these code paths were either no-ops (fd-cli skips Chia explicitly) or wasteful (forktools clone, random sleep). The random 1-180s sleep was designed to stagger multiple fork containers — irrelevant with a single blockchain.

### Impact
- Startup is up to 3 minutes faster (removed random sleep)
- No more runtime git clone of forktools
- worker_port_warning.sh reduced from 103 lines to 4 lines
- start_machinaris.sh plotman config simplified to Chia-only path

### Follow-up Required
- [x] Test Docker build and container startup end-to-end

---
## [2026-03-22] — Chia 2.6.x RPC Import Migration

**Type:** Bugfix
**Affects:** api/commands/rpc.py, api/views/plotnfts/resources.py
**Design doc ref:** BLOCKCHAIN-INTEGRATION.md

### Context
Chia 2.6.1 reorganized its Python module structure. RPC clients moved from `chia.rpc.*` to service-specific directories. `chia.util.ints` moved to `chia_rs.sized_ints`. The Machinaris API server failed to start due to `ModuleNotFoundError`.

### Options Considered
- **Option A:** Pin Chia to older version — Pro: No code changes Con: Miss security fixes, falling behind
- **Option B:** Update imports to match Chia 2.6.x module paths — Pro: Current, correct Con: Breaking change if reverting Chia version

### Decision
Update all Chia imports to the new 2.6.x paths. Also replaced the 230-line fork if/elif import chain in rpc.py with 7 lines of Chia-only imports.

### Technical Rationale
Chia 2.6.x moved RPC clients to service directories (e.g., `chia.rpc.farmer_rpc_client` → `chia.farmer.farmer_rpc_client`) and moved sized ints to `chia_rs`. The `bech32m` and `byte_types` util modules were unchanged.

### Impact
- API server starts successfully on Chia 2.6.1
- rpc.py reduced from ~250 lines of imports to ~25 lines
- `bytes32` import in plotnfts/resources.py updated to `chia_rs.sized_bytes`

### Follow-up Required
- [ ] Monitor for additional Chia API changes in future versions

---
## [2026-03-22] — Docker Build Chain: Base Image + GHCR Publishing

**Type:** Implementation
**Affects:** docker/dockerfile, .gitattributes
**Design doc ref:** DOCKER-DEPLOYMENT.md

### Context
The Dockerfile referenced `ghcr.io/guydavis/machinaris-base-noble` (original author's registry) which no longer exists. Building on Windows introduced CRLF line endings that broke shell scripts inside the Linux container.

### Options Considered
- **Option A:** Use guydavis base image — Pro: No build needed Con: Image doesn't exist
- **Option B:** Build own base image under squaremesh namespace — Pro: Self-contained, independent Con: Need to maintain base image

### Decision
Build and publish base image as `ghcr.io/squaremesh/machinaris-base-noble`. Updated Dockerfile FROM to reference `squaremesh` instead of `guydavis`. Added `.gitattributes` forcing LF line endings for all text files.

### Technical Rationale
The base image Dockerfile (`docker/dockerfile-noble.base`) was already in the repo. Publishing under `squaremesh` makes the project fully independent from the original author's infrastructure. The `.gitattributes` fix is essential for Windows development targeting Linux containers.

### Impact
- Published to GHCR: `ghcr.io/squaremesh/machinaris-base-noble:{latest,main}`
- Published to GHCR: `ghcr.io/squaremesh/machinaris:{2.7.0,latest}`
- `.gitattributes` ensures LF endings for sh, py, yaml, json, conf, dockerfile
- Verified working on Unraid deployment

### Follow-up Required
- [ ] Make GHCR packages public (if not already)
- [ ] Link packages to repository on GitHub
