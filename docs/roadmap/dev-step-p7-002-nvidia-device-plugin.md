# P7-002: NVIDIA Device Plugin

| Field | Value |
|-------|-------|
| **ID** | P7-002 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-002-nvidia-device-plugin` |

## Spec References

- [ADR-010](../decisions/ADR-010-gpu-node-pool.md)
- [dev-step-p7-001](dev-step-p7-001-gpu-node-pool.md)

## Scope

One verifiable behavior: **GPU nodes advertise `nvidia.com/gpu` allocatable capacity after device plugin install.**

- Helm or Terraform install of [NVIDIA device plugin](https://github.com/NVIDIA/k8s-device-plugin) on EKS GPU nodes
- Document verify commands in ops README

## Out of Scope

- ASR container (P7-003)
- DCGM / metrics (P7-007)

## Acceptance Criteria

- [ ] Plugin pods Running on GPU nodes
- [ ] `kubectl describe node <gpu-node>` shows `nvidia.com/gpu` allocatable ≥ 1 (operator)

## Manual Test

1. Apply plugin after P7-001
2. `kubectl get pods -A | grep nvidia`
3. Describe GPU node capacity/allocatable

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [infra/eks/README.md](../../infra/eks/README.md) or new `k8s/eks/gpu/README.md`.

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
