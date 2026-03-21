# Design Index

> Maps design document sections to implementation status.
> Status: NOT_STARTED | IN_PROGRESS | IMPLEMENTED | VERIFIED | DRIFT | BLOCKED | DEFERRED
> Updated by /session-end, /design-audit, and /commit.

| Section | Status | Code Location | Last Verified | Notes |
|---|---|---|---|---|
| ARCHITECTURE.md — System Overview | IMPLEMENTED | entire codebase | 2026-03-21 | Initial documentation of existing system |
| ARCHITECTURE.md — Controller-Worker Model | IMPLEMENTED | api/, web/, docker/ | 2026-03-21 | Hub-and-spoke pattern |
| ARCHITECTURE.md — Data Flow | IMPLEMENTED | api/schedules/, api/commands/ | 2026-03-21 | Worker-to-Controller status pipeline |
| API.md — Flask-Smorest Framework | IMPLEMENTED | api/__init__.py, api/views/ | 2026-03-21 | 27 resource modules |
| API.md — Background Scheduler | IMPLEMENTED | api/schedules/, gunicorn.conf.py | 2026-03-21 | APScheduler with 22+ jobs |
| API.md — Endpoint Catalog | IMPLEMENTED | api/views/ | 2026-03-21 | ~100 endpoints |
| WEB-FRONTEND.md — Flask Blueprints | IMPLEMENTED | web/blueprints/ | 2026-03-21 | 14 blueprints |
| WEB-FRONTEND.md — Templates and Assets | IMPLEMENTED | web/templates/, web/static/ | 2026-03-21 | Jinja2 + Bootstrap 5 |
| DATA-LAYER.md — Multi-Database Architecture | IMPLEMENTED | common/models/, api/default_settings.py | 2026-03-21 | 21 SQLite databases |
| DATA-LAYER.md — ORM Models | IMPLEMENTED | common/models/ | 2026-03-21 | 18 model classes + 17 stat classes |
| BLOCKCHAIN-INTEGRATION.md — Fork Support | DRIFT | common/config/blockchains.json | 2026-03-21 | Design doc describes 50+ forks but Dockerfile now Chia-only. blockchains.json not yet cleaned up. |
| BLOCKCHAIN-INTEGRATION.md — RPC Client | IMPLEMENTED | api/commands/rpc.py | 2026-03-21 | Async RPC via Chia libraries |
| DOCKER-DEPLOYMENT.md — Container Build | DRIFT | docker/dockerfile | 2026-03-21 | Dockerfile now Chia-only; design doc still describes 34-fork build. Needs design doc update. |
| DOCKER-DEPLOYMENT.md — Entrypoint | DRIFT | docker/entrypoint.sh | 2026-03-21 | Entrypoint still has multi-fork code paths; not yet cleaned up |
| PLOTTING-FARMING.md — Plotter Support | DRIFT | scripts/forks/ | 2026-03-21 | Design doc mentions Gigahorse; removed from build. Bladebit + Madmax remain. |
| MONITORING-ALERTS.md — Chiadog | IMPLEMENTED | scripts/chiadog_setup.sh, config/chiadog/ | 2026-03-21 | Log-based monitoring |
| CONFIGURATION.md — Environment Variables | DRIFT | docker/dockerfile | 2026-03-21 | Dockerfile env vars simplified; design doc still lists fork-specific vars |
| CONFIGURATION.md — i18n | IMPLEMENTED | web/translations/, scripts/i18n/ | 2026-03-21 | 7 languages |
