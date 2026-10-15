# P4-001: Realtime Backend Dockerfile

| Field | Value |
|-------|-------|
| **ID** | P4-001 |
| **Phase** | 4 |
| **Status** | done |
| **Commit** | [`6d3c0c2`](https://github.com/kazusa931209-cmd/Voragon/commit/6d3c0c2) |
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

- [x] `docker build -f docker/realtime-backend/Dockerfile …` succeeds locally
- [x] Container starts; `curl -f http://localhost:8000/health` returns success
- [x] Image size and build steps documented (first-run model download may occur at runtime, not build)

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

### Summary

- Added [`docker/realtime-backend/Dockerfile`](../../docker/realtime-backend/Dockerfile) (Python 3.11 slim, `ffmpeg`, CPU `torch`/`torchaudio`, `pip install` of `backend/`).
- Repo-root [`.dockerignore`](../../.dockerignore) and [`docker/realtime-backend/README.md`](../../docker/realtime-backend/README.md) (build context, run, health).
- Updated [docker.md](../operations/docker.md) with P4-001 build/run commands.

### Spec Changes

- [docker.md](../operations/docker.md) — status and realtime-backend image section.

### Automated Tests Run

```bash
cd backend && source .venv/bin/activate && pytest -q
# 93 passed, 1 skipped (2026-10-15)
```

### Manual Test Result

- [x] Build `voragon/realtime-backend:local` from repo root — **~1.71 GB** image (2026-10-15).
- [x] `docker run -p 8001:8000 -e ASR_MODEL=tiny` → `curl -f http://localhost:8001/health` **healthy** after ASR warmup (~18 s).

### Commit

- **Hash:** `6d3c0c2`

### PR

- **URL:** —
