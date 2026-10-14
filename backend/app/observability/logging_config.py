from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.config import Settings

SERVICE_NAME = "realtime-service"

_LOG_RECORD_STANDARD_KEYS = frozenset(logging.makeLogRecord({}).__dict__.keys())


def _extra_fields(record: logging.LogRecord) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key, value in record.__dict__.items():
        if key in _LOG_RECORD_STANDARD_KEYS:
            continue
        if key.startswith("_"):
            continue
        if value is None:
            continue
        fields[key] = value
    return fields


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname.lower(),
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        payload.update(_extra_fields(record))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class ConsoleLogFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(fmt="%(levelname)s %(name)s: %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        line = super().format(record)
        extras = _extra_fields(record)
        if not extras:
            return line
        suffix = " ".join(f"{key}={extras[key]}" for key in sorted(extras))
        return f"{line} {suffix}"


def configure_logging(settings: Settings) -> None:
    log_format = settings.log_format
    if log_format not in ("console", "json"):
        raise ValueError(f"Unsupported LOG_FORMAT: {log_format}")

    handler = logging.StreamHandler()
    if log_format == "json":
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(ConsoleLogFormatter())

    logging.basicConfig(
        level=settings.log_level.upper(),
        handlers=[handler],
        force=True,
    )


def log_fields(logger: logging.Logger, level: int, message: str, **fields: Any) -> None:
    logger.log(level, message, extra=fields)
