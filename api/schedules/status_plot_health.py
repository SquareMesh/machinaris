#
# Plot directory health monitor. Compares on-disk plot counts per
# directory against the last-known baseline and sends a Telegram alert
# when a directory drops plots or goes empty.
#

import json
import os
import traceback

from api import app
from common.utils import notifications, plot_counter

_STATE_FILE = '/root/.chia/machinaris/config/plot_health_state.json'


def update():
    """Scheduler entry: scan plot dirs, alert on meaningful drops, persist state."""
    try:
        config = notifications.load_config()
        telegram = config.get('telegram', {})
        plot_health = config.get('plot_health', {})

        if not plot_health.get('enabled', True):
            return
        if not telegram.get('enabled'):
            return
        if not telegram.get('bot_token') or not telegram.get('chat_id'):
            return

        plot_dirs = plot_counter.plot_dirs_from_env()
        if not plot_dirs:
            return

        _, _, current = plot_counter.count_plot_files(plot_dirs)
        previous = _load_state()

        # First observation for this container run / persisted state.
        # Record baseline silently; never alert on the first cycle.
        if not previous:
            _save_state({d: v['count'] for d, v in current.items()})
            app.logger.info(
                "plot_health: recorded initial baseline %s",
                {d: v['count'] for d, v in current.items()},
            )
            return

        drops = _detect_drops(previous, current, plot_health)

        # Always update state (even if no alerts) so transient hiccups
        # don't cause repeat alerts once they heal.
        _save_state({d: v['count'] for d, v in current.items()})

        if not drops:
            return

        message = _format_message(previous, current, drops)
        success, error = notifications.send_telegram(
            telegram['bot_token'], telegram['chat_id'], message)
        if success:
            app.logger.info("plot_health: alert sent, drops=%s", drops)
        else:
            app.logger.error("plot_health: failed to send alert: %s", error)

    except Exception as ex:
        app.logger.error("plot_health: unexpected error: %s", str(ex))
        app.logger.error(traceback.format_exc())


def _detect_drops(previous, current, plot_health):
    """Return a list of (dir, prev_count, curr_count, reason) for alert-worthy changes."""
    threshold_pct = float(plot_health.get('decrease_pct_threshold', 5))
    alert_on_empty = plot_health.get('alert_on_empty_dir', True)
    drops = []
    for d, info in current.items():
        curr = info['count']
        prev = previous.get(d)
        if prev is None:
            # New directory appeared — record silently next cycle.
            continue
        if prev > 0 and curr == 0 and alert_on_empty:
            drops.append((d, prev, curr, 'DIR EMPTY'))
        elif prev > 0 and curr < prev * (1.0 - threshold_pct / 100.0):
            drops.append((d, prev, curr, 'DIR DROP'))
    return drops


def _format_message(previous, current, drops):
    """Build the Telegram alert body."""
    hostname = notifications.get_hostname()
    prev_total = sum(previous.get(d, 0) for d in current.keys())
    curr_total = sum(info['count'] for info in current.values())
    diff = curr_total - prev_total

    lines = []
    lines.append("\u26a0\ufe0f Machinaris plot health alert on {0}".format(hostname))
    lines.append("")
    lines.append("Total on disk: {0} \u2192 {1} plots ({2:+d})".format(prev_total, curr_total, diff))
    lines.append("")
    lines.append("Per directory:")
    drop_dirs = {d for d, _, _, _ in drops}
    for d in sorted(current.keys()):
        prev = previous.get(d, 0)
        curr = current[d]['count']
        marker = ''
        for dd, _, _, reason in drops:
            if dd == d:
                marker = ' ({0})'.format(reason)
                break
        lines.append("  {0}: {1} \u2192 {2} plots{3}".format(d, prev, curr, marker))
    lines.append("")
    lines.append("Check your plot mounts.")
    return '\n'.join(lines)


def _load_state():
    if not os.path.exists(_STATE_FILE):
        return {}
    try:
        with open(_STATE_FILE) as f:
            return json.load(f)
    except Exception as ex:
        app.logger.error("plot_health: unable to load state: %s", str(ex))
        return {}


def _save_state(state):
    try:
        os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
        with open(_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as ex:
        app.logger.error("plot_health: unable to save state: %s", str(ex))
