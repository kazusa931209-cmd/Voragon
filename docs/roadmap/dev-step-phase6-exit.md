# Phase 6 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 6 |
| **Status** | planned — pending manual sign-off |
| **Dev-steps** | [P6-001](dev-step-p6-001-ecr-image-push.md)–[P6-008](dev-step-p6-008-aws-dev-docs-exit.md) |

## Exit Criteria ([phases.md](phases.md))

- [ ] Desktop connects to production WebSocket endpoint
- [ ] Authentication works
- [ ] Transcription works (CPU inference initially)
- [ ] Logs visible in CloudWatch

## Prerequisites

See [aws-deployment.md](../operations/aws-deployment.md) and P6-001–P6-007 completion.

```bash
# High level — exact commands in aws-deployment.md after implementation
# 1. Push image (P6-001)
# 2. EKS cluster + deploy (P6-002, P6-003)
# 3. ALB + API Gateway + DNS (P6-004–P6-007)
# 4. Desktop: production URL + JWT → Connect → Start transcription
```

## Manual Checklist

- [ ] Follow [aws-deployment.md](../operations/aws-deployment.md) from repo root — AWS CLI, kubectl, credentials
- [ ] `curl -f https://<api-host>/health` (public URL)
- [ ] Obtain JWT per docs; desktop **Connect** → **Start transcription** → partials/finals
- [ ] Invalid/missing token rejected at gateway
- [ ] CloudWatch Logs show recent structured logs from realtime pods
- [ ] `kubectl rollout restart deployment/realtime-backend -n voragon` (or documented namespace) succeeds; client reconnect acceptable

## Automated Tests (agent / CI)

```bash
cd backend && pytest -q
cd desktop && pnpm test
```

| Run | Date | Result |
|-----|------|--------|
| — | — | — |

## Sign-Off

When complete:

1. [ ] **Status** `done` (header).
2. [ ] [phases.md](phases.md) Phase 6 **Status** complete with exit sign-off.
3. [ ] [dev-steps-index.md](dev-steps-index.md) — Phase 6 exit complete; **Active Step** → Phase 7 planning.
4. [ ] [P6-001](dev-step-p6-001-ecr-image-push.md)–[P6-008](dev-step-p6-008-aws-dev-docs-exit.md) **Manual Test Result** pass with date in **Completion**.
