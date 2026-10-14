# P2-008: Prometheus `/metrics`

| Field | Value |
|-------|-------|
| **ID** | P2-008 |
| **Phase** | 2 |
| **Status** | done |
| **Commit** | [`94d0880`](https://github.com/kazusa931209-cmd/Voragon/commit/94d0880) on `feat/steps-P2-007-008-009` |
| **PR** | — |
| **Branch** | `dev-step/p2-008-prometheus-metrics` |

## Spec References

- [Observability](../operations/observability.md) — Phase 2 metrics list, `/metrics` endpoint
- [Backend Architecture](../architecture/backend.md) — metrics phase note

## Scope

One verifiable behavior: **the realtime backend exposes Prometheus metrics at `GET /metrics` for core WebSocket and pipeline activity.**

- Add `prometheus_client` (or equivalent) dependency
- Expose `GET /metrics` on the FastAPI app (alongside `/health`)
- Minimum counters/gauges for Phase 2 (subset of observability doc):
  - `voragon_sessions_active` (gauge)
  - `voragon_ws_connections` (gauge)
  - `voragon_audio_frames_received_total` (counter)
  - `voragon_audio_frames_dropped_total` (counter; wire from buffer drops when P2-004 merged)
  - `voragon_transcript_partial_total` / `voragon_transcript_final_total` (counters)
  - `voragon_asr_inference_duration_seconds` (histogram) if ASR path is instrumented with low overhead
- Label conventions: avoid high-cardinality labels (no per-session_id on metrics)
- Document scrape URL in `local-development.md`

## Out of Scope

- Grafana dashboards (optional screenshot in docs only)
- OpenTelemetry traces (Phase 6)
- GPU metrics (Phase 7)
- Alertmanager rules

## Acceptance Criteria

- [x] `curl http://localhost:8000/metrics` returns Prometheus text format
- [x] Connecting a WebSocket increments connection gauge; disconnect decrements
- [x] Audio frames and transcripts increment counters in integration test
- [x] `/health` behavior unchanged
- [x] Automated tests for metrics endpoint presence and at least one counter movement

## Manual Test

1. Start backend; `curl -s localhost:8000/metrics | head`
2. Run realtime-cli file replay; scrape metrics again and verify counters increased

## Automated Tests

```bash
cd backend && pytest -v -k "metrics"
cd backend && pytest -v
```

## Spec Changes

Expected: `docs/operations/local-development.md` — metrics URL

---

## Completion

### Summary

- Added `prometheus-client` and [`backend/app/observability/metrics.py`](../../backend/app/observability/metrics.py) with Phase 2 gauges/counters/histogram.
- `GET /metrics` on the FastAPI app refreshes `voragon_ws_connections` and `voragon_sessions_active` at scrape time; pipeline counters updated in the WebSocket handler.
- Tests in [`backend/tests/test_metrics.py`](../../backend/tests/test_metrics.py).

### Spec Changes

- [local-development.md](../operations/local-development.md) — metrics scrape URL
- [observability.md](../operations/observability.md) — Phase 2 metrics status

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v -k "metrics"   # 3 passed
cd backend && .venv/bin/pytest -v                # 90 passed, 1 skipped
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
