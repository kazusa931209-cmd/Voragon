# P4-003: Model Weight Volume Caching

| Field | Value |
|-------|-------|
| **ID** | P4-003 |
| **Phase** | 4 |
| **Status** | planned |
| **Commit** | — |
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

- [ ] First `docker compose up` downloads ASR/VAD weights as today on bare metal
- [ ] After restart, startup skips full re-download (verify via logs or network)
- [ ] Volume documented in compose file comments and ops docs

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

_Fill in after implementation._
