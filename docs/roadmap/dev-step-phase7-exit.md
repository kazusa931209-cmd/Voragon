# Phase 7 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 7 |
| **Status** | planned — pending P7-001–P7-008 and operator sign-off |
| **Dev-steps** | [P7-001](dev-step-p7-001-gpu-node-pool.md)–[P7-008](dev-step-p7-008-gpu-dev-docs-exit.md) |

## Exit Criteria ([phases.md](phases.md))

- [ ] ASR inference runs on GPU
- [ ] Inference latency measured and recorded (engineering targets in docs)
- [ ] GPU metrics visible in dashboards or documented scrape path
- [ ] Horizontal scaling of ASR pods works (second replica or HPA smoke)

## Prerequisites

P7-001–P7-008 complete. Follow Phase 7 steps in [aws-deployment.md](../operations/aws-deployment.md) (after P7-008 updates).

## Manual Checklist

- [ ] GPU nodes Ready with device plugin
- [ ] `asr-service` on GPU; `realtime-service` uses remote ASR
- [ ] Desktop or CLI E2E: partials/finals via production/staging path
- [ ] Metrics show GPU activity during transcription
- [ ] Rollout restart of asr-service; client recovery acceptable

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
2. [ ] [phases.md](phases.md) Phase 7 **Status** complete with exit sign-off.
3. [ ] [dev-steps-index.md](dev-steps-index.md) — Phase 7 exit complete; **Active Step** → Phase 8 planning.
4. [ ] [P7-001](dev-step-p7-001-gpu-node-pool.md)–[P7-008](dev-step-p7-008-gpu-dev-docs-exit.md) **Manual Test Result** pass with date in **Completion**.
