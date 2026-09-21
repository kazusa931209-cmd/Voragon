# P1-006: `transcript.partial` and `transcript.final`

| Field | Value |
|-------|-------|
| **ID** | P1-006 |
| **Phase** | 1 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p1-006-transcript` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `transcript.partial` / `transcript.final` message shapes
- [Transcription API](../api/transcription.md) — partial vs final semantics, sequence numbers, empty transcripts
- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — VAD → ASR flow, partial interval (200–500 ms)
- [Error Handling](../api/error-handling.md) — `ASR_INFERENCE_FAILED`, skip segment on failure
- [Backend Architecture](../architecture/backend.md) — handler orchestration, session state, ASR client usage

## Scope

One verifiable behavior: **after VAD detects speech, the backend invokes the in-process `ASREngine` and emits `transcript.partial` during active speech and `transcript.final` when the segment closes.**

- Add `transcript_partial()` / `transcript_final()` builders in `app/websocket/messages.py`
- Wire ASR into the WebSocket handler using `app.state.asr_engine` (loaded in P1-005 lifespan)
- On `SegmentOpened`: initialize per-segment ASR state (`segment_id`, `sequence`, `start_ms`)
- While a segment is open: periodically call `transcribe_partial` on accumulated segment PCM (throttled by config, default 300 ms)
- On `SegmentClosed`: call `transcribe_final` on segment PCM and emit `transcript.final` with `start_ms` / `end_ms`
- Track monotonic `sequence` per segment; increment for each emitted partial/final
- Track session elapsed time (ms) for `start_ms` / `end_ms` on final transcripts
- Omit `confidence` from WebSocket payload when ASR returns `None`
- Skip emission when ASR returns empty `text` (per transcription spec)
- On `ASRInferenceError`: emit `error` with code `ASR_INFERENCE_FAILED`, skip segment, continue session
- Add `ASR_PARTIAL_INTERVAL_MS` setting (default `300`)
- Automated WebSocket tests with mock VAD + mock ASR (`VAD_BACKEND=mock`, `ASR_BACKEND=mock`)

## Out of Scope

- `audio.stop`, `session.ended`, `session.resume`
- Final transcript flush for VAD degraded mode (segments may stay open indefinitely without `audio.stop`)
- `ASR_MODEL_UNAVAILABLE` fatal handling beyond existing startup failure (model is warmed at lifespan)
- Retry-once logic for `ASR_INFERENCE_FAILED` (emit error and skip segment is sufficient for P1-006)
- `whisper_cpp` adapter
- Prometheus metrics (`voragon_transcript_partial_total`, etc.)
- Desktop or standalone test client (P1-007)
- Full `pipeline/orchestrator.py` (inline handler wiring is OK, matching P1-004)

## Acceptance Criteria

- [x] Client receives `transcript.partial` while speech is ongoing (mock ASR + mock VAD segment)
- [x] Partial payload includes `segment_id`, `sequence`, `text`, `language`; `confidence` included only when present
- [x] Client receives `transcript.final` when VAD closes a segment
- [x] Final payload includes `segment_id`, `sequence`, `text`, `language`, `start_ms`, `end_ms`
- [x] `sequence` increases monotonically within a segment across partials and the final
- [x] Empty ASR results produce no partial/final message for that call
- [x] `ASR_INFERENCE_FAILED` is emitted on recoverable ASR errors; WebSocket stays open
- [x] Partial transcription is throttled (not invoked on every 20 ms frame)
- [x] Existing P1-001–P1-005 tests still pass

## Manual Test

1. `cd backend && source .venv/bin/activate && pip install -e ".[dev]"`
2. Start with mock backends for a quick check:
   ```bash
   ASR_BACKEND=mock VAD_BACKEND=mock python -m app.main
   ```
3. Connect via WebSocket, send `audio.start`, stream frames that trigger mock VAD segment open/close (or use Silero + speech fixture)
4. Verify client receives `transcript.partial` during the open segment and `transcript.final` on close
5. Repeat with `ASR_BACKEND=faster_whisper VAD_BACKEND=silero` and a short speech PCM/WAV fixture — confirm real transcripts
6. Confirm connection stays open after an ASR failure (inject by temporarily breaking mock ASR if needed)

Example WebSocket probe (mock backends, segment behavior depends on VAD mock — prefer automated test script or Silero fixture):

```bash
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
        # Stream enough frames to trigger segment lifecycle; inspect messages
        header = struct.pack('<BIQI', 1, 0, 0, 640)
        for seq in range(200):
            await ws.send(header + (b'\\x00' * 640))
            await asyncio.sleep(0.02)
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.001)
                print(json.loads(msg))
            except asyncio.TimeoutError:
                pass
asyncio.run(main())
"
```

## Automated Tests

```bash
cd backend && pytest -v
```

Expected:

- Unit tests: message builders for `transcript.partial` / `transcript.final` payload shape
- WebSocket integration test: mock VAD emits segment open/close; mock ASR returns deterministic text; assert partial + final messages
- Test: empty ASR result → no transcript message
- Test: `ASRInferenceError` → `ASR_INFERENCE_FAILED` error, session continues
- Existing health, audio, VAD, and ASR tests pass

## Spec Changes

Expected: none

If handler wiring or session fields differ materially from `backend.md` / `realtime-websocket.md`, update those docs in the same PR.

---

## Completion

### Summary

- Added `transcript_partial()` / `transcript_final()` message builders in `messages.py`
- Extended `Session` with segment ASR state (`sequence`, `start_ms`, partial throttle tracking)
- Wired WebSocket handler to `app.state.asr_engine`: partials on open segments, final on `SegmentClosed`
- Added `ASR_PARTIAL_INTERVAL_MS` setting (default 300)
- Added tests: `test_messages.py`, `test_session_asr.py`, `test_transcript_handler.py`

### Spec Changes

- `docs/architecture/backend.md` — noted P1-006 transcript emission

### Automated Tests Run

```bash
cd backend && pytest -v
# 42 passed, 1 skipped in 1.41s
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
