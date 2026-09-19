# P1-001: Backend Scaffold and Health Endpoint

| Field | Value |
|-------|-------|
| **ID** | P1-001 |
| **Phase** | 1 |
| **Status** | planned |
| **PR** | — |
| **Branch** | `dev-step/p1-001-backend-scaffold` |

## Spec References

- [Backend Architecture](../architecture/backend.md) — service structure, `/health` endpoint
- [Local Development](../operations/local-development.md) — planned project layout
- [Architecture Overview](../architecture/overview.md) — engineering principles

## Scope

One verifiable behavior: **a runnable FastAPI backend with project structure and a working health endpoint.**

- Create `backend/` package layout per architecture docs
- FastAPI app entry point (`app/main.py`)
- `GET /health` returns JSON health status
- Configuration via environment variables (`HOST`, `PORT`, `LOG_LEVEL`)
- `pyproject.toml` with dependencies and dev extras
- README or inline docstring with run instructions

## Out of Scope

- WebSocket endpoint
- VAD, ASR, or audio processing
- Docker / containerization
- Authentication
- OpenTelemetry / Prometheus (Phase 2)

## Acceptance Criteria

- [ ] `backend/` directory exists with planned structure (`app/main.py`, `app/config.py`, `tests/`)
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `python -m app.main` (or equivalent) starts the server on configured port
- [ ] `GET http://localhost:8000/health` returns `200` with JSON body indicating healthy status
- [ ] Automated tests cover the health endpoint
- [ ] No Whisper, VAD, or WebSocket code introduced

## Manual Test

1. `cd backend && python -m venv .venv && source .venv/bin/activate`
2. `pip install -e ".[dev]"`
3. `python -m app.main`
4. `curl http://localhost:8000/health` — expect `200` and JSON with status field
5. Stop the server

## Automated Tests

```bash
cd backend && pytest
```

Expected: at least one test asserting `GET /health` returns 200 and expected JSON shape.

## Spec Changes

Expected: none. If project layout differs from `backend.md`, update that doc in the same PR.

---

## Completion

_Fill in after implementation, before PR._

### Summary

- …

### Spec Changes

- …

### Automated Tests Run

```bash
# paste command and result
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
