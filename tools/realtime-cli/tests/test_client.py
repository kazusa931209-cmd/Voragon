import json
from uuid import uuid4

import pytest
import websockets
from websockets.asyncio.server import serve

from realtime_cli.client import RealtimeClient, run_session
from realtime_cli.frames import BYTES_PER_FRAME


async def _mock_backend(websocket) -> None:
    session_id = str(uuid4())
    await websocket.send(
        json.dumps(
            {
                "type": "session.started",
                "id": str(uuid4()),
                "session_id": session_id,
                "timestamp": "2026-09-22T00:00:00.000Z",
                "payload": {"protocol_version": 1, "reconnect_window_s": 30},
            }
        )
    )

    async for message in websocket:
        if isinstance(message, str):
            data = json.loads(message)
            if data["type"] == "audio.start":
                await websocket.send(
                    json.dumps(
                        {
                            "type": "transcript.partial",
                            "id": str(uuid4()),
                            "session_id": session_id,
                            "timestamp": "2026-09-22T00:00:01.000Z",
                            "payload": {
                                "segment_id": "seg-1",
                                "sequence": 1,
                                "text": "hello",
                                "language": "en",
                            },
                        }
                    )
                )
                await websocket.send(
                    json.dumps(
                        {
                            "type": "transcript.final",
                            "id": str(uuid4()),
                            "session_id": session_id,
                            "timestamp": "2026-09-22T00:00:02.000Z",
                            "payload": {
                                "segment_id": "seg-1",
                                "sequence": 2,
                                "text": "hello world",
                                "language": "en",
                                "start_ms": 0,
                                "end_ms": 400,
                            },
                        }
                    )
                )
                break
        elif isinstance(message, bytes):
            continue


async def _one_frame_source():
    yield b"\x01" * BYTES_PER_FRAME


@pytest.mark.asyncio
async def test_run_session_receives_transcripts(capsys: pytest.CaptureFixture[str]) -> None:
    async with serve(_mock_backend, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        url = f"ws://localhost:{port}"

        await run_session(url, _one_frame_source(), realtime_pacing=False, tail_wait_s=0.1)

    output = capsys.readouterr().out
    assert "[partial] hello" in output
    assert "[final]   hello world" in output


@pytest.mark.asyncio
async def test_realtime_client_sends_audio_start_and_binary_frame() -> None:
    received: list[object] = []

    async def handler(websocket) -> None:
        session_id = str(uuid4())
        await websocket.send(
            json.dumps(
                {
                    "type": "session.started",
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "timestamp": "2026-09-22T00:00:00.000Z",
                    "payload": {"protocol_version": 1, "reconnect_window_s": 30},
                }
            )
        )
        async for message in websocket:
            received.append(message)
            if isinstance(message, bytes):
                break

    async with serve(handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        async with RealtimeClient(f"ws://localhost:{port}") as client:
            await client.start_audio()
            await client.send_pcm_frame(b"\x02" * BYTES_PER_FRAME, 0)

    assert any(isinstance(item, str) and "audio.start" in item for item in received)
    assert any(isinstance(item, bytes) for item in received)


@pytest.mark.asyncio
async def test_realtime_client_sends_audio_stop() -> None:
    received: list[str] = []

    async def handler(websocket) -> None:
        session_id = str(uuid4())
        await websocket.send(
            json.dumps(
                {
                    "type": "session.started",
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "timestamp": "2026-09-22T00:00:00.000Z",
                    "payload": {"protocol_version": 1, "reconnect_window_s": 30},
                }
            )
        )
        async for message in websocket:
            if isinstance(message, str):
                received.append(message)
                if "audio.stop" in message:
                    break

    async with serve(handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        async with RealtimeClient(f"ws://localhost:{port}") as client:
            await client.start_audio()
            await client.send_audio_stop()

    assert any("audio.stop" in item for item in received)


@pytest.mark.asyncio
async def test_run_session_sends_audio_stop_for_file_mode(capsys) -> None:
    received: list[str] = []

    async def handler(websocket) -> None:
        session_id = str(uuid4())
        await websocket.send(
            json.dumps(
                {
                    "type": "session.started",
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "timestamp": "2026-09-22T00:00:00.000Z",
                    "payload": {"protocol_version": 1, "reconnect_window_s": 30},
                }
            )
        )
        async for message in websocket:
            if isinstance(message, str):
                received.append(message)

    async with serve(handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        await run_session(
            f"ws://localhost:{port}",
            _one_frame_source(),
            realtime_pacing=False,
            tail_wait_s=0.05,
            send_stop_after_stream=True,
        )

    assert any("audio.stop" in item for item in received)
