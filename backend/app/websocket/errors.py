from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import WebSocket

from app.observability.logging_config import log_fields
from app.websocket.messages import error_message
from app.websocket.rate_limit import PerSecondRateLimiter

logger = logging.getLogger(__name__)

# Defaults from docs/api/error-handling.md (implemented codes only).
RECOVERABLE_BY_CODE: dict[str, bool] = {
    "INVALID_MESSAGE": True,
    "UNKNOWN_MESSAGE_TYPE": True,
    "AUDIO_NOT_STARTED": True,
    "INVALID_AUDIO_FORMAT": True,
    "AUDIO_SEQUENCE_GAP": True,
    "BUFFER_OVERFLOW": True,
    "ASR_INFERENCE_FAILED": True,
    "VAD_FAILED": True,
    "SESSION_NOT_FOUND": False,
    "SESSION_EXPIRED": False,
    "ASR_MODEL_UNAVAILABLE": False,
    "INTERNAL_ERROR": False,
}

# Unrecoverable resume failures keep the interim WebSocket session open.
RESUME_ERRORS = frozenset({"SESSION_NOT_FOUND", "SESSION_EXPIRED"})


def should_terminate_session(code: str, recoverable: bool) -> bool:
    if code in RESUME_ERRORS:
        return False
    return not recoverable


class WebSocketErrorEmitter:
    def __init__(
        self,
        websocket: WebSocket,
        session_id: str,
        end_session: Callable[[str], Awaitable[None]],
        *,
        max_errors_per_second: int = 10,
    ) -> None:
        self.websocket = websocket
        self._session_id = session_id
        self._end_session = end_session
        self._rate_limiter = PerSecondRateLimiter(max_per_second=max_errors_per_second)

    @property
    def session_id(self) -> str:
        return self._session_id

    def update_session_id(self, session_id: str) -> None:
        self._session_id = session_id

    async def emit(
        self,
        code: str,
        message: str,
        *,
        recoverable: bool | None = None,
        details: dict[str, Any] | None = None,
        terminate_session: bool | None = None,
    ) -> bool:
        """Emit an error envelope. Returns True if the error was sent."""
        now = time.monotonic()
        if not self._rate_limiter.allow(now):
            logger.debug(
                "error rate limited session_id=%s code=%s",
                self._session_id,
                code,
            )
            return False

        rec = (
            recoverable
            if recoverable is not None
            else RECOVERABLE_BY_CODE.get(code, True)
        )
        terminate = (
            terminate_session
            if terminate_session is not None
            else should_terminate_session(code, rec)
        )

        self._rate_limiter.record()
        await self.websocket.send_json(
            error_message(self._session_id, code, message, rec, details)
        )
        log_fields(
            logger,
            logging.WARNING,
            "Client error emitted",
            session_id=self._session_id,
            code=code,
            recoverable=rec,
        )

        if terminate:
            await self._end_session("error")
        return True
