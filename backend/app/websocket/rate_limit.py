from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PerSecondRateLimiter:
    """Allow at most max_per_second events within any rolling 1-second window."""

    max_per_second: int
    _window_start: float = field(default=0.0, init=False)
    _count: int = field(default=0, init=False)

    def _reset_window_if_needed(self, now: float) -> None:
        if self._window_start == 0.0 or now - self._window_start >= 1.0:
            self._window_start = now
            self._count = 0

    def allow(self, now: float) -> bool:
        self._reset_window_if_needed(now)
        return self._count < self.max_per_second

    def record(self) -> None:
        self._count += 1
