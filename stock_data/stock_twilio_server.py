#!/usr/bin/env python3
"""
Compatibility shim to support legacy startup commands that invoke:
    python stock_data/stock_twilio_server.py

This module forwards to the current Flask app defined in Finance/app.py.
It ensures the server binds to 0.0.0.0:3000 by default, while allowing
HOST and PORT environment variables to override defaults.

Do not place secrets or credentials here. Use environment variables.

Usage:
    python stock_data/stock_twilio_server.py
"""
import os
import signal
import socket
import sys
from contextlib import closing
from typing import Optional

# Robust path handling:
# - When run from Finance working directory: this file lives in Finance/stock_data/,
#   so the container root is its parent directory.
# - When run from repo root via a different shim, that shim will manage its own path.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTAINER_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if CONTAINER_ROOT not in sys.path:
    sys.path.insert(0, CONTAINER_ROOT)

try:
    # Import the Flask app from Finance/app.py (module name is "app" from container root)
    import app as finance_app
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "Failed to import Finance/app.py from legacy shim Finance/stock_data/stock_twilio_server.py"
    ) from exc


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch environment variable with optional default."""
    return os.getenv(key, default)


def _get_host() -> str:
    """Resolve host binding with default '0.0.0.0'."""
    return _get_env("HOST", "0.0.0.0") or "0.0.0.0"


def _get_port() -> int:
    """Resolve port with default 3000, tolerant of malformed values."""
    raw = _get_env("PORT", "3000")
    try:
        return int(raw) if raw is not None else 3000
    except ValueError:
        return 3000


def _install_signal_handlers():
    """
    Install minimal signal handlers to ensure clean exit on SIGTERM/SIGINT.
    """
    def _graceful_exit(signum, frame):  # noqa: ARG001
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os._exit(0)

    signal.signal(signal.SIGTERM, _graceful_exit)
    signal.signal(signal.SIGINT, _graceful_exit)


def _port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if a TCP port appears to be in use on the given host."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


# PUBLIC_INTERFACE
def main():
    """
    Launch the Finance Flask app via the legacy shim.

    Binds to HOST:PORT where:
    - HOST defaults to 0.0.0.0
    - PORT defaults to 3000

    If the port is already in use, prints readiness and exits with code 0.
    """
    _install_signal_handlers()
    app = getattr(finance_app, "app", None)
    if app is None:
        raise RuntimeError("Expected 'app' Flask instance in Finance/app.py was not found.")
    host = _get_host()
    port = _get_port()

    # If something already bound to the port (e.g., orchestrator already launched app), treat as ready.
    # Check localhost and 0.0.0.0 variants to be safe.
    if _port_in_use(port, "127.0.0.1") or _port_in_use(port, "0.0.0.0"):
        print(f"[Finance shim] Port {port} already in use; assuming service is already running. Ready.")
        sys.exit(0)

    print(f"[Finance shim] Starting Flask app on {host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
