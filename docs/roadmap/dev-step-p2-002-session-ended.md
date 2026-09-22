# P2-002: `session.ended` Lifecycle

| Field | Value |
|-------|-------|
| **ID** | P2-002 |
| **Phase** | 2 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p2-002-session-ended` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `session.ended`, reasons (`client_stop`, `timeout`, `error`, `server_shutdown`)
- [Error Handling](../api/error-handling.md) — unrecoverable errors then `session.ended`

## Scope

One verifiable behavior: **the server emits `session.ended` when a session ends for defined reasons and then closes the WebSocket.**

- On client WebSocket close or after `audio.stop` when the session is finished (define consistent rule: e.g. `audio.stop` → flush ASR/VAD then `session.ended` `client_stop`)
- On heartbeat idle timeout (`reason: "timeout"`) if not fully covered in P2-001
- On application shutdown: graceful `session.ended` `server_shutdown` for open sessions (lifespan hook)
- On unrecoverable `error` (wire when fatal errors are introduced; at minimum document hook for P2-007)
- `session.ended` uses JSON envelope; `payload.reason` per API table

## Out of Scope

- Retaining session state after disconnect (P2-005)
- `session.resume` (P2-006)
- Auth / rate limits

## Acceptance Criteria

- [x] Client disconnect produces `session.ended` with `client_stop` (or documented mapping) before socket close when possible
- [x] Defined `audio.stop` end-of-session behavior matches spec and docs
- [x] Server shutdown sends `server_shutdown` to connected clients
- [x] Automated tests cover disconnect and `audio.stop` paths
- [x] Existing backend test suite still passes

## Manual Test

1. Connect, `audio.start`, stream briefly, `audio.stop` → receive `session.ended`
2. Connect and close client abruptly → server logs/cleanup; `session.ended` if client still connected long enough to receive it
3. Stop backend process with active session → clients receive `server_shutdown` when feasible

## Automated Tests

```bash
cd backend && pytest -v -k "session_ended"
cd backend && pytest -v
```

## Spec Changes

Expected: update `docs/architecture/backend.md` session lifecycle note if behavior differs from Phase 1

---

## Completion

### Summary

- `session_ended()` in `messages.py`; `end_session(reason)` in WebSocket handler
- `audio.stop` → flush → `session.ended` `client_stop` → close
- Idle timeout → `session.ended` `timeout` → close
- Handler `finally` → `client_stop` when the client disconnects without a prior end
- `connection_registry` + `shutdown_all()` on app lifespan exit for `server_shutdown`
- Tests: `tests/test_session_ended.py`; updated audio/heartbeat tests

### Spec Changes

- `docs/architecture/backend.md`, `docs/api/realtime-websocket.md`, `docs/api/error-handling.md`

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v
# 56 passed, 1 skipped
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
