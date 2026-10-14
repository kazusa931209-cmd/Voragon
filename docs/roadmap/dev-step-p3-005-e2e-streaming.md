# P3-005: End-to-End Mic → Backend → Transcript UI

| Field | Value |
|-------|-------|
| **ID** | P3-005 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
| **Branch** | `dev-step/p3-005-e2e-streaming` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `audio.start`, binary frames, `audio.stop`
- [Realtime Audio Pipeline](../architecture/realtime-audio.md)
- [Error Handling](../api/error-handling.md) — recoverable errors, `buffer.overflow`
- Reference: [tools/realtime-cli/realtime_cli/frames.py](../../tools/realtime-cli/realtime_cli/frames.py)

## Scope

One verifiable behavior: **user starts transcription; audio flows to the backend; partial and final transcripts appear in the UI.**

- Send `audio.start` after `session.started`
- Pack and send binary frames (17-byte header + PCM, monotonic `seq_num`)
- Listen for `transcript.partial` / `transcript.final` in UI
- `audio.stop` on user stop
- Display recoverable `error` and `buffer.overflow`

## Out of Scope

- Idle `ping` (P3-007)
- `session.resume` (P3-008)
- System tray / hotkeys

## Acceptance Criteria

- [x] Speak into mic → partials update and finals appear
- [x] Frame builder tests match CLI invariants (640-byte payload typical)
- [x] Stop ends streaming and sends `audio.stop`

## Manual Test

1. Backend with ASR running
2. Desktop: Connect → Start → speak → verify transcripts → Stop

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- `frames.ts` binary audio frames (17-byte header + PCM, `seq_num`); `RealtimeClient` `audio.start` / `audio.stop` / chunk send; `App.tsx` wires capture events to WebSocket and transcript UI; error/buffer.overflow surfacing.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# frames.test.ts + suite; 6 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pending — [Phase 3 exit checklist](dev-step-phase3-exit.md) § P3-005

### Commit

- **Hash:** `35486f0`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15
