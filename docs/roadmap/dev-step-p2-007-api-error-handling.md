# P2-007: API Error Handling Alignment

| Field | Value |
|-------|-------|
| **ID** | P2-007 |
| **Phase** | 2 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p2-007-api-error-handling` |

## Spec References

- [Error Handling](../api/error-handling.md) — error envelope, codes, severity, server guidelines
- [Realtime WebSocket API](../api/realtime-websocket.md) — `error` message shape

## Scope

One verifiable behavior: **server-emitted errors match the API spec (codes, `recoverable`, envelope) and fatal errors end the session per guidelines.**

- Centralize error emission helper(s) in `app/websocket/` (or `app/errors.py`)
- Validate inbound JSON control messages; malformed → `INVALID_MESSAGE` (`recoverable: true`)
- Keep `UNKNOWN_MESSAGE_TYPE` for unrecognized `type`
- Map existing paths: `AUDIO_NOT_STARTED`, `INVALID_AUDIO_FORMAT`, ASR/VAD failures → spec codes where already partially implemented
- Session errors from resume: `SESSION_NOT_FOUND`, `SESSION_EXPIRED`
- For unrecoverable errors: emit `error` then `session.ended` `reason: "error"` (coordinate with P2-002)
- Per-session error rate limit (max **10/s** per spec) to prevent storms
- Tests assert code + recoverable flag for representative cases

## Out of Scope

- `AUTH_*` and production connection rejection (later phase)
- Client UI for errors
- OpenTelemetry

## Acceptance Criteria

- [x] All documented server paths in this step use consistent `error` payload shape
- [x] `INVALID_MESSAGE` and `UNKNOWN_MESSAGE_TYPE` covered by tests
- [x] Unrecoverable error path emits `session.ended` after `error`
- [x] Error rate limiting tested or unit-tested in isolation
- [x] Existing backend test suite still passes (update expectations where codes change intentionally)

## Manual Test

1. Send malformed JSON and missing `type` → `INVALID_MESSAGE`
2. Send unknown `type` → `UNKNOWN_MESSAGE_TYPE`
3. Trigger `AUDIO_NOT_STARTED` (chunk before start) → correct code

## Automated Tests

```bash
cd backend && pytest -v -k "error"
cd backend && pytest -v
```

## Spec Changes

Expected: none unless code inventory reveals spec gaps (document in Completion)

---

## Completion

### Summary

- Added `WebSocketErrorEmitter` ([`backend/app/websocket/errors.py`](../../backend/app/websocket/errors.py)) with spec `recoverable` defaults, resume errors that do not terminate the connection, fatal → `session.ended` `reason: "error"`, and 10/s rate limiting via `error_max_per_second`.
- Shared `PerSecondRateLimiter` in [`backend/app/websocket/rate_limit.py`](../../backend/app/websocket/rate_limit.py); buffer overflow notifier reuses it; `BUFFER_OVERFLOW` errors go through the emitter.
- Handler routes all server errors through the emitter; inbound JSON validates object root and `type`; unexpected handler exceptions → `INTERNAL_ERROR`; `ASRModelUnavailableError` → `ASR_MODEL_UNAVAILABLE` (fatal).

### Spec Changes

- None — behavior matches existing [error-handling.md](../api/error-handling.md).

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v -k "error"   # 21 passed
cd backend && .venv/bin/pytest -v                # 87 passed, 1 skipped
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
