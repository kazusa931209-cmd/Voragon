# P2-009: Structured JSON Logging

| Field | Value |
|-------|-------|
| **ID** | P2-009 |
| **Phase** | 2 |
| **Status** | planned |
| **PR** | — |
| **Branch** | `dev-step/p2-009-structured-json-logging` |

## Spec References

- [Observability](../operations/observability.md) — structured logging format
- [Error Handling](../api/error-handling.md) — logging guidelines (no transcript text in error logs by default)
- [Backend Architecture](../architecture/backend.md)

## Scope

One verifiable behavior: **the backend emits structured JSON logs to stdout suitable for production ingestion, with a dev-friendly option.**

- Configure logging via settings (e.g. `LOG_FORMAT=json|console`, default `console` for local dev)
- JSON fields at minimum: `timestamp`, `level`, `service` (`realtime-service`), `message`, optional `session_id`, `code` for errors
- Replace ad-hoc `print` / unstructured logs in WebSocket and pipeline paths touched in Phase 2
- Request/session lifecycle events: connect, disconnect, resume, session end (no audio/transcript content)
- Phase 2 exit step: completes observability slice with P2-008

## Out of Scope

- CloudWatch / centralized log shipping
- Trace IDs (OpenTelemetry)
- Log rotation (container runtime handles)

## Acceptance Criteria

- [ ] `LOG_FORMAT=json` produces one JSON object per log line on stdout
- [ ] WebSocket connect/disconnect and error paths include structured fields
- [ ] No transcript text logged at default log levels
- [ ] `LOG_FORMAT=console` remains readable for local development
- [ ] Tests for log formatter or snapshot of JSON structure (lightweight)
- [ ] Existing backend test suite still passes

## Manual Test

1. `LOG_FORMAT=json python -m app.main` → connect client → verify JSON lines on stdout
2. Trigger recoverable error → log line includes `code` without transcript body

## Automated Tests

```bash
cd backend && pytest -v -k "logging or log_format"
cd backend && pytest -v
```

## Spec Changes

Expected: `docs/operations/local-development.md` — logging env vars

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

### PR

- **URL:** —
- **Merged:** —
