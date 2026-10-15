# P3-003: Transcript UI and Client State

| Field | Value |
|-------|-------|
| **ID** | P3-003 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
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

### Summary

- `useTranscript` hook and transcript panel: partial line + final segments; tests in `useTranscript.test.ts`.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# 6 passed (2026-10-15)
```

### Manual Test Result

- [x] Pass — macOS, 2026-10-15 ([Phase 3 exit § P3-003 / P3-005](dev-step-phase3-exit.md))

### Commit

- **Hash:** `35486f0`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15
