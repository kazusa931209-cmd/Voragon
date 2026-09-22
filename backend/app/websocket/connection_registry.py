from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

EndSessionFn = Callable[[str], Awaitable[None]]


@dataclass(frozen=True)
class RegisteredConnection:
    session_id: str
    end_session: EndSessionFn


_lock = asyncio.Lock()
_connections: list[RegisteredConnection] = []


async def register(connection: RegisteredConnection) -> None:
    async with _lock:
        _connections.append(connection)


async def unregister(connection: RegisteredConnection) -> None:
    async with _lock:
        if connection in _connections:
            _connections.remove(connection)


async def shutdown_all(reason: str = "server_shutdown") -> None:
    async with _lock:
        snapshot = list(_connections)
    for connection in snapshot:
        with contextlib.suppress(Exception):
            await connection.end_session(reason)
