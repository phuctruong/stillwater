#!/usr/bin/env bash
# Stillwater LLM Portal — Stop Script
# Auth: 65537 | Port: 8788
# Usage: bash admin/stop-llm-portal.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.llm-portal.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "ℹ️  LLM Portal is not running (no PID file)"
  exit 0
fi

PID="$(cat "$PID_FILE")"

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  # Wait up to 5s for graceful shutdown
  for i in 1 2 3 4 5; do
    sleep 1
    if ! kill -0 "$PID" 2>/dev/null; then
      rm -f "$PID_FILE"
      echo "✅ LLM Portal stopped (PID $PID)"
      exit 0
    fi
  done
  # Force kill if still running
  kill -9 "$PID" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "✅ LLM Portal force-stopped (PID $PID)"
else
  echo "ℹ️  LLM Portal was not running (stale PID $PID)"
  rm -f "$PID_FILE"
fi
