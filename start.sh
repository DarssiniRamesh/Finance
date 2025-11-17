#!/usr/bin/env bash
# Simple launcher for the Finance Flask backend.
# Ensures the app runs binding to 0.0.0.0:3000 by default.
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-3000}"

# Exec the Python app so signals are forwarded correctly (PID 1 in containers).
exec python app.py
