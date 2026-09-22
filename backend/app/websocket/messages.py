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


def pong(session_id: str) -> dict[str, Any]:
    return make_envelope("pong", session_id, {})


def session_started(session_id: str, reconnect_window_s: int) -> dict[str, Any]:
    return make_envelope(
        "session.started",
        session_id,
        {
            "protocol_version": PROTOCOL_VERSION,
            "reconnect_window_s": reconnect_window_s,
        },
    )


def buffer_overflow(session_id: str, dropped_frames: int) -> dict[str, Any]:
    return make_envelope(
        "buffer.overflow",
        session_id,
        {"dropped_frames": dropped_frames},
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


def _transcript_payload(
    segment_id: str,
    sequence: int,
    text: str,
    language: str,
    confidence: float | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "segment_id": segment_id,
        "sequence": sequence,
        "text": text,
        "language": language,
    }
    if confidence is not None:
        payload["confidence"] = confidence
    return payload


def transcript_partial(
    session_id: str,
    segment_id: str,
    sequence: int,
    text: str,
    language: str,
    confidence: float | None = None,
) -> dict[str, Any]:
    return make_envelope(
        "transcript.partial",
        session_id,
        _transcript_payload(segment_id, sequence, text, language, confidence),
    )


def transcript_final(
    session_id: str,
    segment_id: str,
    sequence: int,
    text: str,
    language: str,
    start_ms: int,
    end_ms: int,
    confidence: float | None = None,
) -> dict[str, Any]:
    payload = _transcript_payload(segment_id, sequence, text, language, confidence)
    payload["start_ms"] = start_ms
    payload["end_ms"] = end_ms
    return make_envelope("transcript.final", session_id, payload)
