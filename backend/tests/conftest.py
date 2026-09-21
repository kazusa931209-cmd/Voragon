import pytest


@pytest.fixture(autouse=True)
def use_mock_vad_backend(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("silero"):
        return
    monkeypatch.setenv("VAD_BACKEND", "mock")
