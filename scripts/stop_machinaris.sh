#!/usr/bin/env bash
set -eo pipefail
#
# Stops only the Machinaris WebUI and API servers. Leaves other services
# such as Chia, Flax, Chiadog, Plotman, Madmax, etc all running.
#

echo 'Stopping Machinaris WebUI...'
kill "$(pidof 'gunicorn: master [web:app]')" || true
echo 'Stopping Machinaris API...'
kill "$(pidof 'gunicorn: master [api:app]')" || true
