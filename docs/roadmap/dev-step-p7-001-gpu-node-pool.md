# P7-001: EKS GPU Node Pool

| Field | Value |
|-------|-------|
| **ID** | P7-001 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-001-gpu-node-pool` |

## Spec References

- [ADR-010: GPU Node Pool](../decisions/ADR-010-gpu-node-pool.md)
- [Kubernetes Architecture](../architecture/kubernetes.md) — GPU Node Pool
- [AWS Deployment](../operations/aws-deployment.md) — Phase 7
- [dev-step-p6-002](dev-step-p6-002-eks-cluster-cpu.md)

## Scope

One verifiable behavior: **staging EKS has a managed GPU node group (e.g. g5.xlarge) with GPU taint and `node-type=gpu` label; nodes reach Ready.**

- Extend [infra/eks](../../infra/eks/) Terraform (second `eks_managed_node_groups` entry)
- Taint: `nvidia.com/gpu=true:NoSchedule` (per ADR-010)
- Document min/desired/max sizing and cost note in [infra/eks/README.md](../../infra/eks/README.md)

## Out of Scope

- NVIDIA device plugin (P7-002)
- ASR workloads (P7-004+)

## Acceptance Criteria

- [ ] `terraform apply` creates GPU node group on existing P6-002 cluster
- [ ] `kubectl get nodes -l node-type=gpu` shows Ready (operator)
- [ ] GPU nodes have documented taint; CPU realtime pods stay on CPU pool (operator smoke)

## Manual Test

1. `terraform -chdir=infra/eks apply` with GPU variables enabled
2. `kubectl get nodes -L node-type -o wide`
3. Confirm CPU `realtime-backend` pods unchanged on CPU nodes

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [infra/eks/README.md](../../infra/eks/README.md), [aws-deployment.md](../operations/aws-deployment.md) Phase 7 step 1.

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
