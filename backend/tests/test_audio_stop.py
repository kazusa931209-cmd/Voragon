from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import SegmentClosed, SegmentOpened, VadConfig
from app.websocket.audio_frame import build_audio_frame
from app.websocket.messages import utc_timestamp


def _ping_message(session_id: str) -> dict:
    return {
        "type": "ping",
        "id": "msg-ping",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


class OpenSegmentVadStream:
    """Opens a segment on first frame and keeps it open until flush."""

    def __init__(self, tracker: SegmentTracker) -> None:
        self.tracker = tracker
        self._opened = False

    def process_frame(self, pcm_data: bytes) -> list[SegmentOpened | SegmentClosed]:
        events: list[SegmentOpened | SegmentClosed] = []
        if not self._opened:
            events.append(self.tracker.on_speech_start())
            self._opened = True
        if self.tracker.active_segment is not None:
            self.tracker.append_frame(pcm_data)
        return events

    def enter_degraded_mode(self) -> None:
        self.tracker.enter_degraded_mode()

    def process_degraded_frame(self, pcm_data: bytes) -> list[SegmentOpened | SegmentClosed]:
        return self.tracker.process_degraded_frame(pcm_data)

    def flush_active_segment(self) -> list[SegmentOpened | SegmentClosed]:
        return self.tracker.flush_active_segment()


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def _audio_stop_message(session_id: str) -> dict:
    return {
        "type": "audio.stop",
        "id": "msg-audio-stop",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def test_audio_stop_flushes_open_segment_and_emits_final() -> None:
    tracker = SegmentTracker(VadConfig(min_speech_duration_ms=250, frame_duration_ms=20))
    stream = OpenSegmentVadStream(tracker)
    speech_pcm = b"\x01" * 640

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with client.websocket_connect("/v1/realtime") as websocket:
                started = websocket.receive_json()
                session_id = started["session_id"]
                websocket.send_json(_audio_start_message(session_id))

                for seq in range(20):
                    websocket.send_bytes(build_audio_frame(speech_pcm, seq_num=seq))

                websocket.send_json(_audio_stop_message(session_id))

                messages = [websocket.receive_json()]
                if messages[0]["type"] != "transcript.final":
                    messages.append(websocket.receive_json())

    finals = [m for m in messages if m["type"] == "transcript.final"]
    assert len(finals) == 1
    assert finals[0]["payload"]["text"].startswith("final-")


def test_audio_stop_discards_short_open_segment() -> None:
    tracker = SegmentTracker(VadConfig(min_speech_duration_ms=250, frame_duration_ms=20))
    stream = OpenSegmentVadStream(tracker)
    speech_pcm = b"\x01" * 640

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with client.websocket_connect("/v1/realtime") as websocket:
                started = websocket.receive_json()
                session_id = started["session_id"]
                websocket.send_json(_audio_start_message(session_id))
                websocket.send_bytes(build_audio_frame(speech_pcm, seq_num=0))
                websocket.send_json(_audio_stop_message(session_id))
                websocket.send_json(_ping_message(session_id))
                response = websocket.receive_json()

    assert response["type"] == "pong"


def test_audio_stop_before_audio_start_returns_error() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/realtime") as websocket:
            started = websocket.receive_json()
            session_id = started["session_id"]
            websocket.send_json(_audio_stop_message(session_id))
            error = websocket.receive_json()

    assert error["type"] == "error"
    assert error["payload"]["code"] == "AUDIO_NOT_STARTED"
