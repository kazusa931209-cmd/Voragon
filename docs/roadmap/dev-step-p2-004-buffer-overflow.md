# P2-004: `buffer.overflow` and `BUFFER_OVERFLOW`

| Field | Value |
|-------|-------|
| **ID** | P2-004 |
| **Phase** | 2 |
| **Status** | planned |
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

- [ ] Flooding frames faster than processing fills buffer → `buffer.overflow` received
- [ ] `BUFFER_OVERFLOW` error received with `recoverable: true`
- [ ] Transcription can continue after overflow in tests
- [ ] Automated tests simulate buffer pressure without real-time sleep where possible
- [ ] Existing backend test suite still passes

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

- …

### Spec Changes

- …

### Automated Tests Run

```bash
# paste command and result
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
