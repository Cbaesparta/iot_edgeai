#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
JETSON_USER="${SUDO_USER:-$USER}"
SERVICE_DIR="/etc/systemd/system"

BACKEND_TEMPLATE="${PROJECT_DIR}/deployment/systemd/jetson-ai-backend.service"
DASH_TEMPLATE="${PROJECT_DIR}/deployment/systemd/jetson-ai-dashboard.service"
BACKEND_OUT="${SERVICE_DIR}/jetson-ai-backend.service"
DASH_OUT="${SERVICE_DIR}/jetson-ai-dashboard.service"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run with sudo: sudo bash scripts/install_autostart.sh"
  exit 1
fi

if ! command -v mosquitto >/dev/null 2>&1; then
  echo "mosquitto not found. Install it first: sudo apt install -y mosquitto mosquitto-clients"
  exit 1
fi

chmod +x "${PROJECT_DIR}/scripts/wait_for_camera.sh"

sed -e "s|__JETSON_USER__|${JETSON_USER}|g" -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" "${BACKEND_TEMPLATE}" > "${BACKEND_OUT}"
sed -e "s|__JETSON_USER__|${JETSON_USER}|g" -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" "${DASH_TEMPLATE}" > "${DASH_OUT}"

systemctl daemon-reload
systemctl enable mosquitto
systemctl enable jetson-ai-backend.service
systemctl enable jetson-ai-dashboard.service
systemctl restart mosquitto
systemctl restart jetson-ai-backend.service
systemctl restart jetson-ai-dashboard.service

echo "Installed and started services:"
systemctl --no-pager --full status jetson-ai-backend.service | sed -n '1,12p'
systemctl --no-pager --full status jetson-ai-dashboard.service | sed -n '1,12p'

echo "Done. System will auto-start backend + dashboard on every boot without login."
