# Phase 6 Exit Verification


| Field         | Value                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------ |
| **Phase**     | 6                                                                                          |
| **Status**    | ready — pending operator manual sign-off                                                   |
| **Dev-steps** | [P6-001](dev-step-p6-001-ecr-image-push.md)–[P6-008](dev-step-p6-008-aws-dev-docs-exit.md) |


## Exit Criteria ([phases.md](phases.md))

- [ ] Desktop connects to production WebSocket endpoint
- [ ] Authentication works
- [ ] Transcription works (CPU inference initially)
- [ ] Logs visible in CloudWatch

## Prerequisites

P6-001–P6-008 complete in repo. Follow the ordered table in [aws-deployment.md — Contributor path](../operations/aws-deployment.md#contributor-path-phase-6-end-to-end), then run the manual checklist below.

```bash
# After P6-001–P6-007 infrastructure:
curl -f "https://<api-host>/health"
# Mint JWT — see infra/apigateway README
# Desktop — see desktop/README.md#production-aws-staging
```



## Manual Checklist

- [ ] Follow [aws-deployment.md](../operations/aws-deployment.md#contributor-path-phase-6-end-to-end) from repo root — AWS CLI, kubectl, credentials
- [ ] `curl -f https://<api-host>/health` (public URL; valid TLS chain for intended hostname)
- [ ] Obtain JWT per [infra/apigateway](../../infra/apigateway/README.md); desktop **Connect** → **Start transcription** → partials/finals
- [ ] Invalid/missing token rejected at connect (4401)
- [ ] CloudWatch Logs show recent structured logs from realtime pods ([k8s/eks/logging](../../k8s/eks/logging/README.md))
- [ ] `kubectl rollout restart deployment/realtime-backend -n voragon` (or documented namespace) succeeds; client reconnect acceptable



## Automated Tests (agent / CI)

```bash
cd backend && pytest -q
cd desktop && pnpm test
```


| Run | Date | Result |
| --- | ---- | ------ |
| —   | —    | —      |




## Sign-Off

When complete:

1. [ ] **Status** `done` (header).
2. [ ] [phases.md](phases.md) Phase 6 **Status** complete with exit sign-off.
3. [ ] [dev-steps-index.md](dev-steps-index.md) — Phase 6 exit complete; **Active Step** → Phase 7 planning.
4. [ ] [P6-001](dev-step-p6-001-ecr-image-push.md)–[P6-008](dev-step-p6-008-aws-dev-docs-exit.md) **Manual Test Result** pass with date in **Completion**.

