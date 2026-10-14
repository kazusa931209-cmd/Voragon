from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from uuid import UUID

from app.config import Settings
from app.websocket.session import AudioConfig, SegmentAsrState, Session


@dataclass(frozen=True)
class DetachedSessionRecord:
    session_id: str
    expires_at_monotonic: float
    detached_at_monotonic: float
    audio_config: AudioConfig | None
    session_elapsed_ms: int
    segment_asr: SegmentAsrState | None
    vad_degraded: bool
    vad_error_sent: bool

    def is_expired(self, now: float) -> bool:
        return now >= self.expires_at_monotonic


_lock = asyncio.Lock()
_detached: dict[str, DetachedSessionRecord] = {}


def snapshot_session(session: Session) -> DetachedSessionRecord:
    segment = session.segment_asr
    segment_copy = (
        SegmentAsrState(
            segment_id=segment.segment_id,
            start_ms=segment.start_ms,
            sequence=segment.sequence,
            last_partial_ms=segment.last_partial_ms,
        )
        if segment is not None
        else None
    )
    audio_config = session.audio_config
    return DetachedSessionRecord(
        session_id=str(session.session_id),
        expires_at_monotonic=0.0,
        detached_at_monotonic=0.0,
        audio_config=audio_config,
        session_elapsed_ms=session.session_elapsed_ms,
        segment_asr=segment_copy,
        vad_degraded=session.vad_degraded,
        vad_error_sent=session.vad_error_sent,
    )


async def detach_session(
    session: Session,
    reconnect_window_s: int,
    *,
    now: float | None = None,
) -> DetachedSessionRecord:
    monotonic_now = now if now is not None else time.monotonic()
    record = snapshot_session(session)
    record = DetachedSessionRecord(
        session_id=record.session_id,
        expires_at_monotonic=monotonic_now + reconnect_window_s,
        detached_at_monotonic=monotonic_now,
        audio_config=record.audio_config,
        session_elapsed_ms=record.session_elapsed_ms,
        segment_asr=record.segment_asr,
        vad_degraded=record.vad_degraded,
        vad_error_sent=record.vad_error_sent,
    )
    async with _lock:
        _purge_expired_locked(monotonic_now)
        _detached[record.session_id] = record
    return record


async def peek_detached(
    session_id: str,
    *,
    now: float | None = None,
) -> DetachedSessionRecord | None:
    monotonic_now = now if now is not None else time.monotonic()
    async with _lock:
        _purge_expired_locked(monotonic_now)
        record = _detached.get(session_id)
        if record is None or record.is_expired(monotonic_now):
            if record is not None:
                del _detached[session_id]
            return None
        return record


async def take_detached(
    session_id: str,
    *,
    now: float | None = None,
) -> DetachedSessionRecord | None:
    record, error_code = await claim_detached(session_id, now=now)
    if error_code is not None:
        return None
    return record


async def claim_detached(
    session_id: str,
    *,
    now: float | None = None,
) -> tuple[DetachedSessionRecord | None, str | None]:
    """Claim a detached session for resume. Returns (record, error_code)."""
    monotonic_now = now if now is not None else time.monotonic()
    async with _lock:
        record = _detached.get(session_id)
        if record is None:
            _purge_expired_locked(monotonic_now)
            return None, "SESSION_NOT_FOUND"
        if record.is_expired(monotonic_now):
            del _detached[session_id]
            _purge_expired_locked(monotonic_now)
            return None, "SESSION_EXPIRED"
        del _detached[session_id]
        _purge_expired_locked(monotonic_now)
        return record, None


async def purge_expired(*, now: float | None = None) -> int:
    monotonic_now = now if now is not None else time.monotonic()
    async with _lock:
        return _purge_expired_locked(monotonic_now)


async def clear_all() -> None:
    async with _lock:
        _detached.clear()


async def detached_count() -> int:
    async with _lock:
        return len(_detached)


def _purge_expired_locked(now: float) -> int:
    expired = [sid for sid, record in _detached.items() if record.is_expired(now)]
    for sid in expired:
        del _detached[sid]
    return len(expired)


def restore_session(
    record: DetachedSessionRecord,
    settings: Settings,
    buffer_seconds: int,
) -> Session:
    """Rebuild a live Session from detached state (used by P2-006 resume)."""
    session = Session(session_id=UUID(record.session_id))
    session.session_elapsed_ms = record.session_elapsed_ms
    session.vad_degraded = record.vad_degraded
    session.vad_error_sent = record.vad_error_sent
    session.segment_asr = (
        SegmentAsrState(
            segment_id=record.segment_asr.segment_id,
            start_ms=record.segment_asr.start_ms,
            sequence=record.segment_asr.sequence,
            last_partial_ms=record.segment_asr.last_partial_ms,
        )
        if record.segment_asr is not None
        else None
    )
    if record.audio_config is not None:
        session.start_audio(record.audio_config, buffer_seconds, settings)
    return session
