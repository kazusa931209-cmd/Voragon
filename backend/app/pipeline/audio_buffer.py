from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class BufferedAudioFrame:
    seq_num: int
    timestamp_us: int
    pcm_data: bytes


class AudioBuffer:
    """Per-session ring buffer that drops oldest frames when full."""

    def __init__(self, max_bytes: int) -> None:
        self._frames: deque[BufferedAudioFrame] = deque()
        self._total_bytes = 0
        self.max_bytes = max_bytes

    def append(self, frame: BufferedAudioFrame) -> int:
        frame_bytes = len(frame.pcm_data)
        dropped = 0

        while self._frames and self._total_bytes + frame_bytes > self.max_bytes:
            removed = self._frames.popleft()
            self._total_bytes -= len(removed.pcm_data)
            dropped += 1

        self._frames.append(frame)
        self._total_bytes += frame_bytes
        return dropped

    def __len__(self) -> int:
        return len(self._frames)

    def total_bytes(self) -> int:
        return self._total_bytes
