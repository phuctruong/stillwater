#!/usr/bin/env bash
# Stillwater LLM Portal — Status Script
# Auth: 65537 | Port: 8788
# Usage: bash admin/llm-portal-status.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.llm-portal.pid"
LOG_FILE="$SCRIPT_DIR/.llm-portal.log"
PORT="${LLM_PORTAL_PORT:-8788}"

echo ""
echo "============================================================"
echo "  Stillwater LLM Portal — Status"
echo "============================================================"

# Process status
if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    echo "  Process:  ✅ Running (PID $PID)"
    echo "  URL:      http://localhost:$PORT"
  else
    echo "  Process:  ❌ Dead (stale PID $PID)"
  fi
else
  echo "  Process:  ⏹  Not running"
fi

# HTTP health check
if curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
  HEALTH="$(curl -sf "http://localhost:$PORT/api/health" 2>/dev/null)"
  ACTIVE="$(echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_provider','?'))" 2>/dev/null || echo '?')"
  echo "  HTTP:     ✅ Responding (active provider: $ACTIVE)"
else
  echo "  HTTP:     ❌ Not responding on port $PORT"
fi

# Log file
if [[ -f "$LOG_FILE" ]]; then
  SIZE="$(wc -c < "$LOG_FILE")"
  echo "  Log:      $LOG_FILE ($SIZE bytes)"
  echo ""
  echo "  --- Last 20 log lines ---"
  tail -20 "$LOG_FILE" 2>/dev/null | sed 's/^/  /'
else
  echo "  Log:      (not found)"
fi

echo "============================================================"
echo "  Commands:"
echo "    Start:   bash $SCRIPT_DIR/start-llm-portal.sh"
echo "    Stop:    bash $SCRIPT_DIR/stop-llm-portal.sh"
echo "    Restart: bash $SCRIPT_DIR/restart-llm-portal.sh"
echo "    Dev:     bash $SCRIPT_DIR/start-llm-portal.sh --dev"
echo "============================================================"
