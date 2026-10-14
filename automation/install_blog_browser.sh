#!/usr/bin/env bash
# Only dependency installation is retried; native blog submissions are never retried here.
set -euo pipefail
python -m pip install --quiet playwright
# GitHub runner IPv6 can be unroutable while Ubuntu/Microsoft repositories work over IPv4.
# Preserve repository signature/security validation and all configured sources.
printf 'Acquire::ForceIPv4 "true";\n' | sudo tee /etc/apt/apt.conf.d/99afp-force-ipv4 >/dev/null
for attempt in 1 2 3; do
  if python -m playwright install --with-deps chromium; then exit 0; fi
  if [ "$attempt" = 3 ]; then echo 'Browser dependency installation failed after three bounded attempts.' >&2; exit 1; fi
  sleep 15
done
