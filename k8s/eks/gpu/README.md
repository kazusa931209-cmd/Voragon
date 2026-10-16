# EKS GPU (Phase 7)

GPU node pool and device plugin are provisioned by Terraform ([infra/eks/README.md](../../../infra/eks/README.md)):

| Step | Dev-step | Component |
|------|----------|-----------|
| Node pool | P7-001 | Managed node group `gpu`, taint `nvidia.com/gpu=true:NoSchedule` |
| Device plugin | P7-002 | Helm `nvidia-device-plugin` in `kube-system` |

## Verify device plugin (P7-002)

```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=nvidia-device-plugin -o wide
kubectl describe node -l node-type=gpu | grep -A5 'Capacity:\|Allocatable:'
```

Allocatable should include `nvidia.com/gpu`.

## Next

- P7-003 — ASR inference image + ECR
- P7-004 — `asr-service` Deployment with `resources.limits.nvidia.com/gpu: 1`
