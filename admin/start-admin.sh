#!/usr/bin/env bash
# Usage: From repo root: bash admin/start-admin.sh
# Delegates to the unified server manager to avoid split startup paths.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT_DIR}/stillwater-server.sh" start
