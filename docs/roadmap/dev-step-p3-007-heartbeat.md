# P3-007: Client Heartbeat and Session Lifecycle

| Field | Value |
|-------|-------|
| **ID** | P3-007 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p3-007-heartbeat` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md#heartbeat) — 15 s `ping`, idle while not streaming
- [dev-step-p2-001](dev-step-p2-001-ping-pong-heartbeat.md) — server behavior

## Scope

One verifiable behavior: **while connected and not streaming audio, the client sends `ping` every 15 s; stop sends `audio.stop`; server `session.ended` is handled cleanly.**

- Ping timer when connected and not actively sending `audio.chunk`
- No ping requirement during active streaming
- Resume ping after `audio.stop`
- Handle `session.ended` (clear session, update UI)

## Out of Scope

- `session.resume` (P3-008)
- Server changes

## Acceptance Criteria

- [x] Connected idle >45 s without ping does not occur (ping every 15 s)
- [x] During streaming, connection stays alive via chunks
- [x] Stop transcription sends `audio.stop`
- [x] Unit tests for ping scheduling logic

## Manual Test

1. Connect without starting transcription; wait 60 s — connection remains
2. Start/stop transcription; verify `audio.stop` and finals

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation._
