# Voragon Backend

Python FastAPI realtime backend for Voragon.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env   # optional; edit ASR_MODEL, VAD_BACKEND, etc.
```

## Run

```bash
cd backend
python -m app.main
```

Faster local ASR (smaller model):

```bash
ASR_MODEL=tiny python -m app.main
```

Startup logs show the resolved model, e.g. `Warming up ASR backend=faster_whisper model=tiny`.

Server listens on `http://0.0.0.0:8000` by default.

### Configuration

See [`.env.example`](.env.example) for all settings. Common overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `info` | Logging level |
| `ASR_BACKEND` | `faster_whisper` | ASR adapter (`faster_whisper`, `mock`) |
| `ASR_MODEL` | `large-v3-turbo` | Whisper model id (e.g. `tiny`, `base`, `large-v3-turbo`) |

## Health Check

```bash
curl http://localhost:8000/health
```

## WebSocket

Connect to `ws://localhost:8000/v1/realtime`. The server sends `session.started` immediately after the connection is accepted.

## Tests

```bash
pytest
```
