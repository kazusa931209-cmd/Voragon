# Realtime backend image

CPU image for the Voragon FastAPI WebSocket service (`backend/`).

## Build

Run from the **repository root** (build context includes `backend/`):

```bash
docker build -f docker/realtime-backend/Dockerfile -t voragon/realtime-backend:local .
```

The image installs **CPU** `torch`/`torchaudio` (via PyTorch’s CPU wheel index), `onnxruntime`, and `faster-whisper` for in-process ASR. Expect a large image (often **1–2 GB+** on disk after build).

## Run

```bash
docker run --rm -p 8000:8000 \
  -e ASR_MODEL=tiny \
  voragon/realtime-backend:local
```

First startup downloads VAD/ASR weights from Hugging Face (not done at `docker build` time). Use a smaller `ASR_MODEL` (e.g. `tiny`, `base`) for faster first run.

Health check (after ASR warmup completes):

```bash
curl -f http://localhost:8000/health
```

Override server and ASR settings with the same env vars as [backend/.env.example](../../backend/.env.example).
