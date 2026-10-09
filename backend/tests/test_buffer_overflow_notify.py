import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.audio_buffer import AudioBuffer, BufferedAudioFrame
from app.websocket.audio_frame import build_audio_frame
from app.websocket.buffer_overflow import BufferOverflowNotifier
from app.websocket.messages import utc_timestamp
from app.websocket.session import Session


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def test_audio_buffer_pop_oldest() -> None:
    buffer = AudioBuffer(max_bytes=1280)
    pcm = b"\x00" * 640
    buffer.append(BufferedAudioFrame(seq_num=1, timestamp_us=0, pcm_data=pcm))
    buffer.append(BufferedAudioFrame(seq_num=2, timestamp_us=0, pcm_data=pcm))

    assert buffer.pop_oldest() is True
    assert len(buffer) == 1
    assert buffer.pop_oldest() is True
    assert buffer.pop_oldest() is False


def test_buffer_overflow_notifier_rate_limit() -> None:
    notifier = BufferOverflowNotifier(max_per_second=2)
    t0 = 1000.0

    assert notifier.should_notify(t0) is True
    notifier.record_notification()
    assert notifier.should_notify(t0) is True
    notifier.record_notification()
    assert notifier.should_notify(t0) is False
    assert notifier.should_notify(t0 + 1.1) is True


def test_buffer_overflow_emits_error_and_event(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIO_BUFFER_SECONDS", "1")

    def noop_release(_self: Session) -> None:
        return None

    monkeypatch.setattr(Session, "release_processed_audio_frame", noop_release)

    pcm = b"\x00" * 640
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            websocket.send_json(_audio_start_message(started["session_id"]))

            for seq in range(60):
                websocket.send_bytes(build_audio_frame(pcm, seq_num=seq))

            overflow = websocket.receive_json()
            error = websocket.receive_json()

    assert overflow["type"] == "buffer.overflow"
    assert overflow["payload"]["dropped_frames"] >= 1
    assert error["type"] == "error"
    assert error["payload"]["code"] == "BUFFER_OVERFLOW"
    assert error["payload"]["recoverable"] is True
    assert error["payload"]["details"]["dropped_frames"] >= 1


def test_release_processed_frame_keeps_buffer_small() -> None:
    from app.config import get_settings
    from app.websocket.session import AudioConfig

    session = Session.create()
    settings = get_settings()
    session.start_audio(AudioConfig(), buffer_seconds=30, settings=settings)
    pcm = b"\x00" * 640
    for seq in range(100):
        session.append_audio_frame(
            BufferedAudioFrame(seq_num=seq, timestamp_us=0, pcm_data=pcm)
        )
        session.release_processed_audio_frame()

    assert session.audio_buffer is not None
    assert len(session.audio_buffer) == 0
