# P3-006: Settings and Connection Chrome

| Field | Value |
|-------|-------|
| **ID** | P3-006 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p3-006-settings` |

## Spec References

- [Desktop Architecture](../architecture/desktop.md) — settings, connection status
- [Local Development](../operations/local-development.md) — default WebSocket URL

## Scope

One verifiable behavior: **backend URL and optional input device persist across restarts; connection status is visible in the UI.**

- Persist backend URL (default `ws://localhost:8000/v1/realtime`)
- Connection status indicator wired to WebSocket state
- List input devices (Rust) and allow selection stored in settings

## Out of Scope

- Auth / wss credentials (keychain)
- Model / capability selection

## Acceptance Criteria

- [x] Change URL, restart app, reconnect uses saved URL
- [x] Status shows disconnected / connecting / connected / error
- [x] Device list populated; selected device used for capture

## Manual Test

1. Change backend URL in settings; reconnect
2. Select alternate input device if available

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation._
