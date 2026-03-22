# Entrypoint Fork Code Path Review

**Pushed:** 2026-03-21
**Source:** Response 1 in conversation (most recent)
**Context:** User asked to review entrypoint.sh for fork-specific code paths that may break on Chia-only

---

Here's the full analysis of `entrypoint.sh` and its referenced scripts for Chia-only compatibility.

## Findings

### No Breaking Issues

With `blockchains=chia`, the entrypoint works end-to-end. The dynamic dispatch on line 82 (`scripts/forks/${blockchains}_launch.sh`) resolves to `chia_launch.sh` which is fully Chia-specific and correct. The `blockchains.json` jq lookup on line 88 will find the `chia` entry fine.

### Problems to Fix

| Priority | File | Line(s) | Issue |
|---|---|---|---|
| **HIGH** | `entrypoint.sh` | 98 | Random sleep 1-180 seconds "to stagger fork containers" — completely pointless with one blockchain. Up to 3 minutes wasted every startup. |
| **HIGH** | `entrypoint.sh` | 113 | `forktools_setup.sh` — will `git clone` and install forktools at runtime unless `forktools_skip_build=true`. Forktools is a multi-fork management tool, useless for Chia-only. Wastes time and bandwidth. |
| **MEDIUM** | `entrypoint.sh` | 100-101 | `fd-cli_setup.sh` — explicitly skips Chia (`blockchains != 'chia'`), so it's a no-op. Dead call. |
| **LOW** | `worker_port_warning.sh` | 1-103 | 32 of 33 fork-specific port checks are dead code. Only the `chia` check (line 20-22) fires. |
| **LOW** | `start_machinaris.sh` | 8-17 | Plotman config has `chives`/`mmx`/`gigahorse` branches that never match. Falls through to the correct `else` (Chia) branch. |

### Safe / No Action Needed

- **Line 15-19**: `chia,flax` guard — legacy upgrade check, harmless, never matches
- **Line 29-37**: Chia upgrade migration steps — still relevant for existing users
- **Line 48-65**: plotman YAML upgrade — still relevant
- **Line 82**: `chia_launch.sh` dispatch — works correctly
- **Line 88**: `blockchains.json` jq for `chia.binary` — works
- **Line 92, 95**: plotman_setup.sh, chiadog_setup.sh — both support Chia
- **Line 104-107**: bladebit/madmax — Chia plotters, correct

## Recommended Cleanup

1. **Remove the random sleep** (line 98) — no multi-container staggering needed
2. **Remove the forktools_setup.sh call** (line 113) — not useful for Chia-only
3. **Remove the fd-cli_setup.sh call** (line 100-101) — explicit Chia skip makes it a no-op
4. **Simplify worker_port_warning.sh** to Chia-only check
5. **Simplify start_machinaris.sh** plotman config to remove dead branches
