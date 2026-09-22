import time

from app.pipeline.audio_buffer import BufferedAudioFrame
from app.pipeline.audio_sequence import AudioSequenceReorderer


def _frame(seq_num: int, marker: int = 0) -> BufferedAudioFrame:
    return BufferedAudioFrame(
        seq_num=seq_num,
        timestamp_us=0,
        pcm_data=bytes([marker]),
    )


def test_in_order_frames_release_immediately() -> None:
    reorderer = AudioSequenceReorderer(buffer_ms=100)
    t0 = time.monotonic()

    first = reorderer.ingest(_frame(0, 1), t0)
    second = reorderer.ingest(_frame(1, 2), t0)

    assert [frame.pcm_data for frame in first.ready] == [b"\x01"]
    assert first.gaps == []
    assert [frame.pcm_data for frame in second.ready] == [b"\x02"]
    assert second.gaps == []


def test_out_of_order_within_buffer_reorders() -> None:
    reorderer = AudioSequenceReorderer(buffer_ms=100)
    t0 = time.monotonic()

    reorderer.ingest(_frame(0, 1), t0)
    late = reorderer.ingest(_frame(2, 3), t0)
    assert late.ready == []
    assert reorderer.waiting_for_reorder is True

    middle = reorderer.ingest(_frame(1, 2), t0)
    assert [frame.pcm_data for frame in middle.ready] == [b"\x02", b"\x03"]
    assert reorderer.waiting_for_reorder is False


def test_gap_after_buffer_timeout() -> None:
    reorderer = AudioSequenceReorderer(buffer_ms=50)
    t0 = 1000.0

    reorderer.ingest(_frame(0, 1), t0)
    buffered = reorderer.ingest(_frame(2, 3), t0)
    assert buffered.ready == []

    flushed = reorderer.flush(t0 + 0.05)
    assert flushed.gaps[0].first_missing == 1
    assert flushed.gaps[0].last_missing == 1
    assert [frame.pcm_data for frame in flushed.ready] == [b"\x03"]


def test_duplicate_and_regressed_seq_are_dropped() -> None:
    reorderer = AudioSequenceReorderer(buffer_ms=100)
    t0 = time.monotonic()

    reorderer.ingest(_frame(0), t0)
    duplicate = reorderer.ingest(_frame(0), t0)
    reorderer.ingest(_frame(1), t0)
    regressed = reorderer.ingest(_frame(0), t0)

    assert duplicate.ready == []
    assert regressed.ready == []


def test_session_continues_after_gap() -> None:
    reorderer = AudioSequenceReorderer(buffer_ms=10)
    t0 = 500.0

    reorderer.ingest(_frame(0), t0)
    reorderer.ingest(_frame(3), t0)
    gap_result = reorderer.flush(t0 + 0.02)
    assert gap_result.gaps[0].first_missing == 1
    assert gap_result.gaps[0].last_missing == 2

    follow_up = reorderer.ingest(_frame(4), t0 + 0.03)
    assert [frame.seq_num for frame in follow_up.ready] == [4]
