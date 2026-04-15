#!/usr/bin/env bash
set -euo pipefail

CAMERA_DEV="${1:-/dev/video0}"
TIMEOUT_SEC="${2:-120}"

START_TS="$(date +%s)"

echo "Waiting for camera device: ${CAMERA_DEV} (timeout ${TIMEOUT_SEC}s)"

while true; do
  if [ -e "${CAMERA_DEV}" ]; then
    echo "Camera found: ${CAMERA_DEV}"
    exit 0
  fi

  NOW_TS="$(date +%s)"
  ELAPSED="$((NOW_TS - START_TS))"

  if [ "${ELAPSED}" -ge "${TIMEOUT_SEC}" ]; then
    echo "Timeout waiting for camera ${CAMERA_DEV}" >&2
    exit 1
  fi

  sleep 1
done
