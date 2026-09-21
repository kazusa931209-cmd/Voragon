# Voragon Backend

Python FastAPI realtime backend for Voragon.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m app.main
```

Server listens on `http://0.0.0.0:8000` by default.

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `info` | Logging level |

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
