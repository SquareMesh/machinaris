# Docker and Deployment Design

> Container build process, entrypoint orchestration, scripts, and deployment.
>
> **Note:** As of v2.7.0, Machinaris is Chia-only. The Docker image builds only Chia. Base image published under `squaremesh` namespace on GHCR.

## 1. Docker Image Architecture

### Base Image

| Image | OS | Architectures |
|---|---|---|
| `ghcr.io/squaremesh/machinaris-base-noble` | Ubuntu 24.04 (Noble) | linux/amd64, linux/arm64 |

Base image installs: Python 3, build tools, git, cmake, sqlite3, smartmontools, archive utilities, Docker networking tools.

### Main Dockerfile

Single-stage build inheriting from the base image:

```dockerfile
FROM ghcr.io/squaremesh/machinaris-base-noble:${MACHINARIS_STREAM}
```

**Build sequence:**
1. Copy Machinaris source code to `/machinaris/`
2. Run Chia install script
3. Pull 3rd-party JS libraries (vendored, no CDN)
4. Install Machinaris application
5. Compile i18n translation files
6. Clean up apt cache and temp files

### Build Arguments

```dockerfile
ARG CHIA_BRANCH=latest
```

### Exposed Ports

| Port | Service | Notes |
|---|---|---|
| 8444 | Chia protocol | Forward at router for syncing |
| 8447 | Farmer port | Internal only (DO NOT forward) |
| 8926 | Machinaris WebUI | Proxy if exposing externally |
| 8927 | Machinaris API | Workers connect here |

### Volume Mounts

| Path | Purpose |
|---|---|
| `/id_rsa` | Optional SSH key for remote plot management |
| `/plots*` | Plot directories (read by farmer/harvester) |
| `/plotting*` | Temporary plotting directories |
| `/root/.chia` | Persistent configuration, wallets, databases |

## 2. Entrypoint Orchestration

### File: `docker/entrypoint.sh`

The entrypoint is the container startup orchestrator. It runs sequentially:

```
1. Validate hostname (no spaces/quotes)
2. Validate worker_address is set
3. Run version-specific upgrade migrations
4. Launch Chia blockchain services (via chia_launch.sh)
5. Start Machinaris WebUI + API (via start_machinaris.sh)
6. Install tools:
   a. Plotman (plotters/fullnodes only)
   b. Chiadog (fullnodes/harvesters only)
   c. Bladebit (Chia plotters)
   d. Madmax (CPU plotting, x86_64 only)
   e. Plotman auto-plot/archive (if AUTO_PLOT/AUTO_ARCHIVE)
7. Tail /dev/null (keep container alive)
```

### Upgrade Migrations

The entrypoint includes version-specific migration checks:

| Version | Migration |
|---|---|
| v0.6.0 | Single blockchain enforcement |
| v0.6.8 | Move plotnft.log location |
| v0.7.0 | Move cache JSON files |
| v0.8.3 | Refresh blockchain prices cache |
| v0.8.5 | Upgrade fd-cli, plotman logging |

### Machinaris Startup (`start_machinaris.sh`)

1. Create log and config directories
2. Configure Plotman with Chia sample config
3. Inject farmer_pk, pool_pk, pool_contract_address via sed
4. Import SSH key if `/id_rsa` volume mounted
5. Initialize database (`setup_databases.sh` → `flask db upgrade`)
6. Launch two Gunicorn servers:
   - API: port 8927, 12 threads, 1 worker
   - WebUI: port 8926, 12 threads, 1 worker

## 3. Script Architecture

### Chia Installation

| Script | Purpose |
|---|---|
| `scripts/forks/chia_install.sh` | Clone repo, build, install dependencies |
| `scripts/forks/chia_launch.sh` | Start services based on operating mode |

**Launch pattern (mode-dependent):**
- `fullnode` → `chia start farmer` (or `farmer-no-wallet`)
- `farmer` → `chia start farmer-only`
- `harvester` → Fetch certs from controller, configure peer, `chia start harvester`
- `plotter` → No blockchain services started

### Tool Installation Scripts

| Script | Condition | Purpose |
|---|---|---|
| `plotman_setup.sh` | fullnode/plotter | Install Plotman plot scheduler |
| `chiadog_setup.sh` | fullnode/harvester | Install log monitoring daemon |
| `bladebit_setup.sh` | fullnode/plotter | Download Bladebit plotters |
| `madmax_setup.sh` | fullnode/plotter | Download Madmax plotters (CPU + CUDA) |
| `gpu_drivers_install.sh` | build time | Install OpenCL + AMD GPU drivers |
| `gpu_drivers_setup.sh` | runtime | Enable GPU-specific features |

### Infrastructure Scripts

| Script | Purpose |
|---|---|
| `setup_databases.sh` | Flask-Migrate DB initialization |
| `config_api_server.sh` | Create API config with arch-specific defaults |
| `pull_3rd_party_libs.sh` | Download and vendor all JS/CSS libraries |
| `mount_remote_shares.sh` | Mount CIFS/SMB network shares |
| `worker_port_warning.sh` | Validate worker API port (simplified to 4 lines) |
| `chiadog_notifier.sh` | Custom notification hook |
| `plotman_autoplot.sh` | Auto-start plotting/archiving |

### Development Scripts (`scripts/dev/`)

| Script | Purpose |
|---|---|
| `start-api.sh` | Dev API server with auto-reload |
| `start-web.sh` | Dev WebUI server |
| `swap-plotman.sh` | Switch Plotman versions |

### i18n Scripts (`scripts/i18n/`)

| Script | Purpose |
|---|---|
| `extract.sh` | Extract translatable strings from source |
| `compile.sh` | Compile .po to .mo files |
| `init.sh` | Initialize new language translation |

## 4. Deployment Patterns

### Standalone Fullnode

Single container running everything:
```yaml
environment:
  - blockchains=chia
  - mode=fullnode
  - worker_address=192.168.1.100
```

### Distributed Farm

```
Controller (fullnode):
  blockchains=chia, mode=fullnode, worker_address=192.168.1.100

Harvester 1:
  blockchains=chia, mode=harvester
  farmer_address=192.168.1.100
  worker_address=192.168.1.101

Plotter 1:
  blockchains=chia, mode=plotter
  controller_host=192.168.1.100
  worker_address=192.168.1.102
  AUTO_PLOT=true
```

## 5. CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `unit-tests.yml` | Push to develop | Run pytest on Ubuntu |
| `test-base.yaml` | Manual dispatch | Build test base images |
| `develop-base.yaml` | Manual dispatch | Build develop base images |
| `main-base.yaml` | Manual dispatch | Build production base images |
| `test-blockchains.yaml` | Manual dispatch | Build test blockchain images |
| `develop-blockchains.yaml` | Manual dispatch | Build develop blockchain images |
| `main-blockchains.yaml` | Manual dispatch | Build production blockchain images |
| `codeql-analysis.yml` | Scheduled | Security scanning |

### Container Registry

- GitHub Container Registry (GHCR): `ghcr.io/squaremesh/machinaris`
- Base images: `ghcr.io/squaremesh/machinaris-base-noble`

### Image Tags

- `:latest` — Production release
- `:develop` — Development builds
- `:test` — Test builds
- `:<version>` — Pinned version (e.g., `:2.7.0`)

## 6. Log Rotation

| Service | Config | Rotation |
|---|---|---|
| Machinaris (apisrv, webui) | `/etc/logrotate.d/machinaris` | 7-day daily |
| Plotman | `/etc/logrotate.d/plotman` | 3-day daily |

## 7. Python Dependencies

Installed from `docker/requirements.txt`:
- Flask, flask-smorest, flask-migrate, flask-babel
- SQLAlchemy, marshmallow-sqlalchemy
- APScheduler
- Gunicorn
- psutil, requests, pexpect
