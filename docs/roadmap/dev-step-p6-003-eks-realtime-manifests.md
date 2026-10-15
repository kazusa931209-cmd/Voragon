# P6-003: EKS Realtime Manifests and Deploy

| Field | Value |
|-------|-------|
| **ID** | P6-003 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-003-eks-realtime-manifests` |

## Spec References

- [Kubernetes Architecture](../architecture/kubernetes.md) — Deployments, Health Probes
- [k8s/local/](../../k8s/local/) — Kind parity reference
- [dev-step-p5-002](dev-step-p5-002-local-manifests.md), [dev-step-p5-003](dev-step-p5-003-model-cache-pvc.md), [dev-step-p5-004](dev-step-p5-004-probes-rolling-restart.md)
- [dev-step-p6-001](dev-step-p6-001-ecr-image-push.md), [dev-step-p6-002](dev-step-p6-002-eks-cluster-cpu.md)

## Scope

One verifiable behavior: **`kubectl apply` of EKS manifests deploys `realtime-backend` using the ECR image; pods reach Ready and in-cluster `/health` succeeds.**

- Manifests under `k8s/eks/` (or documented path): namespace, configmap, deployment, service, storage for model cache (EBS / PVC class appropriate for EKS)
- Deployment `image` points at ECR URI from P6-001; probes aligned with Kind (startup/liveness/readiness on `/health`)
- Initial replica count: 1 for first E2E; document path to 2 replicas before ALB (P6-004)
- **In-process ASR** only (same as Phase 5); no `asr-service` sidecar

## Out of Scope

- Internet-facing Ingress (P6-004)
- API Gateway / JWT (P6-005)
- HPA (optional follow-up within Phase 6 if not in P6-004 scope)

## Acceptance Criteria

- [ ] EKS manifests committed and documented
- [ ] Pod Ready after ASR warmup on EKS
- [ ] `kubectl exec` or port-forward → `curl -f http://localhost:8000/health` succeeds
- [ ] Model cache survives pod restart (PVC or equivalent)

## Manual Test

1. P6-002 cluster + P6-001 image tag referenced in Deployment
2. `kubectl apply -f k8s/eks/` (exact paths per README)
3. `kubectl wait` for Ready; port-forward Service → `/health`
4. Delete pod; confirm replacement Ready and faster warmup when cache populated

## Automated Tests

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

## Spec Changes

Expected: [kubernetes-local.md](../operations/kubernetes-local.md) or new EKS ops doc — Kind vs EKS manifest table; [architecture/kubernetes.md](../architecture/kubernetes.md) if EKS path differs from Kind.

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
