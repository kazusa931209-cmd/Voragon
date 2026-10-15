# Build context: repository root (see docker/realtime-backend/README.md).
FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/pyproject.toml backend/README.md ./
COPY backend/app ./app

# CPU-only PyTorch (default pip torch on Linux pulls CUDA extras and a much larger image).
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    "torch>=2.2.0" "torchaudio>=2.2.0" \
    && pip install --no-cache-dir .

ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_FORMAT=json

EXPOSE 8000

CMD ["python", "-m", "app.main"]
