# P2-004: `buffer.overflow` and `BUFFER_OVERFLOW`

| Field | Value |
|-------|-------|
| **ID** | P2-004 |
| **Phase** | 2 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p2-004-buffer-overflow` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — `buffer.overflow` message
- [Error Handling](../api/error-handling.md) — `BUFFER_OVERFLOW`
- [Backend Architecture](../architecture/backend.md) — per-session audio buffer

## Scope

One verifiable behavior: **when the per-session audio ring buffer drops frames, the server notifies the client via `buffer.overflow` and a recoverable `BUFFER_OVERFLOW` error.**

- When `AudioBuffer.append` drops oldest frame(s), aggregate drop count for notification
- Emit `buffer.overflow` with `payload.dropped_frames` (per event or cumulative per spec—align with API examples)
- Emit matching recoverable `error` (`BUFFER_OVERFLOW`) per error-handling doc
- Rate-limit overflow notifications if needed (align with P2-007 server guidelines)
- Session continues after overflow

## Out of Scope

- Increasing buffer size dynamically
- Client throttling / backpressure protocol changes
- Metrics counters (P2-008 may wire `voragon_audio_frames_dropped_total`)

## Acceptance Criteria

- [x] Flooding frames faster than processing fills buffer → `buffer.overflow` received
- [x] `BUFFER_OVERFLOW` error received with `recoverable: true`
- [x] Transcription can continue after overflow in tests
- [x] Automated tests simulate buffer pressure without real-time sleep where possible
- [x] Existing backend test suite still passes

## Manual Test

1. Fast file replay (`realtime-cli` without pacing) against small test buffer config → observe overflow messages

## Automated Tests

```bash
cd backend && pytest -v -k "overflow or buffer"
cd backend && pytest -v
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- `emit_buffer_overflow_notifications()` in `app/websocket/buffer_overflow.py` — sends `buffer.overflow` then `error` `BUFFER_OVERFLOW` with `details.dropped_frames`
- Per-session `BufferOverflowNotifier` rate limit (`BUFFER_OVERFLOW_NOTIFY_MAX_PER_SECOND`, default 10)
- After VAD, `release_processed_audio_frame()` pops the processed frame from the ring buffer (steady mic streaming no longer fills 30s cap)
- Tests: `tests/test_buffer_overflow_notify.py`; updated `test_websocket_audio.py`, `test_audio_buffer.py`

### Spec Changes

- `docs/architecture/realtime-audio.md`, `docs/architecture/backend.md`, `backend/.env.example`

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v -k "overflow or buffer"
# 13 passed

cd backend && .venv/bin/pytest -v
# 67 passed, 1 skipped (full suite; local .env ASR_MODEL may affect test_health)
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
