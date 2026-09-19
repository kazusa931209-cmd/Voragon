# ADR-006: Local-First Architecture

## Status

Accepted

## Context

Voragon is described as a "local-first" platform. The initial product must work entirely on a developer's machine without cloud dependencies. Users should be able to transcribe speech locally with no data leaving their machine (in local mode). The architecture must also support a future transition to cloud-based GPU inference for production scale.

## Problem

Define what "local-first" means for Voragon and how it shapes architectural decisions.

## Decision

Adopt a **local-first architecture** where:

1. All components (desktop, backend, inference) run on localhost during development
2. The desktop application defaults to connecting to `localhost`
3. Audio data does not leave the machine in local mode
4. Cloud deployment is an extension, not a replacement, of the local architecture
5. The same API contracts work in both local and cloud environments

## Alternatives Considered

### Cloud-First

| Pros | Cons |
|------|------|
| Immediate access to GPU inference | Requires cloud infrastructure from day one |
| No local model management | Development depends on network and cloud availability |
| | Higher development cost and complexity |
| | Privacy concerns for audio data |

### Hybrid (Local UI, Cloud Inference)

| Pros | Cons |
|------|------|
| Lightweight local client | Audio leaves the machine (privacy concern) |
| GPU inference in cloud | Requires internet for all transcription |
| | Higher latency (network round-trip) |
| | Cannot develop offline |

### Local-First

| Pros | Cons |
|------|------|
| Full offline development | Local GPU/CPU may be slower than cloud GPU |
| No cloud cost during development | Model weights must be downloaded locally |
| Privacy by default | Developer must manage local inference setup |
| Same API works locally and in cloud | |
| One engineer can build and operate | |

## Trade-offs

- **Local inference performance**: Developer hardware varies. Apple Silicon (whisper.cpp) and NVIDIA GPU (faster-whisper) perform differently. Documentation must cover both paths.
- **Model weight management**: Developers must download model weights (~1.5 GB). This is a one-time cost but adds onboarding friction.
- **Cloud transition**: Moving to cloud requires only changing the backend URL and deploying services. The desktop application does not change.

## Consequences

- Desktop defaults to `ws://localhost:8000/v1/realtime`
- Backend runs as a local Python process (Phase 1) or Docker container (Phase 4)
- Inference runs in-process or as a local sidecar
- No authentication required in local mode
- No TLS required in local mode
- Cloud deployment is additive: API Gateway, EKS, GPU nodes are layered on top
- Settings UI allows changing backend URL for cloud connectivity

## Future Reconsideration

Reconsider if:
- Local inference performance is consistently unacceptable across target developer hardware
- A cloud-only mode is needed for users without capable local hardware
- Regulatory requirements mandate cloud processing for certain use cases
