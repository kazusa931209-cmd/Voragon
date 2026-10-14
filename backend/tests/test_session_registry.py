import asyncio
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.websocket.messages import utc_timestamp
from app.websocket.session import AudioConfig, Session
from app.websocket.session_registry import (
    clear_all,
    detach_session,
    peek_detached,
    purge_expired,
    restore_session,
    snapshot_session,
    take_detached,
)


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    asyncio.run(clear_all())
    yield
    asyncio.run(clear_all())


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {"language": "en"},
    }


@pytest.mark.asyncio
async def test_detach_and_peek_within_window() -> None:
    session = Session.create()
    settings = get_settings()
    session.start_audio(AudioConfig(), buffer_seconds=30, settings=settings)
    session.session_elapsed_ms = 120
    session.begin_segment_asr("seg-1", 100)

    t0 = 1000.0
    record = await detach_session(session, reconnect_window_s=30, now=t0)

    assert record.session_id == str(session.session_id)
    assert record.expires_at_monotonic == t0 + 30
    assert record.audio_config is not None
    assert record.segment_asr is not None
    assert record.segment_asr.segment_id == "seg-1"

    found = await peek_detached(record.session_id, now=t0 + 10)
    assert found is not None
    assert found.session_id == record.session_id

    expired = await peek_detached(record.session_id, now=t0 + 30)
    assert expired is None


@pytest.mark.asyncio
async def test_purge_expired_removes_stale_sessions() -> None:
    session = Session.create()
    settings = get_settings()
    session.start_audio(AudioConfig(), buffer_seconds=30, settings=settings)

    t0 = 500.0
    await detach_session(session, reconnect_window_s=5, now=t0)
    assert await peek_detached(str(session.session_id), now=t0 + 4) is not None

    removed = await purge_expired(now=t0 + 5)
    assert removed == 1
    assert await peek_detached(str(session.session_id), now=t0 + 5) is None


@pytest.mark.asyncio
async def test_take_detached_removes_from_registry() -> None:
    session = Session.create()
    settings = get_settings()
    session.start_audio(AudioConfig(), buffer_seconds=30, settings=settings)
    t0 = 0.0
    await detach_session(session, reconnect_window_s=30, now=t0)

    taken = await take_detached(str(session.session_id), now=t0 + 1)
    assert taken is not None
    assert await peek_detached(str(session.session_id), now=t0 + 1) is None


def test_restore_session_rebuilds_audio_state() -> None:
    settings = get_settings()
    original = Session.create()
    original.start_audio(AudioConfig(language="de"), buffer_seconds=30, settings=settings)
    original.session_elapsed_ms = 80
    record = replace(
        snapshot_session(original),
        expires_at_monotonic=999.0,
        detached_at_monotonic=0.0,
    )

    restored = restore_session(record, settings, buffer_seconds=30)
    assert str(restored.session_id) == record.session_id
    assert restored.audio_started is True
    assert restored.audio_config is not None
    assert restored.audio_config.language == "de"
    assert restored.session_elapsed_ms == 80


@pytest.mark.asyncio
async def test_websocket_detach_on_abrupt_disconnect_after_audio_start() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_audio_start_message(session_id))

        record = await peek_detached(session_id)
        assert record is not None
        assert record.audio_config is not None


@pytest.mark.asyncio
async def test_websocket_no_detach_after_audio_stop() -> None:
    def _audio_stop_message(session_id: str) -> dict:
        return {
            "type": "audio.stop",
            "id": "msg-audio-stop",
            "session_id": session_id,
            "timestamp": utc_timestamp(),
            "payload": {},
        }

    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_audio_start_message(session_id))
            websocket.send_json(_audio_stop_message(session_id))
            ended = websocket.receive_json()
            assert ended["type"] == "session.ended"

        record = await peek_detached(session_id)
        assert record is None
