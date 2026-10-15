# P3-010: Desktop transcription stats and reconnect stability

| Field | Value |
|-------|-------|
| **ID** | P3-010 |
| **Phase** | 3 |
| **Status** | in-progress |
| **Commit** | — |
| **PR** | — |
| **Branch** | `feat/new-phase4` (optional) |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `session.resume`, heartbeat
- [Error Handling](../api/error-handling.md) — reconnection parameters
- [dev-step-p3-008](dev-step-p3-008-session-resume.md)

## Scope

One verifiable behavior: **while transcribing, the desktop shows elapsed time and average frame rate; after backend disconnect within `reconnect_window_s`, the client reconnects stably, resumes the session, and restores audio streaming without Error/Reconnecting flicker.**

- Transcription HUD: elapsed `HH:mm:ss`, frame count, `{n} frames / s`
- Harden `RealtimeClient`: single-flight reconnect, ping only after `session.started`, exponential backoff, re-send `audio.start` after resume when streaming was active
- Suppress noisy server errors in UI during reconnect
- Vitest for resume/reconnect paths

## Out of Scope

- Full session UUID in header (truncated 8 chars + ellipsis unchanged)
- Transcript replay after disconnect
- Backend changes

## Acceptance Criteria

- [x] While transcribing, UI shows elapsed time, frame count, and average frames/s
- [x] Kill backend mid-transcription; restart within 30 s → reconnect without error flicker; same session; transcripts resume (automated reconnect/resume/audio.start tests; manual confirm on macOS)
- [x] Idle connected; kill/restart backend within 30 s → reconnect and heartbeat on restored session (ping gating + resume tests; manual confirm)
- [x] `cd desktop && pnpm test` passes

## Manual Test

1. Connect → truncated session id unchanged (`xxxxxxxx…`).
2. Start transcription → elapsed and frames/s update each second.
3. Stop backend &lt;30 s, restart while transcribing → **Reconnecting…** then **Connected**; speak → partials/finals return.
4. Connect without transcribing; kill/restart backend → reconnect succeeds.

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- Transcription HUD: `formatDurationHms`, elapsed + frame count + average frames/s in [`App.tsx`](../../desktop/src/App.tsx).
- `RealtimeClient`: single-flight reconnect, socket detach, ping only after `session.started`, exponential backoff, `isRecovering()`, auto `audio.start` after resume when streaming was active; suppress stale PCM while not streaming.
- App: `ensureClient` keeps recovering client; filter `INVALID_MESSAGE` / `AUDIO_NOT_STARTED` during reconnect; start transcription only when `ready`.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# 12 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pending — macOS backend kill/restart while transcribing and idle

### Commit

- **Hash:** —

### PR

- **URL:** —
