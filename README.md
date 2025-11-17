# Finance Backend (Flask)

This is a minimal Flask entrypoint to ensure the Finance backend starts and binds to `0.0.0.0:3000`.

## Startup behavior

- The Procfile configures the preview/orchestrator to run: `web: bash start.sh`.
- `start.sh` launches the service via `python app.py`, which binds to `HOST`:`PORT` (defaults: `0.0.0.0:3000`).
- Legacy script `stock_data/stock_twilio_server.py` is no longer used and any orchestrator manifests should not reference it. The correct startup is `bash start.sh` or `python app.py`. The project manifest (.project_manifest.yaml) has been updated to use `bash start.sh`.

## Run locally

1. Create/activate a virtual environment (optional).
2. Install dependencies:

   pip install -r requirements.txt

3. Start the server (either):

   python app.py
   # or
   bash start.sh

The server binds to `0.0.0.0:3000` by default. You can override with:

- HOST (default: 0.0.0.0)
- PORT (default: 3000)

## Health checks

- GET `/` returns basic status
- GET `/healthz` returns healthy status
