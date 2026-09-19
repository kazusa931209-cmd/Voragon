# ADR-002: Rust Native Layer

## Status

Accepted

## Context

Voragon's desktop application requires native OS integration: microphone capture, system tray, global shortcuts, notifications, window management, and future display-capture privacy controls. These capabilities are platform-specific and cannot be reliably implemented in a web-based UI layer.

## Problem

Determine where native OS functionality lives in the desktop architecture and which language implements it.

## Decision

Implement all native OS integration in a **Rust layer** within the Tauri application. React/TypeScript accesses native capabilities exclusively through Tauri commands and events (IPC).

## Alternatives Considered

### JavaScript/TypeScript Native Modules (Node.js NAPI)

| Pros | Cons |
|------|------|
| Single language for UI and native | Requires Node.js runtime |
| npm ecosystem | Not compatible with Tauri's architecture |
| | Performance overhead for audio processing |

### Platform-Specific Code in React (Web APIs)

| Pros | Cons |
|------|------|
| No additional language | Web Audio API insufficient for low-latency capture |
| | No system tray, shortcuts, or notifications |
| | No display-capture privacy controls |
| | Inconsistent across platforms |

### Rust Native Layer (via Tauri)

| Pros | Cons |
|------|------|
| Tauri's intended architecture | Requires Rust expertise |
| Direct OS API access | Two-language codebase |
| Low overhead for audio processing | Build complexity (cross-compilation) |
| Platform-specific code isolated in Rust modules | |
| Strong audio ecosystem (cpal, rodio) | |

## Trade-offs

- **Two-language codebase**: Frontend developers work in TypeScript; native features require Rust.
- **IPC overhead**: Audio frames cross the Tauri IPC boundary. This must be measured; if overhead is significant, buffering strategies in Rust reduce crossing frequency.
- **Build complexity**: Cross-compilation for macOS and Windows requires platform-specific toolchains.

## Consequences

- Audio capture, system tray, shortcuts, notifications, and privacy controls are Rust modules
- React communicates with Rust via Tauri commands (`invoke`) and events (`emit`/`listen`)
- Platform-specific code is isolated in Rust modules with conditional compilation (`#[cfg(target_os = "macos")]`)
- Future native inference (on-device) would also live in the Rust layer

## Future Reconsideration

Reconsider if:
- Tauri IPC overhead for audio frames proves too high (> 5 ms per frame)
- A platform is added that Tauri does not support
- On-device inference requires a different runtime (e.g., Core ML on macOS via Swift)
