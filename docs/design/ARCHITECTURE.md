# Architecture Overview

> System-level architecture of Machinaris — how all components fit together.

## 1. System Overview

Machinaris is a **multi-tier, multi-container** application for managing Chia blockchain farming. It bundles several open-source tools into a unified Docker image with a web dashboard and REST API.

### Core Components

| Component | Technology | Purpose |
|---|---|---|
| **WebUI** | Flask + Jinja2 + Bootstrap 5 | User-facing dashboard (port 8926) |
| **API Server** | Flask + flask-smorest | REST API + background data collection (port 8927) |
| **Common Layer** | SQLAlchemy + shared models | Shared data models, config, utilities |
| **Plotman** | Python CLI tool | Plot job scheduling and archiving |
| **Chiadog** | Python daemon | Log monitoring and alerting |
| **Bladebit/Madmax** | Native binaries | Plot file creation |
| **Chia Blockchain** | Python + native | Blockchain node, farmer, harvester, wallet |

### Technology Stack

```
Frontend:  Bootstrap 5, Chart.js, DataTables, Leaflet, jQuery
Backend:   Python 3.12+, Flask, Gunicorn, SQLAlchemy, APScheduler
Database:  SQLite (21 separate databases via WAL mode)
Infra:     Docker (Ubuntu 24.04 Noble), multi-arch (amd64/arm64)
```

## 2. Architecture Tiers

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1: Browser                                        │
│  HTML/CSS/JS (Bootstrap, Chart.js, DataTables, Leaflet) │
│  Auto-refresh (120s meta-refresh) + AJAX polling        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│  Tier 2: Web Application (Flask — port 8926)            │
│  14 blueprints, Jinja2 templates, Flask-Babel i18n      │
│  Action modules bridge to API and blockchain services   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (requests library)
┌────────────────────────▼────────────────────────────────┐
│  Tier 3: API Server (Flask-Smorest — port 8927)         │
│  27 resource modules, OpenAPI 3.0.2 spec                │
│  APScheduler background jobs (22+ scheduled tasks)      │
└──────┬─────────────────┬────────────────────────────────┘
       │ SQLAlchemy       │ RPC/CLI
┌──────▼──────┐   ┌──────▼──────────────────────────────┐
│ SQLite DBs  │   │ Blockchain Services                  │
│ 21 databases│   │ Chia full node, farmer, harvester,   │
│ WAL mode    │   │ wallet (+ 34 fork variants)          │
└─────────────┘   └─────────────────────────────────────┘
```

## 3. Controller-Worker Model

Machinaris uses a **hub-and-spoke** distributed architecture:

### Controller Node
- Runs the **WebUI** (user-facing dashboard)
- Runs a **fullnode** (blockchain sync, farming, wallet)
- Collects status from all workers via API
- Stores aggregated data in local SQLite databases
- Single controller per blockchain per deployment

### Worker Nodes
- Run as **harvesters**, **plotters**, or **farmers**
- Collect local status (plots, disk, memory) on a 2-minute interval
- POST status data to the controller's API endpoint
- Do NOT run the WebUI (API only)
- Fetch SSL certificates from controller for RPC access

### Communication Pattern

```
Worker Node                          Controller Node
┌──────────────┐                    ┌──────────────────┐
│ API Server   │───POST /farms/────▶│ API Server       │
│ (port 8927)  │───POST /plots/────▶│ (port 8927)      │
│              │───POST /stats/*───▶│                  │
│ Scheduler    │                    │ SQLite DBs       │
│ (every 2min) │                    │ WebUI (port 8926)│
└──────────────┘                    └──────────────────┘
```

### Operating Modes

| Mode | Services Started | Typical Role |
|---|---|---|
| `fullnode` | Full node + farmer + wallet + harvester | Controller (all-in-one) |
| `farmer` | Farmer only (connects to remote full node) | Dedicated farmer |
| `harvester` | Harvester only (connects to remote farmer) | Plot scanning on remote disks |
| `plotter` | No blockchain services | Dedicated plot creation |
| `farmer+plotter` | Farmer + plotter | Combined role |
| `harvester+plotter` | Harvester + plotter | Combined role |

## 4. Data Flow

### Status Collection Pipeline

Every 2 minutes (configurable), each node runs scheduled jobs that:

1. **Collect** — Query local blockchain services via RPC or CLI
2. **Transform** — Parse output into structured data
3. **Send** — POST JSON to controller API (or store locally if controller)
4. **Store** — Controller upserts data into SQLite databases

### Example: Farm Status Flow

```
1. Worker scheduler fires status_farm.update()
2. Calls chia_cli.load_farm_summary("chia")
3. Runs `chia farm summary` subprocess, parses output
4. Creates FarmSummary JSON payload
5. POSTs to http://controller:8927/farms/
6. Controller endpoint receives, upserts to farms.db
7. WebUI queries GET /farms/?hostname=worker1 to display
```

### Stats Aggregation

Time-series data follows a separate pipeline:
- Workers collect metric snapshots (plot count, disk usage, balances)
- POST batches to `/stats/*` endpoints
- Controller stores in dedicated `stat_*.db` files (one per metric)
- WebUI queries trends for Chart.js visualization

## 5. Process Architecture (Inside Container)

```
Gunicorn (API)              Gunicorn (WebUI)
├── Worker process          ├── Worker process
│   ├── Flask app           │   ├── Flask app
│   ├── APScheduler         │   └── Jinja2 renderer
│   │   ├── status_farm     │
│   │   ├── status_plots    │
│   │   ├── status_wallets  │
│   │   └── ... (22+ jobs)  │
│   └── SQLAlchemy          │
│                           │
Blockchain Services         Tool Daemons
├── chia (full_node)        ├── chiadog (log monitor)
├── chia (farmer)           ├── plotman (plot scheduler)
├── chia (harvester)        └── fd-cli (rewards)
└── chia (wallet)
```

Both Gunicorn servers run with 1 worker and 12 threads each. The API server additionally hosts the APScheduler instance that drives all background data collection.

## 6. Key Architectural Decisions

| Decision | Rationale |
|---|---|
| **Multi-database SQLite** | Isolation of concerns; independent backup; no external DB dependency |
| **Single blockchain per container** | Resource isolation; clean lifecycle; avoids port/config conflicts |
| **Stateless workers** | Workers don't persist state — all data centralized on controller |
| **APScheduler in Gunicorn** | Avoids separate daemon; integrates with Flask app context |
| **CLI subprocess parsing** | Works even without library updates; supports all fork variants |
| **Async RPC with asyncio** | Non-blocking I/O for parallel harvester queries |
| **SQLite WAL mode** | Better concurrency for write-heavy background collection |
| **Blueprint-per-resource** | Scalable API organization; automatic OpenAPI spec generation |

## 7. Security Model

- **No explicit authentication** — relies on Docker network isolation
- **No CSRF tokens** — forms protected by deployment-level security
- **SSL/TLS for RPC** — Chia-generated certificates for node communication
- **Implicit trust** — workers and controller trust each other within Docker network
- **ETAG disabled** — simplifies API responses (`ETAG_DISABLED = True`)
- **Hardcoded session key** — acceptable for single-user Docker deployment

## 8. Scalability Characteristics

- **Horizontal:** Add worker containers for more harvesters/plotters
- **Vertical:** Increase Gunicorn threads; adjust scheduler intervals for ARM64
- **Storage:** Plot directories mounted as Docker volumes (unlimited)
- **Multi-fork:** One container per blockchain fork, all reporting to same controller
- **Staggered startup:** Random 1-180s sleep prevents resource thundering in multi-container deployments
