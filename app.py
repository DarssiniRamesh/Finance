#!/usr/bin/env python3
"""
Flask application entrypoint for the Finance backend.

This minimal app is provided to ensure the service can start and bind to the expected port (3000) on all interfaces.
It exposes a simple health endpoint at '/' and '/healthz' to allow readiness checks.

Environment variables:
- PORT: Optional. Port to bind the Flask server to. Defaults to 3000.
- HOST: Optional. Host interface to bind to. Defaults to 0.0.0.0.

Note:
Do not hardcode secrets here. Use environment variables configured via the orchestrator.
"""
import os
from flask import Flask, jsonify

# Create Flask app instance
app = Flask(__name__)


# PUBLIC_INTERFACE
@app.get("/")
def root():
    """Root endpoint that returns a basic JSON payload indicating the service is running."""
    return jsonify({"status": "ok", "service": "Finance", "message": "Finance backend is running"}), 200


# PUBLIC_INTERFACE
@app.get("/healthz")
def healthz():
    """Health check endpoint used by orchestrators to determine readiness/liveness."""
    return jsonify({"status": "healthy"}), 200


def _get_host() -> str:
    """
    Resolve the host binding from environment variables with a secure default.
    Returns:
        str: Host interface to bind to.
    """
    return os.getenv("HOST", "0.0.0.0")


def _get_port() -> int:
    """
    Resolve the port from environment variables with a default of 3000.
    Returns:
        int: TCP port to bind to.
    """
    raw = os.getenv("PORT", "3000")
    try:
        return int(raw)
    except ValueError:
        # Fall back to 3000 if PORT is malformed
        return 3000


if __name__ == "__main__":
    # Bind to 0.0.0.0 and port 3000 by default so the container can be reached externally.
    app.run(host=_get_host(), port=_get_port())
