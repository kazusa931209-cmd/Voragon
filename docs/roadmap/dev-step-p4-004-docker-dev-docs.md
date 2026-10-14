# P4-004: Docker Development Docs and Phase 4 Exit

| Field | Value |
|-------|-------|
| **ID** | P4-004 |
| **Phase** | 4 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p4-004-docker-dev-docs` |

## Spec References

- [phases.md](phases.md) — Phase 4 exit criteria
- [Local Development](../operations/local-development.md)
- [Docker Compose](../operations/docker.md)
- [Desktop README](../../desktop/README.md)

## Scope

One verifiable behavior: **documentation describes the Docker-based dev loop; desktop E2E against compose backend satisfies Phase 4 exit.**

- [local-development.md](../operations/local-development.md): mark Docker path implemented; two-terminal flow (compose + `pnpm tauri dev`)
- [docker.md](../operations/docker.md): status **implemented** for CPU in-process ASR path
- Root or `docker/README.md`: quick start (`compose up`, health, WebSocket URL)
- Cross-link Phase 4 dev-steps in [dev-steps-index.md](dev-steps-index.md)

## Out of Scope

- `docker-compose.gpu.yml`
- `asr-inference` sidecar (future dev-step if needed)
- Desktop launcher that starts compose automatically ([desktop.md](../architecture/desktop.md) Phase 4+)

## Acceptance Criteria

- [ ] New contributor can follow docs: compose backend + desktop transcript E2E
- [ ] Phase 4 exit criteria in [phases.md](phases.md) checked off in this doc’s manual test
- [ ] No contradiction between bare-metal and Docker instructions (when to use each)

## Manual Test

1. Follow docs from clean clone (no local venv backend required)
2. `docker compose up` → desktop connect → speak → transcripts
3. Restart compose; confirm cached models (P4-003) still allow E2E

## Automated Tests

```bash
cd backend && pytest -v
cd desktop && pnpm test
```

## Spec Changes

Expected: [local-development.md](../operations/local-development.md), [docker.md](../operations/docker.md), possibly [phases.md](phases.md) Phase 4 status.

---

## Completion

_Fill in after implementation._
