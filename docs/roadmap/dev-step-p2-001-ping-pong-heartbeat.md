# P2-001: `ping` / `pong` Heartbeat

| Field | Value |
|-------|-------|
| **ID** | P2-001 |
| **Phase** | 2 |
| **Status** | done |
| **PR** | [#9](https://github.com/kazusa931209-cmd/Voragon/pull/9) |
| **Branch** | `dev-step/p2-001-ping-pong-heartbeat` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `ping`, `pong`, heartbeat parameters
- [Backend Architecture](../architecture/backend.md) — WebSocket handler

## Scope

One verifiable behavior: **the server responds to client `ping` with `pong` and ends idle sessions when no heartbeat is received within the spec timeout.**

- Handle JSON `ping` (valid envelope) → immediate `pong` with same `session_id`
- Track last heartbeat time per connection; configurable idle timeout (default **45 s** per spec)
- On idle timeout: close the connection (P2-002 adds `session.ended` with `reason: "timeout"` on the same path)
- Reject or ignore `ping` before required envelope fields are present per existing validation patterns
- Update tests that currently expect `UNKNOWN_MESSAGE_TYPE` for `ping`

## Out of Scope

- Client-side 15 s ping interval (desktop / CLI)
- Authentication
- `session.resume`
- Prometheus metrics (P2-008)

## Acceptance Criteria

- [x] Valid `ping` receives `pong` with correct envelope
- [x] No `ping` for 45 s (configurable) ends the connection (idle timeout hook for P2-002)
- [x] Malformed `ping` receives recoverable `error` (align with P2-007 when merged; until then, match existing error style)
- [x] Automated WebSocket tests cover ping/pong and idle timeout (use short timeout in test settings)
- [x] Existing backend test suite still passes

## Manual Test

1. Start backend; connect with `wscat` or realtime-cli after it sends `ping` (optional CLI update) or a one-off script
2. Send `ping` → verify `pong`
3. Connect and wait > idle timeout without sending `ping` → verify connection closes and `session.ended` if implemented in this step

## Automated Tests

```bash
cd backend && pytest -v -k "ping or pong or heartbeat"
cd backend && pytest -v
```

## Spec Changes

Documented before implementation (P2-001 spec PR):

- [Realtime WebSocket API](../api/realtime-websocket.md) — `ping`/`pong` rules, expanded [Heartbeat](../api/realtime-websocket.md#heartbeat) (liveness, idle timer, P2-001 vs P2-002)
- [Error Handling](../api/error-handling.md) — heartbeat idle timeout behavior
- [Backend Architecture](../architecture/backend.md) — `HEARTBEAT_IDLE_TIMEOUT_S`, idle task, session `last_activity_at`
- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — heartbeat alignment
- [Local Development](../operations/local-development.md) — env var
- `backend/.env.example` — `HEARTBEAT_IDLE_TIMEOUT_S`

---

## Completion

### Summary

- Added `HEARTBEAT_IDLE_TIMEOUT_S` (default 45) in `app/config.py`
- `pong()` builder in `messages.py`; `_handle_ping()` and per-connection idle watchdog in `handler.py`
- Any inbound WebSocket message resets the idle timer; expiry closes with code 1000 (no `session.ended` until P2-002)
- Tests: `tests/test_heartbeat.py`; updated session/audio/transcript tests for `ping` handling

### Spec Changes

- See **Spec Changes** section above (documented before code)

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v
# 51 passed, 1 skipped
```

### Manual Test Result

- [x] Pass — 2026-09-22 — ping/pong and idle timeout verified locally

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/9
- **Merged:** 2026-09-22
