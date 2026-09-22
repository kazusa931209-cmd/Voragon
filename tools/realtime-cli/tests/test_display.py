from realtime_cli.display import TranscriptDisplay, format_server_message


def test_format_transcript_partial() -> None:
    line = format_server_message(
        {
            "type": "transcript.partial",
            "payload": {"text": "hello", "sequence": 1},
        }
    )
    assert line == "[partial] hello"


def test_transcript_display_records_finals_and_prints_summary(capsys) -> None:
    display = TranscriptDisplay()
    display.handle_message(
        {"type": "transcript.partial", "payload": {"text": "hel"}}
    )
    display.handle_message(
        {"type": "transcript.final", "payload": {"text": "hello world"}}
    )
    display.handle_message(
        {"type": "transcript.final", "payload": {"text": "again"}}
    )
    display.print_combined_summary()

    output = capsys.readouterr().out
    assert "[final]   hello world" in output
    assert "[final]   again" in output
    assert "--- combined finals ---" in output
    assert "hello world again" in output


def test_format_session_started_is_silent() -> None:
    assert format_server_message({"type": "session.started", "payload": {}}) is None
