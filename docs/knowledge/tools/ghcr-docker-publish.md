# GHCR Docker Image Publishing

**Category:** tools
**Relevance:** DOCKER-DEPLOYMENT.md, CI/CD workflows
**Date researched:** 2026-03-22

## Summary
Publishing Docker images to GitHub Container Registry (ghcr.io) for the SquareMesh/machinaris project. Covers authentication, build chain, and Unraid deployment.

## Key Findings
- GHCR packages default to **private** even if the repo is public — must explicitly change visibility
- Packages pushed via `docker push` appear under the **user's** profile, not the org, unless pushed via GitHub Actions with `GITHUB_TOKEN`
- To link a package to a repo: Package settings → Repository source → connect
- Two-image build chain: base image (`machinaris-base-noble`) + main image (`machinaris`)
- Base image rarely changes (system packages only), main image changes with every code update
- Unraid pulls by tag — `docker rmi` + `docker pull` needed to force update, or use "Force Update" in UI
- **Critical**: `docker stop` + `docker start` reuses the OLD container filesystem. Must `docker rm` and recreate to pick up new image.

## Windows Build Gotchas
- `git config core.autocrlf=true` (Windows default) converts all files to CRLF
- Shell scripts with CRLF fail inside Linux containers: `$'\r': command not found`
- Fix: `.gitattributes` with `* text=auto eol=lf` forces LF for all text files
- After adding `.gitattributes`: `git rm --cached -r . && git reset --hard` to re-normalize

## PAT Requirements for GHCR Push
- Scope needed: `write:packages`, `read:packages`
- Auth: `echo TOKEN | docker login ghcr.io -u USERNAME --password-stdin`
- Token type: Classic PAT (fine-grained tokens don't support packages yet)

## Sources
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
