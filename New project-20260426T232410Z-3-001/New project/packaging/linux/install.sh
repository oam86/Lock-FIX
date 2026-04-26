#!/usr/bin/env bash
set -euo pipefail

APP_NAME="lockfix-poc"
INSTALL_DIR="${INSTALL_DIR:-/opt/lockfix-poc}"
SERVICE_NAME="${SERVICE_NAME:-lockfix-poc}"
RUN_USER="${RUN_USER:-${SUDO_USER:-$USER}}"
PORT="${PORT:-8088}"
HOST="${HOST:-0.0.0.0}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run with sudo or as root." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="$SCRIPT_DIR/payload"

if [ ! -d "$PAYLOAD_DIR" ]; then
  echo "payload directory not found: $PAYLOAD_DIR" >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR"
rsync -a --delete "$PAYLOAD_DIR"/ "$INSTALL_DIR"/
mkdir -p "$INSTALL_DIR/runtime"
chown -R "$RUN_USER":"$RUN_USER" "$INSTALL_DIR"

cat >"/etc/systemd/system/${SERVICE_NAME}.service" <<SERVICE
[Unit]
Description=LOCK-FIX PoC Mock Web UI
After=network.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/webui.py --host ${HOST} --port ${PORT} --config ${INSTALL_DIR}/config/lockfix.example.json
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo "Installed ${APP_NAME} to ${INSTALL_DIR}"
echo "Start service: sudo systemctl start ${SERVICE_NAME}"
echo "Check status:  sudo systemctl status ${SERVICE_NAME}"
echo "Open UI:       http://<server-ip>:${PORT}"
