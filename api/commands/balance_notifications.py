#
# Balance change detection and Telegram notification dispatch
#

import locale
import traceback

from api import app
from common.utils import fiat, notifications

# In-memory dedup: tracks last notified balance per hostname:blockchain
_last_notified = {}


def check_and_notify(blockchain, hostname, old_details, new_details, cold_balance=None):
    """Compare old vs new wallet balance and send Telegram notification if changed.

    Called from Wallets.post() after upsert. Must never raise — all exceptions are caught.
    """
    try:
        config = notifications.load_config()
        telegram = config.get('telegram', {})
        if not telegram.get('enabled'):
            return
        if not telegram.get('bot_token') or not telegram.get('chat_id'):
            return

        # Skip first insert (no previous balance to compare)
        if old_details is None:
            new_balance = notifications.parse_chia_balance(new_details)
            cold = _parse_cold(cold_balance, telegram)
            _last_notified[_key(hostname, blockchain)] = new_balance + cold
            app.logger.info("Balance notifications: initial balance recorded for {0}/{1}: {2} XCH".format(
                hostname, blockchain, new_balance + cold))
            return

        # Skip if wallet is not synced (balance may be inaccurate)
        if not notifications.is_wallet_synced(new_details):
            return

        new_balance = notifications.parse_chia_balance(new_details)
        old_balance = notifications.parse_chia_balance(old_details)

        cold = _parse_cold(cold_balance, telegram)

        new_total = new_balance + cold
        old_total = old_balance + cold

        # Check against last notified balance for dedup
        key = _key(hostname, blockchain)
        if key in _last_notified and abs(_last_notified[key] - new_total) < 1e-12:
            return

        diff = new_total - old_total
        if abs(diff) < 1e-12:
            # No change
            _last_notified[key] = new_total
            return

        # Check threshold
        threshold = telegram.get('min_change_threshold', 0.0)
        if abs(diff) < threshold:
            _last_notified[key] = new_total
            return

        # Check direction
        if diff > 0 and not telegram.get('notify_on_increase', True):
            _last_notified[key] = new_total
            return
        if diff < 0 and not telegram.get('notify_on_decrease', False):
            _last_notified[key] = new_total
            return

        # Format and send
        message = _format_message(diff, new_total, blockchain, hostname)
        success, error = notifications.send_telegram(
            telegram['bot_token'], telegram['chat_id'], message)

        if success:
            app.logger.info("Balance notification sent: {0:+f} XCH for {1}/{2}".format(
                diff, hostname, blockchain))
        else:
            app.logger.error("Failed to send balance notification: {0}".format(error))

        _last_notified[key] = new_total

    except Exception as ex:
        app.logger.error("Balance notification error: {0}".format(str(ex)))
        app.logger.error(traceback.format_exc())


def _key(hostname, blockchain):
    return "{0}:{1}".format(hostname, blockchain)


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
