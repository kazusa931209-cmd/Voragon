from app.websocket.session import SegmentAsrState, Session


def test_should_emit_partial_respects_interval() -> None:
    session = Session.create()
    session.segment_asr = SegmentAsrState(segment_id="seg-1", start_ms=0, last_partial_ms=0)
    session.session_elapsed_ms = 299

    assert session.should_emit_partial(300) is False

    session.session_elapsed_ms = 300
    assert session.should_emit_partial(300) is True


def test_mark_partial_emitted_updates_last_partial_ms() -> None:
    session = Session.create()
    session.segment_asr = SegmentAsrState(segment_id="seg-1", start_ms=0, last_partial_ms=0)
    session.session_elapsed_ms = 300

    session.mark_partial_emitted()

    assert session.segment_asr.last_partial_ms == 300
    assert session.should_emit_partial(300) is False
