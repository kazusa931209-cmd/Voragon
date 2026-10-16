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

## ASR image (P7-003)

Build and push: [docker/asr-inference/README.md](../../../docker/asr-inference/README.md).

## Deploy asr-service (P7-004)

Requires P7-001 GPU nodes, P7-002 device plugin, and P7-003 image in ECR.

From the **repository root**:

```bash
export AWS_REGION="${AWS_REGION:-ap-northeast-1}"
export ECR_URI="$(terraform -chdir=infra/ecr output -raw repository_url)"
export ASR_ECR_URI="$(terraform -chdir=infra/ecr output -raw asr_repository_url)"
export TAG="${TAG:-$(git rev-parse --short HEAD)}"

cd k8s/eks
kustomize edit set image "voragon/realtime-backend=${ECR_URI}:${TAG}"
kustomize edit set image "voragon/asr-inference=${ASR_ECR_URI}:${TAG}"
kubectl apply -k .
kubectl wait -n voragon --for=condition=ready pod -l app=asr-service --timeout=900s
```

Verify scheduling on GPU nodes:

```bash
kubectl get pods -n voragon -l app=asr-service -o wide
kubectl describe pod -n voragon -l app=asr-service | grep -E 'Node:|nvidia.com/gpu'
```

In-cluster health (from a debug pod):

```bash
kubectl run -n voragon curl-asr --rm -it --restart=Never --image=curlimages/curl:8.5.0 -- \
  curl -sf http://asr-service:8081/health
```

Port-forward alternative:

```bash
kubectl port-forward -n voragon svc/asr-service 8081:8081
curl -sf http://localhost:8081/health | jq .
```

Model weight PVC caching is [P7-005](../../../docs/roadmap/dev-step-p7-005-model-weights-gpu.md).
