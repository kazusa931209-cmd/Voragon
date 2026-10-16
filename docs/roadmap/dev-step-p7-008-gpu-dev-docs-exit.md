# P7-008: GPU Dev Docs and Phase 7 Exit Prep

| Field | Value |
|-------|-------|
| **ID** | P7-008 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-008-gpu-dev-docs-exit` |

## Spec References

- [phases.md](phases.md) — Phase 7 exit criteria
- [aws-deployment.md](../operations/aws-deployment.md)
- [kubernetes.md](../architecture/kubernetes.md)
- [dev-step-phase7-exit.md](dev-step-phase7-exit.md)

## Scope

One verifiable behavior: **documentation describes the GPU inference loop; [dev-step-phase7-exit.md](dev-step-phase7-exit.md) checklist is complete and cross-linked.**

- Contributor path: GPU pool → device plugin → ASR image → deploy → remote ASR → metrics
- Update [aws-deployment.md](../operations/aws-deployment.md) Phase 7 section from planned to implemented steps
- [phases.md](phases.md) Phase 7 status when signed off

## Out of Scope

- Phase 8 AI Gateway dev-steps

## Acceptance Criteria

- [ ] aws-deployment Phase 7 reflects implemented path
- [ ] Phase 7 exit checklist ready for operator sign-off
- [ ] dev-steps-index and docs README link GPU path

## Manual Test

1. Follow contributor path from clean clone (AWS GPU quota assumed)
2. Complete phase7-exit checklist draft
3. Link check from docs README

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md), [docs/README.md](../README.md), [phases.md](phases.md).

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
