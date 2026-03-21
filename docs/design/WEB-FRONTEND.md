# Web Frontend Design

> Flask WebUI architecture, templates, JavaScript, CSS, and user interaction patterns.

## 1. Framework

- **Framework:** Flask (Python WSGI)
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstrap 5.3.8
- **WSGI Server:** Gunicorn (1 worker, 12 threads, port 8926)
- **Entry Point:** `web/__init__.py`

### Initialization

1. Create Flask app with secret key
2. Configure SQLAlchemy with 21 database bindings
3. Initialize Flask-Babel for i18n (7 languages)
4. Register 14 blueprints
5. Register custom Jinja2 filters

## 2. Blueprint Architecture

```
web/
├── __init__.py              # App factory, filter registration
├── default_settings.py      # DB bindings, cache config
├── utils.py                 # HTTP helpers (send_get/post/put/delete)
│
├── blueprints/              # 14 route modules
│   ├── index/               # Dashboard, charts, summary
│   ├── landing/             # Landing page
│   ├── setup/               # Initial setup wizard
│   ├── farming/             # Plot management, workers, warnings
│   ├── plotting/            # Job queue, transfers, workers
│   ├── wallet/              # Wallet balances, cold wallets
│   ├── keys/                # Key management
│   ├── blockchains/         # Blockchain status
│   ├── connections/         # Peer connections, geo-map
│   ├── alerts/              # Chiadog alerts
│   ├── pools/               # Pool configuration
│   ├── workers/             # Distributed worker status
│   ├── drives/              # Drive health (smartctl)
│   ├── settings/            # Configuration pages
│   ├── logs/                # Log viewer
│   └── transactions/        # Transaction history
│
├── actions/                 # Business logic bridge
│   ├── chia.py              # Farm, wallet, blockchain operations
│   ├── plotman.py           # Plotting job management
│   ├── worker.py            # Worker queries
│   ├── stats.py             # Statistics aggregation
│   ├── chiadog.py           # Alert management
│   ├── pools.py             # Pool config
│   ├── drives.py            # Drive monitoring
│   ├── mapping.py           # Geolocation
│   ├── log_handler.py       # Log retrieval
│   ├── warnings.py          # Plot warnings
│   └── forktools.py         # Fork tools
│
├── models/                  # View models (data transformation)
│   ├── chia.py              # FarmSummary, Wallets, Blockchains
│   ├── worker.py            # Host, WorkerSummary
│   ├── plotman.py           # Plotting models
│   ├── pools.py             # Pool models
│   └── drives.py            # Drive models
│
├── templates/               # Jinja2 templates
│   ├── base.html            # Master layout
│   └── ...                  # ~30 template files
│
├── static/                  # CSS, JS, images
│   ├── styles.css           # Custom dark theme
│   ├── 3rd_party/           # Vendored JS/CSS libraries
│   └── landings/            # Localized landing assets
│
└── translations/            # i18n .po/.mo files
    ├── de_DE/
    ├── fr_FR/
    ├── it_IT/
    ├── nl_NL/
    ├── pt_PT/
    └── zh/
```

## 3. Route Map

### Navigation Routes

| Route | Blueprint | Methods | Purpose |
|---|---|---|---|
| `/` | landing | GET | Landing page |
| `/setup` | setup | GET/POST | Initial blockchain setup |
| `/index` | index | GET | Main dashboard |
| `/summary` | index | GET | Summary cards |
| `/chart` | index | GET | Chart popup window |

### Farming Routes

| Route | Blueprint | Methods | Purpose |
|---|---|---|---|
| `/farming/plots` | farming | GET/POST | Plot management |
| `/farming/data` | farming | GET | DataTables server-side JSON |
| `/farming/workers` | farming | GET/POST | Farming worker stats |
| `/farming/warnings` | farming | GET/POST | Plot warnings |

### Plotting Routes

| Route | Blueprint | Methods | Purpose |
|---|---|---|---|
| `/plotting/jobs` | plotting | GET/POST | Plotting jobs |
| `/plotting/transfers` | plotting | GET/POST | Plot archiving |
| `/plotting/workers` | plotting | GET | Plotter status |

### Management Routes

| Route | Blueprint | Methods | Purpose |
|---|---|---|---|
| `/wallet` | wallet | GET/POST | Wallet management |
| `/keys` | keys | GET/POST | Key management |
| `/blockchains` | blockchains | GET/POST | Blockchain status |
| `/connections` | connections | GET/POST | Peer connections |
| `/alerts` | alerts | GET/POST | Chiadog alerts |
| `/pools` | pools | GET | Pool overview |
| `/workers` | workers | GET/POST | All workers |
| `/worker` | workers | GET | Single worker detail |
| `/drives` | drives | GET/POST | Drive monitoring |
| `/transactions` | transactions | GET | Transaction history |
| `/logs` | logs | GET | Log viewer |

### Settings Routes

| Route | Blueprint | Methods | Purpose |
|---|---|---|---|
| `/settings/alerts` | settings | GET/POST | Alert configuration |
| `/settings/farming` | settings | GET/POST | Farming settings |
| `/settings/plotting` | settings | GET/POST | Plotting settings |
| `/settings/pools` | settings | GET/POST | Pool settings |
| `/settings/tools` | settings | GET/POST | Fork tool settings |

## 4. Template System

### Base Template (`base.html`)

- Dark-themed master layout with collapsible left sidebar
- Bootstrap 5 grid system for responsive design
- Footer displays component versions (Chia, Plotman, Chiadog, Bladebit, Madmax, Machinaris)
- Auto-refresh via `<meta http-equiv="refresh" content="{{ reload_seconds }}">` (default: 120s)

### Custom Jinja2 Filters

| Filter | Purpose |
|---|---|
| `bytesfilter` | Human-readable byte sizes |
| `datetimefilter` | Date formatting |
| `timesecondstrimmer` | Remove seconds from time |
| `plotnameshortener` | First 30 chars of plot name |
| `launcheridshortener` | First 12 chars + ellipsis |
| `alltheblocks_blockchainlink` | External explorer link |
| `escape_single_quotes` | JS-safe string escaping |

## 5. JavaScript Libraries

| Library | Version | Purpose |
|---|---|---|
| jQuery | 3.7.1 | DOM manipulation |
| Bootstrap Bundle | 5.3.8 | UI components (modal, dropdown, collapse) |
| Chart.js | 4.5.1 | Data visualization (line, scatter, bar) |
| Luxon | 3.7.2 | DateTime formatting for Chart.js |
| DataTables | 2.3.5 | Server-side paginated tables |
| Leaflet | 1.9.4 | Interactive peer connection maps |

All libraries are vendored locally in `web/static/3rd_party/` (no CDN dependencies).

### Chart.js Usage

- Line charts: Wallet balances, netspace, plot counts over time
- Scatter plots: Farming challenges and proof times
- Bar charts: Partial submissions per hour
- Dark theme colors (#c7c7c7 text, custom palette)
- Time axes via Luxon adapter

### DataTables Usage

- Server-side pagination for the plots table (`/farming/data`)
- Request: `draw`, `start`, `length`, `search[value]`, `order[0][column]`
- Response: JSON with `draw`, `recordsTotal`, `recordsFiltered`, `data`
- Localized column headers via i18n translation files

## 6. AJAX Patterns

### Log Streaming
- XMLHttpRequest polling every 5 seconds
- Endpoint: `/logfile?hostname=X&log=farming&blockchain=chia`
- Auto-scroll on new content

### Plot Analysis
- XHR for plot integrity checks and analysis
- Modal dialogs display progress and results
- Endpoints: `?analyze=plot_id` or `?check=plot_id`

### Drive SMART Info
- XHR query for device SMART data
- Endpoint: `?device=sda&hostname=worker1`

### Form Submissions
- Traditional POST forms for actions (start/stop/suspend/resume)
- Redirect-after-POST pattern to prevent resubmission
- Hidden inputs for action parameters

## 7. Styling

### Dark Theme (`styles.css`)

```
Background:  #15171a
Text:        #c7c7c7
Accent:      #3aac59 (success green)
Cards:       .rounded-3 with shadow
Scrollbar:   Green thumb on dark track
```

- Custom Bootstrap overrides for dark appearance
- DataTables integration styling
- Responsive sidebar (collapsible on mobile)

## 8. Web-to-API Communication

The web layer communicates with the distributed API via HTTP:

```python
# web/utils.py
def send_get(worker, path, query_params, timeout=30)
def send_post(worker, path, payload)
def send_put(worker, path, payload)
def send_delete(worker, path)
```

Each request:
- Targets the worker's API URL (`http://hostname:port`)
- Includes `Accept-Language` header for i18n
- Has 30-second default timeout
- Returns JSON response data

## 9. Auto-Refresh Pattern

Most dashboard pages refresh automatically:

```html
{% if reload_seconds %}
<meta http-equiv="refresh" content="{{ reload_seconds }}">
{% endif %}
```

Default interval: 120 seconds. This keeps data current without JavaScript polling (except for log streaming which uses 5-second XHR polling).

## 10. Security Considerations

- Jinja2 auto-escapes by default (XSS protection)
- SQLAlchemy ORM parameterized queries (SQL injection protection)
- No CSRF tokens (relies on Docker network isolation)
- Hardcoded Flask session secret key
- Log type whitelist: `['alerts', 'farming', 'plotting', 'archiving', 'apisrv', 'webui', 'pooling', 'rewards']`
