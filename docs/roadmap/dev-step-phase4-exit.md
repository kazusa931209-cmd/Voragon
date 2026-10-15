# Phase 4 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 4 |
| **Status** | in-progress (manual verification) |
| **Dev-steps** | [P4-001](dev-step-p4-001-backend-dockerfile.md)–[P4-004](dev-step-p4-004-docker-dev-docs.md) |

## Exit Criteria ([phases.md](phases.md))

- [ ] `docker compose up` starts a working backend
- [ ] Desktop connects to containerized backend
- [ ] Model weights persist across container restarts

## Prerequisites

See [docker/README.md](../../docker/README.md) and [local-development.md](../operations/local-development.md).

```bash
cd docker && docker compose up --build
cd desktop && pnpm tauri dev
```

## Manual Checklist

- [ ] Follow [docker/README.md](../../docker/README.md) from clone — no local backend venv required
- [ ] `curl -f http://localhost:8000/health` → healthy after warmup
- [ ] Desktop **Connect** → **Start transcription** → partials/finals
- [ ] `docker compose down` && `docker compose up` — faster startup; E2E still works (cached models)

## Sign-Off

When all boxes are checked:

1. Set **Status** in this file to `done` with date.
2. Update [phases.md](phases.md) Phase 4 **Status** to complete.
3. Update [dev-steps-index.md](dev-steps-index.md) if needed.
