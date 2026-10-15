# P3-008: `session.resume` Reconnection

| Field | Value |
|-------|-------|
| **ID** | P3-008 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
| **Branch** | `dev-step/p3-008-session-resume` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `session.resume`, reconnection
- [Error Handling](../api/error-handling.md) — `SESSION_NOT_FOUND`, `SESSION_EXPIRED`
- [dev-step-p2-006](dev-step-p2-006-session-resume.md)

## Scope

One verifiable behavior: **after unexpected disconnect within `reconnect_window_s`, the client reconnects, sends `session.resume` with the previous session id, and continues on the restored session or falls back to a fresh session.**

- Track previous vs interim session ids per spec
- Auto-reconnect with resume when window allows
- UI: reconnecting state; toast on unrecoverable session errors
- Vitest for resume success/failure sequences

## Out of Scope

- Transcript replay after disconnect
- Cross-machine resume

## Acceptance Criteria

- [x] Kill backend mid-session; restore within window → resume and continue streaming
- [x] Expired session → fresh session without crash
- [x] Tests cover connect → disconnect → resume flows

## Manual Test

1. Start transcription; stop backend briefly; restart within 30 s; continue speaking

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- Auto-reconnect on unexpected close; `session.resume` with `lastSessionId` within `reconnect_window_s`; `reconnecting` state; fresh session on `SESSION_NOT_FOUND` / `SESSION_EXPIRED`; Vitest resume sequences.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# 6 passed (2026-10-15)
```

### Manual Test Result

- [x] Pass — macOS, 2026-10-15 ([Phase 3 exit § P3-008](dev-step-phase3-exit.md))

### Commit

- **Hash:** `35486f0`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15
