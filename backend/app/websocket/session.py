from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Session:
    session_id: UUID

    @classmethod
    def create(cls) -> Session:
        return cls(session_id=uuid4())
