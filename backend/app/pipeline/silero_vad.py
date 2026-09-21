from __future__ import annotations

import threading

import numpy as np
import torch

from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import VadConfig, VadError, VadEvent, VadStream

SILERO_WINDOW_SAMPLES = 512
SILERO_WINDOW_BYTES = SILERO_WINDOW_SAMPLES * 2


class SileroVadEngine:
    _model = None
    _lock = threading.Lock()

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            with cls._lock:
                if cls._model is None:
                    try:
                        from silero_vad import load_silero_vad
                    except ImportError as exc:
                        raise VadError("Silero VAD dependencies are not installed") from exc
                    cls._model = load_silero_vad()
        return cls._model

    def create_stream(self, config: VadConfig) -> VadStream:
        return SileroVadStream(self._get_model(), config)


class SileroVadStream:
    def __init__(self, model, config: VadConfig) -> None:
        from silero_vad import VADIterator

        self._tracker = SegmentTracker(config)
        self._iterator = VADIterator(
            model,
            threshold=config.speech_threshold,
            sampling_rate=config.sample_rate,
            min_silence_duration_ms=config.min_silence_duration_ms,
            speech_pad_ms=config.speech_pad_ms,
        )
        self._pending = bytearray()

    @property
    def tracker(self) -> SegmentTracker:
        return self._tracker

    def process_frame(self, pcm_data: bytes) -> list[VadEvent]:
        if self._tracker.is_degraded:
            return self._tracker.process_degraded_frame(pcm_data)

        self._pending.extend(pcm_data)
        events: list[VadEvent] = []

        try:
            while len(self._pending) >= SILERO_WINDOW_BYTES:
                chunk = bytes(self._pending[:SILERO_WINDOW_BYTES])
                del self._pending[:SILERO_WINDOW_BYTES]
                audio = self._pcm_to_tensor(chunk)
                speech_event = self._iterator(audio, return_seconds=False)

                if speech_event and "start" in speech_event:
                    events.append(self._tracker.on_speech_start())
                if speech_event and "end" in speech_event:
                    events.extend(self._tracker.on_speech_end())
        except Exception as exc:
            raise VadError(str(exc)) from exc

        if self._tracker.active_segment is not None:
            self._tracker.append_frame(pcm_data)

        return events

    def enter_degraded_mode(self) -> None:
        self._pending.clear()
        self._tracker.enter_degraded_mode()

    def process_degraded_frame(self, pcm_data: bytes) -> list[VadEvent]:
        self._pending.clear()
        return self._tracker.process_degraded_frame(pcm_data)

    @staticmethod
    def _pcm_to_tensor(pcm_data: bytes) -> torch.Tensor:
        audio_int16 = np.frombuffer(pcm_data, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0
        return torch.from_numpy(audio_float)
