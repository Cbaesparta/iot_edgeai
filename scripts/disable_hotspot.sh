#!/usr/bin/env bash
set -euo pipefail

CON_NAME="jetson-hotspot"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash scripts/disable_hotspot.sh"
  exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
  echo "nmcli not found."
  exit 1
fi

if nmcli -t -f NAME connection show | grep -qx "${CON_NAME}"; then
  nmcli connection down "${CON_NAME}" || true
  nmcli connection modify "${CON_NAME}" connection.autoconnect no
  echo "Hotspot disabled (autoconnect off)."
else
  echo "No hotspot profile named ${CON_NAME} found."
fi
