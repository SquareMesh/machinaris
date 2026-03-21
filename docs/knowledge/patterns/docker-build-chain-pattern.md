# Docker Build Chain Pattern — Machinaris

**Category:** patterns
**Relevance:** DOCKER-DEPLOYMENT.md — how Docker images are built and published
**Date researched:** 2026-03-21

## Summary
Machinaris uses a two-stage Docker build: a base image (Ubuntu + system packages) and a main image (blockchain + app). Understanding this chain is essential for build optimization and CI/CD configuration.

## Key Findings
- **Stage 1 (base):** `dockerfile-noble.base` → Ubuntu 24.04 + python3, git, cmake, sqlite3, smarttools. Published as `machinaris-base-noble:latest`.
- **Stage 2 (main):** `dockerfile` → `FROM machinaris-base-noble` + blockchain install + Machinaris app. Published as `machinaris:latest`.
- The base image rarely changes. Reusing Guy Davis's published base image (`ghcr.io/guydavis/machinaris-base-noble:latest`) is valid and saves significant build time.
- Fork install scripts use a guard pattern: if `_BRANCH` arg is empty, the script exits immediately. This means you can control which forks are built purely through build args.
- CI/CD uses `docker/build-push-action@v6` with QEMU for multi-arch (amd64 + arm64).

## Code Example / Reference
```dockerfile
# Base image reference (line 4 of dockerfile)
FROM ghcr.io/guydavis/machinaris-base-${UBUNTU_VER}:${MACHINARIS_STREAM}

# Fork install guard pattern (typical fork script)
if [ -z "${1}" ]; then echo "Skipping..."; exit 0; fi
```

## Decision / Recommendation
For our Chia-only fork: keep using the upstream base image until we need to customize system packages. Only build our own base when Ubuntu version or system deps change. The Chia-only Dockerfile removes all non-Chia install steps entirely rather than relying on empty branch guards.
