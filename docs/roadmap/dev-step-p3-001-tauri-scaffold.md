# P3-001: Tauri 2 + React + TypeScript Scaffold

| Field | Value |
|-------|-------|
| **ID** | P3-001 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
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

### Summary

- Added `desktop/` Tauri 2 app (Vite, React, TypeScript), `src-tauri/`, Vitest smoke test (`App.test.tsx`), minimal shell UI.

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
# 6 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pending — [Phase 3 exit checklist](dev-step-phase3-exit.md) § P3-001

### Commit

- **Hash:** `35486f0`
- **Message:** `[P3-001–P3-009] Tauri desktop client and Phase 3 roadmap`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15 (merge commit `305f943`)
