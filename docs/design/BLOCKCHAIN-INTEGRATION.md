# Blockchain Integration Design

> How Machinaris interfaces with Chia and 34+ blockchain forks.

## 1. Blockchain Registry

All supported blockchains are defined in `common/config/blockchains.json`. This file is the single source of truth for blockchain metadata.

### Per-Blockchain Configuration

```json
{
  "chia": {
    "name": "Chia",
    "symbol": "XCH",
    "binary": "/chia-blockchain/venv/bin/chia",
    "network_path": "/root/.chia/mainnet",
    "network_name": "mainnet",
    "network_port": 8444,
    "farmer_port": 8447,
    "fullnode_rpc_port": 8555,
    "worker_port": 8927,
    "reward": 1.0,
    "mojos_per_coin": 1000000000000,
    "blocks_per_day": 4608,
    "git_url": "https://github.com/Chia-Network/chia-blockchain",
    "discord_url": "https://discord.gg/...",
    "website_url": "https://www.chia.net"
  }
}
```

### Fields

| Field | Purpose |
|---|---|
| `name` | Display name in UI |
| `symbol` | Ticker symbol (XCH, XCC, etc.) |
| `binary` | Path to blockchain CLI executable |
| `network_path` | Data directory for blockchain state |
| `network_name` | Network identifier (mainnet/testnet) |
| `network_port` | P2P protocol port |
| `farmer_port` | Farmer service port |
| `fullnode_rpc_port` | RPC endpoint port |
| `worker_port` | Machinaris API port for this fork |
| `reward` | Block reward amount |
| `mojos_per_coin` | Smallest unit conversion factor |
| `blocks_per_day` | Block frequency (affects win probability) |

## 2. Supported Blockchains

### Active (with install scripts)

| Blockchain | Symbol | Worker Port | Notes |
|---|---|---|---|
| **Chia** | XCH | 8927 | Reference implementation |
| **Gigahorse** | XCH | 8959 | Madmax compressed farming |
| **MMX** | MMX | 8940 | Madmax alternative blockchain |
| **Chives** | XCC | 8931 | Alternative CLI wrapper |
| **BPX** | BPX | 8945 | |
| **Cactus** | CAC | 8936 | |
| **Flax** | XFX | 8928 | Early Chia fork |
| **Flora** | XFL | 8932 | |
| **HddCoin** | HDD | 8930 | |
| **Staicoin** | STAI | 8948 | Half-mojos conversion quirk |
| + 24 more forks | Various | 8929-8960 | See blockchains.json |

### Deprecated/Legacy

These forks are still in `blockchains.json` but many appear abandoned:
achi, ballcoin, coffee, ecostake, gold, mint, nchain, petroleum, profit, silicoin, stor

### Special Cases

| Blockchain | Speciality |
|---|---|
| **Gigahorse** | Closed-source binary from Madmax; uses alternative Chia binary at `/chia-gigahorse-farmer/chia.bin`; requires GPU drivers |
| **MMX** | Not a traditional Chia fork; uses Madmax binaries; JSON config instead of YAML; testnet10 network |
| **Chives** | Alternative fork URL support (Foxy fork); creates symlinks to `/chia-blockchain` |
| **Staicoin** | Unit conversion quirk (half-mojos, renamed to "stai") |

## 3. RPC Client Architecture

### File: `api/commands/rpc.py`

Dynamic imports for 40+ blockchains based on `globals.enabled_blockchains()`:

```python
# Each blockchain provides RPC client classes:
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.rpc.wallet_rpc_client import WalletRpcClient
```

### Key RPC Methods

| Method | Client | Purpose |
|---|---|---|
| `get_all_plots()` | FarmerRpcClient | Retrieve plots from all harvesters |
| `get_wallets()` | WalletRpcClient | Wallet information |
| `get_transactions()` | WalletRpcClient | Transaction history |
| `get_harvester_warnings()` | FarmerRpcClient | Invalid/duplicate plots |
| `get_pool_states()` | FarmerRpcClient | Pool join status |
| `get_blockchain_state()` | FullNodeRpcClient | Sync status, peak height |

### Async Pattern

```python
async def get_all_plots():
    client = await FarmerRpcClient.create(...)
    try:
        result = await client.get_harvesters()
    finally:
        client.close()
    return result
```

Uses `asyncio` for non-blocking I/O when querying multiple harvesters in parallel.

## 4. CLI Interaction

### File: `api/commands/chia_cli.py`

For operations not available via RPC, Machinaris falls back to subprocess calls:

```python
# Example: farm summary
result = subprocess.run(
    ['chia', 'farm', 'summary'],
    capture_output=True, text=True, timeout=30
)
```

### CLI Commands Used

| Command | Purpose |
|---|---|
| `chia farm summary` | Plot count, total coins, netspace, ETW |
| `chia wallet show` | Wallet balances and sync status |
| `chia wallet transaction list` | Transaction history |
| `chia keys add` | Import mnemonic keys |
| `chia plots add` | Register plot directories |
| `chia init --fix-ssl-permissions` | Fix SSL certificate permissions |
| `chia start farmer` | Start blockchain services |
| `chia version` | Get blockchain version |

### Output Parsing

CLI output is parsed using regex and text matching. Results are stored in model `details` columns as raw text, with property methods extracting structured data on demand.

## 5. External Services

### File: `api/commands/websvcs.py`

| Service | Purpose | Endpoint Pattern |
|---|---|---|
| AllTheBlocks | Cold wallet balance tracking | `https://api.alltheblocks.net/{blockchain}/address/{address}` |
| CoinGecko | Blockchain price data | Via API |
| CoinPaprika | Alternative price source | Via API |

### Caching

- Prices cached in `/root/.chia/machinaris/cache/blockchain_prices_cache.json`
- Exchange rates cached in `/root/.chia/machinaris/cache/exchange_rates_cache.json`
- Transaction pagination limited to 20 pages max

## 6. Global Configuration Functions

### File: `common/config/globals.py`

| Function | Returns |
|---|---|
| `get_supported_blockchains()` | All blockchain keys from JSON |
| `enabled_blockchains()` | Currently enabled blockchains (from env) |
| `get_blockchain_binary(bc)` | Executable path |
| `get_blockchain_network_path(bc)` | Network data directory |
| `get_blockchain_symbol(bc)` | Ticker symbol |
| `get_full_node_rpc_port(bc)` | RPC port |
| `get_blocks_per_day(bc)` | Block frequency |
| `get_block_reward(bc)` | Block reward amount |
| `get_mojos_per_coin(bc)` | Unit conversion |
| `load_blockchain_version(bc)` | Version string (cached 1+ day) |
| `load_fullnode_db_version()` | v1 or v2 database format |
| `plotting_enabled()` | Whether this mode supports plotting |
| `harvesting_enabled()` | Whether this mode supports harvesting |

### Version Caching

```python
RELOAD_MINIMUM_DAYS = 1
```

Version detection runs `<binary> version` via subprocess. Results are cached for at least 1 day to avoid repeated subprocess overhead. Handles pre-release suffixes (`.dev`, `rc`, `b1-b3`).

## 7. Certificate Management

Harvesters need SSL certificates from the farmer/fullnode for RPC access:

1. Harvester container starts with `mode=harvester`
2. Fetches certificates via HTTP GET to controller: `/certificates/?type=chia`
3. Stores certificates in local blockchain config directory
4. Uses certificates for all subsequent RPC calls

## 8. Chia Version Alignment

**Key project goal:** Maintain alignment with latest Chia versions from chia.net.

Current state (v2.6.0):
- Chia v2.6.0 support (Python 3.13, TLS 1.3, preliminary V2 plot format)
- Chia blockchain download via torrent bootstrapping
- V1 and V2 blockchain database format detection
- GPU-accelerated binary support (CUDA chia-blockchain-cli)

Upgrade considerations:
- New Chia versions may introduce breaking changes to RPC APIs
- V2 plot format support is preliminary — full support pending
- Python version requirements may change with new Chia releases
