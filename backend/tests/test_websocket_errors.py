from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.asr.base import ASRModelUnavailableError
from app.main import app
from app.websocket.errors import WebSocketErrorEmitter
from app.websocket.messages import utc_timestamp
from app.websocket.rate_limit import PerSecondRateLimiter
from tests.test_transcript_handler import (
    _audio_start_message,
    _scripted_vad_stream,
    _speech_pcm,
    _stream_frames,
)


def test_missing_message_type_invalid_message() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(
                {
                    "id": "msg-no-type",
                    "session_id": started["session_id"],
                    "timestamp": utc_timestamp(),
                    "payload": {},
                }
            )
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert error["payload"]["recoverable"] is True


def test_non_object_json_root_invalid_message() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_text('"hello"')
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert error["payload"]["recoverable"] is True


def test_per_second_rate_limiter_caps_at_max() -> None:
    limiter = PerSecondRateLimiter(max_per_second=10)
    t0 = 100.0
    for _ in range(10):
        assert limiter.allow(t0) is True
        limiter.record()
    assert limiter.allow(t0) is False
    assert limiter.allow(t0 + 1.0) is True


@pytest.mark.asyncio
async def test_error_emitter_rate_limit_drops_excess() -> None:
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    end_session = AsyncMock()
    emitter = WebSocketErrorEmitter(
        websocket,
        "session-id",
        end_session,
        max_errors_per_second=10,
    )

    for i in range(10):
        sent = await emitter.emit("INVALID_MESSAGE", f"err-{i}")
        assert sent is True

    sent = await emitter.emit("INVALID_MESSAGE", "err-11")
    assert sent is False
    assert websocket.send_json.await_count == 10
    end_session.assert_not_awaited()


@pytest.mark.asyncio
async def test_error_emitter_fatal_ends_session() -> None:
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    end_session = AsyncMock()
    emitter = WebSocketErrorEmitter(
        websocket,
        "session-id",
        end_session,
        max_errors_per_second=10,
    )

    await emitter.emit(
        "ASR_MODEL_UNAVAILABLE",
        "ASR model is not loaded or unhealthy",
    )

    end_session.assert_awaited_once_with("error")


def test_fatal_asr_model_unavailable_emits_session_ended() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with patch.object(
                client.app.state.asr_engine,
                "transcribe_final",
                new=AsyncMock(
                    side_effect=ASRModelUnavailableError("model down"),
                ),
            ):
                with client.websocket_connect("/v1/realtime") as websocket:
                    started = websocket.receive_json()
                    session_id = started["session_id"]
                    websocket.send_json(_audio_start_message(session_id))
                    _stream_frames(websocket, 20, _speech_pcm())

                    partial = websocket.receive_json()
                    error = websocket.receive_json()
                    ended = websocket.receive_json()

    assert partial["type"] == "transcript.partial"
    assert error["type"] == "error"
    assert error["payload"]["code"] == "ASR_MODEL_UNAVAILABLE"
    assert error["payload"]["recoverable"] is False
    assert ended["type"] == "session.ended"
    assert ended["payload"]["reason"] == "error"
