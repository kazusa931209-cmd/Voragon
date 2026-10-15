# Phase 5 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 5 |
| **Status** | planned — pending manual sign-off |
| **Dev-steps** | [P5-001](dev-step-p5-001-kind-cluster.md)–[P5-005](dev-step-p5-005-k8s-dev-docs-exit.md) |

## Exit Criteria ([phases.md](phases.md))

- [ ] Services deploy and pass health checks on Kind
- [ ] Desktop connects via port-forward
- [ ] Rolling restart works without manual pod delete

## Prerequisites

See [k8s/README.md](../../k8s/README.md) and [kubernetes-local.md](../operations/kubernetes-local.md).

```bash
# One-time (or after cluster delete)
kind create cluster --name voragon --config k8s/kind/voragon.yaml
docker build -f docker/realtime-backend/Dockerfile -t voragon/realtime-backend:local .
kind load docker-image voragon/realtime-backend:local --name voragon

kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/
kubectl wait -n voragon --for=condition=ready pod -l app=realtime-backend --timeout=300s

kubectl port-forward -n voragon svc/realtime-service 8000:8000
cd desktop && pnpm tauri dev
```

## Manual Checklist

- [ ] Follow [k8s/README.md](../../k8s/README.md) from repo root — Kind + kubectl installed
- [ ] `curl -f http://localhost:8000/health` after port-forward (healthy after warmup)
- [ ] Desktop **Connect** → **Start transcription** → partials/finals
- [ ] `kubectl delete pod -n voragon -l app=realtime-backend` → new pod Ready; faster warmup (PVC cache)
- [ ] `kubectl rollout restart deployment/realtime-backend -n voragon` → rollout succeeds; port-forward restored → health OK

## Automated Tests (agent / CI)

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

| Run | Date | Result |
|-----|------|--------|
| pytest + desktop Vitest | 2026-10-15 | 93 passed, 1 skipped; 14 Vitest passed |

## Sign-Off

When complete:

1. [ ] **Status** `done` (header).
2. [ ] [phases.md](phases.md) Phase 5 **Status** complete with exit sign-off.
3. [ ] [dev-steps-index.md](dev-steps-index.md) — Phase 5 exit complete; **Active Step** → Phase 6 planning.
4. [ ] [P5-001](dev-step-p5-001-kind-cluster.md)–[P5-005](dev-step-p5-005-k8s-dev-docs-exit.md) **Manual Test Result** pass with date in **Completion**.
