from __future__ import annotations

from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import VadConfig, VadEvent, VadStream


class MockVadEngine:
    def create_stream(self, config: VadConfig) -> VadStream:
        return MockVadStream(config)


class MockVadStream:
    def __init__(self, config: VadConfig) -> None:
        self.tracker = SegmentTracker(config)

    def process_frame(self, pcm_data: bytes) -> list[VadEvent]:
        return []

    def enter_degraded_mode(self) -> None:
        self.tracker.enter_degraded_mode()

    def process_degraded_frame(self, pcm_data: bytes) -> list[VadEvent]:
        return self.tracker.process_degraded_frame(pcm_data)
