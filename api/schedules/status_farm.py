#
# Performs a REST call to controller (possibly localhost) of latest farm status.
#

import os
import traceback

from flask import g

from common.config import globals
from common.utils import converters, plot_counter
from api import app
from api.commands import chia_cli, mmx_cli
from api import utils

# On initialization Chia outputs 
def safely_gather_plots_size_gibs(plots_size):
    plots_size_gibs = 0
    try:
        plots_size_gibs = converters.str_to_gibs(plots_size)
    except Exception:
        app.logger.info("Unconvertable plots size: {0}  Using zero.".format(plots_size))
        plots_size_gibs = 0
    try:
        float(plots_size_gibs)
    except Exception:
        app.logger.info("Unfloatable plots size: {0}  Using zero.".format(plots_size))
        plots_size_gibs = 0
    return plots_size_gibs

def update():
    if not utils.is_fullnode():
        return # Only fullnodes have farm info, skip on harvesters & plotters.
    with app.app_context():
        hostname = utils.get_hostname()
        blockchain = globals.enabled_blockchains()[0]
        try:
            if blockchain == 'mmx':
                farm_summary = mmx_cli.load_farm_info(blockchain)
            else:
                farm_summary = chia_cli.load_farm_summary(blockchain)
                # Override Chia's cached plot count with a fresh on-disk scan.
                # Chia's plot_cache.dat can report plots that are no longer
                # readable (e.g. a dropped remote mount), which misleads the
                # Summary page. Disk scan is authoritative.
                plot_dirs = plot_counter.plot_dirs_from_env()
                if plot_dirs:
                    verified_count, verified_bytes, per_dir = plot_counter.count_plot_files(plot_dirs)
                    farm_summary.plot_count = verified_count
                    farm_summary.plots_size = converters.gib_to_fmt(verified_bytes / (1024 ** 3))
                    app.logger.info(
                        "Verified plots on disk: %s across %s dirs (%s)",
                        verified_count, len(plot_dirs),
                        {d: v['count'] for d, v in per_dir.items()},
                    )
            payload = {
                "hostname": hostname,
                "blockchain": blockchain,
                "mode": os.environ['mode'],
                "status": "" if not hasattr(farm_summary, 'status') else farm_summary.status,
                "plot_count": farm_summary.plot_count,
                "plots_size": safely_gather_plots_size_gibs(farm_summary.plots_size),
                "total_coins": 0 if not hasattr(farm_summary, 'total_coins') else farm_summary.total_coins,
                "netspace_size": 0 if not hasattr(farm_summary, 'netspace_size') else converters.str_to_gibs(farm_summary.netspace_size),
                "expected_time_to_win": "" if not hasattr(farm_summary, 'time_to_win') else farm_summary.time_to_win,
            }
            utils.send_post('/farms/', payload, debug=False)
        except Exception as ex:
            app.logger.info("Failed to load and send farm summary because {0}".format(str(ex)))
