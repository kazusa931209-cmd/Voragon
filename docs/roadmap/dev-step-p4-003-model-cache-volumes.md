# P4-003: Model Weight Volume Caching

| Field | Value |
|-------|-------|
| **ID** | P4-003 |
| **Phase** | 4 |
| **Status** | done |
| **Commit** | [`981b2cc`](https://github.com/kazusa931209-cmd/Voragon/commit/981b2cc) |
| **PR** | — |
| **Branch** | `dev-step/p4-003-model-cache-volumes` |

## Spec References

- [Docker Compose](../operations/docker.md) — volume mounts table
- [Backend README](../../backend/README.md) — `ASR_MODEL`, faster-whisper
- [Model Serving](../architecture/model-serving.md) — sidecar note (in-process for Phase 4 default)

## Scope

One verifiable behavior: **model artifacts downloaded on first container run are reused after `docker compose down` / `up` without re-downloading.**

- Named Docker volume (e.g. `voragon-model-cache`) mounted at predictable path
- Set `HF_HOME` and/or faster-whisper cache env vars in compose to that mount
- Document which caches apply (Hugging Face hub, faster-whisper) in `docker.md`
- Optional bind-mount override documented for developers who already have a host cache

## Out of Scope

- Pre-baking model weights into the image
- GPU model storage
- Separate `asr-inference` service

## Acceptance Criteria

- [x] First `docker compose up` downloads ASR/VAD weights as today on bare metal
- [x] After restart, startup skips full re-download (verify via logs or network)
- [x] Volume documented in compose file comments and ops docs

## Manual Test

1. Fresh volume: `docker compose up`; note first-run download / warmup
2. `docker compose down` then `up` again; confirm faster startup and no full re-fetch
3. Optional: `docker volume inspect` shows populated cache

## Automated Tests

```bash
cd backend && pytest -v
```

## Spec Changes

Update [docker.md](../operations/docker.md) volume table and env vars; extend `backend/.env.example` or `docker/.env.example` if new vars are introduced.

---

## Completion

### Summary

- Named volume `voragon-model-cache` in [`docker/docker-compose.yml`](../../docker/docker-compose.yml) mounted at `/var/lib/voragon/model-cache`.
- `HF_HOME` and `TORCH_HOME` under that path for faster-whisper (Hub) and Torch/Silero caches.
- [`docker/compose.env.example`](../../docker/compose.env.example) documents optional bind-mount override.
- Updated [docker.md](../operations/docker.md) volume table and env cache mapping.

### Spec Changes

- [docker.md](../operations/docker.md) — volume mounts and cache env vars.

### Automated Tests Run

```bash
cd backend && source .venv/bin/activate && pytest -q
# 93 passed, 1 skipped (2026-10-15)
```

### Manual Test Result

- [x] Fresh volume: first healthy `/health` ~325 s; compose logs show Hugging Face fetches (2026-10-15).
- [x] `docker compose down` / `up`: second healthy `/health` ~**2 s**; no full model re-download in logs.
- [x] `docker volume inspect docker_voragon-model-cache` — populated mount under `/var/lib/docker/volumes/...`.

### Commit

- **Hash:** `981b2cc`

### PR

- **URL:** —
