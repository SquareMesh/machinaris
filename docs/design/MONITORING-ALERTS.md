# Monitoring and Alerts Design

> Chiadog monitoring, scheduled background jobs, drive health, and notification system.

## 1. Overview

Machinaris provides three layers of monitoring:

| Layer | Tool | Purpose |
|---|---|---|
| **Log Monitoring** | Chiadog | Watch blockchain debug logs for events |
| **Status Collection** | APScheduler jobs | Periodic RPC/CLI data collection |
| **Drive Health** | smartctl integration | Disk S.M.A.R.T. monitoring |

## 2. Chiadog (Log Monitor)

### Installation

- **Script:** `scripts/chiadog_setup.sh`
- **Source:** `guydavis/chiadog` (enhanced fork)
- **Condition:** fullnode/harvester modes, all forks except MMX
- **Runs as:** Background Python process reading blockchain `debug.log`

### Configuration

Per-blockchain config files in `config/chiadog/`:

```yaml
notification_title_prefix: "$HOSTNAME-chia"
log_level: INFO

chia:
  coin_name: Chia
  coin_symbol: XCH

file_log_consumer:
  file_path: /root/.chia/mainnet/log/debug.log

daily_stats:
  time_of_day: "20:00"
  frequency_hours: 24

handlers:
  wallet_added_coin_handler:
    enable: true
    min_mojos_amount: 5
```

### Supported Events

| Event | Description |
|---|---|
| Wallet rewards | New coins received |
| Farming status | Changes in farming state |
| Pool changes | Pool join/leave events |
| Harvester warnings | Invalid or missing plots |
| Sync issues | Blockchain sync problems |
| Daily stats | Summary report at configured time |

### Notification Channels

| Channel | Configuration |
|---|---|
| Pushover | API token + user key |
| Telegram | Bot token + chat ID |
| SMTP (Email) | Server, credentials, recipients |
| Gotify | Server URL + token |
| Discord | Webhook URL |
| Custom Script | `chiadog_notifier.sh` hook |

### Custom Notifier

`scripts/chiadog_notifier.sh` provides a hook for custom notification integrations beyond the built-in channels.

## 3. Scheduled Background Jobs

The APScheduler instance (initialized in `gunicorn.conf.py`) runs 22+ jobs:

### Status Collection Jobs (every 2 minutes)

These jobs collect current state from local blockchain services:

| Job | Module | Data Collected | Target DB |
|---|---|---|---|
| `status_worker` | `status_worker.py` | Container memory, CPU | `workers.db` |
| `status_farm` | `status_farm.py` | Plot count, coins, netspace, ETW | `farms.db` |
| `status_wallets` | `status_wallets.py` | Wallet balances, sync status | `wallets.db` |
| `status_blockchains` | `status_blockchains.py` | Node sync, peak height | `blockchains.db` |
| `status_connections` | `status_connections.py` | P2P peer count | `connections.db` |
| `status_keys` | `status_keys.py` | Key validity | `keys.db` |
| `status_plots` | `status_plots.py` | Plot list via RPC | `plots.db` |
| `status_plotting` | `status_plotting.py` | Active plotting jobs | `plottings.db` |
| `status_challenges` | `status_challenges.py` | Recent challenges | `challenges.db` |
| `status_alerts` | `status_alerts.py` | Node alerts | `alerts.db` |
| `status_pools` | `status_pools.py` | Pool metadata | `pools.db` |
| `status_plotnfts` | `status_plotnfts.py` | Pool join status | `plotnfts.db` |
| `status_partials` | `status_partials.py` | Partial submissions | `partials.db` |
| `status_drives` | `status_drives.py` | Disk S.M.A.R.T. | `drives.db` |

### Statistics Snapshot Jobs

| Job | Interval | Data |
|---|---|---|
| `stats_farm` | Hourly/10-min | Farm metrics (plot count, netspace, ETW) |
| `stats_balances` | Hourly/10-min | Wallet balances |
| `stats_blocks` | Hourly/10-min | Farmed block count |
| `stats_disk` | Hourly/10-min | Disk usage metrics |
| `stats_effort` | Hourly/10-min | Actual vs expected blocks |

### Housekeeping Jobs

| Job | Interval | Purpose |
|---|---|---|
| `log_rotate` | Hourly | Rotate application log files |
| `plots_check` | 2 min (30 min startup delay) | Validate plot integrity |
| `nft_recover` | Hourly | NFT recovery attempts |
| `restart_stuck_farmer` | 10 min | Auto-restart stalled farmer |
| `periodically_sync_wallet` | 15 min | Force wallet sync |
| `geolocate_peers` | 2 min | Map peer locations (controller only) |
| `plots_replot` | Continuous | Monitor replot queue |
| `status_warnings` | 20 min | Check for invalid/duplicate plots (fullnodes) |
| `status_archiving` | 2 min | Monitor archive operations (plotters) |
| `status_controller` | 2 min | Controller-specific status (controller only) |
| `status_exchange_prices` | 2 min | Update crypto prices (controller only) |
| `status_blockchain_networks` | 2 min | Network status (controller only) |

### Job Configuration

```python
# ARM64 runs less frequently due to slower CPU
STATUS_EVERY_X_MINUTES = 2  # x86_64
STATUS_EVERY_X_MINUTES = 4  # ARM64
```

Jitter is applied to job scheduling to prevent thundering herd on multi-container deployments.

### Job Dispatch Pattern

```
1. Scheduler fires job → calls schedule module
2. Within Flask app context, runs RPC or CLI query
3. Sends POST to controller API (or stores locally if controller)
4. Controller upserts into SQLite database
```

## 4. Drive Health Monitoring

### S.M.A.R.T. Integration

- Drive data collected via `smartctl` (smartmontools package)
- Status collected by `status_drives` job every 2 minutes
- Data stored in `drives.db` with `Drive` model

### Drive Model Fields

| Field | Purpose |
|---|---|
| `device` | Device identifier (sda, sdb, etc.) |
| `hostname` | Which worker owns this drive |
| `serial_number` | Drive serial |
| `model_family` | Drive model family |
| `status` | Health status (PASSED/FAILED) |
| `temperature` | Current temperature |
| `power_on_hours` | Total hours of operation |
| `size_gibs` | Drive capacity |
| `smart_info` | Full S.M.A.R.T. JSON data |

### WebUI Integration

- Drives page shows all drives across all workers
- AJAX request for detailed S.M.A.R.T. info per device
- Temperature and health status displayed in dashboard

## 5. Alerting Architecture

### Alert Sources

| Source | Trigger |
|---|---|
| Chiadog | Log events (wallet rewards, sync issues, harvester problems) |
| Drive monitoring | S.M.A.R.T. warnings, disk space alerts |
| Farming | Plot warnings (invalid, duplicate) |
| Worker status | Unresponsive workers, high memory |

### Alert Model

```python
class Alert(db.Model):
    unique_id = db.Column(db.String, primary_key=True)
    hostname = db.Column(db.String(255))
    blockchain = db.Column(db.String(64))
    priority = db.Column(db.String(32))
    service = db.Column(db.String(64))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
```

### Alert Management

- View all alerts in WebUI (`/alerts`)
- Delete individual or bulk alerts via POST
- Alerts persist in `alerts.db` until manually deleted
- Configure alert channels in `/settings/alerts`

## 6. Metrics Export

### Prometheus Integration

Optional Prometheus-compatible metrics via `chia-exporter`:

- Enable with `chia_exporter=true` environment variable
- Exposes metrics at `/metrics` API endpoint
- Covers: farming, wallet, blockchain sync metrics

### Built-in Statistics

17 time-series stat tables provide historical data for:
- Dashboard charts (Chart.js)
- Trend analysis
- Capacity planning

## 7. Log Management

### Log Files

| Log | Path | Purpose |
|---|---|---|
| API server | `/root/.chia/machinaris/logs/apisrv.log` | API request/schedule logs |
| WebUI server | `/root/.chia/machinaris/logs/webui.log` | Web request logs |
| Farming | Blockchain debug.log | Full node, farmer events |
| Plotting | Plotman logs | Plot job status |
| Archiving | Plotman archive logs | Transfer status |
| Alerts | Chiadog logs | Monitoring events |
| Pooling | Pool-related logs | Pool submissions |

### Log Viewer

The WebUI log viewer (`/logs`) provides:
- Real-time log streaming via 5-second XHR polling
- Log type selection (farming, plotting, archiving, alerts, etc.)
- Per-worker, per-blockchain filtering
- Auto-scroll on new content
- Endpoint: `/logfile?hostname=X&log=farming&blockchain=chia`

### Log Rotation

All logs are rotated via logrotate:
- Machinaris logs: 7-day daily rotation
- Plotman logs: 3-day daily rotation
- MMX logs: 3-day daily rotation
