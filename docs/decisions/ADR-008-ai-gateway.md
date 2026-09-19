# ADR-008: AI Gateway

## Status

Accepted

## Context

Voragon is designed as an extensible AI inference platform, not a single-purpose Whisper application. Future capabilities include LLM inference, embeddings, vision, and agents. The system must support multiple models, model versioning, fallback, and capability-based routing without changing client or realtime-service code.

## Problem

How should the system route inference requests to the correct model backend, and how should new model types be added without modifying existing services?

## Decision

Introduce an **AI Gateway** service that routes inference requests to model backends based on **capability aliases** (e.g., `asr.default`, `llm.default`). The AI Gateway is an internal service, separate from the external API Gateway.

## Alternatives Considered

### Direct Model Calls from Realtime Service

| Pros | Cons |
|------|------|
| Simplest architecture | Tight coupling to specific model |
| No additional service | Adding models requires realtime-service changes |
| | No fallback, versioning, or health checking |
| | Does not scale to multiple model types |

### Configuration-Based Routing in Realtime Service

| Pros | Cons |
|------|------|
| No additional service | Routing logic mixed with session management |
| Configurable model selection | Realtime-service grows in complexity |
| | No centralized model health monitoring |

### AI Gateway (Dedicated Service)

| Pros | Cons |
|------|------|
| Clean separation of concerns | Additional service to deploy and operate |
| Model-agnostic routing | Not needed until multiple models exist |
| Centralized health checking | Adds latency hop (minimal for internal HTTP) |
| Capability aliases decouple clients from models | |
| Supports fallback, versioning, policies | |
| Extensible to any model type | |

### Managed AI Gateway (AWS Bedrock, etc.)

| Pros | Cons |
|------|------|
| Managed service | Vendor lock-in |
| Multi-model support | Per-request pricing |
| | Less control over model deployment |
| | Conflicts with self-hosted requirement |

## Trade-offs

- **Premature for Phase 1**: The AI Gateway is not needed until Phase 8. Phases 1–7 use direct ASR adapter calls. This is acceptable; the abstraction interface is designed from the start.
- **Additional latency**: One HTTP hop between realtime-service and inference. Expected < 5 ms for internal cluster communication.
- **Operational complexity**: One more service to deploy, monitor, and scale.

## Consequences

- Phase 1–7: realtime-service calls ASR adapter directly (in-process or sidecar)
- Phase 8: AI Gateway introduced; realtime-service routes through it
- Model registry stored in ConfigMap (Kubernetes) or config file (local)
- Capability aliases defined in AI Gateway config, not in application code
- New model types added by registering in AI Gateway, not modifying realtime-service
- AI Gateway is internal-only; never exposed to external clients

## Future Reconsideration

Reconsider if:
- Only one model type is ever needed (unlikely given platform goals)
- AI Gateway latency or complexity is not justified by the number of models deployed
- A managed service (Bedrock, etc.) provides better cost/performance for specific model types
