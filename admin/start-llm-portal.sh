#!/usr/bin/env bash
# Stillwater LLM Portal — Start Script
# Auth: 65537 | Port: 8788
# Usage: bash admin/start-llm-portal.sh [--dev]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SCRIPT_DIR/.llm-portal.pid"
LOG_FILE="$SCRIPT_DIR/.llm-portal.log"
PORT="${LLM_PORTAL_PORT:-8788}"
HOST="${LLM_PORTAL_HOST:-0.0.0.0}"
DEV_MODE=false

for arg in "$@"; do
  [[ "$arg" == "--dev" ]] && DEV_MODE=true
done

# Check if already running
if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    echo "✅ LLM Portal already running (PID $PID)"
    echo "   URL:  http://localhost:$PORT"
    echo "   Log:  $LOG_FILE"
    echo "   Stop: bash $SCRIPT_DIR/stop-llm-portal.sh"
    exit 0
  else
    # Stale PID file
    rm -f "$PID_FILE"
  fi
fi

cd "$REPO_ROOT"

# Verify dependencies
python3 -c "import fastapi, uvicorn" 2>/dev/null || {
  echo "❌ Missing dependencies. Run: pip install 'fastapi[standard]' uvicorn httpx"
  exit 1
}

python3 -c "from stillwater.llm_client import llm_call" 2>/dev/null || {
  echo "❌ stillwater.llm_client not importable. Run: pip install -e cli/ --quiet"
  exit 1
}

echo ""
echo "============================================================"
echo "  Stillwater LLM Portal — Starting"
echo "============================================================"

if $DEV_MODE; then
  echo "  Mode:  DEV (auto-reload)"
  echo "  URL:   http://localhost:$PORT"
  echo "  Press Ctrl+C to stop"
  echo "============================================================"
  python3 -m uvicorn admin.llm_portal:app \
    --host "$HOST" --port "$PORT" --reload
else
  # Background mode
  nohup python3 -m uvicorn admin.llm_portal:app \
    --host "$HOST" --port "$PORT" \
    > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"

  # Wait up to 5s for it to start
  for i in 1 2 3 4 5; do
    sleep 1
    if curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
      echo "  ✅ Started (PID $(cat "$PID_FILE"))"
      echo "  URL:  http://localhost:$PORT"
      echo "  Log:  $LOG_FILE"
      echo "  Stop: bash $SCRIPT_DIR/stop-llm-portal.sh"
      echo "============================================================"
      exit 0
    fi
  done

  # Check if process is alive
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "  ⚠️  Process started but health check timed out (may still be starting)"
    echo "  PID:  $(cat "$PID_FILE")"
    echo "  URL:  http://localhost:$PORT"
    echo "  Log:  $LOG_FILE"
  else
    echo "  ❌ Failed to start — check log:"
    tail -20 "$LOG_FILE" 2>/dev/null || echo "  (no log file)"
    rm -f "$PID_FILE"
    exit 1
  fi
  echo "============================================================"
fi
