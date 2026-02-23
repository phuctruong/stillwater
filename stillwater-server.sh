#!/usr/bin/env bash
# stillwater-server.sh — start|stop|restart|status|tail|log|test|session
# Manages the Stillwater Admin Backend (FastAPI + OAuth3)
#
# This is a webservice-first architecture for:
#  - Data access (identity, preferences, orchestration, facts, jokes, wishes)
#  - Firebase authentication
#  - API key management
#  - Cloud sync (optional Firestore integration)
#
# The admin backend runs FastAPI with optional Firebase auth.
# Local data comes from data/default and data/custom directories.
#
# This script replaces the three old scripts:
#   - admin/start-llm-portal.sh
#   - admin/stop-llm-portal.sh
#   - admin/restart-llm-portal.sh
#
# Usage:
#   ./stillwater-server.sh start          # Start and open browser
#   ./stillwater-server.sh stop           # Stop the server
#   ./stillwater-server.sh restart        # Restart
#   ./stillwater-server.sh status         # Show running status
#   ./stillwater-server.sh tail           # Monitor logs in real-time
#   ./stillwater-server.sh log            # Show full log
#   ./stillwater-server.sh test           # Run health checks
#   ./stillwater-server.sh help           # Show this help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

# Configuration
PORT="${STILLWATER_ADMIN_PORT:-8000}"
HOST="${STILLWATER_ADMIN_HOST:-127.0.0.1}"
PID_FILE="${HOME}/.stillwater/admin.pid"
LOG_DIR="${HOME}/.stillwater/logs"
LOG_FILE="${LOG_DIR}/admin-$(date +%Y%m%d).log"
URL="http://${HOST}:${PORT}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helpers
# ============================================================================

_log() {
    echo -e "${BLUE}[stillwater-server]${NC} $*"
}

_error() {
    echo -e "${RED}[stillwater-server]${NC} ERROR: $*" >&2
}

_success() {
    echo -e "${GREEN}[stillwater-server]${NC} $*"
}

_warn() {
    echo -e "${YELLOW}[stillwater-server]${NC} WARNING: $*"
}

_pid_running() {
    local pid="$1"
    kill -0 "$pid" 2>/dev/null
}

_read_pid() {
    [[ -f "$PID_FILE" ]] && cat "$PID_FILE" || echo ""
}

_open_browser() {
    sleep 1
    _log "Opening admin UI at $URL"
    if command -v xdg-open &>/dev/null; then
        xdg-open "$URL" &>/dev/null &
    elif command -v open &>/dev/null; then
        open "$URL" &>/dev/null &
    else
        _warn "Could not auto-open browser (no xdg-open or open command)"
    fi
}

_ensure_dirs() {
    mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")" "$(dirname "$LOG_FILE")"
}

# ============================================================================
# Commands
# ============================================================================

cmd_start() {
    local existing_pid
    existing_pid=$(_read_pid)
    if [[ -n "$existing_pid" ]] && _pid_running "$existing_pid"; then
        _log "Already running (pid=$existing_pid) at $URL"
        return 0
    fi

    _ensure_dirs

    _log "Starting admin backend (FastAPI + OAuth3)..."
    _log "Server will listen on: $URL"
    _log "Data directory: $REPO_ROOT/data/"
    _log "Skills directory: $REPO_ROOT/skills/"
    _log "Log file: $LOG_FILE"

    # Set up environment
    export PYTHONPATH="${REPO_ROOT}/cli/src${PYTHONPATH:+:${PYTHONPATH}}"

    # Start the server
    nohup "$PYTHON" -m uvicorn admin.backend.app:app \
        --host "$HOST" \
        --port "$PORT" \
        --app-dir "$REPO_ROOT" \
        --log-level info \
        >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    _success "Started (pid=$pid)"

    # Wait for server to be ready
    sleep 2
    if _pid_running "$pid"; then
        _success "Server is running and ready"
        _open_browser
    else
        _error "Server failed to start. Check logs:"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

cmd_stop() {
    local pid
    pid=$(_read_pid)

    # Kill any existing uvicorn processes on the port
    if command -v lsof &>/dev/null; then
        local port_pid
        port_pid=$(lsof -ti :"$PORT" 2>/dev/null | head -1)
        if [[ -n "$port_pid" ]] && [[ "$port_pid" != "$pid" ]]; then
            _log "Found orphan process on port $PORT (pid=$port_pid), killing..."
            kill -9 "$port_pid" 2>/dev/null || true
        fi
    fi

    if [[ -z "$pid" ]] || ! _pid_running "$pid"; then
        _log "Not running"
        rm -f "$PID_FILE"
        return 0
    fi

    _log "Stopping server (pid=$pid)..."
    kill "$pid" 2>/dev/null || true
    sleep 1

    if _pid_running "$pid"; then
        _warn "Process didn't stop gracefully, killing it..."
        kill -9 "$pid" 2>/dev/null || true
    fi

    # Kill any child processes that may have been orphaned
    pkill -P "$pid" 2>/dev/null || true

    rm -f "$PID_FILE"
    _success "Stopped (pid=$pid)"
}

cmd_restart() {
    _log "Restarting server..."
    cmd_stop
    sleep 1
    cmd_start
}

cmd_status() {
    local pid
    pid=$(_read_pid)
    if [[ -n "$pid" ]] && _pid_running "$pid"; then
        _success "RUNNING (pid=$pid) at $URL"
        # Show additional status info
        if command -v curl &>/dev/null; then
            _log "Checking health endpoint..."
            if curl -s "$URL/health" > /dev/null 2>&1; then
                _success "Health check: PASS"
            else
                _warn "Health check: FAILED (endpoint not responding)"
            fi
        fi
    else
        _log "STOPPED"
        rm -f "$PID_FILE"
    fi
}

cmd_tail() {
    if [[ ! -f "$LOG_FILE" ]]; then
        _error "Log file not found: $LOG_FILE"
        return 1
    fi
    _log "Tailing logs (Ctrl+C to stop)..."
    tail -f "$LOG_FILE"
}

cmd_log() {
    if [[ ! -f "$LOG_FILE" ]]; then
        _error "Log file not found: $LOG_FILE"
        return 1
    fi
    _log "Full log file: $LOG_FILE"
    echo ""
    cat "$LOG_FILE"
}

cmd_test() {
    _log "Running health checks..."
    if ! command -v curl &>/dev/null; then
        _error "curl not installed"
        return 1
    fi

    local pid
    pid=$(_read_pid)
    if [[ -z "$pid" ]] || ! _pid_running "$pid"; then
        _error "Server not running. Start with: $0 start"
        return 1
    fi

    _log "Testing endpoints..."
    echo ""

    # Health check
    _log "GET /health"
    if curl -s "$URL/health" | grep -q "status"; then
        _success "✓ Health check passed"
    else
        _error "✗ Health check failed"
        return 1
    fi
    echo ""

    # Config
    _log "GET /config"
    if curl -s "$URL/config" | grep -q "firebase"; then
        _success "✓ Config endpoint working"
    else
        _error "✗ Config endpoint failed"
        return 1
    fi
    echo ""

    # Data endpoints
    for endpoint in "facts" "jokes" "identity" "preferences" "orchestration"; do
        _log "GET /api/data/$endpoint"
        if curl -s "$URL/api/data/$endpoint" > /dev/null 2>&1; then
            _success "✓ /api/data/$endpoint working"
        else
            _warn "⚠ /api/data/$endpoint failed"
        fi
    done

    echo ""
    _success "All available endpoints tested!"
}

cmd_help() {
    cat << 'EOF'
stillwater-server.sh — Manage the Stillwater Admin Backend

USAGE:
  ./stillwater-server.sh <command>

COMMANDS:
  start          Start admin backend (opens browser)
  stop           Stop admin backend
  restart        Stop and start
  status         Show running status
  tail           Tail logs in real-time
  log            Show full log file
  test           Run health checks
  help           Show this help

ENVIRONMENT VARIABLES:
  STILLWATER_ADMIN_PORT    API port (default: 8000)
  STILLWATER_ADMIN_HOST    API host (default: 127.0.0.1)

EXAMPLES:
  # Start the server
  ./stillwater-server.sh start

  # Check if server is running
  ./stillwater-server.sh status

  # Monitor logs
  ./stillwater-server.sh tail

  # Restart for a clean session
  ./stillwater-server.sh restart

  # Run health checks
  ./stillwater-server.sh test

API ENDPOINTS (when server is running):
  Health/Status:
    GET /health                    Server health
    GET /config                    Firebase configuration

  Data Access:
    GET /api/data/identity         User identity info
    GET /api/data/preferences      User preferences
    GET /api/data/orchestration    Orchestration workflow
    GET /api/data/facts            Interesting facts
    GET /api/data/jokes            Jokes collection
    GET /api/data/wishes           User goals/wishes

  Authentication:
    POST /api/auth/verify-token    Verify Firebase token
    GET /api/auth/user             Get current user
    POST /api/keys/generate        Generate API key
    GET /api/keys/list             List user's API keys

  File Management:
    POST /api/data/jokes           Add joke
    POST /api/data/wishes          Add wish

DEFAULT PORT: 8000
WEB ADDRESS: http://127.0.0.1:8000

For more info, see:
  - NORTHSTAR.md              Project vision
  - TESTING_GUIDE.md          Testing instructions
  - data/README.md            Data structure explanation

ARCHITECTURE:
  Webservice-first design for software 5.0
  - Data: data/default (git-tracked) + data/custom (gitignored overrides)
  - Skills: skills/, recipes/, combos/ (framework files, global)
  - Verification: Rung 641 (local) → 274177 (stable) → 65537 (production)
  - OAuth3-ready for authentication + API key management

EOF
}

# ============================================================================
# Main
# ============================================================================

main() {
    local cmd="${1:-help}"

    case "$cmd" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        tail)
            cmd_tail
            ;;
        log)
            cmd_log
            ;;
        test)
            cmd_test
            ;;
        help|-h|--help)
            cmd_help
            ;;
        *)
            _error "Unknown command: $cmd"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
