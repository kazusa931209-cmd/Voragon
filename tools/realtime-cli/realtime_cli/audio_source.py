from __future__ import annotations

import asyncio
import time
import wave
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import numpy as np

from realtime_cli.frames import BYTES_PER_FRAME, CHANNELS, FRAME_DURATION_MS, SAMPLE_RATE


def iter_pcm_frames_from_file(path: Path) -> Iterator[bytes]:
    if path.suffix.lower() == ".wav":
        yield from _iter_wav_frames(path)
    else:
        yield from _iter_raw_frames(path)


async def iter_pcm_frames_from_file_async(path: Path) -> AsyncIterator[bytes]:
    for frame in iter_pcm_frames_from_file(path):
        yield frame


async def iter_microphone_frames(
    *,
    device: int | None = None,
    duration_s: float | None = None,
) -> AsyncIterator[bytes]:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError(
            "sounddevice is required for microphone capture; install with pip install sounddevice"
        ) from exc

    queue: asyncio.Queue[bytes] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def callback(indata, _frames, _time, _status) -> None:
        pcm = np.asarray(indata, dtype=np.int16).tobytes()
        if len(pcm) < BYTES_PER_FRAME:
            pcm = pcm.ljust(BYTES_PER_FRAME, b"\x00")
        loop.call_soon_threadsafe(queue.put_nowait, pcm)

    deadline = time.monotonic() + duration_s if duration_s is not None else None

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=BYTES_PER_FRAME // 2,
        device=device,
        callback=callback,
    ):
        while deadline is None or time.monotonic() < deadline:
            try:
                pcm = await asyncio.wait_for(queue.get(), timeout=FRAME_DURATION_MS / 1000)
            except asyncio.TimeoutError:
                continue
            yield pcm


def _iter_raw_frames(path: Path) -> Iterator[bytes]:
    data = path.read_bytes()
    for offset in range(0, len(data), BYTES_PER_FRAME):
        chunk = data[offset : offset + BYTES_PER_FRAME]
        if len(chunk) < BYTES_PER_FRAME:
            chunk = chunk.ljust(BYTES_PER_FRAME, b"\x00")
        yield chunk


def _iter_wav_frames(path: Path) -> Iterator[bytes]:
    with wave.open(str(path), "rb") as wav_file:
        if wav_file.getnchannels() != CHANNELS:
            raise ValueError("WAV must be mono")
        if wav_file.getsampwidth() != 2:
            raise ValueError("WAV must be 16-bit PCM")
        if wav_file.getframerate() != SAMPLE_RATE:
            raise ValueError(f"WAV must be {SAMPLE_RATE} Hz")

        while True:
            chunk = wav_file.readframes(BYTES_PER_FRAME // 2)
            if not chunk:
                break
            if len(chunk) < BYTES_PER_FRAME:
                chunk = chunk.ljust(BYTES_PER_FRAME, b"\x00")
            yield chunk
