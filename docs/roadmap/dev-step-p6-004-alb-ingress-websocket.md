# P6-004: ALB Ingress for WebSocket

| Field | Value |
|-------|-------|
| **ID** | P6-004 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-004-alb-ingress-websocket` |

## Spec References

- [Kubernetes Architecture](../architecture/kubernetes.md) — WebSocket Scaling, Networking
- [ADR-004: Realtime WebSocket](../decisions/ADR-004-realtime-websocket.md)
- [realtime-websocket API](../api/realtime-websocket.md) — path `/v1/realtime`
- [dev-step-p6-003](dev-step-p6-003-eks-realtime-manifests.md)

## Scope

One verifiable behavior: **external HTTPS/WSS reaches `realtime-service` through AWS Load Balancer Controller (ALB Ingress); WebSocket upgrade to `/v1/realtime` works from outside the cluster.**

- Install AWS Load Balancer Controller on P6-002 cluster
- Ingress (or IngressClass) targeting `realtime-service:8000`
- Sticky sessions enabled for WebSocket affinity (architecture doc)
- Document ALB listener, target group health check on `/health`
- TLS: ACM cert on ALB (full custom domain in P6-007 if cert not ready here — document minimum for staging hostname)

## Out of Scope

- API Gateway authorizer (P6-005) — may test direct ALB URL first
- `preStop` graceful drain (optional enhancement; document limitation if deferred)
- Multi-replica HPA tuning

## Acceptance Criteria

- [ ] ALB provisioned by Ingress; DNS name or custom hostname documented
- [ ] `curl -f https://<host>/health` returns healthy after warmup
- [ ] WebSocket client connects to `wss://<host>/v1/realtime` and receives `session.started`
- [ ] Sticky session / target group attributes documented per architecture

## Manual Test

1. Deploy Ingress; wait for ALB active
2. Health check via public URL
3. Use desktop (staging URL) or `websocat`/test client — connect, `session.started`
4. Optional: brief audio → partial transcript (CPU inference)

## Automated Tests

```bash
cd backend && pytest -q
```

## Spec Changes

Expected: [aws-deployment.md](../operations/aws-deployment.md) — ALB Ingress section implemented.

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
