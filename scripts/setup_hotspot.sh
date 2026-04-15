#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   sudo bash scripts/setup_hotspot.sh [SSID] [PASSWORD] [WIFI_INTERFACE]
# Example:
#   sudo bash scripts/setup_hotspot.sh JetsonCamNet Jetson1234 wlan0

SSID="${1:-JetsonCamNet}"
PASSWORD="${2:-Jetson1234}"
WIFI_IFACE="${3:-wlan0}"
CON_NAME="jetson-hotspot"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash scripts/setup_hotspot.sh"
  exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
  echo "nmcli not found. Install NetworkManager first."
  exit 1
fi

if [ "${#PASSWORD}" -lt 8 ]; then
  echo "Password must be at least 8 characters."
  exit 1
fi

if ! nmcli -t -f DEVICE,TYPE device status | grep -q "^${WIFI_IFACE}:wifi$"; then
  echo "WiFi interface ${WIFI_IFACE} not found."
  echo "Available interfaces:"
  nmcli -t -f DEVICE,TYPE device status | grep ':wifi$' || true
  exit 1
fi

# If old hotspot profile exists, update it. Otherwise create a new one.
if nmcli -t -f NAME connection show | grep -qx "${CON_NAME}"; then
  nmcli connection modify "${CON_NAME}" connection.interface-name "${WIFI_IFACE}"
  nmcli connection modify "${CON_NAME}" 802-11-wireless.ssid "${SSID}"
else
  nmcli connection add type wifi ifname "${WIFI_IFACE}" con-name "${CON_NAME}" ssid "${SSID}"
fi

nmcli connection modify "${CON_NAME}" \
  connection.autoconnect yes \
  connection.autoconnect-priority 100 \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  ipv4.method shared \
  ipv6.method ignore

nmcli connection modify "${CON_NAME}" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "${PASSWORD}"

# Bring AP up now.
nmcli connection up "${CON_NAME}"

# Best-effort read of AP IPv4 address.
AP_IP="$(nmcli -g IP4.ADDRESS connection show "${CON_NAME}" | head -n 1 | cut -d/ -f1 || true)"
if [ -z "${AP_IP}" ]; then
  AP_IP="10.42.0.1"
fi

echo "Hotspot is ready."
echo "SSID: ${SSID}"
echo "Password: ${PASSWORD}"
echo "Interface: ${WIFI_IFACE}"
echo "Jetson AP IP: ${AP_IP}"
echo "Open dashboard: http://${AP_IP}:8501"
echo "Open stream:    http://${AP_IP}:5000/video"
