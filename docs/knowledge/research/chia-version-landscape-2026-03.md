# Chia Version Landscape — March 2026

**Category:** research
**Relevance:** BLOCKCHAIN-INTEGRATION.md, DOCKER-DEPLOYMENT.md — Chia version alignment strategy
**Date researched:** 2026-03-21

## Summary
Assessed the current Chia blockchain release landscape to determine the correct version target for the Machinaris fork. The latest stable is v2.6.1 with a v3.0 major release on the horizon featuring a new Proof of Space format.

## Key Findings
- **v2.6.1** (2026-03-18) — Latest stable. Structured RPC errors, TransactionQueue optimizations, fast forward state validation, BYC/CRT added to default CAT list.
- **v2.7.0-rc1** (2026-03-20) — Pre-release. mypy exclusion removals, chia_rs updates, mempool improvements.
- **v2.6.0** (2026-02-11) — Soft fork release. Python 3.13 support, TLS 1.3 minimum, preliminary V2 plot format, deficit round robin mempool.
- **v3.0** (upcoming) — Major release with new Proof of Space format. Proposed activation at block height 9,562,000 (~6 months after release). New format eliminates time-space tradeoff exploits and resists rental attacks. Beta testing ongoing.

## Decision / Recommendation
Target v2.6.1 for current release (v2.7.0 of Machinaris). Monitor v3.0 closely — it will require V2 plot format support and may be a breaking change requiring significant testing. The Machinaris v2.6.0 CHANGELOG mentions "preliminary V2 plot format support" already in Chia 2.6.0, so groundwork exists.

## Sources
- https://github.com/Chia-Network/chia-blockchain/releases
- https://www.chia.net/2026/02/27/changes-coming-to-3-0/
