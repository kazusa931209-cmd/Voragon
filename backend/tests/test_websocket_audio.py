import struct

from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.audio_buffer import BufferedAudioFrame
from app.websocket.audio_frame import HEADER_FORMAT, build_audio_frame
from app.websocket.messages import utc_timestamp
from app.websocket.session import AudioConfig, Session


def _audio_start_message(session_id: str, payload: dict | None = None) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": payload or {},
    }


def test_audio_start_accepts_default_config() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))


def test_session_stores_audio_config_after_audio_start() -> None:
    session = Session.create()
    config = AudioConfig(language="en", sample_rate=16000)
    session.start_audio(config, buffer_seconds=30)

    assert session.audio_started is True
    assert session.audio_config == config
    assert session.audio_buffer is not None
    assert session.audio_buffer.max_bytes == 960000


def test_session_buffers_audio_frames() -> None:
    session = Session.create()
    session.start_audio(AudioConfig(), buffer_seconds=30)
    pcm = b"\x00" * 640

    dropped = session.append_audio_frame(
        BufferedAudioFrame(seq_num=1, timestamp_us=0, pcm_data=pcm)
    )

    assert dropped == 0
    assert session.audio_buffer is not None
    assert len(session.audio_buffer) == 1
    assert session.audio_buffer.total_bytes() == 640


def test_audio_chunk_buffered_after_audio_start() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))
            pcm = b"\x00" * 640
            websocket.send_bytes(build_audio_frame(pcm, seq_num=1))
            websocket.send_bytes(build_audio_frame(pcm, seq_num=2))


def test_audio_chunk_before_audio_start_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            pcm = b"\x00" * 640
            websocket.send_bytes(build_audio_frame(pcm))

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "AUDIO_NOT_STARTED"
    assert error["payload"]["recoverable"] is True


def test_invalid_audio_frame_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))
            websocket.send_bytes(b"\x01\x02\x03")

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_AUDIO_FORMAT"
    assert error["payload"]["recoverable"] is True


def test_invalid_audio_start_config_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(
                _audio_start_message(
                    started["session_id"],
                    {"sample_rate": 16000, "channels": 2},
                )
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_AUDIO_FORMAT"


def test_invalid_audio_start_payload_type_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(
                _audio_start_message(started["session_id"], {"sample_rate": "16000"})
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert "sample_rate must be an integer" in error["payload"]["message"]


def test_audio_start_missing_session_id_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "audio.start",
                    "id": "msg-audio-start",
                    "timestamp": utc_timestamp(),
                    "payload": {},
                }
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"


def test_audio_start_wrong_session_id_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_json(
                _audio_start_message("00000000-0000-0000-0000-000000000000")
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"


def test_invalid_audio_frame_version_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))
            pcm = b"\x00" * 640
            websocket.send_bytes(build_audio_frame(pcm, version=2))

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_AUDIO_FORMAT"
    assert "Unsupported frame version" in error["payload"]["message"]


def test_invalid_audio_frame_payload_length_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))
            pcm = b"\x00" * 640
            header = struct.pack(HEADER_FORMAT, 1, 0, 0, 320)
            websocket.send_bytes(header + pcm)

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_AUDIO_FORMAT"
    assert "Payload length" in error["payload"]["message"]


def test_buffer_overflow_emitted_when_capacity_exceeded(monkeypatch) -> None:
    monkeypatch.setenv("AUDIO_BUFFER_SECONDS", "1")

    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))

            pcm = b"\x00" * 640
            for seq in range(60):
                websocket.send_bytes(build_audio_frame(pcm, seq_num=seq))

            overflow = websocket.receive_json()

    assert overflow["type"] == "buffer.overflow"
    assert overflow["payload"]["dropped_frames"] >= 1


def test_unknown_message_type_still_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(
                {
                    "type": "ping",
                    "id": "msg-ping",
                    "session_id": started["session_id"],
                    "timestamp": utc_timestamp(),
                    "payload": {},
                }
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "UNKNOWN_MESSAGE_TYPE"
