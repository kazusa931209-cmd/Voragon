# ADR-003: Python + FastAPI Backend

## Status

Accepted

## Context

Voragon requires a realtime backend service that manages WebSocket sessions, orchestrates the audio pipeline (VAD → ASR), and delivers transcripts. The backend must integrate with Python-based ML libraries (faster-whisper, Silero VAD) and support async I/O for concurrent WebSocket sessions.

## Problem

Select a backend language and framework for the Realtime Backend Service.

## Decision

Use **Python** with **FastAPI** for the Realtime Backend Service.

## Alternatives Considered

### Node.js (Fastify / ws)

| Pros | Cons |
|------|------|
| Same language as frontend (TypeScript) | Weak ML ecosystem for ASR/VAD |
| Excellent WebSocket support | Would require calling Python inference as subprocess |
| | Two runtimes if inference is Python-based |

### Go (Gin / chi)

| Pros | Cons |
|------|------|
| Excellent concurrency and performance | No native ML library ecosystem |
| Small binary, low memory | Would require gRPC/HTTP to Python inference service |
| | Additional service complexity from day one |

### Rust (Axum / tokio)

| Pros | Cons |
|------|------|
| Performance and safety | No mature ASR library ecosystem |
| Low resource usage | Steep development cost for ML integration |
| | Would require bindings to whisper.cpp or sidecar |

### Python + FastAPI

| Pros | Cons |
|------|------|
| Native integration with faster-whisper, Silero VAD | GIL limits CPU-bound parallelism (mitigated by executors) |
| Async WebSocket support (Starlette) | Higher memory usage than Go/Rust |
| Rapid development | Not ideal for extreme scale (mitigated by horizontal scaling) |
| Large ML ecosystem | |
| Pydantic for message validation | |
| OpenTelemetry Python SDK | |

## Trade-offs

- **GIL constraint**: CPU-bound ASR inference blocks the event loop if not offloaded to a thread/process pool. This is a known pattern, not a blocker.
- **Memory usage**: Python processes use more memory than Go/Rust equivalents. Acceptable for the initial scale target (50–100 concurrent sessions per pod).
- **Performance ceiling**: Python is not the fastest runtime, but realtime-service is I/O-bound (WebSocket + inference delegation), not compute-bound. Inference runs on GPU.

## Consequences

- Backend team primarily works in Python
- ASR adapters (faster-whisper, whisper.cpp bindings) are Python modules
- VAD (Silero) runs in-process
- Async WebSocket handling via FastAPI/Starlette
- CPU-bound inference offloaded to thread pool executor
- Pydantic models for WebSocket message validation

## Future Reconsideration

Reconsider if:
- Concurrent session count exceeds Python's practical limit per pod (> 500)
- Inference latency requirements cannot be met with executor-based offloading
- A rewrite of the realtime-service in Go/Rust is justified by measured performance gaps
