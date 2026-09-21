from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

PROTOCOL_VERSION = 1


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def make_envelope(message_type: str, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": message_type,
        "id": str(uuid4()),
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": payload,
    }


def session_started(session_id: str, reconnect_window_s: int) -> dict[str, Any]:
    return make_envelope(
        "session.started",
        session_id,
        {
            "protocol_version": PROTOCOL_VERSION,
            "reconnect_window_s": reconnect_window_s,
        },
    )


def error_message(
    session_id: str,
    code: str,
    message: str,
    recoverable: bool,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return make_envelope(
        "error",
        session_id,
        {
            "code": code,
            "message": message,
            "recoverable": recoverable,
            "details": details or {},
        },
    )
