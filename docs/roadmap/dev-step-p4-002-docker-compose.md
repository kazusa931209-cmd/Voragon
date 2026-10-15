# P4-002: Docker Compose (Realtime Backend)

| Field | Value |
|-------|-------|
| **ID** | P4-002 |
| **Phase** | 4 |
| **Status** | done |
| **Commit** | [`821f7cc`](https://github.com/kazusa931209-cmd/Voragon/commit/821f7cc) |
| **PR** | — |
| **Branch** | `dev-step/p4-002-docker-compose` |

## Spec References

- [Docker Compose](../operations/docker.md) — services, ports, health checks
- [Backend Architecture](../architecture/backend.md) — Docker Compose deployment mode
- [ADR-006: Local-first](../decisions/ADR-006-local-first.md)

## Scope

One verifiable behavior: **`docker compose up` from `docker/` starts `realtime-backend` on host port 8000 with a compose healthcheck.**

- `docker/docker-compose.yml` with service `realtime-backend`
- Build from P4-001 Dockerfile; publish `8000:8000`
- Healthcheck: `curl -f http://localhost:8000/health` (or `wget`) inside container
- Env file or compose `environment` for safe defaults (`LOG_FORMAT=json` optional)
- Desktop remains on host; connects to `ws://localhost:8000/v1/realtime`

## Out of Scope

- Named volumes for models (P4-003)
- `docker-compose.gpu.yml` override
- `asr-inference` sidecar
- Bundling desktop in compose

## Acceptance Criteria

- [x] `cd docker && docker compose up --build` starts backend without manual `python -m app.main`
- [x] Compose healthcheck passes after ASR warmup (document expected startup time)
- [x] WebSocket connect from desktop or `tools/realtime-cli` succeeds against containerized backend

## Manual Test

1. `cd docker && docker compose up --build`
2. `curl http://localhost:8000/health`
3. Desktop or CLI: connect to `ws://localhost:8000/v1/realtime` → `session.started`

## Automated Tests

```bash
cd backend && pytest -v
```

## Spec Changes

Update [docker.md](../operations/docker.md) usage section and [local-development.md](../operations/local-development.md) with compose startup path.

---

## Completion

### Summary

- Added [`docker/docker-compose.yml`](../../docker/docker-compose.yml) — `realtime-backend` service, repo-root build, port 8000, `ASR_MODEL=tiny`, `curl` healthcheck (`start_period: 120s`).
- Extended [Dockerfile](../../docker/realtime-backend/Dockerfile) with `curl` for in-container healthchecks.
- Updated [docker.md](../operations/docker.md), [local-development.md](../operations/local-development.md), [realtime-backend README](../../docker/realtime-backend/README.md).

### Spec Changes

- [docker.md](../operations/docker.md), [local-development.md](../operations/local-development.md).

### Automated Tests Run

```bash
cd backend && source .venv/bin/activate && pytest -q
# 93 passed, 1 skipped (2026-10-15)
```

### Manual Test Result

- [x] `cd docker && docker compose up --build -d` — backend on `:8000` (2026-10-15).
- [x] First cold start ~**4 min** until `docker compose ps` shows **healthy** (HF model download + ASR warmup); subsequent starts faster with cached layers/models in container FS (volumes in P4-003).
- [x] `curl -f http://localhost:8000/health` → **healthy**.
- [x] `realtime_cli --file sample-mono-16khz.wav` → `session.started`, partials/finals.

### Commit

- **Hash:** `821f7cc`

### PR

- **URL:** —
