# ADR-011: Privacy / Display-Capture Architecture

## Status

Accepted

## Context

Voragon may include a feature allowing users to prevent the application window from appearing in ordinary screen capture, screen sharing, and screen recording sessions. This is a user-controlled privacy feature, not a security or monitoring evasion mechanism.

## Problem

How should display-capture privacy be implemented, and what are the platform constraints?

## Decision

Implement display-capture privacy as an **opt-in, user-controlled feature** in the Rust native layer, using OS-supported APIs. The feature is disabled by default and must be explicitly enabled by the user in settings.

## Platform APIs

### macOS

| API | Availability | Behavior |
|-----|-------------|----------|
| `NSWindow.sharingType = .none` | macOS 15+ | Window excluded from ScreenCaptureKit and legacy capture |
| `CGWindowListCreateImage` exclusion | macOS 10.15+ (deprecated approach) | Less reliable; prefer ScreenCaptureKit API |

Implementation: Set `sharingType` on the Tauri window's NSWindow when the user enables the privacy feature.

### Windows

| API | Availability | Behavior |
|-----|-------------|----------|
| `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` | Windows 10 version 2004+ | Window content replaced with black rectangle in capture |
| `WDA_MONITOR` | Windows 10 version 2004+ | Entire monitor excluded (too aggressive; not used) |

Implementation: Call `SetWindowDisplayAffinity` on the Tauri window handle when the user enables the privacy feature.

### Platform Differences

| Aspect | macOS | Windows |
|--------|-------|---------|
| Default behavior | Window visible in capture | Window visible in capture |
| Exclusion method | Window invisible in capture | Black rectangle in capture |
| User control | Settings toggle | Settings toggle |
| Reversible | Yes, toggle off | Yes, toggle off |
| OS version requirement | macOS 15+ for full support | Windows 10 2004+ |
| Older OS behavior | Feature unavailable (graceful degradation) | Feature unavailable (graceful degradation) |

## What This Feature Is

- A user-controlled privacy setting
- Implemented using documented, OS-supported APIs
- Transparent to the user (clearly labeled in settings)
- Reversible at any time
- Disabled by default

## What This Feature Is NOT

- A mechanism to evade EDR, antivirus, or enterprise monitoring
- A way to hide the application from process inspection or system administration tools
- A method to bypass screen recording policies enforced by enterprise software
- A security feature (it does not encrypt or protect data)

## Alternatives Considered

### No Display-Capture Privacy

| Pros | Cons |
|------|------|
| Simpler implementation | Users may be uncomfortable with window visibility during screen share |
| No platform API dependencies | Competitive disadvantage vs apps offering this feature |

### Always-On Exclusion

| Pros | Cons |
|------|------|
| Maximum privacy | User cannot share the Voragon window intentionally |
| | May confuse users who want to demo the app |
| | Aggressive default; should be opt-in |

### User-Controlled Opt-In (Selected)

| Pros | Cons |
|------|------|
| User agency | Requires settings UI and platform-specific implementation |
| Clear intent | Platform API differences require separate implementations |
| Reversible | Older OS versions cannot support the feature |

## Trade-offs

- **Platform fragmentation**: macOS and Windows use different APIs with different visual behavior (invisible vs black rectangle).
- **OS version requirements**: Feature is unavailable on older OS versions. Must degrade gracefully.
- **Not foolproof**: Enterprise screen capture tools may use methods that bypass these APIs (e.g., kernel-level capture). This is acceptable; the feature targets ordinary screen sharing/recording.

## Consequences

- Privacy feature implemented in Rust native layer (`src-tauri/src/privacy/`)
- Settings toggle in React UI
- Feature disabled by default
- Platform-specific implementation with `#[cfg(target_os)]` conditional compilation
- Documentation clearly states what the feature does and does not do
- No attempt to hide from process lists, task managers, or security software

## Future Reconsideration

Reconsider if:
- OS APIs change or are deprecated
- User feedback indicates the feature is not valued
- Enterprise customers require different privacy controls (e.g., admin-enforced policies)
