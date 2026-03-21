# Docker and Deployment Design

> Container build process, entrypoint orchestration, scripts, and multi-container deployment.

## 1. Docker Image Architecture

### Base Images

Two Ubuntu base images support multi-architecture builds:

| Image | OS | Architectures |
|---|---|---|
| `machinaris-base-jammy` | Ubuntu 22.04 (Jammy) | linux/amd64, linux/arm64 |
| `machinaris-base-noble` | Ubuntu 24.04 (Noble) | linux/amd64, linux/arm64 |

Base images install: Python 3, build tools, git, cmake, sqlite3, smartmontools, archive utilities, Docker networking tools.

### Main Dockerfile

Multi-stage build inheriting from the versioned base image:

```dockerfile
FROM ghcr.io/guydavis/machinaris-base-${UBUNTU_VER}:${MACHINARIS_STREAM}
```

**Build sequence:**
1. Copy Machinaris source code to `/machinaris/`
2. Run 34 fork install scripts (chained with `&&`)
3. Pull 3rd-party JS libraries (vendored, no CDN)
4. Install Machinaris application
5. Compile i18n translation files
6. Clean up apt cache and temp files

### Build Arguments

34 blockchain fork branches are parametric build arguments:

```dockerfile
ARG CHIA_BRANCH=latest
ARG CHIVES_BRANCH=latest
ARG MMX_BRANCH=latest
ARG FLAX_BRANCH=latest
# ... 30 more forks
```

### Exposed Ports

| Port | Service | Notes |
|---|---|---|
| 8444 | Chia protocol | Forward at router for syncing |
| 8447 | Farmer port | Internal only (DO NOT forward) |
| 8926 | Machinaris WebUI | Proxy if exposing externally |
| 8927 | Machinaris API | Workers connect here |
| 8928-8960 | Fork-specific worker ports | One per blockchain fork |

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
2. Enforce single-blockchain-per-container
3. Validate worker_address is set
4. Run version-specific upgrade migrations
5. Launch blockchain services (via blockchains_launch.sh)
6. Start Machinaris WebUI + API (via start_machinaris.sh)
7. Install tools (staggered with random sleep):
   a. Plotman (plotters/fullnodes only)
   b. Chiadog (fullnodes/harvesters only)
   c. Random 1-180s sleep (stagger multi-container startup)
   d. fd-cli (non-Chia forks)
   e. Bladebit (Chia plotters)
   f. Madmax (all forks for CPU plotting)
   g. Plotman auto-plot/archive (if AUTO_PLOT/AUTO_ARCHIVE)
   h. Forktools (non-MMX/Gigahorse fullnodes)
8. Tail /dev/null (keep container alive)
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
2. Configure Plotman with blockchain-specific sample config
3. Inject farmer_pk, pool_pk, pool_contract_address via sed
4. Import SSH key if `/id_rsa` volume mounted
5. Initialize database (`setup_databases.sh` → `flask db upgrade`)
6. Launch two Gunicorn servers:
   - API: port 8927, 12 threads, 1 worker
   - WebUI: port 8926, 12 threads, 1 worker

## 3. Script Architecture

### Fork Installation Scripts

Each fork has paired scripts in `scripts/forks/`:

| Script | Purpose |
|---|---|
| `[fork]_install.sh` | Clone repo, build, install dependencies |
| `[fork]_launch.sh` | Start services based on operating mode |

**Installation pattern:**
```bash
git clone --branch ${FORK_BRANCH} [REPO_URL] /[fork]-blockchain
cd /[fork]-blockchain && ./install.sh
# Symlink to /chia-blockchain for tool compatibility
# Create wrapper for `chia` command
```

**Launch pattern (mode-dependent):**
- `fullnode` → `chia start farmer` (or `farmer-no-wallet`)
- `farmer` → `chia start farmer-only`
- `harvester` → Fetch certs from controller, configure peer, `chia start harvester`
- `plotter` → No blockchain services started

### Tool Installation Scripts

| Script | Condition | Purpose |
|---|---|---|
| `plotman_setup.sh` | fullnode/plotter + chia/chives/mmx/gigahorse | Install Plotman plot scheduler |
| `chiadog_setup.sh` | fullnode/harvester, all forks except mmx | Install log monitoring daemon |
| `bladebit_setup.sh` | fullnode/plotter + chia only | Download Bladebit plotters |
| `madmax_setup.sh` | all forks | Download Madmax plotters (CPU + CUDA) |
| `forktools_setup.sh` | fullnode/harvester, non-mmx/gigahorse | Install fork reward recovery |
| `fd-cli_setup.sh` | fullnode, non-chia/chives/mmx/gigahorse | Install Flora dev CLI |
| `gpu_drivers_install.sh` | build time | Install OpenCL + AMD GPU drivers |
| `gpu_drivers_setup.sh` | runtime, per-fork | Enable GPU-specific features |

### Infrastructure Scripts

| Script | Purpose |
|---|---|
| `setup_databases.sh` | Flask-Migrate DB initialization |
| `config_api_server.sh` | Create API config with arch-specific defaults |
| `pull_3rd_party_libs.sh` | Download and vendor all JS/CSS libraries |
| `mount_remote_shares.sh` | Mount CIFS/SMB network shares |
| `worker_port_warning.sh` | Validate worker API ports match fork defaults |
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

## 4. Multi-Container Deployment Patterns

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

### Multi-Fork Farm

One container per fork (enforced single-blockchain):
```
Container 1: blockchains=chia,  mode=fullnode, worker_api_port=8927
Container 2: blockchains=flax,  mode=fullnode, worker_api_port=8928
Container 3: blockchains=chives, mode=fullnode, worker_api_port=8931
```

All connect to same controller for centralized metrics.

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

### Container Registries

- DockerHub: `ghcr.io/guydavis/machinaris-base-*`
- GitHub Container Registry (GHCR): Secondary registry

### Image Tags

- `:latest` — Production release
- `:develop` — Development builds
- `:test` — Test builds

## 6. Log Rotation

| Service | Config | Rotation |
|---|---|---|
| Machinaris (apisrv, webui) | `/etc/logrotate.d/machinaris` | 7-day daily |
| Plotman | `/etc/logrotate.d/plotman` | 3-day daily |
| MMX (node, farmer, harvester) | `/etc/logrotate.d/mmx-*` | 3-day daily |

## 7. Python Dependencies

Installed from `docker/requirements.txt`:
- Flask, flask-smorest, flask-migrate, flask-babel
- SQLAlchemy, marshmallow-sqlalchemy
- APScheduler
- Gunicorn
- psutil, requests, pexpect
- And blockchain-specific libraries per fork
