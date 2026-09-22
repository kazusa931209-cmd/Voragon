# P1-007: Minimal Test Client (Mic → Transcript)

| Field | Value |
|-------|-------|
| **ID** | P1-007 |
| **Phase** | 1 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p1-007-minimal-test-client` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — connect, `audio.start`, binary `audio.chunk`, transcript messages
- [Transcription API](../api/transcription.md) — partial vs final display semantics
- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — 16 kHz mono s16le, 20 ms frames
- [Local Development](../operations/local-development.md) — local backend URL, Phase 1 workflow

## Scope

One verifiable behavior: **a developer can run a minimal CLI test client that captures microphone audio (or replays a file), streams it to the backend, and prints partial/final transcripts.**

- Add `tools/realtime-cli/` Python package — standalone CLI (not the Tauri desktop app)
- Connect to `ws://localhost:8000/v1/realtime` (configurable `--url`)
- Send `audio.start` with default English config after `session.started`
- Capture microphone at 16 kHz mono s16le in 20 ms frames via `sounddevice`
- Pack and send binary frames per WebSocket spec (17-byte header + PCM)
- Print `transcript.partial` and `transcript.final` to stdout; print recoverable `error` messages
- Support `--file` for mono 16 kHz WAV or raw s16le replay (CI-friendly, no mic required)
- Optional `--duration`, `--device`, `--language`, `--realtime`, `--tail` flags
- **File replay extension:** send `audio.stop` after upload; default fast pacing; wait for late transcripts (`--tail`, default 60 s)
- **Backend extension:** handle `audio.stop` — flush open VAD segment and emit `transcript.final` (does not change live VAD frame processing)
- Combined finals summary at CLI exit; revisable partial line on stdout
- Automated tests for frame packing, display formatting, file iteration, mock-server client flow, and `audio.stop` flush

## Out of Scope

- Tauri desktop app (Phase 3)
- `session.ended`, reconnect, ping/pong
- Rich TUI (simple stdout lines only)
- Audio device enumeration UI
- Packaging as standalone binary

## Acceptance Criteria

- [x] `tools/realtime-cli` installs with `pip install -e ".[dev]"`
- [x] `python -m realtime_cli` streams microphone audio to backend and prints transcripts
- [x] `--file` replays PCM/WAV without microphone
- [x] Client sends valid binary frames (640-byte payload for 20 ms @ 16 kHz)
- [x] Partial and final transcript lines appear on stdout
- [x] File replay sends `audio.stop` and receives `[final]` for open segments
- [x] `--tail` keeps connection open for late CPU ASR results
- [x] Combined finals summary printed at session end
- [x] Automated tests pass for frames, display, audio source, mock WebSocket session, and `audio.stop`
- [x] Existing backend P1-001–P1-006 tests still pass

## Manual Test

1. Start backend with real ASR + VAD:
   ```bash
   cd backend && source .venv/bin/activate && python -m app.main
   ```
2. In another terminal:
   ```bash
   cd tools/realtime-cli && source .venv/bin/activate && pip install -e ".[dev]"
   python -m realtime_cli --duration 15
   ```
3. Speak into the microphone — verify `[partial]` lines update and `[final]` lines appear after pauses
4. File replay (fast upload + stop flush + tail wait for CPU ASR):
   ```bash
   python -m realtime_cli --file sample-mono-16khz.wav --tail 90
   ```
   Expect multiple `[final]` lines and `--- combined finals ---` at exit.

## Automated Tests

```bash
cd tools/realtime-cli && pytest -v
cd ../../backend && pytest -v
```

Expected:
- Unit tests: frame header packing, transcript/error display formatting, WAV/PCM iteration
- Async test: mock WebSocket server receives `audio.start` + binary frame; client prints partial/final
- Backend suite unchanged (42+ passed)

## Spec Changes

Expected: none

Update `local-development.md` and root `README.md` with test-client usage in the same PR.

---

## Completion

### Summary

- Added `tools/realtime-cli/` — Python CLI with microphone capture (`sounddevice`) and PCM/WAV file replay
- Implements WebSocket client: `session.started` → `audio.start` → binary frames → `audio.stop` (file mode) → transcript display
- Backend: `audio.stop` flushes open VAD segments via `SegmentTracker.flush_active_segment()`; Silero iterator reset on flush
- CLI: file mode defaults to fast upload, `--tail` (60 s), combined finals summary, revisable partial line
- Modules: `frames`, `audio_source`, `client`, `display`, `__main__`
- Tests: CLI (11), backend `test_audio_stop.py`, segment tracker flush

### Spec Changes

- `docs/operations/local-development.md` — test client setup, file replay with `--tail`
- `README.md` — Phase 1 quick start with backend + CLI
- `docs/architecture/backend.md` — noted P1-007 `audio.stop` segment flush

### Automated Tests Run

```bash
cd tools/realtime-cli && pytest -v
# 11 passed

cd backend && pytest -v
# 46 passed, 1 skipped
```

### Manual Test Result

- [x] Pass — 2026-09-22 — mic streaming and file replay (`--tail`) verified; partial/final transcripts and combined summary as expected

### PR

- **URL:** —
- **Merged:** —
