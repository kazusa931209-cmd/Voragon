from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.config import Settings


@dataclass(frozen=True)
class VadConfig:
    speech_threshold: float = 0.5
    min_speech_duration_ms: int = 250
    min_silence_duration_ms: int = 500
    speech_pad_ms: int = 300
    sample_rate: int = 16000
    frame_duration_ms: int = 20


@dataclass(frozen=True)
class SegmentOpened:
    segment_id: UUID


@dataclass(frozen=True)
class SegmentClosed:
    segment_id: UUID
    duration_ms: int
    pcm_data: bytes


VadEvent = SegmentOpened | SegmentClosed


class VadError(Exception):
    """Raised when VAD inference fails."""


class VadStream(Protocol):
    def process_frame(self, pcm_data: bytes) -> list[VadEvent]: ...

    def enter_degraded_mode(self) -> None: ...

    def process_degraded_frame(self, pcm_data: bytes) -> list[VadEvent]: ...


class VadEngine(Protocol):
    def create_stream(self, config: VadConfig) -> VadStream: ...


def vad_config_from_settings(settings: Settings, sample_rate: int, frame_duration_ms: int) -> VadConfig:
    return VadConfig(
        speech_threshold=settings.vad_speech_threshold,
        min_speech_duration_ms=settings.vad_min_speech_duration_ms,
        min_silence_duration_ms=settings.vad_min_silence_duration_ms,
        speech_pad_ms=settings.vad_speech_pad_ms,
        sample_rate=sample_rate,
        frame_duration_ms=frame_duration_ms,
    )


def create_vad_engine(settings: Settings) -> VadEngine:
    if settings.vad_backend == "silero":
        from app.pipeline.silero_vad import SileroVadEngine

        return SileroVadEngine()
    if settings.vad_backend == "mock":
        from app.pipeline.mock_vad import MockVadEngine

        return MockVadEngine()
    raise ValueError(f"Unsupported VAD backend: {settings.vad_backend}")
