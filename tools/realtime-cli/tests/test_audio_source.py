import wave
from pathlib import Path

import pytest

from realtime_cli.audio_source import iter_pcm_frames_from_file
from realtime_cli.frames import BYTES_PER_FRAME, SAMPLE_RATE


@pytest.fixture
def mono_wav(tmp_path: Path) -> Path:
    path = tmp_path / "tone.wav"
    pcm = (b"\x00\x10" * (BYTES_PER_FRAME // 2)) * 3
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm)
    return path


def test_iter_pcm_frames_from_wav(mono_wav: Path) -> None:
    frames = list(iter_pcm_frames_from_file(mono_wav))

    assert len(frames) == 3
    assert all(len(frame) == BYTES_PER_FRAME for frame in frames)


def test_iter_pcm_frames_from_raw(tmp_path: Path) -> None:
    path = tmp_path / "audio.pcm"
    path.write_bytes(b"\x01" * (BYTES_PER_FRAME * 2 + 100))

    frames = list(iter_pcm_frames_from_file(path))

    assert len(frames) == 3
    assert len(frames[-1]) == BYTES_PER_FRAME
