# API Access Investigation

**Pushed:** 2026-03-23
**Source:** Response 1 in conversation (most recent substantive)
**Context:** User asked if API endpoints are used in single-instance farming and whether API access could be disabled/enabled. Also wants to investigate restricting API to local-only access via configuration, with future option to re-enable for multi-worker setups.

---

Great question — the answer is that the API is **essential even in a single-instance setup**. Here's why:

## How It Works

Machinaris runs **two Flask apps** in the same container:
- **WebUI** (port 8926) — what you see in your browser
- **API** (port 8927) — REST backend that does all the real work

Even on a single instance, the WebUI doesn't talk to Chia directly. Instead:

1. **WebUI → API**: Every button click (start plotting, send transaction, save config) makes an HTTP call from the WebUI to `http://localhost:8927/actions/`, `/configs/`, etc.
2. **API scheduler → API**: ~20 APScheduler jobs run every few minutes, collecting status from Chia's RPC and writing it to the database via the API endpoints (`/farms/`, `/plots/`, `/wallets/`, `/challenges/`, etc.)
3. **Database**: Both apps share SQLite files — API writes, WebUI reads.

## What Breaks If You Disable It

Essentially **everything**:
- Dashboard shows no data (farm summary, plot count, balance — all come from API)
- All buttons fail (start/stop plotting, farming, monitoring — all POST to API)
- Config changes can't save (farming, plotting, wallet configs — all go through API)
- Charts go blank (stats collection stops)
- No alerts or monitoring

The WebUI is just a thin presentation layer — the API is the entire brain.

## Could It Be Redesigned?

In a single-instance setup, the WebUI *could* theoretically talk to Chia's RPC and the database directly, bypassing the HTTP layer. But the current architecture was built for the **multi-worker model** (one controller + N remote workers), where HTTP is genuinely needed. For a single instance it's overengineered, but refactoring it would be a massive rewrite touching every blueprint, action module, and scheduler.

**Bottom line:** The API can't be disabled without breaking the app entirely. It's not an optional external interface — it's the internal communication backbone.

## Next Step

User wants to investigate restricting API access to localhost-only via configuration, with the ability to re-enable for multi-worker setups in the future. This is about network security — keeping port 8927 from being accessible to other machines on the network unless explicitly configured.
