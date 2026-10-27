#!/usr/bin/env bash
# Only dependency installation is retried; native blog submissions are never retried here.
set -euo pipefail
browser="${1:-chromium}"
case "$browser" in chromium|firefox) ;; *) echo "Unsupported browser engine" >&2; exit 2;; esac
python -m pip install --quiet playwright
# GitHub runner IPv6 can be unroutable while Ubuntu/Microsoft repositories work over IPv4.
# Preserve repository signature/security validation and all configured sources.
printf 'Acquire::ForceIPv4 "true";\n' | sudo tee /etc/apt/apt.conf.d/99afp-force-ipv4 >/dev/null
# GitHub-hosted Ubuntu runners already provide the system libraries needed by Chromium.
# Prefer the browser-only download to avoid a large, failure-prone apt transaction;
# retain --with-deps as a bounded fallback for self-hosted runners.
if command -v google-chrome-stable >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
  install_args=("$browser")
else
  install_args=(--with-deps "$browser")
fi
for attempt in 1 2 3; do
  if timeout --foreground --kill-after=30s 240s python -m playwright install "${install_args[@]}"; then exit 0; fi
  if [ "$attempt" = 3 ]; then echo 'Browser dependency installation failed after three bounded attempts.' >&2; exit 1; fi
  sleep 15
done
