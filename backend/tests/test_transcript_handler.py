from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.asr.base import ASRInferenceError, TranscriptResult
from app.main import app
from app.pipeline.segment_tracker import SegmentTracker
from app.pipeline.vad import SegmentClosed, SegmentOpened, VadConfig
from app.websocket.audio_frame import build_audio_frame
from app.websocket.messages import utc_timestamp


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


def _ping_message(session_id: str) -> dict:
    return {
        "type": "ping",
        "id": "msg-ping",
        "session_id": session_id,
        "timestamp": utc_timestamp(),
        "payload": {},
    }


def _audio_start_message(session_id: str) -> dict:
    return {
        "type": "audio.start",
        "id": "msg-audio-start",
        "session_id": session_id,
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


def test_transcript_partial_and_final_emitted_for_segment() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with client.websocket_connect("/v1/realtime") as websocket:
                started = websocket.receive_json()
                session_id = started["session_id"]
                websocket.send_json(_audio_start_message(session_id))
                _stream_frames(websocket, 20, _speech_pcm())

                partial = websocket.receive_json()
                final = websocket.receive_json()

    assert partial["type"] == "transcript.partial"
    assert final["type"] == "transcript.final"

    segment_id = partial["payload"]["segment_id"]
    assert final["payload"]["segment_id"] == segment_id
    assert partial["payload"]["text"].startswith("partial-")
    assert final["payload"]["text"].startswith("final-")
    assert partial["payload"]["sequence"] == 1
    assert final["payload"]["sequence"] == 2
    assert final["payload"]["start_ms"] == 20
    assert final["payload"]["end_ms"] == 400
    assert "confidence" in partial["payload"]
    assert "confidence" in final["payload"]


def test_empty_asr_result_emits_no_transcript() -> None:
    stream = _scripted_vad_stream()
    quiet_pcm = b"\x00" * 640
    empty_result = TranscriptResult(text="", language="en", confidence=None)

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            asr_engine = client.app.state.asr_engine
            with (
                patch.object(
                    asr_engine,
                    "transcribe_partial",
                    new=AsyncMock(return_value=empty_result),
                ),
                patch.object(
                    asr_engine,
                    "transcribe_final",
                    new=AsyncMock(return_value=empty_result),
                ),
            ):
                with client.websocket_connect("/v1/realtime") as websocket:
                    started = websocket.receive_json()
                    session_id = started["session_id"]
                    websocket.send_json(_audio_start_message(session_id))
                    _stream_frames(websocket, 20, quiet_pcm)
                    websocket.send_json(_ping_message(session_id))
                    response = websocket.receive_json()

    assert response["type"] == "pong"


def test_asr_inference_failed_emits_error_and_keeps_session_open() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            with patch.object(
                client.app.state.asr_engine,
                "transcribe_final",
                new=AsyncMock(side_effect=ASRInferenceError("boom")),
            ):
                with client.websocket_connect("/v1/realtime") as websocket:
                    started = websocket.receive_json()
                    session_id = started["session_id"]
                    websocket.send_json(_audio_start_message(session_id))
                    _stream_frames(websocket, 20, _speech_pcm())

                    partial = websocket.receive_json()
                    error = websocket.receive_json()
                    websocket.send_json(_ping_message(session_id))
                    ping_response = websocket.receive_json()

    assert partial["type"] == "transcript.partial"
    assert error["type"] == "error"
    assert error["payload"]["code"] == "ASR_INFERENCE_FAILED"
    assert error["payload"]["recoverable"] is True
    assert ping_response["type"] == "pong"


def test_partial_transcription_is_throttled() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            asr_engine = client.app.state.asr_engine
            with patch.object(
                asr_engine,
                "transcribe_partial",
                wraps=asr_engine.transcribe_partial,
            ) as transcribe_partial:
                with client.websocket_connect("/v1/realtime") as websocket:
                    started = websocket.receive_json()
                    session_id = started["session_id"]
                    websocket.send_json(_audio_start_message(session_id))
                    _stream_frames(websocket, 20, _speech_pcm())
                    websocket.receive_json()
                    websocket.receive_json()

                assert transcribe_partial.await_count < 20
