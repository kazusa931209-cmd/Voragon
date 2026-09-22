from app.websocket.messages import pong, transcript_final, transcript_partial


def test_pong_message_shape() -> None:
    message = pong("session-1")

    assert message["type"] == "pong"
    assert message["session_id"] == "session-1"
    assert message["payload"] == {}


def test_transcript_partial_includes_confidence_when_present() -> None:
    message = transcript_partial(
        "session-1",
        "seg-1",
        1,
        "hello",
        "en",
        0.92,
    )

    assert message["type"] == "transcript.partial"
    assert message["session_id"] == "session-1"
    payload = message["payload"]
    assert payload["segment_id"] == "seg-1"
    assert payload["sequence"] == 1
    assert payload["text"] == "hello"
    assert payload["language"] == "en"
    assert payload["confidence"] == 0.92


def test_transcript_partial_omits_confidence_when_missing() -> None:
    message = transcript_partial("session-1", "seg-1", 2, "hello", "en")

    assert "confidence" not in message["payload"]


def test_transcript_final_includes_timing_fields() -> None:
    message = transcript_final(
        "session-1",
        "seg-1",
        3,
        "hello world",
        "en",
        100,
        2400,
        0.95,
    )

    assert message["type"] == "transcript.final"
    payload = message["payload"]
    assert payload["sequence"] == 3
    assert payload["start_ms"] == 100
    assert payload["end_ms"] == 2400
    assert payload["confidence"] == 0.95
