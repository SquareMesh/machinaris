# Warn if non-standard worker_api_port is being used, likely default value they did not override properly
if [[ "${blockchains}"  == "chia" && "${worker_api_port}" != '8927' ]]; then
  echo "Chia worker with non-standard worker_api_port of ${worker_api_port} found.  Did you mean to use 8927?"
fi
