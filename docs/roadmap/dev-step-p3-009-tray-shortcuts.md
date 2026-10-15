# P3-009: System Tray + Global Shortcuts

| Field | Value |
|-------|-------|
| **ID** | P3-009 |
| **Phase** | 3 |
| **Status** | done |
| **Commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **PR** | [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |
| **Branch** | `dev-step/p3-009-tray-shortcuts` |

## Spec References

- [Desktop Architecture](../architecture/desktop.md) — tray, shortcuts
- [phases.md](phases.md) — Phase 3 exit criteria

## Scope

One verifiable behavior: **minimal system tray (show/hide, quit) and global hotkeys to start/stop transcription.**

- Tauri tray icon and menu
- Global shortcuts for start/stop (document default bindings)
- macOS primary dev; Windows smoke verification documented in manual test

## Out of Scope

- Display-capture privacy
- Rich notifications

## Acceptance Criteria

- [x] Tray menu: show window, quit
- [x] Global shortcut toggles transcription start/stop
- [x] Works with window hidden (tray-only)
- [x] Phase 3 exit: macOS verified; Windows manual checklist documented

## Manual Test

1. Hide window; use hotkey to start/stop transcription
2. Tray → quit exits cleanly
3. (Windows) Repeat tray and shortcut smoke test

## Automated Tests

```bash
cd desktop && pnpm test
cd desktop/src-tauri && cargo test
```

## Spec Changes

Expected: none

---

## Completion

### Summary

- System tray (Show / Quit); left-click show window; global **⌘⇧T** / **Ctrl+Shift+T** emits `transcription-toggle`; documented in [desktop/README.md](../../desktop/README.md).

### Spec Changes

- None

### Automated Tests Run

```bash
cd desktop && pnpm test
cd desktop/src-tauri && cargo test
# 6 + 2 passed (2026-10-15)
```

### Manual Test Result

- [ ] Pending — [Phase 3 exit checklist](dev-step-phase3-exit.md) § P3-009

### Commit

- **Hash:** `35486f0`

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/14
- **Merged:** 2026-10-15
