# P2-006: `session.resume` Reconnection

| Field | Value |
|-------|-------|
| **ID** | P2-006 |
| **Phase** | 2 |
| **Status** | done |
| **Commit** | [`bc0fcb1`](https://github.com/kazusa931209-cmd/Voragon/commit/bc0fcb1) on `dev` |
| **PR** | — (landed on `dev`; no separate PR) |
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

- [x] Disconnect → reconnect within 30 s → `session.resume` → same logical session continues (same `session_id` on wire after restore)
- [x] `audio.start` and chunks work after resume; partial/final transcripts still emit
- [x] Resume after window fails with correct error code; new session path still works
- [x] Automated WebSocket integration test covers happy path and expired session
- [x] Existing backend test suite still passes

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

- `RealtimeConnection` in `app/websocket/handler.py` — mutable session state for resume
- `_handle_session_resume` — `claim_detached` → `restore_session` → second `session.started`
- `claim_detached()` in `app/websocket/session_registry.py` — distinguishes `SESSION_NOT_FOUND` vs `SESSION_EXPIRED`
- Tests: `tests/test_websocket_session_resume.py`

### Spec Changes

- [realtime-websocket.md](../api/realtime-websocket.md) — status, `session.resume` envelope rules

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v -k "resume or reconnect or claim_detached"
# 8 passed

cd backend && .venv/bin/pytest -v
# 81 passed, 1 skipped
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** — (merged directly to `dev`)
- **Merged:** `dev` — [`bc0fcb1`](https://github.com/kazusa931209-cmd/Voragon/commit/bc0fcb1) (2026-10-14)
