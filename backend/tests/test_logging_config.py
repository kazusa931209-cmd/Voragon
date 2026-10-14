import io
import json
import logging

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.observability.logging_config import (
    JsonLogFormatter,
    configure_logging,
    log_fields,
)


def test_json_formatter_emits_required_keys() -> None:
    formatter = JsonLogFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="Client error emitted",
        args=(),
        exc_info=None,
    )
    record.session_id = "sess-123"
    record.code = "INVALID_MESSAGE"
    record.recoverable = True

    payload = json.loads(formatter.format(record))

    assert "timestamp" in payload
    assert payload["level"] == "warning"
    assert payload["service"] == "realtime-service"
    assert payload["message"] == "Client error emitted"
    assert payload["session_id"] == "sess-123"
    assert payload["code"] == "INVALID_MESSAGE"
    assert payload["recoverable"] is True


def test_configure_logging_json_format() -> None:
    stream = io.StringIO()
    configure_logging(Settings(log_format="json", log_level="info"))
    root = logging.getLogger()
    assert len(root.handlers) == 1
    root.handlers[0].stream = stream  # type: ignore[attr-defined]

    log_fields(
        logging.getLogger("test.logging"),
        logging.INFO,
        "websocket.connected",
        session_id="abc",
    )

    line = stream.getvalue().strip()
    payload = json.loads(line)
    assert payload["message"] == "websocket.connected"
    assert payload["session_id"] == "abc"


def test_error_emitter_logs_structured_code() -> None:
    stream = io.StringIO()
    configure_logging(Settings(log_format="json", log_level="warning"))

    root = logging.getLogger()
    assert root.handlers
    root.handlers[0].stream = stream  # type: ignore[attr-defined]

    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_text("not-json")
            websocket.receive_json()

    lines = [line for line in stream.getvalue().splitlines() if line.strip()]
    assert lines
    payload = json.loads(lines[-1])
    assert payload["code"] == "INVALID_MESSAGE"
    assert "session_id" in payload
    assert "transcript" not in payload["message"].lower()
