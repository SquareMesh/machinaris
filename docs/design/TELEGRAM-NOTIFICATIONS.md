# Telegram Wallet Balance Notifications

## Overview

Sends a Telegram message whenever the Chia wallet balance changes, showing the incoming/outgoing XCH amount, new total balance, and approximate fiat value (e.g., AUD).

## Architecture

This feature is **independent from Chiadog**. Chiadog monitors `debug.log` for farming reward events. This system detects *any* balance change (incoming sends, pool payouts, manual transfers) by comparing wallet state on each polling cycle.

### Data Flow

```
status_wallets.update()          [fullnode worker, every ~2 minutes]
  → POST /wallets/               [to controller API]
    → Wallets.post()             [api/views/wallets/resources.py]
      → old_details captured before upsert
      → db commit
      → balance_notifications.check_and_notify()
        → parse old/new balance via regex
        → if changed beyond threshold: format message, call Telegram API
```

No new scheduled job is required. The feature hooks into the existing wallet update flow.

### Components

| Component | File | Purpose |
|---|---|---|
| Config + Telegram sender | `common/utils/notifications.py` | Load/save config JSON, send Telegram messages, parse balance |
| Change detection | `api/commands/balance_notifications.py` | Compare balances, apply filters, dispatch notifications |
| Wallet POST hook | `api/views/wallets/resources.py` | Integration point in `Wallets.post()` |
| Config API | `api/views/configs/resources.py` | GET/PUT for `notifications` config type |
| Web actions | `web/actions/notifications.py` | Bridge between web UI and API |
| Web route | `web/blueprints/settings.py` | `/settings/notifications` endpoint |
| Web template | `web/templates/settings/notifications.html` | Settings form with setup guide |
| Sidebar link | `web/templates/base.html` | Navigation under Settings menu |

## Configuration

Stored at `/root/.chia/machinaris/config/notifications.json`:

```json
{
  "telegram": {
    "enabled": false,
    "bot_token": "",
    "chat_id": "",
    "notify_on_increase": true,
    "notify_on_decrease": false,
    "min_change_threshold": 0.0,
    "include_cold_wallet": true
  }
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | false | Master on/off switch |
| `bot_token` | string | "" | Telegram Bot API token from @BotFather |
| `chat_id` | string | "" | Telegram chat/group ID |
| `notify_on_increase` | bool | true | Notify on incoming XCH |
| `notify_on_decrease` | bool | false | Notify on outgoing XCH |
| `min_change_threshold` | float | 0.0 | Minimum XCH change to trigger notification |
| `include_cold_wallet` | bool | true | Include cold wallet balance in total |

## Message Format

```
Chia Wallet — Balance Changed

Received: +0.250000 XCH
New Balance: 12.500000 XCH
Approx Value: $450.00 AUD

Source: machinaris-controller
```

## Web UI

Located at **Settings > Notifications** in the sidebar.

### Sections

1. **Setup Guide** — Collapsible accordion with step-by-step Telegram bot creation instructions
2. **Configuration Form** — Enable/disable, credentials, trigger options, threshold
3. **Actions** — Save and Send Test Message buttons

## Edge Cases

| Scenario | Behavior |
|---|---|
| First startup (no previous balance) | Record initial balance, skip notification |
| Wallet not synced | Skip notification (balance unreliable) |
| Rapid duplicate updates | In-memory dedup via `_last_notified` dict |
| Telegram API unreachable | Log error, do not block wallet update |
| Change below threshold | Skip notification |
| Notification failure | Caught by try/except, never blocks wallet POST |

## Dependencies

- **Existing**: `common/utils/fiat.py` for fiat conversion (supports AUD via CoinGecko)
- **Existing**: `api/schedules/status_wallets.py` for wallet polling (~2 min interval)
- **External**: Telegram Bot API (`https://api.telegram.org/bot{token}/sendMessage`)
- **Library**: `requests` (already in project dependencies)
