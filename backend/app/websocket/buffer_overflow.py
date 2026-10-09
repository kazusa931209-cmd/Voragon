from __future__ import annotations

import time
from dataclasses import dataclass, field

from fastapi import WebSocket

from app.websocket.messages import buffer_overflow, error_message


@dataclass
class BufferOverflowNotifier:
    """Rate-limit buffer overflow notifications (align with error-handling storm guard)."""

    max_per_second: int = 10
    _window_start: float = field(default=0.0, init=False)
    _count: int = field(default=0, init=False)

    def _reset_window_if_needed(self, now: float) -> None:
        if self._window_start == 0.0 or now - self._window_start >= 1.0:
            self._window_start = now
            self._count = 0

    def should_notify(self, now: float) -> bool:
        self._reset_window_if_needed(now)
        return self._count < self.max_per_second

    def record_notification(self) -> None:
        self._count += 1


async def emit_buffer_overflow_notifications(
    websocket: WebSocket,
    session_id: str,
    dropped_frames: int,
    notifier: BufferOverflowNotifier,
) -> None:
    if dropped_frames <= 0:
        return

    now = time.monotonic()
    if not notifier.should_notify(now):
        return

    notifier.record_notification()
    detail = (
        f"Audio buffer overflow; dropped {dropped_frames} frame(s)"
        if dropped_frames != 1
        else "Audio buffer overflow; dropped 1 frame"
    )
    await websocket.send_json(buffer_overflow(session_id, dropped_frames))
    await websocket.send_json(
        error_message(
            session_id,
            "BUFFER_OVERFLOW",
            detail,
            True,
            details={"dropped_frames": dropped_frames},
        )
    )
