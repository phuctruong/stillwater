#!/usr/bin/env bash
# stillwater-server.sh — start|stop|restart|tail|log|status
# Manages the Stillwater Admin Backend (port 8000)
# Usage: ./stillwater-server.sh <command>
#
# This script replaces the three old scripts:
#   - admin/start-llm-portal.sh
#   - admin/stop-llm-portal.sh
#   - admin/restart-llm-portal.sh
#
# The admin backend runs FastAPI with no authentication required by default.
# Firebase auth is available for optional cloud sync features.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${STILLWATER_ADMIN_PORT:-8000}"
HOST="${STILLWATER_ADMIN_HOST:-127.0.0.1}"
PID_FILE="${HOME}/.stillwater/admin.pid"
LOG_DIR="${HOME}/.stillwater/logs"
LOG_FILE="${LOG_DIR}/admin-$(date +%Y%m%d).log"
URL="http://${HOST}:${PORT}"

# -- helpers -----------------------------------------------------------------

_pid_running() {
    local pid="$1"
    kill -0 "$pid" 2>/dev/null
}

_read_pid() {
    [[ -f "$PID_FILE" ]] && cat "$PID_FILE" || echo ""
}

_open_browser() {
    sleep 1
    if command -v xdg-open &>/dev/null; then
        xdg-open "$URL" &>/dev/null &
    elif command -v open &>/dev/null; then
        open "$URL" &>/dev/null &
    fi
}

# -- commands ----------------------------------------------------------------

cmd_start() {
    local existing_pid
    existing_pid=$(_read_pid)
    if [[ -n "$existing_pid" ]] && _pid_running "$existing_pid"; then
        echo "[stillwater-server] already running (pid=$existing_pid) at $URL"
        return 0
    fi

    mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")"

    export PYTHONPATH="${REPO_ROOT}/cli/src${PYTHONPATH:+:${PYTHONPATH}}"

    echo "[stillwater-server] starting admin backend on $URL"
    nohup python -m uvicorn admin.backend.app:app \
        --host "$HOST" \
        --port "$PORT" \
        --app-dir "$REPO_ROOT" \
        --log-level info \
        >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo "[stillwater-server] started (pid=$pid) — log: $LOG_FILE"

    _open_browser
}

cmd_stop() {
    local pid
    pid=$(_read_pid)
    if [[ -z "$pid" ]] || ! _pid_running "$pid"; then
        echo "[stillwater-server] not running"
        rm -f "$PID_FILE"
        return 0
    fi
    kill "$pid"
    rm -f "$PID_FILE"
    echo "[stillwater-server] stopped (pid=$pid)"
}

cmd_restart() {
    cmd_stop
    sleep 1
    cmd_start
}

cmd_status() {
    local pid
    pid=$(_read_pid)
    if [[ -n "$pid" ]] && _pid_running "$pid"; then
        echo "[stillwater-server] RUNNING (pid=$pid) at $URL"
    else
        echo "[stillwater-server] STOPPED"
        rm -f "$PID_FILE"
    fi
}

cmd_tail() {
    tail -f "${LOG_DIR}/admin-$(date +%Y%m%d).log" 2>/dev/null || \
        echo "[stillwater-server] no log file today: $LOG_FILE"
}

cmd_log() {
    cat "${LOG_DIR}/admin-$(date +%Y%m%d).log" 2>/dev/null || \
        echo "[stillwater-server] no log file today: $LOG_FILE"
}

# -- dispatch ----------------------------------------------------------------

case "${1:-help}" in
    start)   cmd_start   ;;
    stop)    cmd_stop    ;;
    restart) cmd_restart ;;
    status)  cmd_status  ;;
    tail)    cmd_tail    ;;
    log)     cmd_log     ;;
    *)
        echo "Usage: ./stillwater-server.sh {start|stop|restart|status|tail|log}"
        exit 1
        ;;
esac
