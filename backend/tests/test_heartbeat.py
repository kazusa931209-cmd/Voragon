import time
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.websocket.messages import utc_timestamp


def _ping_message(session_id: str) -> dict:
    return {
        "type": "ping",
        "id": "msg-ping",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def test_ping_returns_pong() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_ping_message(session_id))
            response = websocket.receive_json()

    assert response["type"] == "pong"
    assert response["session_id"] == session_id
    UUID(response["id"])
    assert response["payload"] == {}


def test_ping_wrong_session_id_returns_invalid_message() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_ping_message("00000000-0000-0000-0000-000000000099"))
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert error["session_id"] == started["session_id"]


def test_ping_non_object_payload_returns_invalid_message() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(
                {
                    "type": "ping",
                    "id": "msg-ping",
                    "session_id": session_id,
                    "timestamp": utc_timestamp(),
                    "payload": "nope",
                }
            )
            error = websocket.receive_json()

    assert error["payload"]["code"] == "INVALID_MESSAGE"


def test_heartbeat_idle_timeout_closes_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEARTBEAT_IDLE_TIMEOUT_S", "1")

    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            time.sleep(1.25)
            with pytest.raises(WebSocketDisconnect):
                websocket.receive_json()
