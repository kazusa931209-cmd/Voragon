# Phase 4 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 4 |
| **Status** | done — signed off **2026-10-15** (macOS) |
| **Dev-steps** | [P4-001](dev-step-p4-001-backend-dockerfile.md)–[P4-004](dev-step-p4-004-docker-dev-docs.md) |

## Exit Criteria ([phases.md](phases.md))

- [x] `docker compose up` starts a working backend
- [x] Desktop connects to containerized backend
- [x] Model weights persist across container restarts

## Prerequisites

See [docker/README.md](../../docker/README.md) and [local-development.md](../operations/local-development.md).

```bash
cd docker && docker compose up --build
cd desktop && pnpm tauri dev
```

## Manual Checklist

- [x] Follow [docker/README.md](../../docker/README.md) from clone — no local backend venv required
- [x] `curl -f http://localhost:8000/health` → healthy after warmup
- [x] Desktop **Connect** → **Start transcription** → partials/finals
- [x] `docker compose down` && `docker compose up` — faster startup; E2E still works (cached models)

## Sign-Off

Completed **2026-10-15**:

1. [x] **Status** `done` (header).
2. [x] [phases.md](phases.md) Phase 4 **Status** complete with exit sign-off.
3. [x] [dev-steps-index.md](dev-steps-index.md) — Phase 4 exit complete; next Phase 5 planning.
