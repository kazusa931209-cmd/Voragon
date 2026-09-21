import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.websocket.messages import error_message, session_started
from app.websocket.session import Session

logger = logging.getLogger(__name__)

router = APIRouter()


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
                await _handle_text_message(websocket, session_id, message["text"])
            elif "bytes" in message:
                await websocket.send_json(
                    error_message(
                        session_id,
                        "UNKNOWN_MESSAGE_TYPE",
                        "Unrecognized message type",
                        True,
                    )
                )
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected session_id=%s", session_id)


async def _handle_text_message(
    websocket: WebSocket, session_id: str, text: str
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

    message_type = data.get("type", "<missing>")
    await websocket.send_json(
        error_message(
            session_id,
            "UNKNOWN_MESSAGE_TYPE",
            f"Unrecognized message type: {message_type}",
            True,
        )
    )
