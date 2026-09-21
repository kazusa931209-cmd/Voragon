import pytest

from app.pipeline.silero_vad import SileroVadEngine
from app.pipeline.vad import VadConfig


@pytest.mark.silero
def test_silero_vad_processes_silent_frame() -> None:
    pytest.importorskip("silero_vad")
    engine = SileroVadEngine()
    stream = engine.create_stream(VadConfig(sample_rate=16000, frame_duration_ms=20))
    pcm = b"\x00" * 640

    events = stream.process_frame(pcm)

    assert events == []
