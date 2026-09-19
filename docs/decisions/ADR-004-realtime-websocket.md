# ADR-004: WebSocket for Realtime Communication

## Status

Accepted

## Context

Voragon requires bidirectional realtime communication between the desktop application and the backend: continuous audio frame streaming (client → server) and transcript delivery (server → client). The protocol must support low-latency partial transcripts, session management, and reconnection.

## Problem

Select a communication protocol for realtime audio streaming and transcript delivery.

## Decision

Use **WebSocket** over a versioned endpoint (`/v1/realtime`) for all realtime communication between the desktop and backend.

## Alternatives Considered

### HTTP Long Polling

| Pros | Cons |
|------|------|
| Simple, universally supported | High latency (poll interval) |
| Works through restrictive proxies | Inefficient for continuous audio streaming |
| | No binary frame support without encoding overhead |

### Server-Sent Events (SSE)

| Pros | Cons |
|------|------|
| Simple server → client streaming | Unidirectional (no client → server audio) |
| HTTP-based, easy to proxy | Would require separate HTTP endpoint for audio upload |
| | Higher overhead than WebSocket for bidirectional |

### gRPC Streaming

| Pros | Cons |
|------|------|
| Efficient binary protocol | Requires gRPC client in Tauri (no native browser support) |
| Strong typing with protobuf | Additional dependency in desktop app |
| Bidirectional streaming | More complex to debug than WebSocket |
| | API Gateway WebSocket support is more mature than gRPC |

### WebRTC

| Pros | Cons |
|------|------|
| Designed for realtime media | Overkill for client-server (designed for peer-to-peer) |
| Low latency | Requires STUN/TURN infrastructure |
| | Complex signaling |
| | Unnecessary for localhost and single-server deployments |

### WebSocket

| Pros | Cons |
|------|------|
| Bidirectional, full-duplex | Requires connection management (reconnect, heartbeat) |
| Low overhead for binary frames | Stateful (scaling challenges) |
| Native browser/Tauri support | No built-in message ordering guarantees |
| AWS API Gateway supports WebSocket | |
| Well-understood protocol | |
| JSON control + binary audio frames | |

## Trade-offs

- **Stateful connections**: WebSocket connections are long-lived and tied to a server instance. Scaling requires sticky sessions or session migration (see [Kubernetes Architecture](../architecture/kubernetes.md)).
- **No built-in reliability**: Message delivery is not guaranteed. Application-level sequence numbers and reconnection logic are required.
- **Binary + JSON hybrid**: Control messages use JSON; audio frames use binary WebSocket frames. This is a common pattern but requires clear protocol documentation.

## Consequences

- Desktop WebSocket client implemented in TypeScript
- Backend WebSocket handler in FastAPI (Starlette)
- Protocol versioned at `/v1/realtime`
- JSON for control messages; binary for audio frames
- Application-level heartbeat, reconnection, and ordering
- AWS API Gateway WebSocket API for production ingress

## Future Reconsideration

Reconsider if:
- WebSocket scaling becomes a bottleneck at target concurrency
- A move to HTTP/3 datagrams or WebTransport provides measurable latency improvement
- gRPC becomes necessary for internal service-to-service communication (separate from client protocol)
