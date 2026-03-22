# Scenario: Unraid Appdata Volume Mount Can Override Container Code

**Area:** Docker Deployment / Unraid
**Date:** 2026-03-22
**Discovered during:** First Unraid deployment of SquareMesh image

## Setup
- Machinaris Docker image updated with code fixes (new Python imports)
- User pulled correct image (verified by digest match)
- Existing Unraid container config reused from previous guydavis install

## What Happened
Despite pulling the correct image with verified digest, the container kept running old code. The error traceback showed line numbers and imports from the OLD codebase, not the new one.

## Root Cause
1. `docker stop` + `docker start` reuses the existing container's filesystem layers — it does NOT apply the new image
2. Must `docker rm` the container and recreate it to use the new image
3. On Unraid, "Force Update" in the Docker UI handles this correctly, but manual CLI commands require explicit `docker rm`

## Key Insight
**Pulling a new image does NOT update running or stopped containers.** Containers are snapshots created from an image at `docker create`/`docker run` time. To apply a new image, the container must be removed and recreated. This is especially important when iterating on fixes — each rebuild+push cycle requires container removal on the deployment target.

## Validation
After `docker stop && docker rm && docker pull && recreate via UI`, the container ran the correct code and the API server started successfully.
