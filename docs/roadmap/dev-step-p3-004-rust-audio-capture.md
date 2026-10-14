# P3-004: Rust Audio Capture + IPC

| Field | Value |
|-------|-------|
| **ID** | P3-004 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p3-004-rust-audio-capture` |

## Spec References

- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — 16 kHz mono s16le, 20 ms frames
- [ADR-002: Rust Native Layer](../decisions/ADR-002-rust-native-layer.md)
- [Desktop Architecture](../architecture/desktop.md) — audio capture flow

## Scope

One verifiable behavior: **Rust captures microphone PCM, accumulates 20 ms (640-byte) frames, and emits them to the frontend via Tauri events.**

- `cpal` capture with frame accumulator (320 samples)
- Resample/downmix to 16 kHz mono when needed
- Tauri commands: start/stop capture; event `audio-frame` with frame payload
- macOS `NSMicrophoneUsageDescription` in Info.plist

## Out of Scope

- WebSocket send from frontend (P3-005)
- Input device picker (P3-006)
- Windows-specific validation (P3-009)

## Acceptance Criteria

- [x] Start capture from UI; frames emitted at ~50/s
- [x] Each frame is 640 bytes s16le mono @ 16 kHz
- [x] Rust unit tests for frame assembly logic
- [x] Stop capture releases device

## Manual Test

1. Launch app; start capture; speak; observe frame counter or debug log

## Automated Tests

```bash
cd desktop/src-tauri && cargo test
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation._
