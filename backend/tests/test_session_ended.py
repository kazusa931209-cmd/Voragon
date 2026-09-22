import time

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.websocket.connection_registry import RegisteredConnection, register, shutdown_all, unregister
from app.websocket.messages import session_ended, utc_timestamp


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def _audio_stop_message(session_id: str) -> dict:
    return {
        "type": "audio.stop",
        "id": "msg-audio-stop",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def test_audio_stop_emits_session_ended_client_stop() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_audio_start_message(session_id))
            websocket.send_json(_audio_stop_message(session_id))
            ended = websocket.receive_json()

    assert ended["type"] == "session.ended"
    assert ended["session_id"] == session_id
    assert ended["payload"]["reason"] == "client_stop"


def test_heartbeat_idle_timeout_emits_session_ended(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEARTBEAT_IDLE_TIMEOUT_S", "1")

    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            time.sleep(1.25)
            ended = websocket.receive_json()
            assert ended["type"] == "session.ended"
            assert ended["payload"]["reason"] == "timeout"
            with pytest.raises(WebSocketDisconnect):
                websocket.receive_json()


@pytest.mark.asyncio
async def test_shutdown_all_invokes_registered_end_session() -> None:
    reasons: list[str] = []

    async def end_session(reason: str) -> None:
        reasons.append(reason)

    connection = RegisteredConnection("session-test", end_session)
    await register(connection)
    await shutdown_all("server_shutdown")
    await unregister(connection)

    assert reasons == ["server_shutdown"]


def test_session_ended_message_shape() -> None:
    message = session_ended("session-1", "client_stop")
    assert message["type"] == "session.ended"
    assert message["payload"]["reason"] == "client_stop"
