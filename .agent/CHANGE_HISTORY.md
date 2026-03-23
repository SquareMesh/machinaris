# Change History

> Append-only log of all functional decisions made during development.
> Never delete entries. Reference by date + title.
> Format defined in CLAUDE.md Section 6.

---
## [2026-03-21] — Project Fork and Initial Setup

**Type:** Architecture
**Affects:** Entire project
**Design doc ref:** ARCHITECTURE.md

### Context
The original Machinaris project (guydavis/machinaris) was closed as the author no longer has interest in continuing. The project has been forked to SquareMesh/machinaris to continue development with a key focus on maintaining alignment with the latest versions of Chia from chia.net.

### Options Considered
- **Option A:** Start fresh — Pro: Clean slate Con: Lose all existing work and community
- **Option B:** Fork and continue — Pro: Preserve all existing functionality, community, and Docker infrastructure Con: Inherit technical debt

### Decision
Fork the SquareMesh/machinaris repository and continue development. The primary goal is to keep Machinaris aligned with the latest Chia blockchain versions while maintaining the existing multi-fork farming management capabilities.

### Technical Rationale
The existing codebase is mature (v2.6.0) with comprehensive Docker-based deployment, 34+ blockchain fork support, and a well-structured Flask API/WebUI architecture. Forking preserves all of this while allowing independent development direction.

### Impact
- All future development targets the SquareMesh fork
- Priority is Chia version alignment
- Comprehensive design documentation created to enable ongoing development

### Follow-up Required
- [x] Review and update all blockchain fork versions
- [x] Assess which deprecated forks to remove
- [x] Update CI/CD pipelines for the new repository
- [ ] Review and update Docker base images

---
## [2026-03-21] — Chia-Only Focus and v2.6.1 Upgrade

**Type:** Architecture
**Affects:** docker/dockerfile, .github/workflows/*, VERSION, CHANGELOG.md
**Design doc ref:** ARCHITECTURE.md, DOCKER-DEPLOYMENT.md, BLOCKCHAIN-INTEGRATION.md

### Context
User confirmed they only care about Chia blockchain. The codebase supported 34+ forks which added enormous build time, image size, and maintenance burden. Latest stable Chia is v2.6.1 (released 2026-03-18).

### Options Considered
- **Option A:** Keep all forks, only update Chia — Pro: Maximum compatibility Con: Huge build time, massive image, maintenance burden for abandoned forks
- **Option B:** Remove all non-Chia forks from Dockerfile — Pro: Fast builds, smaller image, focused maintenance Con: Can't support other forks without re-adding

### Decision
Remove all 33 non-Chia blockchain forks from the Dockerfile. Upgrade Chia to v2.6.1. The fork install scripts remain in the repo for reference but are not executed during build.

### Technical Rationale
Most forks are abandoned or have negligible user bases. The original author listed many as deprecated. Building 34 forks takes 1-3 hours; Chia-only builds in a fraction of that time. The install scripts are kept in `scripts/forks/` so they can be re-enabled if needed — this is a build-level change, not a code deletion.

### Impact
- Docker image is Chia-only — much smaller and faster to build
- CI/CD workflows simplified: single job (no Gigahorse), GHCR only (no DockerHub)
- Dropped Jammy base image — Noble (24.04) only
- VERSION bumped to 2.7.0 to reflect the breaking change
- Chia upgraded from 2.6.0 to 2.6.1
- Removed: forktools, fd-cli build args (Chia-only, not needed)

### Follow-up Required
- [x] Verify entrypoint.sh handles Chia-only gracefully (no fork-specific code paths break)
- [x] Test Docker build end-to-end
- [ ] Clean up blockchains.json to remove non-Chia entries (optional, app-level)
- [ ] Review common/config/globals.py for dead fork references

---
## [2026-03-22] — Entrypoint Chia-Only Cleanup

**Type:** Implementation
**Affects:** docker/entrypoint.sh, scripts/worker_port_warning.sh, scripts/start_machinaris.sh
**Design doc ref:** DOCKER-DEPLOYMENT.md, BLOCKCHAIN-INTEGRATION.md

### Context
After removing all 33 non-Chia forks from the Dockerfile, the entrypoint and supporting scripts still contained dead code paths for other forks — port warnings, plotman configs, forktools/fd-cli installs, and a multi-container stagger sleep.

### Options Considered
- **Option A:** Leave dead code — Pro: No risk of regression Con: Up to 3 min wasted on startup sleep, forktools clone attempt, confusing dead code
- **Option B:** Strip fork-specific code paths — Pro: Faster startup, cleaner code, no wasted network calls Con: Harder to re-enable forks (mitigated by git history)

### Decision
Strip all dead fork code paths from the entrypoint flow.

### Technical Rationale
With `blockchains=chia` hardcoded in the Dockerfile, these code paths were either no-ops (fd-cli skips Chia explicitly) or wasteful (forktools clone, random sleep). The random 1-180s sleep was designed to stagger multiple fork containers — irrelevant with a single blockchain.

### Impact
- Startup is up to 3 minutes faster (removed random sleep)
- No more runtime git clone of forktools
- worker_port_warning.sh reduced from 103 lines to 4 lines
- start_machinaris.sh plotman config simplified to Chia-only path

### Follow-up Required
- [x] Test Docker build and container startup end-to-end

---
## [2026-03-22] — Chia 2.6.x RPC Import Migration

**Type:** Bugfix
**Affects:** api/commands/rpc.py, api/views/plotnfts/resources.py
**Design doc ref:** BLOCKCHAIN-INTEGRATION.md

### Context
Chia 2.6.1 reorganized its Python module structure. RPC clients moved from `chia.rpc.*` to service-specific directories. `chia.util.ints` moved to `chia_rs.sized_ints`. The Machinaris API server failed to start due to `ModuleNotFoundError`.

### Options Considered
- **Option A:** Pin Chia to older version — Pro: No code changes Con: Miss security fixes, falling behind
- **Option B:** Update imports to match Chia 2.6.x module paths — Pro: Current, correct Con: Breaking change if reverting Chia version

### Decision
Update all Chia imports to the new 2.6.x paths. Also replaced the 230-line fork if/elif import chain in rpc.py with 7 lines of Chia-only imports.

### Technical Rationale
Chia 2.6.x moved RPC clients to service directories (e.g., `chia.rpc.farmer_rpc_client` → `chia.farmer.farmer_rpc_client`) and moved sized ints to `chia_rs`. The `bech32m` and `byte_types` util modules were unchanged.

### Impact
- API server starts successfully on Chia 2.6.1
- rpc.py reduced from ~250 lines of imports to ~25 lines
- `bytes32` import in plotnfts/resources.py updated to `chia_rs.sized_bytes`

### Follow-up Required
- [ ] Monitor for additional Chia API changes in future versions

---
## [2026-03-22] — Docker Build Chain: Base Image + GHCR Publishing

**Type:** Implementation
**Affects:** docker/dockerfile, .gitattributes
**Design doc ref:** DOCKER-DEPLOYMENT.md

### Context
The Dockerfile referenced `ghcr.io/guydavis/machinaris-base-noble` (original author's registry) which no longer exists. Building on Windows introduced CRLF line endings that broke shell scripts inside the Linux container.

### Options Considered
- **Option A:** Use guydavis base image — Pro: No build needed Con: Image doesn't exist
- **Option B:** Build own base image under squaremesh namespace — Pro: Self-contained, independent Con: Need to maintain base image

### Decision
Build and publish base image as `ghcr.io/squaremesh/machinaris-base-noble`. Updated Dockerfile FROM to reference `squaremesh` instead of `guydavis`. Added `.gitattributes` forcing LF line endings for all text files.

### Technical Rationale
The base image Dockerfile (`docker/dockerfile-noble.base`) was already in the repo. Publishing under `squaremesh` makes the project fully independent from the original author's infrastructure. The `.gitattributes` fix is essential for Windows development targeting Linux containers.

### Impact
- Published to GHCR: `ghcr.io/squaremesh/machinaris-base-noble:{latest,main}`
- Published to GHCR: `ghcr.io/squaremesh/machinaris:{2.7.0,latest}`
- `.gitattributes` ensures LF endings for sh, py, yaml, json, conf, dockerfile
- Verified working on Unraid deployment

### Follow-up Required
- [ ] Make GHCR packages public (if not already)
- [ ] Link packages to repository on GitHub

---
## [2026-03-22] — Telegram Wallet Balance Notifications

**Type:** Implementation
**Affects:** common/utils/notifications.py, api/commands/balance_notifications.py, api/views/wallets/resources.py, api/views/configs/resources.py, web/actions/notifications.py, web/blueprints/settings.py, web/templates/settings/notifications.html, web/templates/base.html
**Design doc ref:** TELEGRAM-NOTIFICATIONS.md

### Context
User wants Telegram notifications whenever Chia wallet balance changes, showing incoming XCH amount, new total, and approximate AUD price. Chiadog already supports Telegram but only monitors log file events (farming rewards) — it cannot detect arbitrary balance changes like incoming sends or pool payouts.

### Options Considered
- **Option A:** Extend Chiadog — Pro: Existing notification infrastructure Con: Chiadog watches debug.log, not wallet state; would require fundamental architecture change
- **Option B:** New balance change detection hooked into wallet POST handler — Pro: Near-real-time (~2 min), no new scheduled job, leverages existing wallet polling and fiat conversion Con: New code to maintain

### Decision
Option B — Hook into the existing `Wallets.post()` handler on the controller. When wallet details are POSTed (every ~2 min by `status_wallets.update()`), compare old vs new balance. If changed, send Telegram notification with XCH amount, new total, and fiat value.

### Technical Rationale
The wallet polling infrastructure already runs every ~2 minutes. By comparing balance before and after the upsert in `Wallets.post()`, we get near-real-time change detection without adding a new scheduled job. The existing `common/utils/fiat.py` already supports AUD conversion via CoinGecko. Notification config stored as JSON (like `locale_settings.json` and `wallet_settings.json`) rather than extending Chiadog's YAML config, since this is an independent feature.

### Impact
- 4 new files: `common/utils/notifications.py`, `api/commands/balance_notifications.py`, `web/actions/notifications.py`, `web/templates/settings/notifications.html`
- 4 modified files: wallet resources, config resources, settings blueprint, base template
- New settings page at Settings > Notifications with guided Telegram bot setup
- New design document: `docs/design/TELEGRAM-NOTIFICATIONS.md`
- Docker image rebuilt and pushed to GHCR as `2.7.0` and `latest`

### Follow-up Required
- [ ] Test notification end-to-end on Unraid deployment
- [ ] Consider adding notification history/log to the web UI
- [ ] Update setup guide if chat ID retrieval UX is confusing

---
## [2026-03-22] — Git Repo Cleanup: Exclude Agent Files

**Type:** Implementation
**Affects:** .gitignore
**Design doc ref:** N/A

### Context
The `.agent/` directory and `.claude/commands/` contain local agent framework files (change history, TODO tracking, slash commands) that should not be in the public GitHub repository.

### Options Considered
- **Option A:** Keep in repo — Pro: Visible history Con: Clutters public repo with agent-specific files
- **Option B:** Gitignore and remove from tracking — Pro: Clean public repo Con: Not visible in GitHub

### Decision
Added `.agent/` and `.claude/commands/` to `.gitignore` and removed from git tracking. Files remain locally for agent use.

### Impact
- `.agent/` and `.claude/commands/` no longer tracked in git
- No sensitive data was found in the files (verified before removal)
- Files remain on local disk for continued agent use

---
## [2026-03-22] — Design Docs Chia-Only Update (Resolve 4 DRIFT Entries)

**Type:** Design Update
**Affects:** docs/design/BLOCKCHAIN-INTEGRATION.md, docs/design/DOCKER-DEPLOYMENT.md, docs/design/PLOTTING-FARMING.md, docs/design/CONFIGURATION.md, docs/design/CLAUDE.md, .agent/DESIGN_INDEX.md
**Design doc ref:** All four DRIFT entries in DESIGN_INDEX.md

### Context
After the Chia-only pivot (v2.7.0) and subsequent code changes (Dockerfile, entrypoint, RPC imports), four design documents still described the old 34+ fork architecture. The DESIGN_INDEX flagged them as DRIFT.

### Options Considered
- **Option A:** Leave docs as historical reference — Pro: No work Con: Misleading for anyone reading the docs
- **Option B:** Update all docs to reflect Chia-only reality — Pro: Accurate docs Con: Loses fork reference (mitigated by git history)

### Decision
Update all four design docs and the navigation guide to reflect Chia-only v2.7.0 reality.

### Technical Rationale
Design docs are the authoritative source of truth per CLAUDE.md Section 3. Allowing them to drift from code undermines their purpose. Historical fork information is preserved in git history and in `blockchains.json` (TODO-008).

### Impact
- BLOCKCHAIN-INTEGRATION.md: Removed 34+ fork listings, updated RPC imports to Chia 2.6.x paths, removed Special Cases section
- DOCKER-DEPLOYMENT.md: Updated FROM to squaremesh, removed 34 build args, removed fork-specific ports/scripts, removed Multi-Fork Farm pattern, updated CI/CD to GHCR-only
- PLOTTING-FARMING.md: Removed Gigahorse section, removed fork-specific plotman configs, simplified plotter list to Bladebit + Madmax
- CONFIGURATION.md: Removed fork-specific env vars (chives_masternode, gigahorse_recompute_server, forktools_skip_build), added notifications.json to config tree
- docs/design/CLAUDE.md: Updated version to 2.7.0, added Chia-only scope, added TELEGRAM-NOTIFICATIONS.md to index
- DESIGN_INDEX.md: All 4 DRIFT entries resolved to IMPLEMENTED with updated notes and dates

### Follow-up Required
- [ ] Clean up blockchains.json for Chia-only (TODO-008)

---
## [2026-03-22] — Fix Hardcoded Chia Version in GPU Binary Downloads

**Type:** Bugfix
**Affects:** scripts/forks/chia_install.sh
**Design doc ref:** DOCKER-DEPLOYMENT.md, BLOCKCHAIN-INTEGRATION.md §7

### Context
During a version audit confirming alignment with latest Chia stable (2.6.1), discovered that the CUDA GPU binary download URLs in `chia_install.sh` were hardcoded to `2.6.0` while the Dockerfile and CI workflows correctly specified `CHIA_BRANCH=2.6.1`. This meant the container was building Chia 2.6.1 from source but installing 2.6.0 GPU binaries.

### Options Considered
- **Option A:** Update hardcoded URLs to 2.6.1 — Pro: Quick fix Con: Will drift again on next upgrade
- **Option B:** Use `${CHIA_BRANCH}` variable in URLs — Pro: Always stays in sync with Dockerfile Con: Assumes release asset naming convention stays consistent (it has been stable)

### Decision
Option B — Replace hardcoded `2.6.0` in the download URLs with `${CHIA_BRANCH}` (already passed as `$1` to the script). This ensures GPU binaries always match the source build version.

### Technical Rationale
The `CHIA_BRANCH` arg flows from Dockerfile → install script as `$1`. The GitHub release asset naming convention (`chia-blockchain-cli_<version>-1_<arch>.deb`) has been stable across releases. Using the variable eliminates a manual update step on every Chia version bump.

### Impact
- GPU binaries now match the Chia source version automatically
- No more version mismatch between source build (2.6.1) and CUDA binaries (was 2.6.0)
- Future Chia upgrades only need to change `CHIA_BRANCH` in Dockerfile and workflows

### Follow-up Required
- [ ] Rebuild Docker image to pick up the fix

---
## [2026-03-22] — Eliminate Command Injection Vulnerabilities

**Type:** Bugfix
**Affects:** api/commands/chia_cli.py, api/commands/smartctl.py, api/commands/plotman_cli.py, api/commands/rewards.py, api/commands/log_parser.py, api/schedules/log_rotate.py, common/config/globals.py, web/actions/chia.py
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Comprehensive security audit identified 7+ critical command injection vectors where user-controlled input (node_id, connection, plot_path, device_name, plot_id, wallet_num) was passed into `Popen()` with `shell=True` using `.format()` string interpolation. An attacker could inject arbitrary shell commands via these parameters (e.g., `connection = "localhost:8444; rm -rf /root/.chia"`).

### Options Considered
- **Option A:** Add input validation/sanitization — Pro: Targeted fix Con: Easy to miss edge cases, defense-in-depth failure
- **Option B:** Convert all `Popen(shell=True)` to `Popen(shell=False)` with list args — Pro: Eliminates entire class of vulnerability, OS executes commands directly without shell parsing Con: Commands using shell features (pipes, &&, nohup &) need refactoring

### Decision
Option B — Convert all Popen calls to list args with `shell=False` (the default). For commands using shell pipes (`|`), replaced with Python-level filtering. For `nohup` backgrounding (plotman start, chiadog start), kept `shell=True` since they only use internal constants, not user input.

### Technical Rationale
With `shell=False`, subprocess passes arguments directly to `execvp()` without shell interpretation. Shell metacharacters (`;`, `|`, `&&`, backticks, `$()`) are treated as literal characters, not command separators. This eliminates the entire class of command injection regardless of input content. Shell pipe chains were replaced with equivalent Python: run the first command, filter output in Python (list comprehensions for grep -v, slicing for tail -n).

### Impact
- 39 Popen calls converted from `shell=True` to `shell=False` across 8 files
- 1 `os.system()` call replaced with `Popen()` list args
- Deleted unused `get_free_bytes()` function (used shell pipes, comment said "unused")
- Refactored `load_keys_show()` from single shell `&&`/pipe chain to two sequential Popen calls
- Refactored log_parser.py grep pipe chains to Python-level filtering
- Fixed mnemonic logging: `web/actions/chia.py` no longer logs the 24-word seed phrase
- 10 remaining `shell=True` calls are all either dead code (MMX, forktools) or nohup backgrounding with internal constants only

### Follow-up Required
- [ ] Rebuild Docker image to include the fix
- [ ] Consider removing dead code files (mmx_cli.py, forktools_cli.py) entirely

---
## [2026-03-22] — Mnemonic Flash Display: Keep As-Is

**Type:** Architecture
**Affects:** web/actions/chia.py
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Security audit flagged `flash(mnemonic_words)` on line 232 as a risk — displaying the 24-word seed phrase in the browser during key generation. Evaluated whether to remove it.

### Options Considered
- **Option A:** Remove flash display — Pro: Seed phrase never in browser HTML Con: Users must SSH into container to read `/root/.chia/mnemonic.txt` to back up keys; poor UX for initial setup
- **Option B:** Keep flash display — Pro: Standard wallet UX (show seed once for backup); only appears during setup wizard, not normal operation Con: Visible in page source for that single page load

### Decision
Keep the flash display. The mnemonic logging (to webui.log) was already removed in the command injection fix. The flash display is ephemeral (consumed on render, not persisted) and is the only user-facing way to back up the seed phrase during setup. Removing it would degrade UX without meaningful security gain — the mnemonic file itself remains on disk regardless.

### Technical Rationale
Flask flash messages are stored in the session cookie and consumed (deleted) after the first render. They do not persist in browser history, logs, or database. The page URL (`/setup`) is recorded in history but not the POST response body. Log rotation (7-day daily) has already cycled out any historical log entries. This is consistent with standard cryptocurrency wallet UX (show seed once, user responsible for backup).

### Impact
- No code changes — flash display kept as-is
- Mnemonic logging already removed (Priority 2 partially complete)
- Decision locked in to avoid revisiting

---
## [2026-03-22] — Add CSRF Protection via Flask-WTF

**Type:** Implementation
**Affects:** docker/requirements.txt, web/__init__.py, 18 template files (41 forms)
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Security audit identified that all POST forms lacked CSRF protection. An attacker could craft a malicious page that submits forms on behalf of authenticated users (e.g., change notification settings, import keys, modify farming config).

### Options Considered
- **Option A:** Custom CSRF middleware — Pro: No dependency Con: Error-prone, reinventing the wheel
- **Option B:** Flask-WTF CSRFProtect — Pro: Battle-tested, 2 lines to enable, auto-validates all POST requests Con: New pip dependency

### Decision
Option B — Flask-WTF CSRFProtect. Industry-standard solution with minimal integration effort.

### Technical Rationale
Flask-WTF's CSRFProtect validates a token on every POST/PUT/PATCH/DELETE request automatically. Tokens are generated per-session and embedded as hidden form fields. The web UI's server-to-API communication (via `requests` library in `web/utils.py`) is unaffected since it's not browser-initiated. Only 1 AJAX POST exists (`settings/plotting.html` schedule save) — the token was added to its data payload.

### Impact
- New dependency: `flask-wtf` in `docker/requirements.txt`
- `web/__init__.py`: Added `CSRFProtect(app)` initialization
- 40 hidden `csrf_token` fields added across 18 template files (41 forms)
- 1 jQuery `$.post()` call updated with CSRF token in data payload
- Docker rebuild required to install new pip package
- No config, database, or persistent volume changes
- No impact on API-to-API (controller-worker) communication

### Follow-up Required
- [ ] Rebuild Docker image to include Flask-WTF

---
## [2026-03-22] — Replace Hardcoded Flask Secret Key with File-Based Auto-Generation

**Type:** Bugfix
**Affects:** web/__init__.py
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Flask session secret key was hardcoded as `b'$}#P)eu0A.O,s0Mz'` in `web/__init__.py`. This means every Machinaris installation shares the same key, allowing session cookie forgery across instances. Identified during security audit (Priority 3) and tracked as TODO-002.

### Options Considered
- **Option A:** Environment variable (`SECRET_KEY`) — Pro: Standard Flask pattern Con: Requires user to add env var to Docker template; friction for zero benefit
- **Option B:** File-based auto-generation at `/root/.chia/machinaris/config/secret_key` — Pro: Zero user action, persists across restarts on Docker volume, unique per installation Con: Slightly more code than env var

### Decision
Option B — Generate a 32-byte random key on first boot, write to persistent config volume, reuse on all subsequent boots. No user configuration required.

### Technical Rationale
The config directory (`/root/.chia/machinaris/config/`) is already on the persistent Docker volume and used for other config files (notifications.json, wallet_settings.json, etc.). A file-based key is invisible to the user, survives container rebuilds, and ensures each installation has a unique key. The only user-visible effect of the key changing (on first upgrade) is a one-time session cookie reset — which is invisible since there's no authentication system.

### Impact
- Removed hardcoded secret key from source code
- Each installation now has a unique, cryptographically random 32-byte key
- Existing containers: one-time session reset on first boot after upgrade (no user action needed)
- No new env vars, no Docker template changes, no config changes required

### Follow-up Required
- [ ] Rebuild Docker image to include the fix

---
## [2026-03-22] — Remove All |safe Filters from Templates (XSS Hardening)

**Type:** Bugfix
**Affects:** web/__init__.py, web/actions/plotman.py, web/actions/pools.py, web/blueprints/landing.py, web/models/worker.py, web/models/pools.py, web/templates/_flash_messages.html (new), 22 template files
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Security audit identified 22 `|safe` filter usages across templates. The `|safe` filter disables Jinja2's auto-escaping, opening XSS vectors if any user-controlled content reaches flash messages or template variables. The challenge was that 8 Python-side `flash()` calls embedded intentional HTML (`<pre>` for error output, `<a href>` for wiki links, `<b>` for emphasis).

### Options Considered
- **Option A:** Input validation on flash content — Pro: Targeted Con: Easy to miss, doesn't eliminate the pattern
- **Option B:** Category-based formatting + `markupsafe.Markup()` — Pro: Eliminates all `|safe` from templates, formatting logic lives in template macro, intentional HTML explicitly marked safe at the source Con: Slightly more code in Python

### Decision
Option B — Two-pronged approach:
1. Flash messages with `<pre>` content: changed to category suffixes (e.g., `danger_pre`). New `_flash_messages.html` macro renders `<pre>` tags template-side based on suffix, with auto-escaped content inside.
2. Non-flash intentional HTML (block links, wiki links, pool warnings, worker warnings, landing images): wrapped with `markupsafe.Markup()` at the Python source, making the safety decision explicit and auditable.

### Technical Rationale
`Markup()` is part of markupsafe (a Flask dependency, always available). When Jinja2 encounters a `Markup` object, it skips auto-escaping — but only for that specific value. This is safer than `|safe` because the safety decision is made where the HTML is created (in Python), not where it's rendered (in the template). The `_pre` category suffix pattern keeps formatting logic in one macro file rather than scattered across 20+ templates.

### Impact
- **0** `|safe` filters remain in any template (was 22)
- New file: `web/templates/_flash_messages.html` — reusable macro replacing 20 copy-pasted flash blocks
- `web/actions/plotman.py`: 6 `<pre>` flash calls → category suffix, 1 wiki link → `Markup()`
- `web/actions/pools.py`: 1 `<pre>` flash call → category suffix
- `web/models/pools.py`: 1 faucet link → `Markup()`
- `web/models/worker.py`: title/message → `Markup()` in constructor
- `web/blueprints/landing.py`: image tag → `Markup()`
- `web/__init__.py`: `alltheblocks_blocklink` filter → `Markup()`
- No visual changes — all HTML renders identically to before

### Follow-up Required
- [ ] Rebuild Docker image to include the fix

---
## [2026-03-22] — Dismiss Config File Encryption (TODO-015)

**Type:** Architecture
**Affects:** N/A (no code change)
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Security audit flagged plaintext storage of Telegram bot tokens, Maxmind/Mapbox API keys, and cold wallet addresses in `/root/.chia/machinaris/config/`. These are also exposed via unauthenticated API endpoints (e.g., `GET /configs/notifications/chia` returns the bot token in plain JSON). Evaluated whether encryption at rest or Docker secrets would improve security.

### Options Considered
- **Option A:** Encrypt config files at rest — Pro: Files not readable if volume is exfiltrated Con: App must decrypt to use them, so decryption key must be co-located, defeating the purpose. Adds complexity to every config read/write path.
- **Option B:** Docker secrets — Pro: Slightly better isolation (`/run/secrets/` is tmpfs, not persisted to disk) Con: Unraid's Docker UI doesn't support Docker secrets natively (requires Compose or Swarm mode). App still reads plaintext from the mounted file.
- **Option C:** Dismiss — encrypt-at-rest is security theater in this context. The real attack surface is unauthenticated API access, which TODO-013 (authentication) addresses directly.

### Decision
Option C — Dismiss TODO-015. The threat model doesn't support encryption at rest: if an attacker has access to the container's filesystem, they already have root and can read the decryption key too. If they're on the network, they can hit the unauthenticated API regardless of how files are stored on disk. Authentication (TODO-013) is the correct control for both attack vectors.

### Technical Rationale
Encryption at rest protects against one scenario: physical disk exfiltration (e.g., someone steals the NAS drives). In that scenario, the Chia keys themselves (in `/root/.chia/mainnet/config/`) are a far higher-value target and are also unencrypted — that's a Chia design decision, not a Machinaris one. Encrypting only the Machinaris config files while leaving Chia's own keys unencrypted would give a false sense of security.

### Impact
- No code changes
- TODO-015 dismissed with documented rationale
- TODO-013 (authentication) elevated as the correct mitigation for API exposure

---
## [2026-03-22] — TOTP Two-Factor Authentication for Web UI

**Type:** Implementation
**Affects:** web/__init__.py, web/blueprints/auth.py (new), web/templates/auth/login.html (new), web/templates/auth/setup_totp.html (new), web/templates/base.html, common/utils/totp.py (new), docker/requirements.txt, docs/TOTP_AUTHENTICATION.md (new)
**Design doc ref:** CONFIGURATION.md §6 (Security)

### Context
Security audit (TODO-013) identified that the web UI has no authentication — anyone on the network can access keys, wallets, configs, and certificates. The TODO-015 evaluation confirmed that encrypting config files is the wrong approach; access control is the correct mitigation.

### Options Considered
- **Option A:** Username/password login — Pro: Familiar Con: Password management overhead, password storage, single-user makes username redundant
- **Option B:** HTTP Basic Auth behind reverse proxy — Pro: Zero app changes Con: Requires separate proxy setup, not built-in, user must configure it themselves
- **Option C:** TOTP-only authentication (authenticator app) — Pro: No passwords to manage, strong security, single 6-digit code, familiar UX (same as Gmail/GitHub 2FA) Con: Requires authenticator app on phone

### Decision
Option C — TOTP-only authentication. Single-user model: no username, no password, just a 6-digit authenticator code. Optional enrollment — app runs unauthenticated until the user explicitly sets up TOTP.

### Technical Rationale
TOTP (RFC 6238) is the industry standard for time-based one-time passwords. The shared secret is generated once during enrollment, stored in `/root/.chia/machinaris/config/totp_secret.json`, and used to validate 6-digit codes that rotate every 30 seconds. A `valid_window=1` allows codes from the previous and next 30-second window to account for clock skew.

The `before_app_request` hook on the web Flask app (port 8926) checks authentication on every request. It exempts: the landing page, the Chia setup wizard, the login page, the TOTP setup page, and static assets. The API app (port 8927) is a separate Flask instance and is completely unaffected.

Sessions use Flask's built-in signed cookies with `PERMANENT_SESSION_LIFETIME = 7 days`. The session cookie is marked `permanent` on login so it persists across browser closes. The session signing key was already moved to a file-based auto-generated key (TODO-002).

### Impact
- New dependency: `pyotp`, `qrcode[pil]` in `docker/requirements.txt`
- New files: `common/utils/totp.py`, `web/blueprints/auth.py`, `web/templates/auth/login.html`, `web/templates/auth/setup_totp.html`
- Modified: `web/__init__.py` (auth blueprint, session lifetime, context processor), `web/templates/base.html` (setup banner, logout link)
- New user guide: `docs/TOTP_AUTHENTICATION.md`
- **Backwards compatible** — existing containers work exactly as before until user opts in to TOTP
- No impact on controller-worker API traffic (port 8927)
- Lockout recovery: delete `totp_secret.json` from container or Unraid appdata share

### Follow-up Required
- [ ] Rebuild Docker image to include new dependencies and auth code
- [ ] Test TOTP enrollment and login flow on Unraid deployment
- [ ] Consider rate limiting on login attempts (low priority — TOTP's 30s rotation makes brute force impractical)

---
## [2026-03-23] — Align Python Version to 3.12 (TODO-006)

**Type:** Implementation
**Affects:** .github/workflows/unit-tests.yml, .github/workflows/codeql-analysis.yml, pyproject.toml, docs/design/ARCHITECTURE.md
**Design doc ref:** ARCHITECTURE.md §1 (Technology Stack)

### Context
Three different Python versions were specified across the project: CI ran 3.9, pyproject.toml targeted 3.10, and the Docker Noble base image actually runs 3.12. No deliberate decision had been made — the versions just drifted over time from the original author's setup. Chia 2.6.1 supports 3.9–3.13, so there was no upstream constraint.

### Options Considered
- **Option A:** Pin to 3.10 (lowest common denominator of stated targets) — Pro: Conservative Con: Doesn't match what Docker actually runs (3.12); CI still diverges
- **Option B:** Align everything to 3.12 (match Ubuntu Noble runtime) — Pro: Matches production reality; modern Python features available; CI catches real bugs Con: Drops support for 3.9–3.11 (never actually worked in Docker anyway)
- **Option C:** Jump to 3.13 — Pro: Latest features Con: Not shipped by Ubuntu Noble; would require manual install in Dockerfile; unnecessary complexity

### Decision
Option B — Align to Python 3.12. This documents what the Docker image already runs rather than introducing a new runtime version.

### Technical Rationale
Ubuntu 24.04 (Noble) ships Python 3.12 as its system Python. The `dockerfile-noble.base` installs `python3` without a version pin, which resolves to 3.12. Every Machinaris container built since the Noble migration has been running 3.12 — this change simply makes the rest of the project agree with that fact.

### Impact
- `.github/workflows/unit-tests.yml`: Python 3.9 → 3.12, actions/checkout v3 → v4, actions/setup-python v4 → v5
- `.github/workflows/codeql-analysis.yml`: actions/checkout v3 → v4, codeql-action v2 → v3
- `pyproject.toml`: Added `[project] requires-python = ">= 3.12"`, Black target py310 → py312, added mypy python_version = "3.12"
- `docs/design/ARCHITECTURE.md`: "Python 3.10+" → "Python 3.12+", "Ubuntu 22.04/24.04" → "Ubuntu 24.04 Noble"
- No Docker image changes needed — already running 3.12

### Follow-up Required
- [ ] Run unit tests on Python 3.12 to confirm all pass
- [ ] Consider adopting 3.12+ features in future work (modern typing syntax, tomllib, etc.)

---
## [2026-03-23] — Chia-Only Cleanup: blockchains.json, Forktools, Dead Code (TODO-008)

**Type:** Implementation
**Affects:** common/config/blockchains.json, common/config/globals.py, api/commands/chia_cli.py, common/models/pools.py, common/models/plottings.py, web/models/chia.py, api/views/configs/resources.py, web/blueprints/settings.py, web/templates/base.html
**Design doc ref:** BLOCKCHAIN-INTEGRATION.md §3, CONFIGURATION.md

### Context
After the Chia-only pivot (v2.7.0), `blockchains.json` still contained metadata for 33 non-Chia forks, and several Python files contained dead fork-specific code paths, hardcoded fork lists, and forktools integration that no longer serves any purpose.

### Options Considered
- **Option A:** Leave dead code as reference — Pro: No risk of regression Con: Confusing, misleading, increases cognitive load
- **Option B:** Clean up everything Chia-only — Pro: Smaller, clearer codebase; config matches reality Con: Harder to re-add forks (mitigated by git history)

### Decision
Option B — Full Chia-only cleanup. Git history preserves all fork data if ever needed.

### Technical Rationale
With `blockchains=chia` hardcoded in the Dockerfile and all fork install scripts removed from the build, these code paths are unreachable. Leaving them creates confusion about what the code actually supports. The `legacy_blockchain()` function, `gather_mmx_reward()`, `BLOCKCHAINS_USING_PEER_CMD` with 15 dead entries, and `POOLABLE`/`PLOTTABLE` lists with dead forks all add noise to the codebase.

### Impact
- `blockchains.json`: 34 entries → 1 (Chia only)
- Deleted: `api/commands/forktools_cli.py`, `web/actions/forktools.py`, `web/templates/settings/tools.html`
- Removed: forktools imports from `api/views/configs/resources.py` and `web/blueprints/settings.py`
- Removed: Tools nav link from `web/templates/base.html`, tools route from settings blueprint
- Removed: `gather_mmx_reward()` function and its global variables from `globals.py`
- Simplified: `legacy_blockchain()` → always returns `False`
- Simplified: `get_alltheblocks_name()` → identity function
- Simplified: `wallet_running()` → removed mmx/gigahorse branches
- Simplified: `BLOCKCHAINS_USING_PEER_CMD` → `['chia']`
- Simplified: `POOLABLE_BLOCKCHAINS` → `['chia']`
- Simplified: `PLOTTABLE_BLOCKCHAINS` → `['chia']`
- Removed: hddcoin special case in `web/models/chia.py` connection parsing
- Removed: `'forktools'` from config type list in API
- Removed: `'tools'` config type handlers from API GET/PUT

### Follow-up Required
- [ ] Consider removing mmx_cli.py and its 8 importers (deeper refactor, deferred)
- [ ] Rebuild Docker image to include cleanup

---
## [2026-03-23] — Production Safety: Timeouts, Pinned Deps, Health Check, Shell Error Handling

**Type:** Bugfix
**Affects:** api/utils.py, api/__init__.py, docker/requirements.txt, docker/dockerfile, scripts/forks/chia_install.sh, scripts/machinaris_install.sh, scripts/start_machinaris.sh, scripts/pull_3rd_party_libs.sh, scripts/i18n/compile.sh
**Design doc ref:** DOCKER-DEPLOYMENT.md, API.md

### Context
Performance review identified four critical production safety issues: `send_post()` and `send_delete()` had no timeouts (scheduler deadlock risk), all Python dependencies were unpinned (non-reproducible builds), no Docker HEALTHCHECK existed, and shell scripts had no error handling (`set -e`).

### Options Considered
Single option — fix all four. These are unambiguous improvements with no design tradeoffs.

### Decision
Fix all four as a single Tier 1 production safety batch.

### Technical Rationale
1. **Timeouts:** `send_get()` already had `timeout=30`. `send_post()`, `send_worker_post()`, and `send_delete()` lacked it. Without timeouts, a hanging controller blocks all 15+ scheduler jobs indefinitely — the single most likely production incident.
2. **Pinned deps:** Every other build system in the industry pins dependencies. Unpinned deps mean `pip install` today != tomorrow. One breaking semver bump in any of 30 packages could silently break production.
3. **HEALTHCHECK:** Docker, Unraid, and Kubernetes all use HEALTHCHECK to distinguish "running" from "dead." Without it, a container with crashed services shows as healthy. Added `/ping` endpoint to API and `HEALTHCHECK` instruction with 5-minute start period (Chia init is slow).
4. **Shell `set -eo pipefail`:** Added to build scripts and startup script. NOT added to entrypoint.sh or chia_launch.sh due to complex conditional logic with intentional failures — those need careful per-line auditing.

### Impact
- `api/utils.py`: Added `timeout=30` to `send_post()`, `send_worker_post()`, `send_delete()`
- `api/__init__.py`: Added `/ping` health endpoint
- `docker/requirements.txt`: All 30 packages pinned to specific versions. `marshmallow` uses range pin (`>=3.24.1,<4.0`) due to `marshmallow-toplevel` incompatibility with 4.x
- `docker/dockerfile`: Added `HEALTHCHECK` instruction (60s interval, 10s timeout, 300s start period, 3 retries)
- 5 shell scripts: Added `set -eo pipefail` (chia_install.sh, machinaris_install.sh, start_machinaris.sh, pull_3rd_party_libs.sh, i18n/compile.sh)
- `start_machinaris.sh`: Fixed `pidof` calls to use `|| true` for `set -e` compatibility

### Follow-up Required
- [ ] Rebuild Docker image to verify all pinned versions install correctly
- [x] Audit entrypoint.sh and chia_launch.sh for safe `set -e` adoption (complex conditional logic)
- [ ] Verify HEALTHCHECK works on Unraid deployment
- [x] Note: marshmallow-toplevel is unmaintained (last update 2020) — consider replacement to unblock marshmallow 4.x

---
## [2026-03-23] — Code Quality and Performance Hardening

**Type:** Implementation
**Affects:** All Python files, all shell scripts, SQLAlchemy models, gunicorn config, marshmallow schemas
**Design doc ref:** ARCHITECTURE.md, API.md

### Context
Five TODO items addressed in a single pass to improve code quality, performance, and reliability across the codebase.

### Changes Made

**1. Replace bare `except:` clauses (TODO-018)**
- Replaced 147 bare `except:` with `except Exception:` across 50 Python files
- Prevents accidentally catching SystemExit, KeyboardInterrupt, and GeneratorExit

**2. Add database indexes (TODO-017)**
- Added `index=True` to hostname, blockchain, and created_at columns on all 17 stat tables
- Added indexes to alerts, challenges, partials, and plots operational tables
- Created Alembic migration `b1a2c3d4e5f6` for existing databases
- Critical for dashboard performance as stats tables grow over months

**3. Gunicorn worker recycling (TODO-020)**
- Added `max_requests = 1000` and `max_requests_jitter = 50` to gunicorn.conf.py
- Workers now restart after ~1000 requests, preventing memory accumulation

**4. Replace marshmallow-toplevel (TODO-021)**
- Created inline `TopLevelSchema` class in `api/extensions/api/__init__.py`
- Updated all 21 schema files to import from internal module
- Removed `marshmallow-toplevel==0.1.3` from requirements.txt
- Unpinned marshmallow `<4.0` constraint — future upgrade now possible

**5. Shell script error handling (TODO-019)**
- Added `set -eo pipefail` to 12 shell scripts (entrypoint.sh, chia_launch.sh, setup_databases.sh, stop_machinaris.sh, mount_remote_shares.sh, worker_port_warning.sh, gpu_drivers_setup.sh, plotman_setup.sh, chiadog_setup.sh, bladebit_setup.sh, madmax_setup.sh, plotman_autoplot.sh)
- Fixed `grep -q` + `$?` anti-patterns to use `if ! grep -q` idiom
- Added `|| true` guards to pidof, kill, chmod commands that may legitimately fail
- Standardized shebangs to `#!/usr/bin/env bash`

### Decision
All five changes are low-risk improvements with no behavioral changes to happy paths. Database indexes use CREATE INDEX IF NOT EXISTS via Alembic. TopLevelSchema replacement is API-compatible.

### Impact
- Dashboard queries faster as data accumulates
- Memory leaks prevented by worker recycling
- Silent error swallowing eliminated across Python codebase
- Shell scripts fail fast on real errors instead of continuing silently
- marshmallow 4.x upgrade path unblocked

---
## [2026-03-23] — Add /deploy, /validate Skills and CLAUDE.md Hard Rules

**Type:** Implementation
**Affects:** .claude/commands/, CLAUDE.md
**Design doc ref:** CLAUDE.md §4.2, §5.1, §9b

### Context
Session review identified recurring patterns: Docker build/push cycle was manual and error-prone (forgot :latest tag), pre-existing bugs only caught at runtime (orphaned endif, bootstrap-icons zip change), no local validation before deploy.

### Decision
Created three new capabilities:
1. `/deploy` skill — automates `docker build` + `docker push ghcr.io/squaremesh/machinaris:latest`
2. `/validate` skill — pre-flight checks (Python syntax, Jinja2 tag balance, code quality, shell scripts)
3. CLAUDE.md hard rules (5 rules) and deployment workflow section (§9b)

### Impact
- Future sessions have one-command deploy: `/deploy` or `/deploy full`
- Template tag mismatches caught before deploy, not at runtime
- Hard rules codify lessons learned (no bare except, template tag balance, set -eo pipefail, Chia-only)

---
## [2026-03-23] — API Bind Address Restriction

**Type:** Implementation
**Affects:** docker/dockerfile, scripts/start_machinaris.sh, scripts/dev/start-api.sh, web/blueprints/settings.py, web/templates/settings/network.html, web/templates/base.html
**Design doc ref:** CONFIGURATION.md — Security

### Context
The API server (port 8927) was binding to `0.0.0.0`, making it accessible to any machine on the network. The API has no authentication, so any device on the LAN could read/write configs, trigger actions, and access wallet data. For single-instance farming setups, only the WebUI (inside the same container) needs to reach the API.

### Options Considered
- **Option A:** Bind API to `127.0.0.1` always — Pro: Maximum security Con: Breaks multi-worker setups permanently
- **Option B:** Configurable bind via env var, default `127.0.0.1` — Pro: Secure by default, can be opened for workers Con: Requires restart to change

### Decision
Option B — new `api_bind_address` env var (default `127.0.0.1`). Set to `0.0.0.0` when remote workers are needed.

### Technical Rationale
WebUI calls the API at `http://localhost:8927` from within the container, so binding to `127.0.0.1` doesn't break single-instance usage. Multi-worker mode is a deliberate opt-in via Docker env var.

### Impact
- API is no longer exposed on the network by default
- New Settings > Network page shows current status and provides guidance for both modes
- Network page added to sidebar (always visible, not gated by farming_enabled)

### Follow-up Required
- [ ] None — feature complete

---
## [2026-03-23] — Plotting Tools Disable Toggle

**Type:** Implementation
**Affects:** docker/dockerfile, docker/entrypoint.sh, common/config/globals.py, web/templates/settings/network.html
**Design doc ref:** CONFIGURATION.md — Environment Variables, DOCKER-DEPLOYMENT.md — Entrypoint

### Context
Container boot installs plotman (git clone + pip install + apt), bladebit (binary downloads), and madmax (binary downloads) on every first boot. This takes significant time and resources even when the user is not actively plotting. User requested the ability to skip this entirely.

### Options Considered
- **Option A:** Always install but don't run — Pro: No config needed Con: Still wastes boot time and disk
- **Option B:** New `plotting_disabled` env var that skips setup scripts and hides UI — Pro: Fast boot, clean UI Con: Requires container restart to change

### Decision
Option B — `plotting_disabled=true` by default. When set, skips plotman_setup.sh, bladebit_setup.sh, madmax_setup.sh, and plotman_autoplot.sh. Also returns `False` from `globals.plotting_enabled()` which hides the Plotting page and settings from the sidebar, and skips plotting scheduler jobs.

### Technical Rationale
Chiadog (monitoring) was moved outside the plotting guard since it monitors farming/harvesting, not plotting. The `plotting_enabled()` function in globals.py was the natural place to add the check since it already gates all plotting UI and scheduler behavior.

### Impact
- Default boot is faster (no plotting tool installation)
- Users opt in to plotting when needed by setting `plotting_disabled=false`
- Network & Services settings page provides context-aware guidance for both states
- Farming, harvesting, wallet operations, and existing plots are completely unaffected
