#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/lockfix-poc}"
SERVICE_NAME="${SERVICE_NAME:-lockfix-poc}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run with sudo or as root." >&2
  exit 1
fi

systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload

echo "Service removed."
echo "Application files remain at ${INSTALL_DIR}"
echo "Remove them manually after backup if needed."
