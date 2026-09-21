from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.pipeline.audio_buffer import AudioBuffer, BufferedAudioFrame


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
class Session:
    session_id: UUID
    audio_config: AudioConfig | None = None
    audio_buffer: AudioBuffer | None = None

    @classmethod
    def create(cls) -> Session:
        return cls(session_id=uuid4())

    @property
    def audio_started(self) -> bool:
        return self.audio_config is not None

    def start_audio(self, config: AudioConfig, buffer_seconds: int) -> None:
        self.audio_config = config
        self.audio_buffer = AudioBuffer(config.max_buffer_bytes(buffer_seconds))

    def append_audio_frame(self, frame: BufferedAudioFrame) -> int:
        if self.audio_buffer is None:
            raise RuntimeError("Audio streaming has not started")
        return self.audio_buffer.append(frame)
