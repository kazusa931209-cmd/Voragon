# P2-003: Audio Frame `seq_num` Ordering

| Field | Value |
|-------|-------|
| **ID** | P2-003 |
| **Phase** | 2 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p2-003-audio-seq-ordering` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — binary header `seq_num`, ordering guarantees (100 ms reorder buffer)
- [Error Handling](../api/error-handling.md) — `AUDIO_SEQUENCE_GAP`
- [Realtime Audio Pipeline](../architecture/realtime-audio.md)

## Scope

One verifiable behavior: **audio frames are processed in `seq_num` order; late frames are held up to 100 ms; gaps emit recoverable `AUDIO_SEQUENCE_GAP` and processing continues.**

- Per-session expected `seq_num` (monotonic from `audio.start` or first frame)
- Reorder buffer: hold out-of-order frames up to **100 ms** (configurable), then drop stale frames per spec
- On detected gap after buffer policy: emit `error` with code `AUDIO_SEQUENCE_GAP`, `recoverable: true`
- Continue processing subsequent in-order frames
- Increment `voragon`-relevant counters later in P2-008 (optional hook only)

## Out of Scope

- Client retransmit of lost frames
- Cross-session ordering
- `buffer.overflow` (P2-004)

## Acceptance Criteria

- [x] Frames delivered to VAD/ASR in `seq_num` order when client sends in order
- [x] Brief out-of-order delivery within 100 ms is reordered correctly (test with controlled seq)
- [x] Sequence gap emits `AUDIO_SEQUENCE_GAP` and session continues
- [x] Duplicate or regressed `seq_num` handled deterministically (document choice in PR)
- [x] Unit tests for reorder/gap logic; WebSocket integration test with injected frame order
- [x] Existing backend test suite still passes

## Manual Test

1. Use a test harness or modified CLI to send frames with intentional gap → observe `AUDIO_SEQUENCE_GAP` and continued transcription

## Automated Tests

```bash
cd backend && pytest -v -k "seq or sequence"
cd backend && pytest -v
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- `AudioSequenceReorderer` in `app/pipeline/audio_sequence.py` with configurable `AUDIO_REORDER_BUFFER_MS` (default 100)
- Per-session reorderer reset on `audio.start`; binary frames pass through reorder before ring buffer / VAD
- After reorder wait expires, missing sequences emit recoverable `AUDIO_SEQUENCE_GAP`; processing continues with next available frame
- **Duplicate / regressed `seq_num`:** frames with `seq_num < next_expected` are dropped silently (no error)
- Async flush task per WebSocket connection when the reorder buffer is waiting
- Tests: `tests/test_audio_sequence.py`, `tests/test_websocket_audio_sequence.py`

### Spec Changes

- `docs/architecture/backend.md`, `backend/.env.example` — env var only

### Automated Tests Run

```bash
cd backend && .venv/bin/pytest -v
# 62 passed, 1 skipped
```

### Manual Test Result

- [ ] Pass — date, notes

### PR

- **URL:** —
- **Merged:** —
