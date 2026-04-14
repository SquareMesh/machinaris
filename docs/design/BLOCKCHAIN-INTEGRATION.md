# Blockchain Integration Design

> How Machinaris interfaces with the Chia blockchain.
>
> **Note:** As of v2.7.0, Machinaris is Chia-only. All 33 non-Chia forks have been removed from the Docker build. The fork install scripts remain in `scripts/forks/` for reference but are not executed. `blockchains.json` still contains legacy fork metadata (see TODO-008).

## 1. Blockchain Registry

Blockchain metadata is defined in `common/config/blockchains.json`. Only the Chia entry is active.

### Chia Configuration

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
| `symbol` | Ticker symbol (XCH) |
| `binary` | Path to blockchain CLI executable |
| `network_path` | Data directory for blockchain state |
| `network_name` | Network identifier (mainnet) |
| `network_port` | P2P protocol port |
| `farmer_port` | Farmer service port |
| `fullnode_rpc_port` | RPC endpoint port |
| `worker_port` | Machinaris API port (8927) |
| `reward` | Block reward amount |
| `mojos_per_coin` | Smallest unit conversion factor |
| `blocks_per_day` | Block frequency (affects win probability) |

## 2. RPC Client Architecture

### File: `api/commands/rpc.py`

Chia-only RPC imports using Chia 2.6.x module paths:

```python
# Chia 2.6.x moved RPC clients to service-specific directories
from chia.farmer.farmer_rpc_client import FarmerRpcClient
from chia.full_node.full_node_rpc_client import FullNodeRpcClient
from chia.wallet.wallet_rpc_client import WalletRpcClient
from chia.data_layer.data_layer_rpc_client import DataLayerRpcClient
from chia.daemon.client import DaemonProxy

# Sized ints moved to chia_rs in 2.6.x
from chia_rs.sized_ints import uint16, uint64
from chia_rs.sized_bytes import bytes32
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

## 3. CLI Interaction

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

## 4. External Services

### File: `api/commands/websvcs.py`

| Service | Purpose | Endpoint Pattern |
|---|---|---|
| AllTheBlocks | Cold wallet balance tracking | `https://api.alltheblocks.net/chia/address/{address}` |
| CoinGecko | Chia price data | Via API |
| CoinPaprika | Alternative price source | Via API |

### Caching

- Prices cached in `/root/.chia/machinaris/cache/blockchain_prices_cache.json`
- Exchange rates cached in `/root/.chia/machinaris/cache/exchange_rates_cache.json`
- Transaction pagination limited to 20 pages max

## 5. Global Configuration Functions

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

Version detection runs `chia version` via subprocess. Results are cached for at least 1 day to avoid repeated subprocess overhead.

## 6. Certificate Management

Harvesters need SSL certificates from the farmer/fullnode for RPC access:

1. Harvester container starts with `mode=harvester`
2. Fetches certificates via HTTP GET to controller: `/certificates/?type=chia`
3. Stores certificates in local blockchain config directory
4. Uses certificates for all subsequent RPC calls

## 7. Chia Version Alignment

**Key project goal:** Maintain alignment with latest Chia versions from chia.net.

Current state (v2.7.0):
- Chia v2.7.0 support
- Chia 2.7.0 adds Remote Wallet with new RPC calls, security hardening, soft fork/mempool handling improvements
- Chia 2.6.x module restructure: RPC clients moved to service directories, sized ints moved to `chia_rs`
- V1 and V2 blockchain database format detection
- GPU-accelerated binary support (CUDA chia-blockchain-cli)

Upgrade considerations:
- New Chia versions may introduce breaking changes to RPC APIs
- V2 plot format support is preliminary — full support pending (see TODO-009)
- Python version requirements may change with new Chia releases
