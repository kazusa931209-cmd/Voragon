from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import suppress
from datetime import datetime, timezone
from uuid import uuid4

import websockets
from websockets.asyncio.client import ClientConnection

from realtime_cli.display import TranscriptDisplay
from realtime_cli.frames import FRAME_DURATION_MS, build_audio_frame


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


class RealtimeClient:
    def __init__(self, url: str, *, language: str = "en") -> None:
        self.url = url
        self.language = language
        self.session_id: str | None = None
        self._ws: ClientConnection | None = None

    async def __aenter__(self) -> RealtimeClient:
        self._ws = await websockets.connect(self.url)
        started = json.loads(await self._ws.recv())
        if started.get("type") != "session.started":
            raise RuntimeError(f"Expected session.started, got {started.get('type')}")
        self.session_id = started["session_id"]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def start_audio(self) -> None:
        if self._ws is None or self.session_id is None:
            raise RuntimeError("WebSocket session is not connected")
        await self._ws.send(
            json.dumps(
                {
                    "type": "audio.start",
                    "id": str(uuid4()),
                    "session_id": self.session_id,
                    "timestamp": utc_timestamp(),
                    "payload": {"language": self.language},
                }
            )
        )

    async def send_audio_stop(self) -> None:
        if self._ws is None or self.session_id is None:
            raise RuntimeError("WebSocket session is not connected")
        await self._ws.send(
            json.dumps(
                {
                    "type": "audio.stop",
                    "id": str(uuid4()),
                    "session_id": self.session_id,
                    "timestamp": utc_timestamp(),
                    "payload": {},
                }
            )
        )

    async def send_pcm_frame(self, pcm_data: bytes, seq_num: int) -> None:
        if self._ws is None:
            raise RuntimeError("WebSocket session is not connected")
        await self._ws.send(build_audio_frame(pcm_data, seq_num))

    async def receive_messages(self) -> AsyncIterator[dict]:
        if self._ws is None:
            raise RuntimeError("WebSocket session is not connected")
        async for raw in self._ws:
            yield json.loads(raw)


async def stream_audio_frames(
    frame_source: AsyncIterator[bytes],
    send_frame: Callable[[bytes, int], Awaitable[None]],
    *,
    frame_delay_s: float = FRAME_DURATION_MS / 1000,
) -> None:
    seq_num = 0
    async for pcm_data in frame_source:
        await send_frame(pcm_data, seq_num)
        seq_num += 1
        if frame_delay_s > 0:
            await asyncio.sleep(frame_delay_s)


async def receive_and_display(client: RealtimeClient, display: TranscriptDisplay) -> None:
    async for message in client.receive_messages():
        display.handle_message(message)


async def run_session(
    url: str,
    frame_source: AsyncIterator[bytes],
    *,
    language: str = "en",
    realtime_pacing: bool = True,
    tail_wait_s: float = 5.0,
    send_stop_after_stream: bool = False,
) -> None:
    display = TranscriptDisplay()
    async with RealtimeClient(url, language=language) as client:
        print(f"Connected session_id={client.session_id}", flush=True)
        await client.start_audio()

        receiver = asyncio.create_task(receive_and_display(client, display))
        try:
            delay = FRAME_DURATION_MS / 1000 if realtime_pacing else 0.0
            await stream_audio_frames(frame_source, client.send_pcm_frame, frame_delay_s=delay)
            if send_stop_after_stream:
                await client.send_audio_stop()
            await asyncio.sleep(tail_wait_s)
        finally:
            receiver.cancel()
            with suppress(asyncio.CancelledError):
                await receiver
            display.print_combined_summary()
