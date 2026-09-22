from uuid import UUID

from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import SegmentClosed, SegmentOpened, VadConfig


def _tracker(min_speech_ms: int = 250) -> SegmentTracker:
    return SegmentTracker(
        VadConfig(
            min_speech_duration_ms=min_speech_ms,
            frame_duration_ms=20,
            sample_rate=16000,
        )
    )


def test_segment_opens_on_speech_start() -> None:
    tracker = _tracker()
    event = tracker.on_speech_start()

    assert isinstance(event, SegmentOpened)
    UUID(str(event.segment_id))
    assert tracker.active_segment is not None


def test_segment_closes_after_speech_end_with_enough_duration() -> None:
    tracker = _tracker(min_speech_ms=40)
    tracker.on_speech_start()
    pcm = b"\x00" * 640

    for _ in range(3):
        tracker.append_frame(pcm)

    events = tracker.on_speech_end()

    assert len(events) == 1
    closed = events[0]
    assert isinstance(closed, SegmentClosed)
    assert closed.duration_ms == 60
    assert len(closed.pcm_data) == 640 * 3
    assert tracker.active_segment is None
    assert len(tracker.closed_segments) == 1


def test_short_segment_discarded() -> None:
    tracker = _tracker(min_speech_ms=250)
    tracker.on_speech_start()
    tracker.append_frame(b"\x00" * 640)

    events = tracker.on_speech_end()

    assert events == []
    assert tracker.closed_segments == []


def test_flush_active_segment_closes_open_segment() -> None:
    tracker = _tracker(min_speech_ms=40)
    tracker.on_speech_start()
    pcm = b"\x00" * 640

    for _ in range(3):
        tracker.append_frame(pcm)

    events = tracker.flush_active_segment()

    assert len(events) == 1
    assert isinstance(events[0], SegmentClosed)
    assert tracker.active_segment is None


def test_degraded_mode_opens_segment_and_accumulates_pcm() -> None:
    tracker = _tracker()
    pcm = b"\x01" * 640

    first = tracker.process_degraded_frame(pcm)
    second = tracker.process_degraded_frame(pcm)

    assert len(first) == 1
    assert isinstance(first[0], SegmentOpened)
    assert second == []
    assert tracker.active_segment is not None
    assert tracker.active_segment.frame_count == 2
