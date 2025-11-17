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
import sys
from typing import Optional

# Ensure imports work even if the preview system runs from a different working dir.
# We adjust sys.path to include the Finance container root. This is absolute-safe.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTAINER_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if CONTAINER_ROOT not in sys.path:
    sys.path.insert(0, CONTAINER_ROOT)

try:
    # Import the Flask app and helpers from app.py at the container root
    import app as finance_app
except Exception as exc:  # pragma: no cover - defensive fallback
    # Provide a clear error if the import fails
    raise RuntimeError(
        "Failed to import Finance/app.py from legacy shim stock_data/stock_twilio_server.py"
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
    Flask's development server handles KeyboardInterrupt but in container
    environments PID 1 may receive SIGTERM; this forwards to a clean exit.
    """
    def _graceful_exit(signum, frame):  # noqa: ARG001 - signature required by signal.signal
        # Flush stdout/stderr and exit; Flask server should stop cleanly.
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os._exit(0)  # Use os._exit to avoid hanging threads

    signal.signal(signal.SIGTERM, _graceful_exit)
    signal.signal(signal.SIGINT, _graceful_exit)


# PUBLIC_INTERFACE
def main():
    """
    Launch the Finance Flask app via the legacy shim.

    Binds to HOST:PORT where:
    - HOST defaults to 0.0.0.0
    - PORT defaults to 3000

    Returns:
        None
    """
    _install_signal_handlers()
    # Use the app instance defined in app.py
    app = getattr(finance_app, "app", None)
    if app is None:
        raise RuntimeError("Expected 'app' Flask instance in Finance/app.py was not found.")
    host = _get_host()
    port = _get_port()
    # Run using Flask's built-in server. For production, a WSGI server is preferred,
    # but this matches the existing behavior in Finance/app.py and container preview.
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
