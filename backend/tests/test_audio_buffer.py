from app.pipeline.audio_buffer import AudioBuffer, BufferedAudioFrame


def _frame(pcm: bytes, seq_num: int = 0) -> BufferedAudioFrame:
    return BufferedAudioFrame(seq_num=seq_num, timestamp_us=0, pcm_data=pcm)


def test_audio_buffer_appends_frames_within_capacity() -> None:
    buffer = AudioBuffer(max_bytes=1280)
    pcm = b"\x00" * 640

    dropped = buffer.append(_frame(pcm, seq_num=1))
    dropped += buffer.append(_frame(pcm, seq_num=2))

    assert dropped == 0
    assert len(buffer) == 2
    assert buffer.total_bytes() == 1280


def test_audio_buffer_drops_oldest_when_full() -> None:
    buffer = AudioBuffer(max_bytes=1280)
    pcm = b"\x00" * 640

    buffer.append(_frame(pcm, seq_num=1))
    buffer.append(_frame(pcm, seq_num=2))
    dropped = buffer.append(_frame(pcm, seq_num=3))

    assert dropped == 1
    assert len(buffer) == 2
    assert buffer.total_bytes() == 1280


def test_audio_buffer_drops_multiple_frames_in_single_append() -> None:
    buffer = AudioBuffer(max_bytes=1000)
    small = b"\x00" * 200
    large = b"\x00" * 800

    for seq in range(1, 6):
        buffer.append(_frame(small, seq_num=seq))

    dropped = buffer.append(_frame(large, seq_num=6))

    assert dropped == 4
    assert len(buffer) == 2
    assert buffer.total_bytes() == 1000
