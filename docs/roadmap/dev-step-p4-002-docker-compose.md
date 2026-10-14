# P4-002: Docker Compose (Realtime Backend)

| Field | Value |
|-------|-------|
| **ID** | P4-002 |
| **Phase** | 4 |
| **Status** | planned |
| **Commit** | — |
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

- [ ] `cd docker && docker compose up --build` starts backend without manual `python -m app.main`
- [ ] Compose healthcheck passes after ASR warmup (document expected startup time)
- [ ] WebSocket connect from desktop or `tools/realtime-cli` succeeds against containerized backend

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

_Fill in after implementation._
