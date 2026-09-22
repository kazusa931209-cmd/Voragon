from __future__ import annotations

import struct
import time

HEADER_FORMAT = "<B I Q I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FRAME_VERSION = 1

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 20
SAMPLES_PER_FRAME = SAMPLE_RATE * FRAME_DURATION_MS // 1000
BYTES_PER_FRAME = SAMPLES_PER_FRAME * CHANNELS * 2


def build_audio_frame(
    pcm_data: bytes,
    seq_num: int,
    timestamp_us: int | None = None,
) -> bytes:
    if len(pcm_data) != BYTES_PER_FRAME:
        raise ValueError(f"Expected {BYTES_PER_FRAME} bytes of PCM, got {len(pcm_data)}")
    if timestamp_us is None:
        timestamp_us = time.time_ns() // 1000
    header = struct.pack(HEADER_FORMAT, FRAME_VERSION, seq_num, timestamp_us, len(pcm_data))
    return header + pcm_data
