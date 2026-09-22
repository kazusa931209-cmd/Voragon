# P2-003: Audio Frame `seq_num` Ordering

| Field | Value |
|-------|-------|
| **ID** | P2-003 |
| **Phase** | 2 |
| **Status** | planned |
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

- [ ] Frames delivered to VAD/ASR in `seq_num` order when client sends in order
- [ ] Brief out-of-order delivery within 100 ms is reordered correctly (test with controlled seq)
- [ ] Sequence gap emits `AUDIO_SEQUENCE_GAP` and session continues
- [ ] Duplicate or regressed `seq_num` handled deterministically (document choice in PR)
- [ ] Unit tests for reorder/gap logic; WebSocket integration test with injected frame order
- [ ] Existing backend test suite still passes

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
