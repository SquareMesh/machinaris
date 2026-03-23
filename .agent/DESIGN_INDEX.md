# Design Index

> Maps design document sections to implementation status.
> Status: NOT_STARTED | IN_PROGRESS | IMPLEMENTED | VERIFIED | DRIFT | BLOCKED | DEFERRED
> Updated by /session-end, /design-audit, and /commit.

| Section | Status | Code Location | Last Verified | Notes |
|---|---|---|---|---|
| ARCHITECTURE.md — System Overview | IMPLEMENTED | entire codebase | 2026-03-23 | Updated: Python 3.12+, Ubuntu Noble-only |
| ARCHITECTURE.md — Controller-Worker Model | IMPLEMENTED | api/, web/, docker/ | 2026-03-21 | Hub-and-spoke pattern |
| ARCHITECTURE.md — Data Flow | IMPLEMENTED | api/schedules/, api/commands/ | 2026-03-21 | Worker-to-Controller status pipeline |
| API.md — Flask-Smorest Framework | IMPLEMENTED | api/__init__.py, api/views/ | 2026-03-23 | 27 resource modules. /ping health endpoint added. Request timeouts on all HTTP utils. marshmallow-toplevel replaced with inline TopLevelSchema. |
| API.md — Background Scheduler | IMPLEMENTED | api/schedules/, gunicorn.conf.py | 2026-03-21 | APScheduler with 22+ jobs |
| API.md — Endpoint Catalog | IMPLEMENTED | api/views/ | 2026-03-21 | ~100 endpoints |
| WEB-FRONTEND.md — Flask Blueprints | IMPLEMENTED | web/blueprints/ | 2026-03-22 | 15 blueprints (added auth_bp for TOTP) |
| WEB-FRONTEND.md — Templates and Assets | IMPLEMENTED | web/templates/, web/static/ | 2026-03-22 | Jinja2 + Bootstrap 5. All |safe filters removed. Flash macro in _flash_messages.html. |
| DATA-LAYER.md — Multi-Database Architecture | IMPLEMENTED | common/models/, api/default_settings.py | 2026-03-23 | 21 SQLite databases. Indexes added on hostname, blockchain, created_at. |
| DATA-LAYER.md — ORM Models | IMPLEMENTED | common/models/ | 2026-03-23 | 18 model classes + 17 stat classes. All bare except: replaced. |
| BLOCKCHAIN-INTEGRATION.md — Chia Integration | VERIFIED | common/config/blockchains.json, api/commands/rpc.py | 2026-03-23 | Chia-only. blockchains.json trimmed to single entry. All fork-specific code paths cleaned. |
| BLOCKCHAIN-INTEGRATION.md — RPC Client | IMPLEMENTED | api/commands/rpc.py | 2026-03-22 | Updated for Chia 2.6.x module restructure. Chia-only imports. |
| DOCKER-DEPLOYMENT.md — Container Build | IMPLEMENTED | docker/dockerfile | 2026-03-23 | Added HEALTHCHECK. Deps pinned. Build scripts have set -eo pipefail. |
| DOCKER-DEPLOYMENT.md — Entrypoint | VERIFIED | docker/entrypoint.sh | 2026-03-23 | set -eo pipefail added to entrypoint.sh + 11 other scripts. grep -q anti-patterns fixed. |
| PLOTTING-FARMING.md — Plotter Support | IMPLEMENTED | scripts/bladebit_setup.sh, scripts/madmax_setup.sh | 2026-03-22 | Gigahorse removed. Bladebit + Madmax remain. Design doc updated. |
| MONITORING-ALERTS.md — Chiadog | IMPLEMENTED | scripts/chiadog_setup.sh, config/chiadog/ | 2026-03-21 | Log-based monitoring |
| CONFIGURATION.md — Environment Variables | IMPLEMENTED | docker/dockerfile | 2026-03-22 | Fork-specific vars removed. Chia-only env vars. Design doc updated. |
| CONFIGURATION.md — Security | VERIFIED | web/__init__.py, web/blueprints/auth.py, common/utils/totp.py, web/templates/ | 2026-03-22 | TOTP auth (optional). CSRF (Flask-WTF). Command injection eliminated. Mnemonic logging removed. All |safe filters removed. Secret key file-based. Verified on Unraid. |
| CONFIGURATION.md — i18n | IMPLEMENTED | web/translations/, scripts/i18n/ | 2026-03-21 | 7 languages |
| TELEGRAM-NOTIFICATIONS.md — Balance Change Detection | IMPLEMENTED | api/commands/balance_notifications.py, api/views/wallets/resources.py | 2026-03-22 | Hooks into Wallets.post() for near-real-time detection |
| TELEGRAM-NOTIFICATIONS.md — Notification Config | IMPLEMENTED | common/utils/notifications.py, api/views/configs/resources.py | 2026-03-22 | JSON config at /root/.chia/machinaris/config/notifications.json |
| TELEGRAM-NOTIFICATIONS.md — Web UI | IMPLEMENTED | web/blueprints/settings.py, web/templates/settings/notifications.html | 2026-03-22 | Settings > Notifications page with guided setup |
