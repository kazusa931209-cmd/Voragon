# P6-008: AWS Dev Docs and Phase 6 Exit Prep

| Field | Value |
|-------|-------|
| **ID** | P6-008 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-008-aws-dev-docs-exit` |

## Spec References

- [phases.md](phases.md) — Phase 6 exit criteria
- [local-development.md](../operations/local-development.md)
- [aws-deployment.md](../operations/aws-deployment.md)
- [desktop/README.md](../../desktop/README.md)
- [dev-step-phase6-exit.md](dev-step-phase6-exit.md)

## Scope

One verifiable behavior: **documentation describes the full AWS staging/prod loop; [dev-step-phase6-exit.md](dev-step-phase6-exit.md) checklist is complete and cross-linked from index and ops docs.**

- Contributor path: ECR → EKS → deploy → ALB → API Gateway → desktop E2E
- Kind vs EKS vs Compose comparison updated
- [phases.md](phases.md) Phase 6 status when signed off
- [architecture/kubernetes.md](../architecture/kubernetes.md) — note Phase 6 CPU-only realtime on EKS (GPU in Phase 7)

## Out of Scope

- Phase 7 GPU dev-steps
- Cost automation / FinOps tooling

## Acceptance Criteria

- [ ] [aws-deployment.md](../operations/aws-deployment.md) status reflects implemented Phase 6 path
- [ ] [dev-step-phase6-exit.md](dev-step-phase6-exit.md) manual checklist ready for operator sign-off
- [ ] [dev-steps-index.md](dev-steps-index.md) and [local-development.md](../operations/local-development.md) link EKS path
- [ ] Desktop production connect documented (URL + auth)

## Manual Test

1. Follow aws-deployment contributor path from clean clone (AWS creds assumed)
2. Complete [dev-step-phase6-exit.md](dev-step-phase6-exit.md) checklist
3. Confirm docs README / roadmap links resolve

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md), [local-development.md](../operations/local-development.md), [phases.md](phases.md), [docs/README.md](../README.md).

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
