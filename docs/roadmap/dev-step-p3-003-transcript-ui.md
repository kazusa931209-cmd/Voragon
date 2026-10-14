# P3-003: Transcript UI and Client State

| Field | Value |
|-------|-------|
| **ID** | P3-003 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p3-003-transcript-ui` |

## Spec References

- [Transcription API](../api/transcription.md) — partial vs final semantics
- [Realtime WebSocket API](../api/realtime-websocket.md) — `transcript.partial`, `transcript.final`

## Scope

One verifiable behavior: **the UI renders live partial text and stable final segment lines from WebSocket transcript events.**

- Hook/state layer for transcript accumulation
- Accessible transcript panel (partials + finals list)
- Tests with fixture JSON messages

## Out of Scope

- Microphone / audio streaming
- Settings persistence
- Reconnection

## Acceptance Criteria

- [x] `transcript.partial` updates a single live line
- [x] `transcript.final` appends a stable segment
- [x] Vitest covers reducer/hook behavior with fixtures

## Manual Test

1. With backend connected, use dev simulation or wait for P3-005 for live audio
2. Inject fixture messages in tests; optional dev-only simulate button

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation._
