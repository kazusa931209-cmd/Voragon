import re
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.websocket.messages import utc_timestamp

ISO_8601_UTC_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
)


def test_websocket_session_started_on_connect() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            message = websocket.receive_json()

    assert message["type"] == "session.started"
    UUID(message["session_id"])
    UUID(message["id"])
    assert ISO_8601_UTC_PATTERN.match(message["timestamp"])
    assert message["payload"]["protocol_version"] == 1
    assert message["payload"]["reconnect_window_s"] == 30


def test_websocket_unknown_message_type_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(
                {
                    "type": "not.a.real.message",
                    "id": "msg-unknown",
                    "session_id": started["session_id"],
                    "timestamp": utc_timestamp(),
                    "payload": {},
                }
            )

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "UNKNOWN_MESSAGE_TYPE"
    assert error["payload"]["recoverable"] is True


def test_websocket_invalid_message_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_text("not-json")

            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert error["payload"]["recoverable"] is True
