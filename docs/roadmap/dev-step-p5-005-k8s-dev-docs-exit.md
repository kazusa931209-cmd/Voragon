# P5-005: Kubernetes Dev Docs and Phase 5 Exit

| Field | Value |
|-------|-------|
| **ID** | P5-005 |
| **Phase** | 5 |
| **Status** | in-progress |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p5-005-k8s-dev-docs-exit` |

## Spec References

- [phases.md](phases.md) — Phase 5 exit criteria
- [local-development.md](../operations/local-development.md)
- [kubernetes-local.md](../operations/kubernetes-local.md)
- [desktop/README.md](../../desktop/README.md)

## Scope

One verifiable behavior: **documentation describes the Kind dev loop; desktop E2E via port-forward satisfies Phase 5 exit checklist.**

- [dev-step-phase5-exit.md](dev-step-phase5-exit.md) manual checklist
- Cross-links in [dev-steps-index.md](dev-steps-index.md), [local-development.md](../operations/local-development.md), [k8s/README.md](../../k8s/README.md)
- [phases.md](phases.md) Phase 5 status when signed off
- [architecture/kubernetes.md](../architecture/kubernetes.md) note: Phase 5 Kind uses single realtime Deployment (no ASR sidecar yet)

## Out of Scope

- EKS / Ingress / ALB
- CI pipeline for Kind

## Acceptance Criteria

- [x] [k8s/README.md](../../k8s/README.md) contributor path (Kind → apply → port-forward)
- [x] [dev-step-phase5-exit.md](dev-step-phase5-exit.md) checklist
- [x] Compose vs Kind guidance in docs
- [ ] Desktop speak E2E vs Kind (operator sign-off on phase5 exit)

## Manual Test

1. Follow [k8s/README.md](../../k8s/README.md) from clean clone (Kind installed)
2. Port-forward → desktop Connect → speak → partials/finals
3. `kubectl rollout restart` → desktop reconnect / new session acceptable

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [kubernetes-local.md](../operations/kubernetes-local.md), [local-development.md](../operations/local-development.md), [phases.md](phases.md), [architecture/kubernetes.md](../architecture/kubernetes.md).

---

## Completion

### Summary

- Added [dev-step-phase5-exit.md](dev-step-phase5-exit.md).
- Updated [local-development.md](../operations/local-development.md), [phases.md](phases.md), [architecture/kubernetes.md](../architecture/kubernetes.md), [docs/README.md](../README.md).

### Spec Changes

- [kubernetes-local.md](../operations/kubernetes-local.md), [local-development.md](../operations/local-development.md), [phases.md](phases.md), [architecture/kubernetes.md](../architecture/kubernetes.md), [docs/README.md](../README.md).

### Automated Tests Run

```bash
cd backend && pytest -q   # 93 passed, 1 skipped (2026-10-15)
cd desktop && pnpm test  # 14 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pass — pending [Phase 5 exit](dev-step-phase5-exit.md) sign-off

### Commit

- **Hash:** —
