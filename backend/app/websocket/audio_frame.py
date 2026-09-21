from __future__ import annotations

import struct
from dataclasses import dataclass

from app.websocket.session import AudioConfig

HEADER_FORMAT = "<B I Q I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FRAME_VERSION = 1


@dataclass(frozen=True)
class ParsedAudioFrame:
    seq_num: int
    timestamp_us: int
    pcm_data: bytes


class AudioFrameError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def build_audio_frame(
    pcm_data: bytes,
    seq_num: int = 0,
    timestamp_us: int = 0,
    version: int = FRAME_VERSION,
) -> bytes:
    header = struct.pack(HEADER_FORMAT, version, seq_num, timestamp_us, len(pcm_data))
    return header + pcm_data


def parse_audio_frame(data: bytes, config: AudioConfig) -> ParsedAudioFrame:
    if len(data) < HEADER_SIZE:
        raise AudioFrameError("Frame too short for header")

    version, seq_num, timestamp_us, payload_length = struct.unpack(
        HEADER_FORMAT, data[:HEADER_SIZE]
    )

    if version != FRAME_VERSION:
        raise AudioFrameError(f"Unsupported frame version: {version}")

    expected_payload = config.expected_frame_bytes()
    if payload_length != expected_payload:
        raise AudioFrameError(
            f"Payload length {payload_length} does not match expected {expected_payload}"
        )

    pcm_data = data[HEADER_SIZE:]
    if len(pcm_data) != payload_length:
        raise AudioFrameError("Frame length does not match payload_length")

    return ParsedAudioFrame(
        seq_num=seq_num,
        timestamp_us=timestamp_us,
        pcm_data=pcm_data,
    )
