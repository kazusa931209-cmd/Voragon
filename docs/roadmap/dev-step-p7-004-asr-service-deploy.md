# P7-004: asr-service Deployment on GPU

| Field | Value |
|-------|-------|
| **ID** | P7-004 |
| **Phase** | 7 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p7-004-asr-service-deploy` |

## Spec References

- [Kubernetes Architecture](../architecture/kubernetes.md) — asr-service
- [dev-step-p7-003](dev-step-p7-003-asr-image-ecr.md)
- [k8s/eks](../../k8s/eks/)

## Scope

One verifiable behavior: **`asr-service` runs on GPU nodes with `nvidia.com/gpu: 1`, ClusterIP Service, readiness when model ready.**

- Manifests under `k8s/eks/` (Kustomize overlay or new base)
- nodeSelector `node-type=gpu`, toleration for GPU taint, resource limits per ADR-010
- Probes aligned with [kubernetes.md](../architecture/kubernetes.md) ASR probe table

## Out of Scope

- Model cache strategy details (P7-005)
- realtime-service routing (P7-006)

## Acceptance Criteria

- [ ] `kubectl apply -k` deploys asr-service to GPU nodes only
- [ ] `kubectl get pods -n voragon -l app=asr-service` Ready (operator)
- [ ] In-cluster `curl` to Service `/health` succeeds from debug pod

## Manual Test

1. Set ECR image tag in Kustomize
2. Apply and wait for Ready
3. Port-forward or exec curl `/health`

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [k8s/eks/README.md](../../k8s/eks/README.md), [kubernetes-local.md](../operations/kubernetes-local.md) note (EKS-only GPU).

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
