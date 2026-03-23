"""Add indexes for query performance

Revision ID: b1a2c3d4e5f6
Revises: 6cda05ff2952
Create Date: 2026-03-23 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = '6cda05ff2952'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


# --- Default bind (no-op) ---

def upgrade_():
    pass

def downgrade_():
    pass


# --- Alerts ---

def upgrade_alerts():
    op.create_index(op.f('ix_alerts_hostname'), 'alerts', ['hostname'])
    op.create_index(op.f('ix_alerts_blockchain'), 'alerts', ['blockchain'])
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'])

def downgrade_alerts():
    op.drop_index(op.f('ix_alerts_created_at'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_blockchain'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_hostname'), table_name='alerts')


# --- Challenges ---

def upgrade_challenges():
    op.create_index(op.f('ix_challenges_hostname'), 'challenges', ['hostname'])
    op.create_index(op.f('ix_challenges_blockchain'), 'challenges', ['blockchain'])
    op.create_index(op.f('ix_challenges_created_at'), 'challenges', ['created_at'])

def downgrade_challenges():
    op.drop_index(op.f('ix_challenges_created_at'), table_name='challenges')
    op.drop_index(op.f('ix_challenges_blockchain'), table_name='challenges')
    op.drop_index(op.f('ix_challenges_hostname'), table_name='challenges')


# --- Partials ---

def upgrade_partials():
    op.create_index(op.f('ix_partials_hostname'), 'partials', ['hostname'])
    op.create_index(op.f('ix_partials_blockchain'), 'partials', ['blockchain'])
    op.create_index(op.f('ix_partials_created_at'), 'partials', ['created_at'])

def downgrade_partials():
    op.drop_index(op.f('ix_partials_created_at'), table_name='partials')
    op.drop_index(op.f('ix_partials_blockchain'), table_name='partials')
    op.drop_index(op.f('ix_partials_hostname'), table_name='partials')


# --- Plots ---

def upgrade_plots():
    op.create_index(op.f('ix_plots_blockchain'), 'plots', ['blockchain'])
    op.create_index(op.f('ix_plots_created_at'), 'plots', ['created_at'])

def downgrade_plots():
    op.drop_index(op.f('ix_plots_created_at'), table_name='plots')
    op.drop_index(op.f('ix_plots_blockchain'), table_name='plots')


# --- Stat tables with blockchain column ---

def _upgrade_stat_blockchain(table):
    op.create_index(op.f('ix_%s_hostname' % table), table, ['hostname'])
    op.create_index(op.f('ix_%s_blockchain' % table), table, ['blockchain'])
    op.create_index(op.f('ix_%s_created_at' % table), table, ['created_at'])

def _downgrade_stat_blockchain(table):
    op.drop_index(op.f('ix_%s_created_at' % table), table_name=table)
    op.drop_index(op.f('ix_%s_blockchain' % table), table_name=table)
    op.drop_index(op.f('ix_%s_hostname' % table), table_name=table)

def _upgrade_stat_path(table):
    op.create_index(op.f('ix_%s_hostname' % table), table, ['hostname'])
    op.create_index(op.f('ix_%s_created_at' % table), table, ['created_at'])

def _downgrade_stat_path(table):
    op.drop_index(op.f('ix_%s_created_at' % table), table_name=table)
    op.drop_index(op.f('ix_%s_hostname' % table), table_name=table)


def upgrade_stat_plot_count():
    _upgrade_stat_blockchain('stat_plot_count')

def downgrade_stat_plot_count():
    _downgrade_stat_blockchain('stat_plot_count')

def upgrade_stat_plots_size():
    _upgrade_stat_blockchain('stat_plots_size')

def downgrade_stat_plots_size():
    _downgrade_stat_blockchain('stat_plots_size')

def upgrade_stat_total_coins():
    _upgrade_stat_blockchain('stat_total_coins')

def downgrade_stat_total_coins():
    _downgrade_stat_blockchain('stat_total_coins')

def upgrade_stat_netspace_size():
    _upgrade_stat_blockchain('stat_netspace_size')

def downgrade_stat_netspace_size():
    _downgrade_stat_blockchain('stat_netspace_size')

def upgrade_stat_time_to_win():
    _upgrade_stat_blockchain('stat_time_to_win')

def downgrade_stat_time_to_win():
    _downgrade_stat_blockchain('stat_time_to_win')

def upgrade_stat_effort():
    _upgrade_stat_blockchain('stat_effort')

def downgrade_stat_effort():
    _downgrade_stat_blockchain('stat_effort')

def upgrade_stat_plots_total_used():
    _upgrade_stat_blockchain('stat_plots_total_used')

def downgrade_stat_plots_total_used():
    _downgrade_stat_blockchain('stat_plots_total_used')

def upgrade_stat_plotting_total_used():
    _upgrade_stat_blockchain('stat_plotting_total_used')

def downgrade_stat_plotting_total_used():
    _downgrade_stat_blockchain('stat_plotting_total_used')

def upgrade_stat_farmed_blocks():
    _upgrade_stat_blockchain('stat_farmed_blocks')

def downgrade_stat_farmed_blocks():
    _downgrade_stat_blockchain('stat_farmed_blocks')

def upgrade_stat_wallet_balances():
    _upgrade_stat_blockchain('stat_wallet_balances')

def downgrade_stat_wallet_balances():
    _downgrade_stat_blockchain('stat_wallet_balances')

def upgrade_stat_container_mem_gib():
    _upgrade_stat_blockchain('stat_container_mem_gib')

def downgrade_stat_container_mem_gib():
    _downgrade_stat_blockchain('stat_container_mem_gib')


# --- Stat tables with path column (no blockchain) ---

def upgrade_stat_plots_disk_used():
    _upgrade_stat_path('stat_plots_disk_used')

def downgrade_stat_plots_disk_used():
    _downgrade_stat_path('stat_plots_disk_used')

def upgrade_stat_plots_disk_free():
    _upgrade_stat_path('stat_plots_disk_free')

def downgrade_stat_plots_disk_free():
    _downgrade_stat_path('stat_plots_disk_free')

def upgrade_stat_plotting_disk_used():
    _upgrade_stat_path('stat_plotting_disk_used')

def downgrade_stat_plotting_disk_used():
    _downgrade_stat_path('stat_plotting_disk_used')

def upgrade_stat_plotting_disk_free():
    _upgrade_stat_path('stat_plotting_disk_free')

def downgrade_stat_plotting_disk_free():
    _downgrade_stat_path('stat_plotting_disk_free')


# --- Stat tables without blockchain or path ---

def upgrade_stat_total_balance():
    op.create_index(op.f('ix_stat_total_balance_hostname'), 'stat_total_balance', ['hostname'])
    op.create_index(op.f('ix_stat_total_balance_created_at'), 'stat_total_balance', ['created_at'])

def downgrade_stat_total_balance():
    op.drop_index(op.f('ix_stat_total_balance_created_at'), table_name='stat_total_balance')
    op.drop_index(op.f('ix_stat_total_balance_hostname'), table_name='stat_total_balance')

def upgrade_stat_host_mem_pct():
    op.create_index(op.f('ix_stat_host_mem_pct_hostname'), 'stat_host_mem_pct', ['hostname'])
    op.create_index(op.f('ix_stat_host_mem_pct_created_at'), 'stat_host_mem_pct', ['created_at'])

def downgrade_stat_host_mem_pct():
    op.drop_index(op.f('ix_stat_host_mem_pct_created_at'), table_name='stat_host_mem_pct')
    op.drop_index(op.f('ix_stat_host_mem_pct_hostname'), table_name='stat_host_mem_pct')


# --- Tables that don't need index changes (composite PKs cover queries) ---

def upgrade_blockchains():
    pass

def downgrade_blockchains():
    pass

def upgrade_connections():
    pass

def downgrade_connections():
    pass

def upgrade_drives():
    pass

def downgrade_drives():
    pass

def upgrade_farms():
    pass

def downgrade_farms():
    pass

def upgrade_keys():
    pass

def downgrade_keys():
    pass

def upgrade_plotnfts():
    pass

def downgrade_plotnfts():
    pass

def upgrade_plottings():
    pass

def downgrade_plottings():
    pass

def upgrade_pools():
    pass

def downgrade_pools():
    pass

def upgrade_wallets():
    pass

def downgrade_wallets():
    pass

def upgrade_workers():
    pass

def downgrade_workers():
    pass

def upgrade_warnings():
    pass

def downgrade_warnings():
    pass

def upgrade_transfers():
    pass

def downgrade_transfers():
    pass
