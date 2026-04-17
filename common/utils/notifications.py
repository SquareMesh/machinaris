#
# Telegram notification utilities for wallet balance changes
#

import json
import locale
import os
import re
import socket
import traceback

import requests

NOTIFICATIONS_CONFIG = '/root/.chia/machinaris/config/notifications.json'

DEFAULT_CONFIG = {
    "telegram": {
        "enabled": False,
        "bot_token": "",
        "chat_id": "",
        "notify_on_increase": True,
        "notify_on_decrease": False,
        "min_change_threshold": 0.0,
        "include_cold_wallet": True
    },
    "plot_health": {
        "enabled": True,
        "decrease_pct_threshold": 5,
        "alert_on_empty_dir": True
    }
}


def load_config():
    """Load notification config from JSON file, returning defaults for missing fields."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy defaults
    if os.path.exists(NOTIFICATIONS_CONFIG):
        try:
            with open(NOTIFICATIONS_CONFIG) as f:
                saved = json.load(f)
                if 'telegram' in saved:
                    config['telegram'].update(saved['telegram'])
                if 'plot_health' in saved:
                    config['plot_health'].update(saved['plot_health'])
        except Exception as ex:
            print("Unable to read notifications config from {0}: {1}".format(
                NOTIFICATIONS_CONFIG, str(ex)))
    return config


def save_config(config):
    """Validate and save notification config to JSON file."""
    os.makedirs(os.path.dirname(NOTIFICATIONS_CONFIG), exist_ok=True)
    with open(NOTIFICATIONS_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)


def send_telegram(bot_token, chat_id, message):
    """Send a message via Telegram Bot API. Returns (success, error_message)."""
    try:
        resp = requests.post(
            "https://api.telegram.org/bot{0}/sendMessage".format(bot_token),
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        if resp.status_code == 200:
            return True, None
        else:
            error = resp.json().get('description', resp.text)
            return False, error
    except Exception as ex:
        return False, str(ex)


def parse_chia_balance(details_text):
    """Parse total XCH balance from Chia wallet CLI output text.

    Excludes CAT, DISTRIBUTED_ID, DECENTRALIZED_ID, and NFT wallet types.
    Returns float balance or 0.0 if parsing fails.
    """
    if not details_text:
        return 0.0
    try:
        # Filter out non-standard wallet types
        filtered = _exclude_special_wallets(details_text)
        numeric_const_pattern = r'-Total\sBalance:\s+((?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ )?)'
        rx = re.compile(numeric_const_pattern, re.VERBOSE)
        total = 0.0
        for balance in rx.findall(filtered):
            try:
                total += locale.atof(balance)
            except ValueError:
                total += float(balance)
        return total
    except Exception as ex:
        print("Failed to parse chia balance: {0}".format(str(ex)))
        return 0.0


def is_wallet_synced(details_text):
    """Check if wallet is synced from CLI output text."""
    if not details_text:
        return False
    return bool(re.search(r'Sync status:\s*Synced', details_text))


def get_hostname():
    """Return the current hostname for notification messages."""
    try:
        return socket.gethostname()
    except Exception:
        return 'machinaris'


def _exclude_special_wallets(wallet_details):
    """Filter out CAT, NFT, and DID wallet types from details text."""
    details = []
    chunks = wallet_details.split('\n\n')
    for chunk in chunks:
        exclude_wallet = False
        lines = chunk.split('\n')
        for line in lines:
            if re.match(r'^\s+-Type:\s+CAT$', line) or \
               re.match(r'^\s+-Type:\s+DISTRIBUTED_ID$', line) or \
               re.match(r'^\s+-Type:\s+DECENTRALIZED_ID$', line) or \
               re.match(r'^\s+-Type:\s+NFT$', line):
                exclude_wallet = True
        if not exclude_wallet:
            details.extend(chunk.split('\n'))
    return '\n'.join(details)
