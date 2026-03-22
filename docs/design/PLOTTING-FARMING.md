# Plotting and Farming Design

> Plot creation tools, farming operations, GPU support, archiving, and replotting.
>
> **Note:** As of v2.7.0, Machinaris is Chia-only. Gigahorse has been removed from the build. Bladebit and Madmax remain as the supported plotters.

## 1. Overview

Machinaris orchestrates plotting tools and farming operations through Plotman (plot scheduler) and direct integration with the Chia farmer service.

### Plotting Pipeline

```
Plotman (scheduler)
  ↓ spawns
Plotter (Bladebit or Madmax)
  ↓ creates
Plot files (.plot)
  ↓ optionally
Archive (rsync to remote destinations)
  ↓
Farmer/Harvester reads plots for challenges
```

## 2. Supported Plotters

### Bladebit

| Attribute | Value |
|---|---|
| **Install script** | `scripts/bladebit_setup.sh` |
| **Binary location** | `/usr/bin/bladebit`, `/usr/bin/bladebit_cuda` |
| **Architectures** | x86_64, ARM64 |
| **Modes** | Disk, RAM, GPU (CUDA) |
| **Version** | v3.1.0 (prebuilt binaries from Chia-Network/bladebit) |
| **Skip flag** | `bladebit_skip_build=true` |

### Madmax

| Attribute | Value |
|---|---|
| **Install script** | `scripts/madmax_setup.sh` |
| **Binary location** | `/usr/bin/chia_plot`, `/usr/bin/chia_plot_k34` |
| **Architectures** | x86_64 only (ARM64 unsupported, prints warning) |
| **Variants** | CPU (`chia_plot`), CUDA (`cuda_plot_k26` through `cuda_plot_k33`) |
| **Additional tools** | ProofOfSpace binary for compressed plot verification |
| **Skip flag** | `madmax_skip_build=true` |

## 3. Plotman (Plot Scheduler)

### Installation

- **Script:** `scripts/plotman_setup.sh`
- **Source:** `guydavis/plotman` (enhanced fork)
- **Condition:** fullnode/plotter modes

### Configuration

```yaml
# config/plotman.sample.yaml — Chia default
directories:
  tmp: [/plotting]       # Temp space for plot creation
  dst: [/plots]          # Final plot destination

scheduling:
  tmpdir_stagger_phase: [5, 0]  # Major/minor phase stagger
  tmpdir_max_jobs: 2             # Max concurrent per temp dir
  global_max_jobs: 2             # Max concurrent total
  global_stagger_m: 30           # Minutes between starts
  polling_time_s: 20             # Status check interval

plotting:
  farmer_pk: <injected>
  pool_pk: <injected>
  pool_contract_address: <injected>
```

### Auto-Plot / Auto-Archive

Environment variables trigger automatic operations:

```
AUTO_PLOT=true   → plotman plot (background via nohup)
AUTO_ARCHIVE=true → plotman archive (background via nohup)
```

Script: `scripts/plotman_autoplot.sh`

## 4. Plot Sizes

```
k29:  ~6.3 GiB  (13 GiB temp required)
k30:  ~12.6 GiB (26 GiB temp required)
k31:  ~25.2 GiB (52 GiB temp required)
k32:  ~101 GiB  (104 GiB temp required)  ← Standard
k33:  ~208 GiB  (210 GiB temp required)
k34:  ~429 GiB  (432 GiB temp required)
```

Defined in `common/models/plottings.py`:
```python
KSIZES = [29, 30, 31, 32, 33, 34]
FREE_GIBS_REQUIRED_FOR_KSIZE = {29: 13, 30: 26, 31: 52, 32: 104, 33: 210, 34: 432}
```

## 5. GPU Support

### Installation

- **Build time:** `scripts/gpu_drivers_install.sh` (OpenCL packages, AMD drivers)
- **Runtime:** `scripts/gpu_drivers_setup.sh` (GPU enablement)

### Environment Variables

```
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility
OPENCL_GPU=null|amd|nvidia
```

### GPU Plotters

| Plotter | GPU Support |
|---|---|
| Bladebit CUDA | NVIDIA (via `bladebit_cuda`) |
| Madmax CUDA | NVIDIA (`cuda_plot_k26` through `cuda_plot_k33`) |

### AMD GPU Notes

- Driver pinned to version 5.4 (5.5 reported broken)
- Installs `amdgpu-install` stub + `radeontop` monitoring
- OpenCL development packages for compute

## 6. Farming Operations

### Challenge Processing

The farmer receives challenges from the blockchain network:

1. Challenge arrives from full node
2. Farmer queries all harvesters for qualifying plots
3. Harvesters scan plot files, return proofs
4. Farmer submits proofs to network
5. Machinaris records challenge data in `challenges.db`

### Harvester Management

- Harvesters connect to farmer via configured `farmer_address`
- SSL certificates exchanged for secure RPC communication
- Plot directories registered via `chia plots add`
- Status collected every 2 minutes by API scheduler

### Wallet Operations

- Wallet sync managed by Chia blockchain service
- Auto-sync every 15 minutes (`periodically_sync_wallet`)
- Wallet can be paused/resumed via config file
- Cold wallet balance tracking via AllTheBlocks API
- Stuck farmer auto-restart every 10 minutes
- Balance change notifications via Telegram (see TELEGRAM-NOTIFICATIONS.md)

## 7. Archiving

Plot archiving moves completed plots from local temp storage to remote destinations:

### rsync-Based

```yaml
# plotman.yaml archiving section
archiving:
  target: rsync
  env:
    dst: user@remote:/plots
```

### Features

- Plotman manages archive queue
- Transfer progress tracked in `transfers.db`
- Log directory: `/root/.chia/plotman/logs/archiving/`
- Log rotation: 3-day daily

## 8. Replotting

The WebUI supports replotting criteria:

- Select plots to replace based on type, size, age
- Verify free space meets k-size requirements
- Queue new plot jobs via Plotman
- Old plots deleted after successful replacement

### Free Space Requirements

Before replotting, Machinaris checks:
```python
if free_gibs < FREE_GIBS_REQUIRED_FOR_KSIZE[target_ksize]:
    # Reject replot — insufficient space
```

## 9. Plot Integrity

### Plot Check

Scheduled every 2 minutes (with 30-minute startup delay):

- Verifies plot file integrity
- Results stored in plot's `plot_check` field
- Warnings generated for invalid/duplicate plots
- Status in: `/root/.chia/plotman/status.json`

### Plot Analysis

On-demand via WebUI:
- Detailed analysis of individual plot files
- Results stored in plot's `plot_analyze` field
- Triggered via AJAX request to farming blueprint
