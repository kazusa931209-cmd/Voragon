# P6-002: EKS Cluster and CPU Node Group

| Field | Value |
|-------|-------|
| **ID** | P6-002 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-002-eks-cluster-cpu` |

## Spec References

- [ADR-009: Kubernetes / EKS](../decisions/ADR-009-kubernetes-eks.md)
- [AWS Deployment](../operations/aws-deployment.md) — Prerequisites, Phase 6 steps
- [Kubernetes Architecture](../architecture/kubernetes.md) — CPU Node Pool
- [dev-step-p6-001](dev-step-p6-001-ecr-image-push.md)

## Scope

One verifiable behavior: **a non-production or staging EKS cluster exists with a CPU node group; `kubectl` access works and nodes are Ready.**

- VPC/subnets (new or documented reuse) suitable for EKS + ALB (P6-004)
- Managed node group on CPU instance type (e.g. `m6i.large` per aws-deployment.md)
- Document cluster name, region, and kubeconfig context
- ECR pull permissions for worker nodes (IAM / `AmazonEC2ContainerRegistryReadOnly` or scoped policy)

## Out of Scope

- GPU node pool (Phase 7)
- Application Deployments (P6-003)
- ALB Ingress Controller install (P6-004)

## Acceptance Criteria

- [ ] Cluster and CPU node group created via documented IaC or eksctl commands
- [ ] `kubectl get nodes` shows Ready CPU nodes
- [ ] Worker IAM allows pulling images from P6-001 ECR repo
- [ ] Cluster version and sizing noted in ops docs

## Manual Test

1. Apply/create cluster per docs
2. `kubectl get nodes -o wide` — all Ready
3. From a node or test pod: confirm ECR pull of P6-001 image (optional smoke Job)

## Automated Tests

```bash
cd backend && pytest -q
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md) — EKS cluster section with implemented commands/paths.

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
