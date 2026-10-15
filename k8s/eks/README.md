# EKS: realtime-backend (P6-003)

Deploy **in-process ASR** `realtime-backend` to the [P6-002 EKS cluster](../../infra/eks/README.md) using the [P6-001 ECR image](../../infra/ecr/README.md).

Parity with [k8s/local/](../local/) (Kind), with ECR image pull and `gp2` PVC for model cache.

## Prerequisites

- P6-002 cluster and kubeconfig (`aws eks update-kubeconfig …`)
- Image pushed to ECR ([infra/ecr/README.md](../../infra/ecr/README.md))

## 1. Point the Deployment at ECR

From the **repository root**:

```bash
export AWS_REGION="${AWS_REGION:-ap-northeast-1}"
export ECR_URI="$(terraform -chdir=infra/ecr output -raw repository_url)"
export TAG="${TAG:-$(git rev-parse --short HEAD)}"

cd k8s/eks
kustomize edit set image "voragon/realtime-backend=${ECR_URI}:${TAG}"
```

This updates `kustomization.yaml` locally (do not commit your account-specific URI unless intentional).

## 2. Apply

```bash
kubectl apply -k .
kubectl wait -n voragon --for=condition=ready pod -l app=realtime-backend --timeout=600s
```

First startup may take several minutes (ASR warmup + model download into PVC).

## 3. Health check

```bash
kubectl port-forward -n voragon svc/realtime-service 8000:8000
curl -f http://localhost:8000/health
```

## 4. PVC / pod restart

```bash
kubectl delete pod -n voragon -l app=realtime-backend
kubectl wait -n voragon --for=condition=ready pod -l app=realtime-backend --timeout=600s
```

Second startup should be faster when weights are cached on the PVC.

## Replicas before ALB (P6-004)

Default **1** replica for first E2E. Before ALB Ingress, scale to **2** for rolling updates with `maxUnavailable: 0`:

```bash
kubectl scale deployment/realtime-backend -n voragon --replicas=2
```

## Related

- [k8s/README.md](../README.md) — Kind local path
- [docs/operations/aws-deployment.md](../../docs/operations/aws-deployment.md)
