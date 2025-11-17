#!/usr/bin/env bash
# Simple launcher for the Finance Flask backend.
# Ensures the app runs binding to 0.0.0.0:3000 by default.
# Note: Legacy entrypoint 'stock_data/stock_twilio_server.py' is not used anymore.
# This script is idempotent and depends only on HOST/PORT env vars.
set -euo pipefail

# Default bindings if not provided by orchestrator
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-3000}"

echo "[Finance] Starting Flask app with HOST=${HOST} PORT=${PORT}"
echo "[Finance] Health endpoint expected at http://${HOST}:${PORT}/healthz"

# Some orchestrators may not preserve execute bit on checkout; keep script POSIX compliant.
# Exec the Python app so signals are forwarded correctly (PID 1 in containers).
exec python app.py
