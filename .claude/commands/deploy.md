---
description: Build Docker image, push to GHCR, and optionally commit+push code first
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# Deploy Protocol

Build and push the Machinaris Docker image to GHCR as `:latest`.

## Arguments

- No arguments: build and push only (code must already be committed and pushed)
- `full`: commit, push code, then build and push Docker image

## Steps

### 1. Pre-flight Check

Run `/validate` checks first. If any fail, STOP and report — do not deploy broken code.

### 2. Code Push (if `full`)

If argument is `full`:
1. Run `git status` — if there are uncommitted changes, commit them using the `/commit` protocol
2. Run `git push origin main`

If no argument, verify the working tree is clean and code is pushed:
```bash
git status
git log origin/main..HEAD --oneline
```
If there are unpushed commits, warn the user and ask to confirm.

### 3. Docker Build

```bash
docker build -t ghcr.io/squaremesh/machinaris:latest -f docker/dockerfile .
```

If the build fails:
- Read the last 50 lines of output
- Diagnose the failure
- STOP and report — do not push a broken image

### 4. Docker Push

```bash
docker push ghcr.io/squaremesh/machinaris:latest
```

### 5. Post-Deploy Summary

Output:
```
DEPLOYED ghcr.io/squaremesh/machinaris:latest
Digest: sha256:[digest]
Git: [commit hash] on main
Build: [success/cached layers info]

To update Unraid: pull the new image and restart the container.
```
