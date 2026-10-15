# Docker Compose

## Overview

Docker Compose provides a local development and testing environment for Voragon. **Quick start:** [docker/README.md](../../docker/README.md).

**Status:** **Implemented** (CPU, in-process ASR) — [P4-001](../roadmap/dev-step-p4-001-backend-dockerfile.md)–[P4-004](../roadmap/dev-step-p4-004-docker-dev-docs.md). Quick start: [docker/README.md](../../docker/README.md). GPU override and ASR sidecar deferred.

## Architecture

```mermaid
flowchart LR
    Desktop["Desktop App<br/>(host)"]
    Backend["realtime-backend<br/>:8000"]
    ASR["asr-inference<br/>:8081<br/>(optional sidecar)"]

    Desktop -->|ws://localhost:8000| Backend
    Backend -->|"HTTP (internal)"| ASR
```

The desktop application runs on the host (not containerized) for native audio capture and OS integration. The backend and optional ASR sidecar run in containers.

## Services

| Service | Image | Port | GPU | Status |
|---------|-------|------|-----|--------|
| `realtime-backend` | `voragon/realtime-backend:local` | 8000 | No | **Implemented** ([docker-compose.yml](../../docker/docker-compose.yml)) |
| `asr-inference` | `voragon/asr-inference` | 8081 | Optional | Planned (sidecar) |

### When to Use ASR Sidecar

| Scenario | ASR Location |
|----------|-------------|
| faster-whisper, in-process | Inside `realtime-backend` container |
| whisper.cpp binary | Separate `asr-inference` container |
| GPU inference (NVIDIA) | Separate `asr-inference` container with GPU access |

## Planned Compose File Structure

```
docker/
├── docker-compose.yml          # Main compose file
├── docker-compose.gpu.yml      # GPU override (NVIDIA)
├── realtime-backend/
│   └── Dockerfile
└── asr-inference/
    └── Dockerfile
```

## Realtime backend image (P4-001)

Build and run from the **repository root** (see [docker/realtime-backend/README.md](../../docker/realtime-backend/README.md)):

```bash
docker build -f docker/realtime-backend/Dockerfile -t voragon/realtime-backend:local .
docker run --rm -p 8000:8000 -e ASR_MODEL=tiny voragon/realtime-backend:local
curl -f http://localhost:8000/health
```

Model weights download on **first container start**, not during `docker build`.

## Usage

From the `docker/` directory (repository root is the image build context). Compose project name is **`voragon`** (see `name:` in [`docker-compose.yml`](../../docker/docker-compose.yml)), so resources are prefixed `voragon_` (not `docker_`).

```bash
cd docker
docker compose up --build
```

Stop any host backend or other container already using port **8000** first. First startup may take **1–2 minutes** until the compose healthcheck passes (model download + ASR warmup).

```bash
curl -f http://localhost:8000/health
```

### Planned later

```bash
# Start with ASR sidecar (not implemented)
docker compose up

# Start with GPU support (not implemented)
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

## Volume Mounts

| Mount | Purpose |
|-------|---------|
| `voragon-model-cache` (named volume) | Persists model downloads at `/var/lib/voragon/model-cache` in the container (Docker volume name `voragon_voragon-model-cache`) |
| Configuration | Override via compose `environment` or [compose.env.example](../../docker/compose.env.example) |

Compose sets:

| Env var | Cache |
|---------|--------|
| `HF_HOME` | Hugging Face Hub — **faster-whisper** ASR weights (`Systran/faster-whisper-*`) |
| `TORCH_HOME` | PyTorch hub / **Silero VAD** artifacts when fetched at runtime |

`docker compose down` keeps the named volume; `docker compose down -v` removes it. To reuse a host cache, bind-mount e.g. `~/.cache/huggingface` → `/var/lib/voragon/model-cache/huggingface` (see [compose.env.example](../../docker/compose.env.example)).

## Networking

- `realtime-backend` exposed on `localhost:8000`
- `asr-inference` accessible only within the Docker network (not exposed to host)
- Desktop connects to `ws://localhost:8000/v1/realtime`

## Health Checks

| Service | Check |
|---------|-------|
| `realtime-backend` | `curl -f http://localhost:8000/health` |
| `asr-inference` | `curl -f http://localhost:8081/health` |

## Related Documents

- [Local Development](local-development.md)
- [Kubernetes Local](kubernetes-local.md)
- [Backend Architecture](../architecture/backend.md)
