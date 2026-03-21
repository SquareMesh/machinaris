# API Layer Design

> REST API architecture, endpoint catalog, schemas, and background scheduler.

## 1. Framework

- **Framework:** Flask with flask-smorest (REST API scaffolding)
- **Serialization:** Marshmallow + marshmallow-sqlalchemy
- **Spec:** OpenAPI 3.0.2 (auto-generated at `/api-spec.json`, ReDoc UI at `/`)
- **WSGI Server:** Gunicorn (1 worker, 12 threads)
- **Entry Point:** `api/__init__.py` creates Flask app, `api:app` is the WSGI target

### Initialization Flow

1. Create Flask app instance
2. Load config from `default_settings.py` (overridable via `API_SETTINGS_FILE` env var)
3. Initialize extensions (SQLAlchemy, Flask-Babel, Flask-Migrate)
4. Set SQLite PRAGMA for WAL mode
5. Register all blueprint modules
6. Gunicorn `on_starting` hook initializes APScheduler

## 2. Code Organization

```
api/
├── __init__.py              # Flask app factory
├── default_settings.py      # Database bindings, API config
├── gunicorn.conf.py         # Gunicorn + APScheduler lifecycle
├── log.conf                 # Python logging config
│
├── commands/                # Blockchain interaction layer
│   ├── chia_cli.py          # Subprocess calls to chia CLI
│   ├── rpc.py               # Async RPC client for all forks
│   └── websvcs.py           # External API calls (AllTheBlocks, prices)
│
├── extensions/              # Flask extension init
│   └── api/
│       └── __init__.py      # Custom Schema, AutoSchema, SQLCursorPage
│
├── schedules/               # Background job modules (22+)
│   ├── status_farm.py
│   ├── status_plots.py
│   ├── stats_farm.py
│   └── ...
│
└── views/                   # REST endpoint modules (27)
    ├── actions/
    ├── alerts/
    ├── blockchains/
    ├── challenges/
    ├── connections/
    ├── configs/
    ├── drives/
    ├── farms/
    ├── keys/
    ├── logs/
    ├── partials/
    ├── plotnfts/
    ├── plots/
    ├── plottings/
    ├── pools/
    ├── stats/
    ├── wallets/
    ├── warnings/
    └── workers/
```

Each view module follows a consistent structure:
- `__init__.py` — imports and exposes the `blp` blueprint
- `resources.py` — Flask MethodView classes with GET/POST/PUT/DELETE
- `schemas.py` — Marshmallow validation schemas

## 3. Endpoint Catalog

### Core Operations

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Ping | `/ping` | GET | Health check |
| Actions | `/actions` | POST | Dispatch farming/plotting/pooling actions |
| Configs | `/configs` | GET/POST/PUT | Blockchain configuration file management |
| Logs | `/logs` | GET | API server log retrieval |

### Blockchain Status

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Blockchains | `/blockchains` | GET/POST/PUT/DELETE | Node sync status per host |
| Connections | `/connections` | GET/POST/PUT/DELETE | P2P peer connections |
| Keys | `/keys` | GET/POST/PUT/DELETE | Wallet/farmer/pool keys |
| Certificates | `/certificates` | GET | SSL certificates for RPC access |

### Farming

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Wallets | `/wallets` | GET/POST/PUT/DELETE | Wallet balances and sync status |
| Plots | `/plots` | GET/POST/PUT/DELETE | Plot metadata and validation |
| Challenges | `/challenges` | GET/POST/PUT/DELETE | Farming challenges received |
| Partials | `/partials` | GET/POST/PUT/DELETE | Pool partial submissions |
| Rewards | `/rewards` | GET | Farmed blocks and balance changes |
| Transactions | `/transactions` | GET | Wallet transaction history |

### Plotting

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Plottings | `/plottings` | GET/POST/PUT/DELETE | Active plotting jobs |
| Plot NFTs | `/plotnfts` | GET/POST/PUT/DELETE | Pool join events and contract state |

### Infrastructure

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Pools | `/pools` | GET/POST/PUT/DELETE | Pool metadata and difficulty |
| Drives | `/drives` | GET/POST/PUT/DELETE | Disk usage and S.M.A.R.T. status |
| Alerts | `/alerts` | GET/POST/PUT/DELETE | Node alerts |
| Warnings | `/warnings` | GET/POST/PUT/DELETE | Invalid/duplicate plot warnings |
| Workers | `/workers` | GET/POST/PUT/DELETE | Harvester/plotter node metadata |

### Time-Series Statistics

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| PlotCount | `/stats/plotcount` | GET/POST | Historical plot counts |
| PlotsSize | `/stats/plotssize` | GET/POST | Total plot size over time |
| TotalCoins | `/stats/totalcoins` | GET/POST | Accumulated farmed coins |
| NetspaceSize | `/stats/netspacesize` | GET/POST | Network difficulty trend |
| TimeToWin | `/stats/timetowin` | GET/POST | Expected block win rate |
| Effort | `/stats/effort` | GET/POST | Actual vs expected blocks |
| DiskUsed/Free | `/stats/plotsdiskused` etc. | GET/POST | Storage trends |
| FarmedBlocks | `/stats/farmedblocks` | GET/POST | Block farming history |
| WalletBalances | `/stats/walletbalances` | GET/POST | Balance history |
| ContainerMem | `/stats/containermem` | GET/POST | Container memory usage |
| HostMemPct | `/stats/hostmempct` | GET/POST | Host memory percentage |

### Analysis

| Resource | URL Prefix | Methods | Purpose |
|---|---|---|---|
| Analysis | `/analysis` | GET | Computed metrics (ROI, efficiency) |
| Metrics | `/metrics` | GET | Prometheus-compatible metrics export |

## 4. API Patterns

### Request/Response

```python
# List with filtering
GET /farms/?hostname=worker1&blockchain=chia

# Batch upsert (workers POST status)
POST /farms/
Content-Type: application/json
[{hostname: "worker1", blockchain: "chia", plot_count: 500, ...}]

# Single resource
GET /farms/<id>
PUT /farms/<id>
DELETE /farms/<id>
```

### Schema Pattern

```python
class FarmSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Farm.__table__

class FarmQueryArgsSchema(Schema):
    hostname = ma.fields.Str()
    blockchain = ma.fields.Str()
```

### Upsert Logic

Most POST endpoints use upsert: lookup by hostname + blockchain, update timestamps, merge fields. This supports the worker status collection pattern where workers repeatedly POST their current state.

## 5. Background Scheduler

The APScheduler instance is initialized in Gunicorn's `on_starting` hook and runs 22+ jobs:

### Status Collection (every 2 minutes)

| Job | Module | Collects |
|---|---|---|
| status_worker | status_worker.py | Container memory/CPU |
| status_farm | status_farm.py | Farm summary (plots, coins, netspace) |
| status_wallets | status_wallets.py | Wallet balances |
| status_blockchains | status_blockchains.py | Node sync/peak height |
| status_connections | status_connections.py | P2P peer count |
| status_keys | status_keys.py | Key validity |
| status_plots | status_plots.py | Plot list via RPC |
| status_plotting | status_plotting.py | Active plotting jobs |
| status_challenges | status_challenges.py | Recent challenges |
| status_alerts | status_alerts.py | Node alerts |
| status_pools | status_pools.py | Pool metadata |
| status_plotnfts | status_plotnfts.py | Pool join status |
| status_partials | status_partials.py | Partial submissions |
| status_drives | status_drives.py | Disk S.M.A.R.T. |

### Stats Snapshots (hourly / 10-minute)

| Job | Collects |
|---|---|
| stats_farm | Farm metrics snapshot |
| stats_balances | Wallet balance snapshot |
| stats_blocks | Farmed block count |
| stats_disk | Disk usage metrics |
| stats_effort | Actual vs expected blocks |

### Housekeeping

| Job | Interval | Purpose |
|---|---|---|
| log_rotate | Hourly | Rotate log files |
| plots_check | 2 min (30 min delay) | Validate plot integrity |
| nft_recover | Hourly | NFT recovery |
| restart_stuck_farmer | 10 min | Auto-restart stalled farmer |
| periodically_sync_wallet | 15 min | Force wallet sync |
| geolocate_peers | 2 min | Map peer locations (controller only) |

### Job Dispatch Pattern

1. Scheduler fires job within Flask app context
2. Job runs RPC queries or CLI commands
3. Sends POST to controller API (or localhost if controller)
4. Controller upserts data into SQLite

## 6. Blockchain Interaction

### RPC Client (`api/commands/rpc.py`)

- Dynamic imports for 40+ blockchains based on `globals.enabled_blockchains()`
- Uses each blockchain's Python library for typed RPC access
- Async operations with `asyncio` for non-blocking queries
- Key methods: `get_all_plots()`, `get_wallets()`, `get_transactions()`, `get_pool_states()`

### CLI Interaction (`api/commands/chia_cli.py`)

- Spawns subprocess calls to blockchain binaries (e.g., `chia farm summary`)
- Parses text output with regex
- 30-second timeout management
- Fallback when RPC is unavailable

### External Services (`api/commands/websvcs.py`)

- AllTheBlocks API for cold wallet balance tracking
- Blockchain price data from CoinGecko/CoinPaprika
- Exchange rate caching for fiat conversion

## 7. Configuration

### Database Bindings (`default_settings.py`)

21 separate SQLite databases with independent bindings:
- Core: `default.db`, `alerts.db`, `blockchains.db`, `farms.db`, `plots.db`, `wallets.db`, `workers.db`, etc.
- Stats: `stat_plot_count.db`, `stat_plots_size.db`, `stat_total_coins.db`, etc.

All databases stored at `/root/.chia/machinaris/dbs/`.

### API Settings

```
ETAG_DISABLED = True
SEND_FILE_MAX_AGE_DEFAULT = 86400
STATUS_EVERY_X_MINUTES = 2 (x86_64) / 4 (ARM64)
ALLOW_HARVESTER_CERT_LAN_DOWNLOAD = True
```

### Localization

Flask-Babel with 7 languages: en, de_DE, fr_FR, it_IT, nl_NL, pt_PT, zh.
