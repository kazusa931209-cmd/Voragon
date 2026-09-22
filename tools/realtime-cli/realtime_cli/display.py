from __future__ import annotations

import sys
from typing import Any


class TranscriptDisplay:
    def __init__(self) -> None:
        self._finals: list[str] = []
        self._partial_line_active = False

    def handle_message(self, message: dict[str, Any]) -> None:
        message_type = message.get("type")
        payload = message.get("payload", {})

        if message_type == "transcript.partial":
            self._print_partial(payload.get("text", ""))
            return
        if message_type == "transcript.final":
            text = payload.get("text", "")
            self._clear_partial_line()
            print(f"[final]   {text}", flush=True)
            if text:
                self._finals.append(text)
            return
        if message_type == "error":
            self._clear_partial_line()
            code = payload.get("code", "UNKNOWN")
            detail = payload.get("message", "")
            print(f"[error]   {code}: {detail}", flush=True)
            return
        if message_type == "buffer.overflow":
            dropped = payload.get("dropped_frames", 0)
            print(f"[warn]    buffer overflow: dropped {dropped} frame(s)", flush=True)
            return
        if message_type in {"session.started", "session.ended", "pong"}:
            return
        print(f"[{message_type}] {payload}", flush=True)

    def print_combined_summary(self) -> None:
        self._clear_partial_line()
        if not self._finals:
            return
        print("--- combined finals ---", flush=True)
        print(" ".join(self._finals), flush=True)

    def _print_partial(self, text: str) -> None:
        line = f"[partial] {text}"
        sys.stdout.write("\r" + line + " " * max(0, 80 - len(line)))
        sys.stdout.flush()
        self._partial_line_active = True

    def _clear_partial_line(self) -> None:
        if self._partial_line_active:
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()
            self._partial_line_active = False


def format_server_message(message: dict[str, Any]) -> str | None:
    """Legacy helper for tests; prefer TranscriptDisplay for interactive output."""
    message_type = message.get("type")
    payload = message.get("payload", {})

    if message_type == "transcript.partial":
        return f"[partial] {payload.get('text', '')}"
    if message_type == "transcript.final":
        return f"[final]   {payload.get('text', '')}"
    if message_type == "error":
        code = payload.get("code", "UNKNOWN")
        detail = payload.get("message", "")
        return f"[error]   {code}: {detail}"
    if message_type == "buffer.overflow":
        dropped = payload.get("dropped_frames", 0)
        return f"[warn]    buffer overflow: dropped {dropped} frame(s)"
    if message_type in {"session.started", "session.ended", "pong"}:
        return None
    return f"[{message_type}] {payload}"
