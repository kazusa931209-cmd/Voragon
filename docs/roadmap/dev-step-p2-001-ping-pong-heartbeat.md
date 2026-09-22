# P2-001: `ping` / `pong` Heartbeat

| Field | Value |
|-------|-------|
| **ID** | P2-001 |
| **Phase** | 2 |
| **Status** | in-progress |
| **PR** | — |
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

- [ ] Valid `ping` receives `pong` with correct envelope
- [ ] No `ping` for 45 s (configurable) ends the connection (idle timeout hook for P2-002)
- [ ] Malformed `ping` receives recoverable `error` (align with P2-007 when merged; until then, match existing error style)
- [ ] Automated WebSocket tests cover ping/pong and idle timeout (use short timeout in test settings)
- [ ] Existing backend test suite still passes

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
