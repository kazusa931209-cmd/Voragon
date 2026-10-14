import re
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from tests.test_transcript_handler import (
    _audio_start_message,
    _scripted_vad_stream,
    _speech_pcm,
    _stream_frames,
)


def _gauge_value(body: str, name: str) -> float:
    pattern = rf"^{re.escape(name)} (\d+(?:\.\d+)?(?:e[+-]?\d+)?)$"
    for line in body.splitlines():
        match = re.match(pattern, line)
        if match:
            return float(match.group(1))
    raise AssertionError(f"Gauge {name} not found in metrics body")


def _counter_value(body: str, name: str) -> float:
    pattern = rf"^{re.escape(name)} (\d+(?:\.\d+)?(?:e[+-]?\d+)?)$"
    for line in body.splitlines():
        match = re.match(pattern, line)
        if match:
            return float(match.group(1))
    raise AssertionError(f"Counter {name} not found in metrics body")


def test_metrics_endpoint_returns_prometheus_text() -> None:
    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "# HELP voragon_ws_connections" in body
    assert "# TYPE voragon_ws_connections gauge" in body
    assert "# HELP voragon_audio_frames_received_total" in body


def test_ws_connection_gauge_increments() -> None:
    with TestClient(app) as client:
        baseline = _gauge_value(client.get("/metrics").text, "voragon_ws_connections")
        with client.websocket_connect("/v1/realtime") as websocket:
            websocket.receive_json()
            during = _gauge_value(client.get("/metrics").text, "voragon_ws_connections")
            assert during == baseline + 1
        after = _gauge_value(client.get("/metrics").text, "voragon_ws_connections")
    assert after == baseline


def test_audio_and_transcript_counters_move() -> None:
    stream = _scripted_vad_stream()

    with patch("app.websocket.session.create_vad_engine") as create_engine:
        engine = MagicMock()
        engine.create_stream.return_value = stream
        create_engine.return_value = engine

        with TestClient(app) as client:
            before = client.get("/metrics").text
            frames_before = _counter_value(
                before, "voragon_audio_frames_received_total"
            )
            partial_before = _counter_value(
                before, "voragon_transcript_partial_total"
            )
            final_before = _counter_value(
                before, "voragon_transcript_final_total"
            )

            with client.websocket_connect("/v1/realtime") as websocket:
                started = websocket.receive_json()
                session_id = started["session_id"]
                websocket.send_json(_audio_start_message(session_id))
                _stream_frames(websocket, 20, _speech_pcm())
                websocket.receive_json()
                websocket.receive_json()

            after = client.get("/metrics").text

    assert _counter_value(after, "voragon_audio_frames_received_total") > frames_before
    assert _counter_value(after, "voragon_transcript_partial_total") > partial_before
    assert _counter_value(after, "voragon_transcript_final_total") > final_before
