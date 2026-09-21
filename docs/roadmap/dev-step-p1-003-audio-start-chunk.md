# P1-003: `audio.start` and Binary `audio.chunk` Reception

| Field | Value |
|-------|-------|
| **ID** | P1-003 |
| **Phase** | 1 |
| **Status** | in-progress |
| **PR** | — (pending) |
| **Branch** | `dev-step/p1-003-audio-start-chunk` (committed to `dev` as `6192ca1`) |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `audio.start`, binary `audio.chunk` frame format
- [Error Handling](../api/error-handling.md) — `AUDIO_NOT_STARTED`, `INVALID_AUDIO_FORMAT`, `BUFFER_OVERFLOW`
- [Realtime Audio Pipeline](../architecture/realtime-audio.md) — frame size, ring buffer
- [Backend Architecture](../architecture/backend.md) — `pipeline/audio_buffer.py`, session state

## Scope

One verifiable behavior: **after `session.started`, a client can send `audio.start` and stream binary `audio.chunk` frames that the backend parses and buffers per session.**

- Handle `audio.start` JSON control message with spec defaults and validation
- Transition session to active audio state; store audio config on the session
- Parse binary WebSocket frames (17-byte header + PCM payload per field table)
- Validate frame version, payload length, and PCM size against `audio.start` config
- Append valid frames to a per-session ring buffer (30 s capacity, drop-oldest)
- Emit `buffer.overflow` when frames are dropped due to buffer capacity
- Return `AUDIO_NOT_STARTED` if binary frames arrive before `audio.start`
- Return `INVALID_AUDIO_FORMAT` for malformed or mismatched binary frames
- Other unsolicited JSON message types still receive `UNKNOWN_MESSAGE_TYPE`

## Out of Scope

- `audio.stop` and `session.ended`
- VAD, ASR, `transcript.partial`, `transcript.final`
- `session.resume`, `ping` / `pong`
- `AUDIO_SEQUENCE_GAP` error emission (log only if needed)
- Authentication / TLS
- Prometheus metrics for dropped frames

## Acceptance Criteria

- [x] Client can send valid `audio.start` after connect without error
- [x] `audio.start` stores config with spec defaults (`en`, 16000 Hz, mono, s16le, 20 ms)
- [x] Binary frames sent after `audio.start` are parsed and buffered
- [x] Binary frames before `audio.start` receive `error` with code `AUDIO_NOT_STARTED`
- [x] Malformed binary frames receive `error` with code `INVALID_AUDIO_FORMAT`
- [x] Buffer overflow drops oldest frames and emits `buffer.overflow`
- [x] Unsolicited JSON types (e.g. `ping`) still receive `UNKNOWN_MESSAGE_TYPE`
- [x] Existing `session.started` and health tests still pass
- [x] Automated WebSocket tests cover `audio.start` + binary chunk reception

## Manual Test

1. `cd backend && source .venv/bin/activate && python -m app.main`
2. Connect and receive `session.started`:
   ```bash
   python -c "
   import asyncio, json, struct, websockets
   async def main():
       async with websockets.connect('ws://localhost:8000/v1/realtime') as ws:
           started = json.loads(await ws.recv())
           sid = started['session_id']
           await ws.send(json.dumps({
               'type': 'audio.start', 'id': 'msg-1', 'session_id': sid,
               'timestamp': '2026-09-21T00:00:00.000Z',
               'payload': {'language': 'en'}
           }))
           pcm = b'\\x00' * 640
           header = struct.pack('<BIQI', 1, 0, 0, len(pcm))
           await ws.send(header + pcm)
           print('audio.start + chunk sent OK')
   asyncio.run(main())
   "
   ```
3. Verify no error response; connection stays open
4. Send a binary frame before `audio.start` on a fresh connection — expect `AUDIO_NOT_STARTED`

## Automated Tests

```bash
cd backend && pytest -v
```

Expected:
- New tests: `audio.start` acceptance, binary chunk buffering, `AUDIO_NOT_STARTED`, `INVALID_AUDIO_FORMAT`, buffer overflow
- Existing health and session tests pass

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation, before PR._

### Summary

- Added `app/pipeline/audio_buffer.py` with per-session ring buffer (drop-oldest)
- Added `app/websocket/audio_frame.py` for binary frame parse/build helpers
- Extended `Session` with `AudioConfig`, audio state, and buffer management
- WebSocket handler routes `audio.start`, parses binary `audio.chunk` frames, emits `buffer.overflow`
- Added `audio_buffer_seconds` config (default 30)
- Added payload type validation in `_handle_audio_start` (`INVALID_MESSAGE` for bad types)
- Added `tests/test_audio_buffer.py` (3 unit tests) and expanded `tests/test_websocket_audio.py` (14 tests)

### Spec Changes

- `docs/architecture/backend.md` — noted P1-003 implemented pipeline/audio modules
- `docs/api/realtime-websocket.md` — corrected binary frame header size (16 → 17 bytes)

### Automated Tests Run

```bash
cd backend && pytest -v
# 21 passed in 0.25s
```

### Manual Test Result

- [x] Pass — 2026-09-22, `audio.start` + binary chunk over live WebSocket; `AUDIO_NOT_STARTED` before `audio.start`

### PR

- **URL:** — (not opened yet)
- **Merged:** —
- **Note:** Implementation committed directly to `dev` (`6192ca1`, 2026-09-22). Per workflow, status remains `in-progress` until a PR is merged.
