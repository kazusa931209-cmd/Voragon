# ADR-007: Separate Desktop and Backend Architecture

## Status

Accepted

## Context

Voragon's desktop application and AI inference backend have fundamentally different responsibilities, scaling characteristics, and technology requirements. The desktop is a lightweight client; the backend handles realtime audio processing and model inference.

## Problem

Should the desktop application and the inference backend run as a single process or as separate services?

## Decision

Run the **desktop application** and the **Realtime Backend** as **separate processes**, communicating over WebSocket on localhost (development) or through API Gateway (production).

## Alternatives Considered

### Monolithic Desktop (Embedded Inference)

| Pros | Cons |
|------|------|
| Single process, simpler distribution | Desktop binary includes model weights (~1.5 GB+) |
| No network overhead | High memory and CPU/GPU usage in desktop process |
| No WebSocket complexity | Cannot scale inference independently |
| | Cannot update model without updating desktop app |
| | Violates "lightweight desktop" requirement |

### Desktop + Embedded Backend (Bundled)

| Pros | Cons |
|------|------|
| Single installer | Desktop manages backend lifecycle (complex) |
| User sees one application | Backend crash affects desktop |
| | Still cannot scale independently |
| | Larger install package |

### Separate Desktop and Backend

| Pros | Cons |
|------|------|
| Independent deployment and scaling | Two processes to manage locally |
| Desktop remains lightweight | WebSocket communication overhead (minimal on localhost) |
| Backend can be updated without desktop changes | Developer must start both processes |
| Same backend serves multiple clients (future) | |
| Inference can move to cloud without desktop changes | |
| Clear service boundary | |

## Trade-offs

- **Developer experience**: Developers must start both the desktop and backend. Mitigated by documentation, scripts, and optional backend auto-launcher in later phases.
- **Network overhead on localhost**: WebSocket on localhost adds ~1–5 ms latency. Negligible compared to inference latency.
- **Distribution**: Desktop and backend are separate artifacts. Docker Compose (Phase 4) bundles them for convenience.

## Consequences

- Desktop and backend have separate repositories or top-level directories
- Desktop connects to backend via configurable WebSocket URL
- Backend can be deployed independently (Docker, Kubernetes)
- Model updates do not require desktop app updates
- Multiple desktop clients can connect to the same backend (future)
- Backend process can be launched by the desktop (Phase 4+) or run separately

## Future Reconsideration

Reconsider if:
- WebSocket overhead on localhost proves measurable and problematic
- A single-installer experience becomes a hard requirement
- On-device inference (Phase 10+) changes the deployment model
