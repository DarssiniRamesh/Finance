# Finance Backend (Flask)

This is a minimal Flask entrypoint to ensure the Finance backend starts and binds to `0.0.0.0:3000`.

## Run locally

1. Create/activate a virtual environment (optional).
2. Install dependencies:

   pip install -r requirements.txt

3. Start the server:

   python app.py

The server binds to `0.0.0.0:3000` by default. You can override with:

- HOST (default: 0.0.0.0)
- PORT (default: 3000)

## Health checks

- GET `/` returns basic status
- GET `/healthz` returns healthy status
