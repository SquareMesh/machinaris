import os

from flask import Blueprint, render_template, request, make_response, abort, current_app, flash
from markupsafe import escape
from flask_babel import _, lazy_gettext as _l
from common.config import globals
from web.actions import worker, chiadog, chia, plotman, notifications
from web.utils import find_selected_worker
import requests

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings/notifications', methods=['GET', 'POST'])
def notifications_settings():
    gc = globals.load()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'test':
            bot_token = request.form.get('bot_token', '').strip()
            chat_id = request.form.get('chat_id', '').strip()
            if not bot_token or not chat_id:
                flash(_('Bot token and chat ID are required to send a test message.'), 'danger')
            else:
                notifications.send_test(bot_token, chat_id)
        else:
            config = {
                "telegram": {
                    "enabled": request.form.get('enabled') == 'on',
                    "bot_token": request.form.get('bot_token', '').strip(),
                    "chat_id": request.form.get('chat_id', '').strip(),
                    "notify_on_increase": request.form.get('notify_on_increase') == 'on',
                    "notify_on_decrease": request.form.get('notify_on_decrease') == 'on',
                    "min_change_threshold": float(request.form.get('min_change_threshold', 0.0) or 0.0),
                    "include_cold_wallet": request.form.get('include_cold_wallet') == 'on',
                }
            }
            notifications.save_config(config)
    config = notifications.load_config()
    return render_template('settings/notifications.html', config=config, global_config=gc)

@settings_bp.route('/settings/network')
def network_settings():
    gc = globals.load()
    api_bind = os.environ.get('api_bind_address', '127.0.0.1')
    api_port = os.environ.get('worker_api_port', '8927')
    web_port = os.environ.get('controller_web_port', '8926')
    plotting_disabled = os.environ.get('plotting_disabled', 'false').lower() == 'true'
    network_info = {
        'api_bind_address': api_bind,
        'api_port': api_port,
        'web_port': web_port,
        'api_local_only': api_bind in ('127.0.0.1', 'localhost'),
        'plotting_disabled': plotting_disabled,
    }
    return render_template('settings/network.html', network=network_info, global_config=gc)

@settings_bp.route('/settings/config', defaults={'path': ''})
@settings_bp.route('/settings/config/<path:path>')
def config(path):
    config_type = request.args.get('type')
    w = worker.get_worker(request.args.get('worker'), request.args.get('blockchain'))
    if not w:
        current_app.logger.info(_l("No worker at %(worker)s for blockchain %(blockchain)s. Please select another blockchain.",
            worker=request.args.get('worker'), blockchain=request.args.get('blockchain')))
        abort(404)
    response = None
    try:
        if config_type == "alerts":
            response = make_response(chiadog.load_config(w, request.args.get('blockchain')), 200)
        elif config_type == "farming":
            response = make_response(chia.load_config(w, request.args.get('blockchain')), 200)
        elif config_type == "plotting":
            [replaced, config] = plotman.load_config(w, request.args.get('blockchain'))
            response = make_response(config, 200)
            response.headers.set('ConfigReplacementsOccurred', replaced)
        elif config_type == "plotting_dirs":
            response = make_response(plotman.load_dirs(w, request.args.get('blockchain')), 200)
        elif config_type == "plotting_schedule":
            response = make_response(plotman.load_schedule(w, request.args.get('blockchain')), 200)
        else:
            abort(400, "Unsupported config type: {0}".format(config_type))
    except requests.exceptions.ConnectionError as ex:
        response = make_response(_("No responding fullnode found for %(blockchain)s. Please check your workers.", blockchain=escape(request.args.get('blockchain'))))
    
    if response:
        response.mimetype = "application/x-yaml"
    return response
