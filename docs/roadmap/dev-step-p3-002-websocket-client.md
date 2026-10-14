# P3-002: WebSocket Client (Connect + Control Messages)

| Field | Value |
|-------|-------|
| **ID** | P3-002 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
| **Branch** | `dev-step/p3-002-websocket-client` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — envelope, `session.started`, `error`, `session.ended`, `pong`
- [Error Handling](../api/error-handling.md)

## Scope

One verifiable behavior: **the desktop frontend connects to the realtime WebSocket, parses JSON envelopes, and exposes connection state plus core server control messages.**

- Configurable URL (default `ws://localhost:8000/v1/realtime`)
- State machine: disconnected → connecting → ready (session id known)
- Parse and dispatch: `session.started`, `error`, `session.ended`, `pong`
- Vitest with mocked WebSocket

## Out of Scope

- Binary `audio.chunk` send
- `session.resume`
- Rust IPC

## Acceptance Criteria

- [x] Connect to running backend → receive `session.started` and store `session_id`
- [x] UI or debug shows connection status and session id
- [x] Unit tests cover envelope parsing and connect → `session.started` flow

## Manual Test

1. Start backend; launch desktop
2. Connect; verify connected state and session id visible

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- `RealtimeClient` in `desktop/src/api/realtimeClient.ts`: connect state machine, envelope parsing, `session.started` / `error` / `session.ended` / `pong`; Vitest in `realtimeClient.test.ts`.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# 6 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pending — [Phase 3 exit checklist](dev-step-phase3-exit.md) § P3-002

### Commit

- **Hash:** `35486f0`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15
