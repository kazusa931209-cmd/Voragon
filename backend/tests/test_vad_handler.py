from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.vad import VadError
from app.websocket.audio_frame import build_audio_frame
from app.websocket.messages import utc_timestamp


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def test_vad_failed_emits_error_and_continues_in_degraded_mode() -> None:
    failing_stream = MagicMock()
    failing_stream.process_frame.side_effect = VadError("inference failed")
    failing_stream.enter_degraded_mode = MagicMock()
    failing_stream.process_degraded_frame.return_value = []

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = failing_stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with client.websocket_connect("/v1/realtime") as websocket:
                started = websocket.receive_json()
                websocket.send_json(_audio_start_message(started["session_id"]))
                pcm = b"\x00" * 640
                websocket.send_bytes(build_audio_frame(pcm))

                error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "VAD_FAILED"
    assert error["payload"]["recoverable"] is True
    failing_stream.enter_degraded_mode.assert_called_once()
    failing_stream.process_degraded_frame.assert_called_once()
