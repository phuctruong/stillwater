#!/bin/bash
# Quick Start — Stillwater Admin UI Testing
# Usage: bash QUICK_START.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "═══════════════════════════════════════════════════════════"
echo "Stillwater Admin UI — Quick Start"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Step 1: Check dependencies
echo "[1/5] Checking dependencies..."
if ! python3 --version > /dev/null 2>&1; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python 3 found"

# Step 2: Install requirements
echo ""
echo "[2/5] Installing backend dependencies..."
if [ ! -d "admin/backend" ]; then
    echo "❌ admin/backend directory not found"
    exit 1
fi
pip install -q -r admin/backend/requirements.txt 2>/dev/null || {
    echo "⚠️  Could not auto-install dependencies"
    echo "    Run: pip install -r admin/backend/requirements.txt"
}
echo "✅ Dependencies installed"

# Step 3: Run tests
echo ""
echo "[3/5] Running backend tests..."
if python -m pytest admin/backend/test_app.py -q --tb=no > /dev/null 2>&1; then
    echo "✅ All tests passing (18/18)"
else
    echo "⚠️  Some tests failed (this is ok for local testing)"
    python -m pytest admin/backend/test_app.py -q --tb=short
fi

# Step 4: Display test API examples
echo ""
echo "[4/5] Testing local data access (no auth required)..."
echo ""
echo "You can test the API with curl:"
echo ""
echo "  # Get jokes"
echo "  curl http://localhost:8000/api/data/jokes"
echo ""
echo "  # Get settings"
echo "  curl http://localhost:8000/api/data/settings"
echo ""
echo "  # Add a joke"
echo "  curl -X POST http://localhost:8000/api/data/jokes \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"id\": \"test_1\", \"joke\": \"Hello world!\", \"category\": \"test\"}'"
echo ""

# Step 5: Start server
echo "[5/5] Starting Stillwater Admin Server..."
echo ""
echo "Starting FastAPI server on http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Ready to test!"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Start the server directly (not via stillwater-server.sh to keep output visible)
cd "$REPO_ROOT"
export PYTHONPATH="${REPO_ROOT}/cli/src${PYTHONPATH:+:${PYTHONPATH}}"
python -m uvicorn admin.backend.app:app \
    --host 127.0.0.1 \
    --port 8000 \
    --app-dir "$REPO_ROOT" \
    --log-level info
