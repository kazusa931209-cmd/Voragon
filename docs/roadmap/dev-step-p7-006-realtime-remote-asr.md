# P7-006: Realtime Backend Remote ASR

| Field | Value |
|-------|-------|
| **ID** | P7-006 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-006-realtime-remote-asr` |

## Spec References

- [Backend Architecture](../architecture/backend.md)
- [Model Serving](../architecture/model-serving.md) — ASREngine abstraction
- [dev-step-p7-004](dev-step-p7-004-asr-service-deploy.md)
- [Realtime WebSocket](../api/realtime-websocket.md)

## Scope

One verifiable behavior: **realtime-service transcribes via HTTP (or gRPC) to in-cluster `asr-service` when `ASR_BACKEND=remote` (or documented env); WebSocket partial/final behavior unchanged for clients.**

- Remote ASR adapter implementing existing engine interface
- asr-service transcribe API (minimal: partial + final segments, health)
- EKS ConfigMap/env for service URL; CPU realtime Deployment updated
- Local dev: optional mock remote URL for pytest

## Out of Scope

- AI Gateway routing (Phase 8)
- Desktop changes (same WebSocket contract)

## Acceptance Criteria

- [ ] pytest covers remote adapter (mock server or contract tests)
- [ ] EKS: realtime pods call asr-service; desktop E2E partials/finals on GPU path (operator)
- [ ] `ASR_BACKEND` in-process still works for Compose/Kind (regression)

## Manual Test

1. Deploy P7-004 + P7-006 manifests
2. Desktop or `realtime_cli` against ALB — transcripts flow
3. Scale asr-service to 0 → degraded health / clear errors per API spec

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [backend.md](../architecture/backend.md), [realtime-websocket.md](../api/realtime-websocket.md) if error codes added, [k8s/eks](../../k8s/eks/).

---

## Completion

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

### Commit

- **Hash:** —

### PR

- **URL:** —
