# P3-001: Tauri 2 + React + TypeScript Scaffold

| Field | Value |
|-------|-------|
| **ID** | P3-001 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | — |
| **PR** | — |
| **Branch** | `dev-step/p3-001-tauri-scaffold` |

## Spec References

- [Desktop Architecture](../architecture/desktop.md) — planned `desktop/` layout
- [ADR-001: Tauri + React + TypeScript](../decisions/ADR-001-tauri-react-typescript.md)
- [Local Development](../operations/local-development.md) — `pnpm tauri dev`

## Scope

One verifiable behavior: **`desktop/` exists; `pnpm install` and `pnpm tauri dev` open a minimal window on macOS.**

- Tauri 2 application with Vite, React, TypeScript
- Directory layout: `desktop/src/`, `desktop/src-tauri/`
- Vitest wired with one smoke test for a trivial component
- Minimal shell UI (title / placeholder)

## Out of Scope

- WebSocket client, audio capture, system tray, global shortcuts
- Windows build verification
- CI workflow

## Acceptance Criteria

- [x] `cd desktop && pnpm install && pnpm tauri dev` launches the app on macOS
- [x] `cd desktop && pnpm test` passes (vitest smoke test)
- [x] Structure matches [desktop.md](../architecture/desktop.md) at a high level

## Manual Test

1. `cd desktop && pnpm install && pnpm tauri dev`
2. Confirm window opens with Voragon placeholder UI

## Automated Tests

```bash
cd desktop && pnpm test
```

## Spec Changes

Expected: none (local-development paths already planned)

---

## Completion

_Fill in after implementation._
