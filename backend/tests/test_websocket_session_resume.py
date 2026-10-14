import asyncio
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import SegmentClosed, SegmentOpened, VadConfig
from app.websocket.audio_frame import build_audio_frame
from app.websocket.messages import utc_timestamp
from app.websocket.session_registry import clear_all, peek_detached


class MonotonicClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


class ScriptedVadStream:
    def __init__(self, tracker: SegmentTracker, *, open_on_frame: int, close_on_frame: int) -> None:
        self.tracker = tracker
        self.open_on_frame = open_on_frame
        self.close_on_frame = close_on_frame
        self.frame_count = 0

    def process_frame(self, pcm_data: bytes) -> list[SegmentOpened | SegmentClosed]:
        self.frame_count += 1
        events: list[SegmentOpened | SegmentClosed] = []

        if self.frame_count == self.open_on_frame:
            events.append(self.tracker.on_speech_start())

        if self.tracker.active_segment is not None:
            self.tracker.append_frame(pcm_data)

        if self.frame_count == self.close_on_frame and self.tracker.active_segment is not None:
            events.extend(self.tracker.on_speech_end())

        return events

    def enter_degraded_mode(self) -> None:
        self.tracker.enter_degraded_mode()

    def process_degraded_frame(self, pcm_data: bytes) -> list[SegmentOpened | SegmentClosed]:
        return self.tracker.process_degraded_frame(pcm_data)


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
        "payload": {},
    }


def _session_resume_message(previous_session_id: str) -> dict:
    return {
        "type": "session.resume",
        "id": "msg-session-resume",
        "session_id": previous_session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def _scripted_vad_stream() -> ScriptedVadStream:
    tracker = SegmentTracker(VadConfig(min_speech_duration_ms=250, frame_duration_ms=20))
    return ScriptedVadStream(tracker, open_on_frame=1, close_on_frame=20)


def _speech_pcm() -> bytes:
    return b"\x01" * 640


def _stream_frames(websocket, frame_count: int, pcm: bytes) -> None:
    for seq in range(frame_count):
        websocket.send_bytes(build_audio_frame(pcm, seq_num=seq))


def _disconnect_after_audio_start(client: TestClient) -> str:
    with client.websocket_connect("/v1/realtime") as websocket:
        started = websocket.receive_json()
        session_id = started["session_id"]
        websocket.send_json(_audio_start_message(session_id))
    return session_id


def test_session_resume_happy_path_transcripts() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            old_session_id = _disconnect_after_audio_start(client)

            with client.websocket_connect("/v1/realtime") as websocket:
                interim = websocket.receive_json()
                assert interim["type"] == "session.started"
                assert interim["session_id"] != old_session_id

                websocket.send_json(_session_resume_message(old_session_id))
                restored = websocket.receive_json()

                assert restored["type"] == "session.started"
                assert restored["session_id"] == old_session_id
                assert restored["payload"]["reconnect_window_s"] == 30

                websocket.send_json(_audio_start_message(old_session_id))
                _stream_frames(websocket, 20, _speech_pcm())

                partial = websocket.receive_json()
                final = websocket.receive_json()

    assert partial["type"] == "transcript.partial"
    assert final["type"] == "transcript.final"
    assert partial["session_id"] == old_session_id
    assert final["session_id"] == old_session_id


@pytest.mark.asyncio
async def test_session_resume_claim_consumes_detached_record() -> None:
    with TestClient(app) as client:
        old_session_id = _disconnect_after_audio_start(client)
        assert await peek_detached(old_session_id) is not None

        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            websocket.send_json(_session_resume_message(old_session_id))
            restored = websocket.receive_json()
            assert restored["session_id"] == old_session_id

    assert await peek_detached(old_session_id) is None


def test_session_resume_unknown_session_id() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            interim = websocket.receive_json()
            unknown_id = str(uuid4())
            websocket.send_json(_session_resume_message(unknown_id))
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["session_id"] == interim["session_id"]
    assert error["payload"]["code"] == "SESSION_NOT_FOUND"
    assert error["payload"]["recoverable"] is False


def test_session_resume_expired_window(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = MonotonicClock(start=5000.0)
    monkeypatch.setattr("app.websocket.handler.time.monotonic", clock)
    monkeypatch.setattr("app.websocket.session_registry.time.monotonic", clock)

    with TestClient(app) as client:
        old_session_id = _disconnect_after_audio_start(client)

        clock.advance(31.0)

        with client.websocket_connect("/v1/realtime") as websocket:
            interim = websocket.receive_json()
            websocket.send_json(_session_resume_message(old_session_id))
            error = websocket.receive_json()

            assert error["type"] == "error"
            assert error["payload"]["code"] == "SESSION_EXPIRED"
            assert error["payload"]["recoverable"] is False

            websocket.send_json(_audio_start_message(interim["session_id"]))


def test_session_resume_rejected_after_interim_audio_start() -> None:
    with TestClient(app) as client:
        old_session_id = _disconnect_after_audio_start(client)

        with client.websocket_connect("/v1/realtime") as websocket:
            interim = websocket.receive_json()
            websocket.send_json(_audio_start_message(interim["session_id"]))
            websocket.send_json(_session_resume_message(old_session_id))
            error = websocket.receive_json()

    assert error["payload"]["code"] == "INVALID_MESSAGE"
    assert error["payload"]["recoverable"] is True
