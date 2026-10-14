from __future__ import annotations

import time
from dataclasses import dataclass, field

from fastapi import WebSocket

from app.websocket.errors import WebSocketErrorEmitter
from app.websocket.messages import buffer_overflow
from app.websocket.rate_limit import PerSecondRateLimiter


@dataclass
class BufferOverflowNotifier:
    """Rate-limit buffer.overflow + error notification bursts."""

    max_per_second: int = 10
    _limiter: PerSecondRateLimiter = field(init=False)

    def __post_init__(self) -> None:
        self._limiter = PerSecondRateLimiter(max_per_second=self.max_per_second)

    def should_notify(self, now: float) -> bool:
        return self._limiter.allow(now)

    def record_notification(self) -> None:
        self._limiter.record()


async def emit_buffer_overflow_notifications(
    websocket: WebSocket,
    session_id: str,
    dropped_frames: int,
    notifier: BufferOverflowNotifier,
    errors: WebSocketErrorEmitter,
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
    await errors.emit(
        "BUFFER_OVERFLOW",
        detail,
        details={"dropped_frames": dropped_frames},
    )
