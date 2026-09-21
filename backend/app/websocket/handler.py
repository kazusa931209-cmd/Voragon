import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import Settings, get_settings
from app.pipeline.audio_buffer import BufferedAudioFrame
from app.websocket.audio_frame import AudioFrameError, parse_audio_frame
from app.websocket.messages import buffer_overflow, error_message, session_started
from app.websocket.session import AudioConfig, Session

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_SAMPLE_FORMATS = {"s16le"}


@router.websocket("/v1/realtime")
async def realtime_websocket(websocket: WebSocket) -> None:
    settings = get_settings()
    await websocket.accept()

    session = Session.create()
    session_id = str(session.session_id)

    await websocket.send_json(
        session_started(session_id, settings.reconnect_window_s)
    )

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                break

            if "text" in message:
                await _handle_text_message(
                    websocket, session, session_id, message["text"], settings
                )
            elif "bytes" in message:
                await _handle_binary_message(websocket, session, session_id, message["bytes"])
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected session_id=%s", session_id)


async def _handle_text_message(
    websocket: WebSocket,
    session: Session,
    session_id: str,
    text: str,
    settings: Settings,
) -> None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_MESSAGE",
                "Malformed message",
                True,
            )
        )
        return

    message_type = data.get("type")
    if message_type == "audio.start":
        await _handle_audio_start(websocket, session, session_id, data, settings)
        return

    await websocket.send_json(
        error_message(
            session_id,
            "UNKNOWN_MESSAGE_TYPE",
            f"Unrecognized message type: {message_type or '<missing>'}",
            True,
        )
    )


async def _handle_audio_start(
    websocket: WebSocket,
    session: Session,
    session_id: str,
    data: dict[str, Any],
    settings: Settings,
) -> None:
    if data.get("session_id") != session_id:
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_MESSAGE",
                "session_id does not match active session",
                True,
            )
        )
        return

    payload = data.get("payload")
    if payload is not None and not isinstance(payload, dict):
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_MESSAGE",
                "audio.start payload must be an object",
                True,
            )
        )
        return

    config, parse_error = _parse_audio_start_payload(payload or {})
    if parse_error is not None:
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_MESSAGE",
                parse_error,
                True,
            )
        )
        return

    validation_error = _validate_audio_config(config)
    if validation_error is not None:
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_AUDIO_FORMAT",
                validation_error,
                True,
            )
        )
        return

    session.start_audio(config, settings.audio_buffer_seconds)
    logger.debug(
        "Audio started session_id=%s sample_rate=%s channels=%s",
        session_id,
        config.sample_rate,
        config.channels,
    )


def _parse_audio_start_payload(payload: dict[str, Any]) -> tuple[AudioConfig | None, str | None]:
    language, error = _parse_string_field(payload, "language", "en")
    if error:
        return None, error
    model, error = _parse_string_field(payload, "model", "asr.default")
    if error:
        return None, error
    sample_format, error = _parse_string_field(payload, "sample_format", "s16le")
    if error:
        return None, error
    sample_rate, error = _parse_int_field(payload, "sample_rate", 16000)
    if error:
        return None, error
    channels, error = _parse_int_field(payload, "channels", 1)
    if error:
        return None, error
    frame_duration_ms, error = _parse_int_field(payload, "frame_duration_ms", 20)
    if error:
        return None, error

    return (
        AudioConfig(
            language=language,
            model=model,
            sample_rate=sample_rate,
            channels=channels,
            sample_format=sample_format,
            frame_duration_ms=frame_duration_ms,
        ),
        None,
    )


def _parse_string_field(
    payload: dict[str, Any], field_name: str, default: str
) -> tuple[str, str | None]:
    if field_name not in payload:
        return default, None
    value = payload[field_name]
    if not isinstance(value, str):
        return default, f"{field_name} must be a string"
    return value, None


def _parse_int_field(
    payload: dict[str, Any], field_name: str, default: int
) -> tuple[int, str | None]:
    if field_name not in payload:
        return default, None
    value = payload[field_name]
    if isinstance(value, bool) or not isinstance(value, int):
        return default, f"{field_name} must be an integer"
    return value, None


def _validate_audio_config(config: AudioConfig) -> str | None:
    if config.sample_rate <= 0:
        return "sample_rate must be positive"
    if config.channels != 1:
        return "only mono audio is supported"
    if config.sample_format not in SUPPORTED_SAMPLE_FORMATS:
        return f"unsupported sample_format: {config.sample_format}"
    if config.frame_duration_ms <= 0:
        return "frame_duration_ms must be positive"
    if config.expected_frame_bytes() <= 0:
        return "invalid audio frame configuration"
    return None


async def _handle_binary_message(
    websocket: WebSocket,
    session: Session,
    session_id: str,
    data: bytes,
) -> None:
    if not session.audio_started or session.audio_config is None:
        await websocket.send_json(
            error_message(
                session_id,
                "AUDIO_NOT_STARTED",
                "Send audio.start before streaming audio frames",
                True,
            )
        )
        return

    try:
        frame = parse_audio_frame(data, session.audio_config)
    except AudioFrameError as exc:
        await websocket.send_json(
            error_message(
                session_id,
                "INVALID_AUDIO_FORMAT",
                exc.message,
                True,
            )
        )
        return

    dropped = session.append_audio_frame(
        BufferedAudioFrame(
            seq_num=frame.seq_num,
            timestamp_us=frame.timestamp_us,
            pcm_data=frame.pcm_data,
        )
    )
    if dropped:
        await websocket.send_json(buffer_overflow(session_id, dropped))
