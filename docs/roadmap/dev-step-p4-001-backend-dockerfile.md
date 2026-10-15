# P4-001: Realtime Backend Dockerfile

| Field | Value |
|-------|-------|
| **ID** | P4-001 |
| **Phase** | 4 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p4-001-backend-dockerfile` |

## Spec References

- [Docker Compose](../operations/docker.md) — planned layout under `docker/realtime-backend/`
- [Backend Architecture](../architecture/backend.md) — deployment modes
- [Local Development](../operations/local-development.md)

## Scope

One verifiable behavior: **`docker/realtime-backend/Dockerfile` builds an image that runs the FastAPI app and responds on `/health`.**

- Multi-stage or slim Python 3.11+ base appropriate for `faster-whisper` / `onnxruntime` (CPU)
- Install backend via `pip install` from `backend/` (editable or copy `app/` + pyproject)
- Default `CMD` runs `python -m app.main` with `HOST=0.0.0.0`, `PORT=8000`
- Document build context (repo root vs `backend/`) in `docker/realtime-backend/README.md` or comment in Dockerfile
- Optional: `.dockerignore` at repo root or under `docker/` to exclude `desktop/`, `.venv`, etc.

## Out of Scope

- `docker-compose.yml` (P4-002)
- GPU / NVIDIA base images
- ASR sidecar container
- CI publish to registry

## Acceptance Criteria

- [ ] `docker build -f docker/realtime-backend/Dockerfile …` succeeds locally
- [ ] Container starts; `curl -f http://localhost:8000/health` returns success
- [ ] Image size and build steps documented (first-run model download may occur at runtime, not build)

## Manual Test

1. Build image with documented command
2. Run container with `-p 8000:8000` and env from `backend/.env.example` as needed
3. `curl http://localhost:8000/health`

## Automated Tests

```bash
# Existing backend suite still passes on host (unchanged behavior)
cd backend && pytest -v
```

Optional follow-up: smoke script that builds and curls health (not required for this step if manual test suffices).

## Spec Changes

Expected: update [docker.md](../operations/docker.md) **Status** and build instructions when implemented.

---

## Completion

_Fill in after implementation._
