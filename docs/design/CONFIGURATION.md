# Configuration Design

> Environment variables, config files, setup flow, internationalization, and security.
>
> **Note:** As of v2.7.0, Machinaris is Chia-only. Fork-specific environment variables and config options have been removed.

## 1. Configuration Sources

Machinaris uses a layered configuration approach:

```
1. Environment variables (Docker container)
2. Config files (JSON/YAML on persistent volume)
3. SQLite database (runtime state)
4. blockchains.json (blockchain metadata, read-only)
```

## 2. Environment Variables

### Core Blockchain

| Variable | Default | Purpose |
|---|---|---|
| `blockchains` | `chia` | Blockchain identifier (Chia-only as of v2.7.0) |
| `mode` | `fullnode` | Operating mode: fullnode, farmer, harvester, plotter, farmer+plotter, harvester+plotter |
| `keys` | — | Colon-separated paths to mnemonic.txt files |
| `plots_dir` | `/plots` | Colon-separated plot directories |

### Farming Credentials

| Variable | Default | Purpose |
|---|---|---|
| `farmer_pk` | `null` | Farmer public key (for plotter mode) |
| `pool_pk` | `null` | Pool public key (old solo plots) |
| `pool_contract_address` | `null` | Pool contract (portable plotting) |

### Network Topology

| Variable | Default | Purpose |
|---|---|---|
| `controller_host` | `localhost` | Controller hostname |
| `controller_web_port` | `8926` | WebUI port |
| `controller_api_port` | `8927` | API port |
| `worker_address` | — | This worker's IP (required for distributed) |
| `worker_api_port` | `8927` | Worker API port |
| `farmer_address` | `null` | Remote farmer IP (harvester mode) |
| `farmer_port` | `8447` | Farmer protocol port |

### Feature Flags

| Variable | Default | Purpose |
|---|---|---|
| `AUTO_PLOT` | `false` | Auto-start plotting on boot |
| `AUTO_ARCHIVE` | `false` | Auto-start archiving on boot |
| `chia_data` | `false` | Enable Chia Data Layer services |
| `chia_exporter` | `false` | Enable Prometheus metrics export |
| `chia_db_download` | `true` | Torrent-based blockchain DB bootstrap |

### GPU Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NVIDIA_VISIBLE_DEVICES` | `all` | GPU visibility for NVIDIA runtime |
| `NVIDIA_DRIVER_CAPABILITIES` | `compute,utility` | NVIDIA capabilities |
| `OPENCL_GPU` | `null` | GPU type: `amd` or `nvidia` |

### Locale and System

| Variable | Default | Purpose |
|---|---|---|
| `TZ` | `Etc/UTC` | Timezone for scheduler and logs |
| `LC_ALL` | `en_US.UTF-8` | Locale setting |
| `LANG` | `en_US.UTF-8` | Language setting |
| `FLASK_DEBUG` | — | Set to `development` for debug SQL logging |

### Tool Branches

| Variable | Default | Purpose |
|---|---|---|
| `PLOTMAN_BRANCH` | `main` | Plotman git branch |
| `CHIADOG_BRANCH` | `main` | Chiadog git branch |
| `BLADEBIT_BRANCH` | `master` | Bladebit git branch |
| `MADMAX_BRANCH` | `master` | Madmax git branch |

### Skip Flags

| Variable | Purpose |
|---|---|
| `bladebit_skip_build=true` | Skip Bladebit installation |
| `madmax_skip_build=true` | Skip Madmax installation |

## 3. Config Files

### Persistent Volume (`/root/.chia/`)

```
/root/.chia/
├── mnemonic.txt                           # Wallet mnemonic key
├── mainnet/config/config.yaml             # Chia blockchain config
├── plotman/
│   ├── plotman.yaml                       # Plotman configuration
│   └── logs/                              # Plotman log files
├── machinaris/
│   ├── config/
│   │   ├── api.cfg                        # API server settings
│   │   ├── web.cfg                        # WebUI settings
│   │   ├── locale_settings.json           # Currency preference
│   │   ├── wallet_settings.json           # Wallet pause state
│   │   ├── cold_wallet_addresses.json     # Cold wallet tracking
│   │   └── notifications.json            # Telegram notification config
│   ├── cache/
│   │   ├── blockchain_prices_cache.json   # USD prices
│   │   └── exchange_rates_cache.json      # Fiat exchange rates
│   ├── dbs/                               # SQLite databases (21+)
│   └── logs/                              # Application logs
└── smbcredentials.txt                     # Optional CIFS mount credentials
```

### API Server Config (`api.cfg`)

```ini
STATUS_EVERY_X_MINUTES = 2          # x86_64 default
# STATUS_EVERY_X_MINUTES = 4        # ARM64 default
ALLOW_HARVESTER_CERT_LAN_DOWNLOAD = True
```

Created automatically by `scripts/config_api_server.sh` with architecture-specific defaults.

### Plotman Config (`plotman.yaml`)

Initialized from `config/plotman.sample.yaml` with credential injection:
```bash
sed -i "s/farmer_pk:.*/farmer_pk: ${farmer_pk}/" plotman.yaml
sed -i "s/pool_pk:.*/pool_pk: ${pool_pk}/" plotman.yaml
sed -i "s/pool_contract_address:.*/pool_contract_address: ${pool_contract_address}/" plotman.yaml
```

## 4. Setup Flow

### Initial Setup Detection

```python
# common/config/globals.py
def is_setup():
    if mode == 'plotter':
        return farmer_pk and (pool_pk or pool_contract_address)
    elif mode == 'harvester':
        return True  # No mnemonic needed
    else:
        return at least one key file exists from 'keys' env var
```

### Setup Page

If `is_setup()` returns False, the WebUI redirects to `/setup`:
1. User can generate new keys or import existing mnemonic
2. Key is stored to `/root/.chia/mnemonic.txt`
3. `chia keys add` imports the mnemonic
4. Plot directories registered via `chia plots add`
5. SSL certificates fixed: `chia init --fix-ssl-permissions`

### Portainer Detection

The entrypoint detects Portainer launch-order issues:
- If `/root/.chia/mnemonic.txt` is a directory (race condition), it's removed
- Prevents cryptic errors from Docker orchestrators launching containers simultaneously

## 5. Internationalization (i18n)

### Framework

- **Library:** Flask-Babel
- **Languages:** 7 supported (en, de_DE, fr_FR, it_IT, nl_NL, pt_PT, zh)
- **Translation files:** `web/translations/[locale]/LC_MESSAGES/messages.po`
- **Babel config:** `web/babel.cfg`

### Translation Workflow

```bash
# Extract strings from source
scripts/i18n/extract.sh

# Initialize new language
scripts/i18n/init.sh [locale]

# Compile translations
scripts/i18n/compile.sh
```

### Template Usage

```html
{{ _('Settings') }}
{{ _('Delete') }}
```

```python
flash(_("Saved local currency setting."), 'success')
```

### Locale Detection

```python
def get_lang():
    # Match Accept-Language header to supported languages
    # Workaround for Babel bug: 'nl' → 'nl_NL'
    # Fallback to 'en'
```

### DataTables Localization

Per-language JSON translation files downloaded during build for DataTables column headers and UI strings.

## 6. Security Configuration

### Current Security Model

| Aspect | Implementation | Notes |
|---|---|---|
| Authentication | None | Relies on Docker network isolation |
| CSRF protection | None | Forms use POST without tokens |
| Session management | Flask secret key (hardcoded) | Single-user, Docker-isolated |
| API security | No auth tokens | Implicit trust within Docker network |
| RPC security | Chia SSL certificates | Auto-generated, exchanged via API |
| Database | SQLite (local filesystem) | No network exposure |

### Recommended Hardening

For production deployments exposed to networks:
- Use reverse proxy (nginx/traefik) with authentication
- Restrict Docker network access
- Use environment variable for Flask secret key
- Consider adding CSRF tokens to forms

## 7. Version Management

### Version File

`/machinaris/VERSION` contains the current version string (e.g., `2.7.0`).

### Component Version Detection

```python
# Cached for 1+ day to avoid subprocess overhead
load_blockchain_version(blockchain)  # Runs `chia version`
load_plotman_version()               # Runs `plotman version`
load_chiadog_version()               # Reads version from package
load_bladebit_version()              # Runs `bladebit --version`
load_madmax_version()                # Reads from binary info
```

### Blockchain Database Version

```python
load_fullnode_db_version()
# Returns "v1" or "v2" based on which DB file exists
# v2 is the newer format introduced in recent Chia versions
```

## 8. Configuration Precedence

```
1. Docker environment variables (highest priority)
2. Config files on persistent volume
3. Default values in code (default_settings.py, globals.py)
4. blockchains.json metadata (read-only reference)
```

When conflicts arise, environment variables always win. This enables Docker Compose overrides without modifying files.
