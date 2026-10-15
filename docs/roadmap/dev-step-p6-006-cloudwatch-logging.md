# P6-006: CloudWatch Logging

| Field | Value |
|-------|-------|
| **ID** | P6-006 |
| **Phase** | 6 |
| **Status** | planned |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p6-006-cloudwatch-logging` |

## Spec References

- [Observability](../operations/observability.md)
- [dev-step-p2-009](dev-step-p2-009-structured-json-logging.md)
- [AWS Deployment](../operations/aws-deployment.md)
- [dev-step-p6-003](dev-step-p6-003-eks-realtime-manifests.md)

## Scope

One verifiable behavior: **structured JSON logs from `realtime-backend` pods appear in CloudWatch Logs with a documented log group and retention.**

- DaemonSet or sidecar pattern (e.g. Fluent Bit / CloudWatch agent) — document choice
- Log group naming convention (e.g. `/voragon/eks/realtime-backend`)
- Correlate with existing JSON log fields from P2-009

## Out of Scope

- Amazon Managed Prometheus / Grafana dashboards (future)
- GPU / ASR service logs (Phase 7)
- Log-based alerting

## Acceptance Criteria

- [ ] Pod stdout/stderr shipped to CloudWatch
- [ ] Operator can find recent logs by pod name or `session_id` field in Logs Insights
- [ ] Setup documented in [aws-deployment.md](../operations/aws-deployment.md) or [observability.md](../operations/observability.md)

## Manual Test

1. Deploy logging stack; generate traffic (health + short WebSocket session)
2. CloudWatch Logs console — new events within expected delay
3. Run sample Logs Insights query from docs

## Automated Tests

```bash
cd backend && pytest -q
```

## Spec Changes

Expected: [observability.md](../operations/observability.md) — CloudWatch section status.

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
