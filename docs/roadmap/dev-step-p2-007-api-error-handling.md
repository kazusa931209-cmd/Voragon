# P2-007: API Error Handling Alignment

| Field | Value |
|-------|-------|
| **ID** | P2-007 |
| **Phase** | 2 |
| **Status** | planned |
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

- [ ] All documented server paths in this step use consistent `error` payload shape
- [ ] `INVALID_MESSAGE` and `UNKNOWN_MESSAGE_TYPE` covered by tests
- [ ] Unrecoverable error path emits `session.ended` after `error`
- [ ] Error rate limiting tested or unit-tested in isolation
- [ ] Existing backend test suite still passes (update expectations where codes change intentionally)

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
