# P1-004: VAD Integration (Silero)

| Field | Value |
|-------|-------|
| **ID** | P1-004 |
| **Phase** | 1 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p1-004-vad-integration` |

## Spec References

- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — VAD placement, behavior, parameters, segment semantics
- [Backend Architecture](../architecture/backend.md) — `pipeline/vad.py`, session `segments`, `VAD_BACKEND` config
- [Error Handling](../api/error-handling.md) — `VAD_FAILED` and degraded-mode behavior
- [Transcription API](../api/transcription.md) — segment lifecycle (onset → partials → offset)
- [Local Development](../operations/local-development.md) — Silero model download (~2 MB)

## Scope

One verifiable behavior: **after `audio.start`, each received audio frame is processed by Silero VAD and the session tracks speech segment lifecycle (silence ↔ speech) with stable `segment_id`s.**

- Add `app/pipeline/vad.py` — abstract VAD interface (`Protocol` or ABC)
- Add `app/pipeline/silero_vad.py` — Silero VAD implementation (loads model on first use)
- Add segment tracking on the session (active segment, open/closed segments with UUID `segment_id`)
- Process each buffered frame through VAD after `audio.chunk` reception (per-frame inference)
- Apply spec default parameters: `speech_threshold=0.5`, `min_speech_duration_ms=250`, `min_silence_duration_ms=500`, `speech_pad_ms=300`
- Expose VAD config via settings (`VAD_BACKEND`, threshold/timing params)
- On recoverable VAD failure: emit `error` with code `VAD_FAILED` and continue session (degraded: treat frames as speech — no ASR yet, but segment state should remain consistent)
- Accumulate PCM audio bytes per open segment for downstream ASR (P1-005/P1-006)
- Structured debug logging for segment open/close events (`segment_id`, duration)

## Out of Scope

- ASR adapter, model load, or inference (P1-005)
- `transcript.partial` / `transcript.final` WebSocket emission (P1-006)
- Full `orchestrator.py` pipeline coordinator (minimal inline wiring in handler is OK)
- `audio.stop`, `session.ended`
- Prometheus metrics (`voragon_vad_segments`)
- `session.resume`, `ping` / `pong`
- Authentication / TLS
- Desktop or test-client changes (P1-007)

## Acceptance Criteria

- [x] `app/pipeline/vad.py` defines a swappable VAD interface
- [x] Silero VAD implementation processes 16 kHz mono s16le frames
- [x] Session opens a new `segment_id` on speech onset and closes it on speech offset (per timing params)
- [x] Segments shorter than `min_speech_duration_ms` are discarded (no segment opened)
- [x] Open segment accumulates PCM bytes for later ASR consumption
- [x] VAD inference runs after each valid `audio.chunk` without blocking the event loop unduly (executor acceptable for CPU work)
- [x] `VAD_FAILED` error is emitted on recoverable VAD errors; session stays open
- [x] Automated tests cover segment state machine with mocked VAD and at least one Silero integration path (synthetic or fixture audio)
- [x] Existing P1-001–P1-003 tests still pass

## Manual Test

1. `cd backend && source .venv/bin/activate && pip install -e ".[dev]"` (installs new VAD deps)
2. `python -m app.main`
3. Connect, send `audio.start`, stream binary frames (silence, then speech-like audio, then silence):
   ```bash
   # Requires a small PCM fixture or mic capture script; verify server logs show
   # segment open/close with segment_id after speech-like audio.
   python -c "
   import asyncio, json, struct, websockets

   async def main():
       async with websockets.connect('ws://localhost:8000/v1/realtime') as ws:
           started = json.loads(await ws.recv())
           sid = started['session_id']
           await ws.send(json.dumps({
               'type': 'audio.start', 'id': 'msg-1', 'session_id': sid,
               'timestamp': '2026-09-22T00:00:00.000Z', 'payload': {}
           }))
           pcm = b'\\x00' * 640
           header = struct.pack('<BIQI', 1, 0, 0, len(pcm))
           for seq in range(100):
               await ws.send(header + pcm)
               await asyncio.sleep(0.02)
           print('streamed 100 silent frames — check logs for no spurious segments')
   asyncio.run(main())
   "
   ```
4. Repeat with speech audio (WAV fixture or recorded PCM) — verify logs show segment open → close
5. Confirm connection stays open; no fatal errors

## Automated Tests

```bash
cd backend && pytest -v
```

Expected:
- Unit tests: segment tracker state transitions (silence → speech → silence)
- Unit tests: VAD interface with mock implementation
- Integration test: Silero VAD on synthetic/fixture PCM (may skip if model unavailable in CI — document skip reason)
- Existing health and WebSocket tests pass

## Spec Changes

Expected: none

If Silero dependency or VAD wiring differs from `backend.md`, update that doc in the same PR.

---

## Completion

_Fill in after implementation, before PR._

### Summary

- Added `app/pipeline/vad.py` (VAD interface, config, factory) and `segment_tracker.py` (segment lifecycle + PCM accumulation)
- Added `app/pipeline/silero_vad.py` — Silero VAD with 512-sample window buffering for 20 ms frames
- Added `app/pipeline/mock_vad.py` for fast tests (`VAD_BACKEND=mock`)
- Wired VAD into WebSocket handler via executor; `VAD_FAILED` degraded mode
- Added VAD settings to `config.py`; dependencies: `silero-vad`, `torch`, `torchaudio`, `onnxruntime`
- Added `tests/test_segment_tracker.py`, `test_vad_handler.py`, `test_silero_vad.py`; `conftest.py` auto-mocks VAD

### Spec Changes

- `docs/architecture/backend.md` — noted P1-004 implemented VAD modules

### Automated Tests Run

```bash
cd backend && pytest -v
# 27 passed in 1.54s
```

### Manual Test Result

- [x] Pass — 2026-09-22, 100 silent frames over live WebSocket with Silero VAD; no errors

### PR

- **URL:** —
- **Merged:** —
