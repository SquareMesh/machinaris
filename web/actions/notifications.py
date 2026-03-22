#
# Web actions for notification settings
#

import json
import traceback

from flask_babel import _, lazy_gettext as _l
from flask import flash

from web import app, utils
from web.actions import worker as wk
from common.utils import notifications as notif_utils


def load_config():
    """Load notification config from the controller API."""
    try:
        w = wk.get_fullnode('chia')
        if not w:
            app.logger.error("No fullnode worker found for loading notification config")
            return notif_utils.DEFAULT_CONFIG
        response = utils.send_get(w, "/configs/notifications/chia", debug=False)
        if response.status_code == 200:
            return response.json()
    except Exception as ex:
        app.logger.error("Failed to load notification config: {0}".format(str(ex)))
    return json.loads(json.dumps(notif_utils.DEFAULT_CONFIG))


def save_config(config):
    """Save notification config via the controller API."""
    try:
        w = wk.get_fullnode('chia')
        if not w:
            flash(_('No fullnode worker found. Cannot save notification settings.'), 'danger')
            return
        response = utils.send_put(w, "/configs/notifications/chia", config, debug=False)
        if response.status_code == 200:
            flash(_('Notification settings saved successfully.'), 'success')
        else:
            flash(_('Failed to save notification settings: %(error)s', error=response.text), 'danger')
    except Exception as ex:
        app.logger.error("Failed to save notification config: {0}".format(str(ex)))
        flash(_('Failed to save notification settings. Please check log files.'), 'danger')


def send_test(bot_token, chat_id):
    """Send a test notification via Telegram."""
    message = "*Machinaris Test Notification*\n\nTelegram notifications are working correctly."
    success, error = notif_utils.send_telegram(bot_token, chat_id, message)
    if success:
        flash(_('Test message sent successfully! Check your Telegram.'), 'success')
    else:
        flash(_('Failed to send test message: %(error)s', error=error), 'danger')
