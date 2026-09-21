from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.config import Settings
from app.pipeline.audio_buffer import AudioBuffer, BufferedAudioFrame
from app.pipeline.vad import VadStream, create_vad_engine, vad_config_from_settings


@dataclass(frozen=True)
class AudioConfig:
    language: str = "en"
    model: str = "asr.default"
    sample_rate: int = 16000
    channels: int = 1
    sample_format: str = "s16le"
    frame_duration_ms: int = 20

    def expected_frame_bytes(self) -> int:
        samples_per_frame = self.sample_rate * self.frame_duration_ms // 1000
        bytes_per_sample = 2 if self.sample_format == "s16le" else 0
        return samples_per_frame * self.channels * bytes_per_sample

    def max_buffer_bytes(self, buffer_seconds: int) -> int:
        return self.sample_rate * self.channels * 2 * buffer_seconds


@dataclass
class SegmentAsrState:
    segment_id: str
    start_ms: int
    sequence: int = 0
    last_partial_ms: int = 0


@dataclass
class Session:
    session_id: UUID
    audio_config: AudioConfig | None = None
    audio_buffer: AudioBuffer | None = None
    vad_stream: VadStream | None = None
    vad_degraded: bool = False
    vad_error_sent: bool = False
    session_elapsed_ms: int = 0
    segment_asr: SegmentAsrState | None = None

    @classmethod
    def create(cls) -> Session:
        return cls(session_id=uuid4())

    @property
    def audio_started(self) -> bool:
        return self.audio_config is not None

    def start_audio(self, config: AudioConfig, buffer_seconds: int, settings: Settings) -> None:
        self.audio_config = config
        self.audio_buffer = AudioBuffer(config.max_buffer_bytes(buffer_seconds))
        vad_config = vad_config_from_settings(
            settings,
            sample_rate=config.sample_rate,
            frame_duration_ms=config.frame_duration_ms,
        )
        self.vad_stream = create_vad_engine(settings).create_stream(vad_config)

    def append_audio_frame(self, frame: BufferedAudioFrame) -> int:
        if self.audio_buffer is None:
            raise RuntimeError("Audio streaming has not started")
        return self.audio_buffer.append(frame)

    def advance_elapsed_ms(self, frame_duration_ms: int) -> None:
        self.session_elapsed_ms += frame_duration_ms

    def begin_segment_asr(self, segment_id: str, start_ms: int) -> None:
        self.segment_asr = SegmentAsrState(
            segment_id=segment_id,
            start_ms=start_ms,
            last_partial_ms=start_ms,
        )

    def clear_segment_asr(self) -> None:
        self.segment_asr = None

    def next_sequence(self) -> int:
        if self.segment_asr is None:
            raise RuntimeError("No active segment ASR state")
        self.segment_asr.sequence += 1
        return self.segment_asr.sequence

    def should_emit_partial(self, interval_ms: int) -> bool:
        if self.segment_asr is None:
            return False
        return self.session_elapsed_ms - self.segment_asr.last_partial_ms >= interval_ms

    def mark_partial_emitted(self) -> None:
        if self.segment_asr is None:
            raise RuntimeError("No active segment ASR state")
        self.segment_asr.last_partial_ms = self.session_elapsed_ms
