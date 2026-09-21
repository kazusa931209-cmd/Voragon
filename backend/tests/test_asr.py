import os

import pytest

from app.asr.base import ASRModelUnavailableError, create_asr_engine
from app.asr.mock_asr import MIN_AUDIO_BYTES_FOR_TEXT
from app.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(asr_backend="mock", asr_model="large-v3-turbo")


async def test_create_asr_engine_selects_mock(mock_settings: Settings) -> None:
    engine = create_asr_engine(mock_settings)

    assert engine.__class__.__name__ == "MockASREngine"


async def test_create_asr_engine_rejects_unknown_backend() -> None:
    settings = Settings(asr_backend="unknown")

    with pytest.raises(ValueError, match="Unsupported ASR backend"):
        create_asr_engine(settings)


async def test_mock_asr_warmup_and_health(mock_settings: Settings) -> None:
    engine = create_asr_engine(mock_settings)

    health_before = await engine.health()
    assert health_before.ready is False

    await engine.warmup()

    health_after = await engine.health()
    assert health_after.ready is True
    assert health_after.backend == "mock"
    assert health_after.model == "large-v3-turbo"


async def test_mock_asr_transcribe_partial_and_final(mock_settings: Settings) -> None:
    engine = create_asr_engine(mock_settings)
    await engine.warmup()
    audio = b"\x00" * MIN_AUDIO_BYTES_FOR_TEXT

    partial = await engine.transcribe_partial(audio, "seg-001", "en")
    final = await engine.transcribe_final(audio, "seg-001", "en")

    assert partial.text == "partial-seg-001"
    assert partial.language == "en"
    assert partial.confidence == 0.9
    assert final.text == "final-seg-001"
    assert final.language == "en"
    assert final.confidence == 0.95


async def test_mock_asr_returns_empty_text_for_short_audio(mock_settings: Settings) -> None:
    engine = create_asr_engine(mock_settings)
    await engine.warmup()

    result = await engine.transcribe_final(b"\x00" * 100, "seg-short", "en")

    assert result.text == ""


async def test_mock_asr_requires_warmup(mock_settings: Settings) -> None:
    engine = create_asr_engine(mock_settings)

    with pytest.raises(ASRModelUnavailableError):
        await engine.transcribe_final(b"\x00" * MIN_AUDIO_BYTES_FOR_TEXT, "seg-001", "en")


@pytest.mark.faster_whisper
@pytest.mark.skipif(
    os.environ.get("RUN_FASTER_WHISPER_TESTS") != "1",
    reason="Set RUN_FASTER_WHISPER_TESTS=1 to run faster-whisper integration test",
)
async def test_faster_whisper_transcribe_silence() -> None:
    pytest.importorskip("faster_whisper")
    settings = Settings(asr_backend="faster_whisper", asr_model="tiny")
    engine = create_asr_engine(settings)

    await engine.warmup()
    health = await engine.health()
    assert health.ready is True

    result = await engine.transcribe_final(b"\x00" * 32000, "seg-test", "en")
    assert result.language == "en"
    assert isinstance(result.text, str)
