import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
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


def test_sequence_gap_emitted_after_reorder_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUDIO_REORDER_BUFFER_MS", "50")

    pcm = b"\x00" * 640
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_audio_start_message(session_id))
            websocket.send_bytes(build_audio_frame(pcm, seq_num=0))
            websocket.send_bytes(build_audio_frame(pcm, seq_num=2))
            time.sleep(0.12)
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "AUDIO_SEQUENCE_GAP"
    assert error["payload"]["recoverable"] is True
