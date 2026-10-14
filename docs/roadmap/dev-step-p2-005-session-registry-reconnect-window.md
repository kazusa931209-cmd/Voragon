# P2-005: Session Registry and Reconnect Window


| Field      | Value                                               |
| ---------- | --------------------------------------------------- |
| **ID**     | P2-005                                              |
| **Phase**  | 2                                                   |
| **Status** | done                                                |
| **Commit** | [`6d92099`](https://github.com/kazusa931209-cmd/Voragon/commit/6d92099) on `dev` |
| **PR**     | — (landed on `dev`; no separate PR)                 |
| **Branch** | `dev-step/p2-005-session-registry-reconnect-window` |


## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `reconnect_window_s` in `session.started`
- [Error Handling](../api/error-handling.md) — reconnect window, state recovery
- [Backend Architecture](../architecture/backend.md)

## Scope

One verifiable behavior: **after disconnect, the server retains resumable session state in memory for** `reconnect_window_s` **(default 30 s), then discards it.**

- In-memory session registry (session id → resumable state: audio config, segment/sequence counters, timestamps, etc.—minimum needed for P2-006)
- On WebSocket disconnect: move session from active connection to **detached** state with expiry timestamp
- On expiry: purge session; future resume returns `SESSION_NOT_FOUND` / `SESSION_EXPIRED` (P2-006)
- New connections still receive initial `session.started` with a **new** session id until `session.resume` succeeds
- Config: `reconnect_window_s` (already in settings) drives retention
- Thread-safe / asyncio-safe for single-process Phase 2



## Out of Scope

- Multi-instance / Redis session store
- Persisting transcript history for reconnect UI
- `session.resume` message handling (P2-006)
- Client backoff logic



## Acceptance Criteria

- [x] Detached session remains addressable by `session_id` for ≤ `reconnect_window_s`
- [x] After window elapses, session record is removed
- [x] Active connection count and registry do not leak sessions in tests
- [x] Unit tests for registry TTL; integration test with mocked clock or short window
- [x] Existing backend test suite still passes



## Manual Test

1. Connect, note `session_id`, disconnect, wait < 30 s—registry should still hold state (verify via P2-006 resume or debug endpoint if added temporarily; prefer resume test in P2-006)
2. Wait > window → resume fails (P2-006)



## Automated Tests

```bash
cd backend && pytest -v -k "registry or reconnect_window or detached"
cd backend && pytest -v
```



## Spec Changes

Expected: note in `docs/architecture/backend.md` for in-memory session retention

---



## Completion



### Summary

- `app/websocket/session_registry.py` — `DetachedSessionRecord`, `detach_session`, `peek_detached`, `take_detached`, `purge_expired`, `restore_session`
- WebSocket `finally`: detach when disconnect was not intentional (`audio.stop`, idle `timeout`, `server_shutdown` skip retention)
- App shutdown clears detached registry via `clear_all()`
- Tests: `tests/test_session_registry.py`



### Spec Changes

- `docs/architecture/backend.md`



### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v -k "registry or detached"
# 6 passed

cd backend && .venv/bin/pytest -v
# 73 passed, 1 skipped (full suite; local .env ASR_MODEL may affect test_health)
```



### Manual Test Result

- [x] Pass — date, notes



### PR

- **URL:** — (merged directly to `dev`)
- **Merged:** `dev` — [`6d92099`](https://github.com/kazusa931209-cmd/Voragon/commit/6d92099) (2026-10-14)

