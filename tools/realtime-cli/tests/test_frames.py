import struct

import pytest

from realtime_cli.frames import (
    BYTES_PER_FRAME,
    FRAME_VERSION,
    HEADER_FORMAT,
    build_audio_frame,
)


def test_build_audio_frame_header_and_payload() -> None:
    pcm = b"\x01" * BYTES_PER_FRAME
    frame = build_audio_frame(pcm, seq_num=7, timestamp_us=123456789)

    version, seq_num, timestamp_us, payload_length = struct.unpack(HEADER_FORMAT, frame[:17])
    assert version == FRAME_VERSION
    assert seq_num == 7
    assert timestamp_us == 123456789
    assert payload_length == BYTES_PER_FRAME
    assert frame[17:] == pcm


def test_build_audio_frame_rejects_wrong_payload_size() -> None:
    with pytest.raises(ValueError, match="Expected 640 bytes"):
        build_audio_frame(b"\x00" * 100, seq_num=0)
