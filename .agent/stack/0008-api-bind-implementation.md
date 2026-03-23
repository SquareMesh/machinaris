# API Bind Address Implementation

**Pushed:** 2026-03-23
**Source:** Response 1 in conversation (most recent)
**Context:** User approved implementing API bind address restriction with web UI guidance

---

All checks pass. Here's a summary of what was changed:

## Changes Made

**1. `docker/dockerfile`** — Added `api_bind_address` env var, defaulting to `127.0.0.1` (local only)

**2. `scripts/start_machinaris.sh`** — API gunicorn bind changed from hardcoded `0.0.0.0` to `${api_bind_address:-127.0.0.1}`

**3. `scripts/dev/start-api.sh`** — Same bind change for dev server

**4. `web/blueprints/settings.py`** — New `/settings/network` route that reads the current env vars and passes them to the template

**5. `web/templates/settings/network.html`** — New settings page with:
   - **Current status card** — shows bind address, ports, and a green "Local only" or amber "Open to network" badge
   - **Single instance guide** — explains why local-only is the default and that no action is needed
   - **Multi-worker guide** — step-by-step instructions for enabling remote workers (set `api_bind_address=0.0.0.0` on controller, set `controller_host` on workers)
   - **Ports reference table** — explains all 4 ports (8444, 8447, 8926, 8927) and which should/shouldn't be exposed

**6. `web/templates/base.html`** — Added "Network" link with shield-lock icon in the Settings sidebar (always visible, not gated by farming_enabled)

### Behavior

| `api_bind_address` | API accessible from | Use case |
|---|---|---|
| `127.0.0.1` (default) | Inside container only | Single-instance farming |
| `0.0.0.0` | Any machine on LAN | Remote harvesters/plotters |

Users switch modes by adding/changing the `api_bind_address` Docker env var and restarting the container.
