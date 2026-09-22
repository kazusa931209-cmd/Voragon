from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.audio_buffer import BufferedAudioFrame


@dataclass(frozen=True)
class SequenceGap:
    first_missing: int
    last_missing: int


@dataclass(frozen=True)
class SequenceProcessResult:
    ready: list[BufferedAudioFrame]
    gaps: list[SequenceGap]


class AudioSequenceReorderer:
    """Reorder out-of-order audio frames and detect sequence gaps."""

    def __init__(self, buffer_ms: int = 100) -> None:
        self.buffer_ms = buffer_ms
        self._next_expected: int | None = None
        self._pending: dict[int, BufferedAudioFrame] = {}
        self._wait_deadline: float | None = None

    def reset(self) -> None:
        self._next_expected = None
        self._pending.clear()
        self._wait_deadline = None

    @property
    def waiting_for_reorder(self) -> bool:
        return self._wait_deadline is not None

    def flush_deadline(self) -> float | None:
        return self._wait_deadline

    def ingest(self, frame: BufferedAudioFrame, now: float) -> SequenceProcessResult:
        if self._next_expected is None:
            self._next_expected = frame.seq_num + 1
            return SequenceProcessResult([frame], [])

        seq = frame.seq_num
        expected = self._next_expected

        if seq < expected:
            return SequenceProcessResult([], [])

        if seq == expected:
            ready = [frame]
            self._next_expected += 1
            ready.extend(self._drain_pending())
            return SequenceProcessResult(ready, [])

        if seq not in self._pending:
            self._pending[seq] = frame
        if self._wait_deadline is None:
            self._wait_deadline = now + self.buffer_ms / 1000.0
        return SequenceProcessResult([], [])

    def flush(self, now: float) -> SequenceProcessResult:
        if self._next_expected is None:
            return SequenceProcessResult([], [])
        if self._wait_deadline is None or now < self._wait_deadline:
            return SequenceProcessResult([], [])
        return self._resolve_gap(now)

    def flush_all(self, now: float) -> SequenceProcessResult:
        if self._next_expected is None or not self._pending:
            self._wait_deadline = None
            return SequenceProcessResult([], [])

        if self._wait_deadline is None:
            self._wait_deadline = now
        return self._resolve_gap(now)

    def _resolve_gap(self, now: float) -> SequenceProcessResult:
        ready: list[BufferedAudioFrame] = []
        gaps: list[SequenceGap] = []

        min_pending = min(self._pending)
        expected = self._next_expected
        assert expected is not None

        if min_pending > expected:
            gaps.append(SequenceGap(expected, min_pending - 1))
            self._next_expected = min_pending

        ready.extend(self._drain_pending())

        if self._pending:
            self._wait_deadline = now + self.buffer_ms / 1000.0
        else:
            self._wait_deadline = None

        return SequenceProcessResult(ready, gaps)

    def _drain_pending(self) -> list[BufferedAudioFrame]:
        ready: list[BufferedAudioFrame] = []
        while self._next_expected in self._pending:
            ready.append(self._pending.pop(self._next_expected))
            self._next_expected += 1
        if not self._pending:
            self._wait_deadline = None
        return ready
