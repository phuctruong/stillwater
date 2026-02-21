#!/usr/bin/env bash
# Stillwater LLM Portal — Restart Script
# Auth: 65537 | Port: 8788
# Usage: bash admin/restart-llm-portal.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Restarting LLM Portal..."
bash "$SCRIPT_DIR/stop-llm-portal.sh" || true
sleep 1
bash "$SCRIPT_DIR/start-llm-portal.sh" "$@"
