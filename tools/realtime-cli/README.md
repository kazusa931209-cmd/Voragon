# Voragon Realtime CLI

Minimal test client for Phase 1: captures microphone audio (or replays a PCM/WAV file), streams it to the backend over WebSocket, and prints partial/final transcripts.

## Setup

```bash
cd tools/realtime-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Ensure the backend is running (`cd backend && python -m app.main`).

## Microphone

```bash
python -m realtime_cli
# or: voragon-realtime
```

Speak into the microphone. Partials update on one line; finals print as stable lines.

Optional flags:

- `--url ws://localhost:8000/v1/realtime`
- `--language en`
- `--device 0` — sounddevice input index
- `--duration 30` — stop after 30 seconds
- `--tail 5` — wait for late transcripts after streaming (default 5 s for mic)

## File replay

Replay mono 16 kHz 16-bit WAV or raw s16le PCM. File mode **uploads as fast as possible**, sends **`audio.stop`** to flush the last segment, then waits for CPU ASR to finish.

```bash
python -m realtime_cli --file sample-mono-16khz.wav --tail 90
python -m realtime_cli --file path/to/audio.pcm --tail 60
python -m realtime_cli --file path/to/audio.wav --realtime   # 20 ms pacing instead
```

On exit, `--- combined finals ---` prints all stable segment transcripts in order.

**Note:** CPU ASR (`large-v3-turbo`) may need a long `--tail` on longer files. For faster local testing, run the backend with `ASR_MODEL=tiny`.

## Tests

```bash
pytest -v
```
