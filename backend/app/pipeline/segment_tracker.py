from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.pipeline.vad import SegmentClosed, SegmentOpened, VadConfig, VadEvent


@dataclass
class SpeechSegment:
    segment_id: UUID
    pcm_data: bytearray = field(default_factory=bytearray)
    frame_count: int = 0

    def duration_ms(self, frame_duration_ms: int) -> int:
        return self.frame_count * frame_duration_ms

    def append(self, pcm_data: bytes) -> None:
        self.pcm_data.extend(pcm_data)
        self.frame_count += 1


class SegmentTracker:
    def __init__(self, config: VadConfig) -> None:
        self._config = config
        self._active: SpeechSegment | None = None
        self._closed: list[SpeechSegment] = []
        self._degraded = False

    @property
    def is_degraded(self) -> bool:
        return self._degraded

    @property
    def active_segment(self) -> SpeechSegment | None:
        return self._active

    @property
    def closed_segments(self) -> list[SpeechSegment]:
        return list(self._closed)

    def enter_degraded_mode(self) -> None:
        self._degraded = True
        if self._active is None:
            self._active = SpeechSegment(segment_id=uuid4())

    def on_speech_start(self) -> VadEvent:
        if self._active is None:
            self._active = SpeechSegment(segment_id=uuid4())
        return SegmentOpened(segment_id=self._active.segment_id)

    def on_speech_end(self) -> list[VadEvent]:
        return self._close_active_segment()

    def flush_active_segment(self) -> list[VadEvent]:
        """Force-close the open segment (e.g. on audio.stop). Same rules as speech end."""
        return self._close_active_segment()

    def _close_active_segment(self) -> list[VadEvent]:
        if self._active is None:
            return []

        segment = self._active
        duration_ms = segment.duration_ms(self._config.frame_duration_ms)
        self._active = None

        if duration_ms < self._config.min_speech_duration_ms:
            return []

        self._closed.append(segment)
        return [
            SegmentClosed(
                segment_id=segment.segment_id,
                duration_ms=duration_ms,
                pcm_data=bytes(segment.pcm_data),
            )
        ]

    def append_frame(self, pcm_data: bytes) -> None:
        if self._active is not None:
            self._active.append(pcm_data)

    def process_degraded_frame(self, pcm_data: bytes) -> list[VadEvent]:
        events: list[VadEvent] = []
        if self._active is None:
            self._active = SpeechSegment(segment_id=uuid4())
            events.append(SegmentOpened(segment_id=self._active.segment_id))
        self._active.append(pcm_data)
        return events
