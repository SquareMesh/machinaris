# Chia 2.6.x Python Module Restructure

**Category:** research
**Relevance:** BLOCKCHAIN-INTEGRATION.md, api/commands/rpc.py
**Date researched:** 2026-03-22

## Summary
Chia 2.6.x (starting around 2.5.5-2.6.0) reorganized its Python package structure. RPC clients moved from a centralized `chia/rpc/` directory to service-specific directories. Sized integer types moved from Python to the Rust-based `chia_rs` package.

## Key Findings
- RPC clients moved: `chia.rpc.<service>_rpc_client` → `chia.<service>.<service>_rpc_client`
- `PlotPathRequestData` moved: `chia.rpc.farmer_rpc_client` → `chia.farmer.farmer_rpc_api`
- `uint16`, `uint32`, `uint64` etc moved: `chia.util.ints` → `chia_rs.sized_ints`
- `bytes32` moved: `chia.types.blockchain_format.sized_bytes` → `chia_rs.sized_bytes`
- `chia.util.bech32m` — UNCHANGED
- `chia.util.byte_types` — UNCHANGED
- `chia.util.default_root` — UNCHANGED
- `chia.util.config` — UNCHANGED
- `chia.types.aliases` moved to `chia.server.aliases` (noted in 2.5.5 changelog)

## Import Migration Table

| Old (pre-2.6) | New (2.6.x) |
|---|---|
| `from chia.rpc.full_node_rpc_client import FullNodeRpcClient` | `from chia.full_node.full_node_rpc_client import FullNodeRpcClient` |
| `from chia.rpc.farmer_rpc_client import FarmerRpcClient` | `from chia.farmer.farmer_rpc_client import FarmerRpcClient` |
| `from chia.rpc.wallet_rpc_client import WalletRpcClient` | `from chia.wallet.wallet_rpc_client import WalletRpcClient` |
| `from chia.rpc.farmer_rpc_client import PlotPathRequestData` | `from chia.farmer.farmer_rpc_api import PlotPathRequestData` |
| `from chia.util.ints import uint16` | `from chia_rs.sized_ints import uint16` |
| `from chia.types.blockchain_format.sized_bytes import bytes32` | `from chia_rs.sized_bytes import bytes32` |

## Decision / Recommendation
Always check Chia's GitHub `main` branch when upgrading Chia versions. The pattern of moving code to `chia_rs` (Rust) is ongoing and likely to continue in future versions. Monitor `chia_rs` changelog alongside `chia-blockchain` changelog.

## Sources
- https://github.com/Chia-Network/chia-blockchain/tree/main/chia/rpc
- https://github.com/Chia-Network/chia-blockchain/blob/main/CHANGELOG.md
