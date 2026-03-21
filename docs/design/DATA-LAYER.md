# Data Layer Design

> Database architecture, ORM models, multi-database design, and statistics storage.

## 1. Technology Stack

- **ORM:** Flask-SQLAlchemy (SQLAlchemy declarative models)
- **Database:** SQLite with WAL (Write-Ahead Logging) mode
- **Migration:** Flask-Migrate (Alembic under the hood)
- **Serialization:** marshmallow-sqlalchemy for API schemas
- **Location:** `/root/.chia/machinaris/dbs/`

## 2. Multi-Database Architecture

Machinaris uses **21 separate SQLite databases** rather than a single monolithic database. Each model binds to its own database via `__bind_key__`.

### Rationale

| Benefit | Explanation |
|---|---|
| Isolation | Stats don't block farm operations |
| Selective backup | Back up only what you need |
| Independent cleanup | Purge old stats without touching farm data |
| Concurrency | WAL mode per DB reduces lock contention |
| No external DB | SQLite requires no separate server |

### Database Registry

```
/root/.chia/machinaris/dbs/
├── default.db                  # Default bind (general)
├── alerts.db                   # Alert events
├── blockchains.db              # Blockchain status per host
├── challenges.db               # Farming challenges
├── connections.db              # P2P peer connections
├── drives.db                   # Storage device SMART data
├── farms.db                    # Farm summary statistics
├── keys.db                     # Blockchain keys
├── partials.db                 # Pool partial submissions
├── plotnfts.db                 # Plot NFTs (pool identity)
├── plots.db                    # Individual plot file metadata
├── plottings.db                # Active plotting jobs
├── pools.db                    # Pool connection state
├── transfers.db                # Plot transfer operations
├── wallets.db                  # Wallet balances
├── warnings.db                 # System warnings
├── workers.db                  # Remote worker nodes
├── stat_plot_count.db          # Plot count time series
├── stat_plots_size.db          # Plot size time series
├── stat_total_coins.db         # Coin balance time series
├── stat_netspace_size.db       # Network space time series
├── stat_time_to_win.db         # Expected win time series
├── stat_effort.db              # Farming effort time series
├── stat_plots_total_used.db    # Total plot disk used
├── stat_plots_disk_used.db     # Per-path plot disk used
├── stat_plots_disk_free.db     # Per-path plot disk free
├── stat_plotting_total_used.db # Total plotting disk used
├── stat_plotting_disk_used.db  # Per-path plotting disk used
├── stat_plotting_disk_free.db  # Per-path plotting disk free
├── stat_farmed_blocks.db       # Farmed block history
├── stat_wallet_balances.db     # Wallet balance history
├── stat_total_balance.db       # Total balance across chains
├── stat_container_mem_gib.db   # Container memory usage
└── stat_host_mem_pct.db        # Host memory percentage
```

## 3. Core Models

### Farm Management

| Model | File | Bind Key | Primary Key | Purpose |
|---|---|---|---|---|
| `Plot` | `common/models/plots.py` | `plots` | `plot_id` | Individual plot file metadata |
| `Plotting` | `common/models/plottings.py` | `plottings` | `plot_id` | Active plotting jobs |
| `Plotnft` | `common/models/plotnfts.py` | `plotnfts` | `unique_id` | Pool NFTs (launcher identity) |
| `Pool` | `common/models/pools.py` | `pools` | `unique_id` | Pool connection state |
| `Partial` | `common/models/partials.py` | `partials` | `unique_id` | Pool share submissions |
| `Transfer` | `common/models/transfers.py` | `transfers` | `log_file` | Plot transfer operations |

### Farm Status

| Model | File | Bind Key | Primary Key | Purpose |
|---|---|---|---|---|
| `Farm` | `common/models/farms.py` | `farms` | `hostname` + `blockchain` | Farm summary stats |
| `Worker` | `common/models/workers.py` | `workers` | `hostname` + `port` | Remote worker nodes |
| `Challenge` | `common/models/challenges.py` | `challenges` | `unique_id` | Farming challenge events |

### Wallet and Assets

| Model | File | Bind Key | Primary Key | Purpose |
|---|---|---|---|---|
| `Wallet` | `common/models/wallets.py` | `wallets` | `hostname` + `blockchain` | Wallet balances and sync |
| `Key` | `common/models/keys.py` | `keys` | `hostname` + `blockchain` | Blockchain keys |

### Infrastructure

| Model | File | Bind Key | Primary Key | Purpose |
|---|---|---|---|---|
| `Drive` | `common/models/drives.py` | `drives` | `device` + `hostname` | Disk S.M.A.R.T. status |
| `Blockchain` | `common/models/blockchains.py` | `blockchains` | `hostname` + `blockchain` | Node sync status |
| `Connection` | `common/models/connections.py` | `connections` | `hostname` + `blockchain` | P2P connectivity |
| `Warning` | `common/models/warnings.py` | `warnings` | `hostname` + `blockchain` + `type` | System warnings |
| `Alert` | `common/models/alerts.py` | `alerts` | `unique_id` | Alert events |

## 4. Statistics Models

17 time-series models for historical charting, all in `common/models/stats.py`:

| Model | Bind Key | Dimensions | Purpose |
|---|---|---|---|
| `StatPlotCount` | `stat_plot_count` | hostname, blockchain | Plot count over time |
| `StatPlotsSize` | `stat_plots_size` | hostname, blockchain | Total plot size (GiB) |
| `StatTotalCoins` | `stat_total_coins` | hostname, blockchain | Wallet balance history |
| `StatNetspaceSize` | `stat_netspace_size` | hostname, blockchain | Network space trend |
| `StatTimeToWin` | `stat_time_to_win` | hostname, blockchain | Expected win time |
| `StatEffort` | `stat_effort` | hostname, blockchain | Luck-adjusted win metric |
| `StatPlotsTotalUsed` | `stat_plots_total_used` | hostname, blockchain | Total plots disk used |
| `StatPlotsDiskUsed` | `stat_plots_disk_used` | hostname, path | Per-path plot disk usage |
| `StatPlotsDiskFree` | `stat_plots_disk_free` | hostname, path | Per-path free space |
| `StatPlottingTotalUsed` | `stat_plotting_total_used` | hostname, blockchain | Total plotting temp used |
| `StatPlottingDiskUsed` | `stat_plotting_disk_used` | hostname, path | Per-path plotting usage |
| `StatPlottingDiskFree` | `stat_plotting_disk_free` | hostname, path | Per-path plotting free |
| `StatFarmedBlocks` | `stat_farmed_blocks` | hostname, blockchain | Won blocks with challenge ID |
| `StatWalletBalances` | `stat_wallet_balances` | hostname, blockchain | Balance per wallet |
| `StatTotalBalance` | `stat_total_balance` | hostname | Total across all chains |
| `StatContainerMemoryUsageGib` | `stat_container_mem_gib` | hostname, blockchain | Container memory |
| `StatHostMemoryUsagePercent` | `stat_host_mem_pct` | hostname | Host OS memory |

## 5. Model Patterns

### Composite Primary Keys

Most models use composite keys (hostname + blockchain) to support multi-worker, multi-fork deployments:

```python
class Farm(db.Model):
    __bind_key__ = 'farms'
    hostname = db.Column(db.String(255), primary_key=True)
    blockchain = db.Column(db.String(64), primary_key=True)
    plot_count = db.Column(db.Integer)
    plots_size = db.Column(db.Float)  # GiB
    total_coins = db.Column(db.Float)
    ...
```

### CLI Output Parsing

Several models parse raw CLI output stored in `details` columns:

```python
class Wallet(db.Model):
    details = db.Column(db.Text)  # Raw `chia wallet show` output

    def wallet_id(self):       # Extract fingerprint
    def wallet_nums(self):     # Extract wallet IDs
    def is_synced(self):       # Check "Sync status: Synced"
    def has_few_mojos(self):   # Detect low balance
```

### JSON Service State

Worker model stores service states as JSON:

```python
class Worker(db.Model):
    services = db.Column(db.Text)  # JSON blob
    config = db.Column(db.Text)    # JSON blob

    def farming_status(self):
        return json.loads(self.services)['farming_status']
    def container_memory_usage_gib(self):
        bytes = json.loads(self.services)['container_memory_usage_bytes']
        return "{:.2f} GiB".format(bytes / 1024**3)
```

### Backward Compatibility

Worker JSON parsing supports old and new key names:

```python
def farming_status(self):
    try:
        return json.loads(self.services)['farming_status']   # New
    except:
        return json.loads(self.services)['farm_status']      # Legacy
```

## 6. Constants

### Plot Sizes

```python
KSIZES = [29, 30, 31, 32, 33, 34]

FREE_GIBS_REQUIRED_FOR_KSIZE = {
    29: 13,   30: 26,   31: 52,
    32: 104,  33: 210,  34: 432,
}
```

### Blockchain Capabilities

```python
PLOTTABLE_BLOCKCHAINS = ['chia', 'chives', 'gigahorse', 'mmx']
POOLABLE_BLOCKCHAINS = ['chia', 'chives', 'gigahorse']
```

## 7. Database Initialization

The `setup_databases.sh` script:
1. Creates `/root/.chia/machinaris/{dbs,cache,logs}` directories
2. Runs `flask db upgrade` (Flask-Migrate/Alembic) to apply schema
3. Supports `reset` mode to clear and recreate all databases

## 8. Utility Functions

### Size Conversion (`common/utils/converters.py`)

| Function | Purpose |
|---|---|
| `sizeof_fmt(num)` | Bytes to human-readable (binary 1024) |
| `gib_to_fmt(gibs, unit)` | GiB to target unit string |
| `str_to_gibs(str)` | Parse size string to GiB |
| `round_balance(value)` | Locale-aware balance formatting |
| `etw_to_minutes(str)` | Parse ETW string to minutes |
| `convert_date_for_luxon(str)` | Format dates for Chart.js |

### Currency Conversion (`common/utils/fiat.py`)

| Function | Purpose |
|---|---|
| `to_fiat(blockchain, coins)` | Convert to local currency |
| `get_local_currency()` | Load user's currency preference |
| `get_fiat_exchange_to_usd()` | Get exchange rate multiplier |

Cache files:
- `/root/.chia/machinaris/cache/blockchain_prices_cache.json`
- `/root/.chia/machinaris/cache/exchange_rates_cache.json`
- `/root/.chia/machinaris/config/locale_settings.json`
