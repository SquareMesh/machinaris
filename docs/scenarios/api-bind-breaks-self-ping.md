# Scenario: Localhost API Bind Breaks Controller Self-Ping

**Area:** Network / Controller-Worker Communication
**Date:** 2026-03-23
**Discovered during:** API bind address security hardening

## Setup
- Single Machinaris instance running as fullnode
- API server bind address changed from `0.0.0.0` to `127.0.0.1`
- Worker registered in database with `url = http://<LAN-IP>:8927`

## What Happened
After deploying with `api_bind_address=127.0.0.1`:
1. Container started, Chia synced normally
2. Blockchain page showed status as "Offline" despite Chia being "Full Node Synced"
3. The controller's `status_controller.py` scheduler pinged `http://<LAN-IP>:8927/ping`
4. API was only listening on `127.0.0.1:8927` — connection refused on the LAN IP
5. `latest_ping_result` set to "Connection Refused" → UI displayed "Offline"

## Why It Matters
This is a second-order effect: changing the API bind address was a security improvement, but it silently broke the status reporting pipeline because the worker URL in the database uses the LAN IP, not localhost. The WebUI actions (start/stop farming, save configs) would also have failed for the same reason.

## Resolution
Added `_resolve_url(worker)` helper to both `api/utils.py` and `web/utils.py`. When the API is bound to localhost and the target worker is the local machine, the URL is transparently rewritten to `http://localhost:<port>`. Remote worker URLs are passed through unchanged.

## Lesson
When restricting network binding on an internal service, audit all code paths that connect to that service — not just external access, but self-referential calls too. In a controller-worker architecture where the controller is also a worker, the controller talks to itself via HTTP using a stored URL that may not match the new binding.
