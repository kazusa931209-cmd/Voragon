import pytest


@pytest.fixture(autouse=True)
def use_mock_backends(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("silero"):
        return
    if request.node.get_closest_marker("faster_whisper"):
        monkeypatch.setenv("ASR_BACKEND", "faster_whisper")
        monkeypatch.setenv("VAD_BACKEND", "mock")
        return
    monkeypatch.setenv("VAD_BACKEND", "mock")
    monkeypatch.setenv("ASR_BACKEND", "mock")
