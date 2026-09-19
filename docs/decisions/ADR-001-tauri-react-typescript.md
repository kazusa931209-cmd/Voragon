# ADR-001: Tauri 2 + React + TypeScript for Desktop

## Status

Accepted

## Context

Voragon requires a cross-platform desktop application (macOS, Windows) that is local-first, lightweight, and capable of native OS integration (microphone, system tray, global shortcuts, notifications). The desktop must not contain AI inference logic.

## Problem

Select a desktop application framework that supports:
- Cross-platform deployment (macOS, Windows)
- Small binary size and low resource usage
- Native OS integration capabilities
- Modern UI development
- WebSocket client for realtime backend communication
- Future extensibility for additional native features

## Decision

Use **Tauri 2** with a **React + TypeScript** frontend and a **Rust** native layer.

## Alternatives Considered

### Electron

| Pros | Cons |
|------|------|
| Mature ecosystem, large community | Large binary size (~150 MB+) |
| Extensive npm package ecosystem | High memory usage (Chromium embedded) |
| Well-documented | Not aligned with "lightweight" requirement |

### Flutter Desktop

| Pros | Cons |
|------|------|
| Cross-platform (including mobile) | Smaller desktop ecosystem |
| Good performance | Dart language less common for systems integration |
| Consistent UI | Limited native OS integration compared to Tauri |

### Native (Swift + C#)

| Pros | Cons |
|------|------|
| Best platform integration | Two separate codebases (macOS + Windows) |
| Optimal performance | Higher development cost |
| Platform-native UX | No code sharing for UI |

### Tauri 2 + React + TypeScript

| Pros | Cons |
|------|------|
| Small binary size (< 50 MB target) | Younger ecosystem than Electron |
| Low memory usage (system WebView) | WebView behavior varies by platform |
| Rust native layer for OS integration | Rust learning curve for frontend developers |
| React ecosystem for UI | Fewer desktop-specific libraries than Electron |
| Active development (Tauri 2) | Plugin ecosystem still maturing |

## Trade-offs

- **WebView dependency**: UI renders in the system WebView (WebKit on macOS, WebView2 on Windows). Behavior may differ slightly between platforms.
- **Rust required for native features**: Any OS-level functionality requires Rust code, creating a two-language codebase.
- **Smaller community**: Fewer Stack Overflow answers and tutorials compared to Electron, but growing rapidly.

## Consequences

- Desktop team needs both TypeScript (UI) and Rust (native) skills
- UI development uses standard React patterns
- Native features (audio, tray, shortcuts) are implemented in Rust and exposed via Tauri IPC
- Binary size and memory usage should meet lightweight targets
- Tauri plugin ecosystem is used where available; custom Rust code where not

## Future Reconsideration

Reconsider if:
- Tauri 2 proves unstable or lacks critical platform support
- WebView inconsistencies cause significant UX problems
- A mobile client is needed (Flutter or React Native may be better for cross-platform including mobile)
