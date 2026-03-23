#
# Balance change detection and Telegram notification dispatch
#

import json
import os
import traceback

from api import app
from common.utils import fiat, notifications

# File-persisted balance state — survives gunicorn worker restarts
_BALANCE_STATE_FILE = '/root/.chia/machinaris/config/balance_state.json'


def check_and_notify(blockchain, hostname, old_details, new_details, cold_balance=None):
    """Compare new wallet balance against last known balance and send Telegram notification if changed.

    Called from Wallets.post() after upsert. Must never raise — all exceptions are caught.
    """
    try:
        config = notifications.load_config()
        telegram = config.get('telegram', {})
        if not telegram.get('enabled'):
            return
        if not telegram.get('bot_token') or not telegram.get('chat_id'):
            return

        # Skip if wallet is not synced (balance may be inaccurate)
        if not notifications.is_wallet_synced(new_details):
            return

        new_balance = notifications.parse_chia_balance(new_details)
        cold = _parse_cold(cold_balance, telegram)
        new_total = new_balance + cold

        # Load persisted balance state
        key = _key(hostname, blockchain)
        state = _load_state()

        if key not in state:
            # First time seeing this wallet — record balance, don't notify
            state[key] = new_total
            _save_state(state)
            app.logger.info("Balance notifications: initial balance recorded for {0}: {1} XCH".format(
                key, new_total))
            return

        last_known = state[key]
        diff = new_total - last_known

        if abs(diff) < 1e-12:
            # No change from last known balance
            return

        # Check threshold
        threshold = telegram.get('min_change_threshold', 0.0)
        if abs(diff) < threshold:
            state[key] = new_total
            _save_state(state)
            return

        # Check direction
        if diff > 0 and not telegram.get('notify_on_increase', True):
            state[key] = new_total
            _save_state(state)
            return
        if diff < 0 and not telegram.get('notify_on_decrease', False):
            state[key] = new_total
            _save_state(state)
            return

        # Format and send
        message = _format_message(diff, new_total, blockchain, hostname)
        success, error = notifications.send_telegram(
            telegram['bot_token'], telegram['chat_id'], message)

        if success:
            app.logger.info("Balance notification sent: {0:+f} XCH for {1}".format(diff, key))
        else:
            app.logger.error("Failed to send balance notification: {0}".format(error))

        # Always update state after attempting notification (success or fail)
        # to prevent repeated notifications for the same change
        state[key] = new_total
        _save_state(state)

    except Exception as ex:
        app.logger.error("Balance notification error: {0}".format(str(ex)))
        app.logger.error(traceback.format_exc())


def _key(hostname, blockchain):
    return "{0}:{1}".format(hostname, blockchain)


def _load_state():
    """Load persisted balance state from disk."""
    if not os.path.exists(_BALANCE_STATE_FILE):
        return {}
    try:
        with open(_BALANCE_STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state):
    """Persist balance state to disk."""
    try:
        os.makedirs(os.path.dirname(_BALANCE_STATE_FILE), exist_ok=True)
        with open(_BALANCE_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as ex:
        app.logger.error("Failed to save balance state: {0}".format(str(ex)))


def _parse_cold(cold_balance, telegram_config):
    """Parse cold balance string to float if cold wallet tracking is enabled."""
    if not telegram_config.get('include_cold_wallet', True):
        return 0.0
    if cold_balance is None:
        return 0.0
    try:
        if isinstance(cold_balance, str):
            return float(cold_balance.replace(',', ''))
        return float(cold_balance)
    except (ValueError, TypeError):
        return 0.0


def _format_message(diff, new_total, blockchain, hostname):
    """Format the Telegram notification message."""
    if diff > 0:
        direction = "Received"
        sign = "+"
    else:
        direction = "Sent"
        sign = ""

    fiat_value = fiat.to_fiat(blockchain, new_total)
    fiat_line = "Approx Value: {0}".format(fiat_value) if fiat_value else ""

    lines = [
        "*Chia Wallet \u2014 Balance Changed*",
        "",
        "{0}: {1}{2:.6f} XCH".format(direction, sign, diff),
        "New Balance: {0:.6f} XCH".format(new_total),
    ]
    if fiat_line:
        lines.append(fiat_line)
    lines.extend([
        "",
        "Source: {0}".format(hostname),
    ])
    return "\n".join(lines)
