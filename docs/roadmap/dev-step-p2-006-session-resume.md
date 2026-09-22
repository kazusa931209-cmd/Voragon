# P2-006: `session.resume` Reconnection

| Field | Value |
|-------|-------|
| **ID** | P2-006 |
| **Phase** | 2 |
| **Status** | planned |
| **PR** | — |
| **Branch** | `dev-step/p2-006-session-resume` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `session.resume`, reconnection flow
- [Error Handling](../api/error-handling.md) — reconnection protocol, `SESSION_NOT_FOUND`, `SESSION_EXPIRED`, state recovery

## Scope

One verifiable behavior: **a client can reconnect within the window, send `session.resume` with the previous `session_id`, and continue streaming on the restored session.**

- After new WebSocket connect, server sends `session.started` (interim new id per spec flow)
- Client sends `session.resume` with **previous** `session_id` in envelope
- Within window: bind connection to restored session; emit `session.started` (or spec-aligned confirmation) with **restored** `session_id` and prior `reconnect_window_s`; allow `audio.start` / chunks to continue
- Outside window or unknown id: `error` `SESSION_NOT_FOUND` or `SESSION_EXPIRED`; client may start fresh with `audio.start`
- Transcript history during disconnect is **not** replayed (per error-handling state recovery)
- Resolve any ambiguity between [realtime-websocket.md](../api/realtime-websocket.md) and [error-handling.md](../api/error-handling.md) in this PR if needed

## Out of Scope

- Desktop reconnection UI (Phase 3)
- Cross-pod session migration
- Auth token refresh on reconnect
- Offline audio catch-up

## Acceptance Criteria

- [ ] Disconnect → reconnect within 30 s → `session.resume` → same logical session continues (same `session_id` on wire after restore)
- [ ] `audio.start` and chunks work after resume; partial/final transcripts still emit
- [ ] Resume after window fails with correct error code; new session path still works
- [ ] Automated WebSocket integration test covers happy path and expired session
- [ ] Existing backend test suite still passes

## Manual Test

1. Connect, `audio.start`, stream, disconnect network tab or kill client
2. Reconnect within 30 s, `session.resume` with saved id, `audio.start`, stream → transcripts resume
3. Repeat with > 30 s delay → expect session error and new session

## Automated Tests

```bash
cd backend && pytest -v -k "resume or reconnect"
cd backend && pytest -v
```

## Spec Changes

Expected: reconcile reconnect message sequence in API docs if implementation picks one canonical flow

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
