from __future__ import annotations

from app.asr.base import ASRModelUnavailableError, HealthStatus, TranscriptResult
from app.config import Settings

MIN_AUDIO_BYTES_FOR_TEXT = 3200


class MockASREngine:
    def __init__(self, settings: Settings) -> None:
        self._backend = settings.asr_backend
        self._model = settings.asr_model
        self._ready = False

    async def warmup(self) -> None:
        self._ready = True

    async def health(self) -> HealthStatus:
        return HealthStatus(
            ready=self._ready,
            backend=self._backend,
            model=self._model,
            message=None if self._ready else "Model not loaded",
        )

    async def transcribe_partial(
        self,
        audio: bytes,
        segment_id: str,
        language: str,
    ) -> TranscriptResult:
        self._ensure_ready()
        text = f"partial-{segment_id}" if len(audio) >= MIN_AUDIO_BYTES_FOR_TEXT else ""
        return TranscriptResult(text=text, language=language, confidence=0.9)

    async def transcribe_final(
        self,
        audio: bytes,
        segment_id: str,
        language: str,
    ) -> TranscriptResult:
        self._ensure_ready()
        text = f"final-{segment_id}" if len(audio) >= MIN_AUDIO_BYTES_FOR_TEXT else ""
        return TranscriptResult(text=text, language=language, confidence=0.95)

    def _ensure_ready(self) -> None:
        if not self._ready:
            raise ASRModelUnavailableError("Mock ASR model is not loaded")
