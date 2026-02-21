#!/usr/bin/env bash
# Usage: From repo root: bash admin/start-admin.sh
#        Or: cd admin && bash start-admin.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${STILLWATER_ADMIN_HOST:-127.0.0.1}"
PORT="${STILLWATER_ADMIN_PORT:-8787}"
URL="http://${HOST}:${PORT}"

export PYTHONPATH="${ROOT_DIR}/cli/src${PYTHONPATH:+:${PYTHONPATH}}"

cd "${ROOT_DIR}"
echo "[start-admin] launching Stillwater Admin Dojo on ${URL}"
python admin/server.py --host "${HOST}" --port "${PORT}" &
SERVER_PID=$!
trap 'kill "${SERVER_PID}" >/dev/null 2>&1 || true' EXIT INT TERM

sleep 1
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${URL}" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "${URL}" >/dev/null 2>&1 || true
fi

wait "${SERVER_PID}"
