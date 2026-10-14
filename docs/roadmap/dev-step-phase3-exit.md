# Phase 3 Exit Verification

| Field | Value |
|-------|-------|
| **Phase** | 3 |
| **Status** | in-progress (manual verification) |
| **Implementation commit** | [`35486f0`](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0) |
| **Merge** | [`305f943`](https://github.com/kazusa931209-cmd/Voragon/commit/305f943) — PR [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |

## Exit Criteria ([phases.md](phases.md))

- [ ] Desktop captures microphone audio and displays realtime transcripts
- [ ] Works on **macOS** (primary dev platform)
- [ ] **Windows** smoke test documented (tray, shortcuts, capture)
- [ ] Reconnection works per API spec (`session.resume` within window)
- [ ] System tray and global shortcuts functional

## Prerequisites

```bash
# Terminal 1 — backend (ASR loaded; first start may download models)
cd backend && source .venv/bin/activate && python -m app.main

# Terminal 2 — desktop
cd desktop && pnpm install && pnpm tauri dev
```

Default WebSocket URL: `ws://localhost:8000/v1/realtime`

## Automated Tests (agent / CI)

Run before signing off manual checks:

```bash
cd desktop && pnpm test
cd desktop/src-tauri && cargo test
```

| Run | Date | Result |
|-----|------|--------|
| Vitest + `cargo test` | 2026-10-15 | 6 passed (Vitest); 2 passed (Rust) |

## Per Dev-Step Manual Checklist

### P3-001 — Scaffold

- [ ] `pnpm tauri dev` opens Voragon window on macOS

### P3-002 — WebSocket client

- [ ] Connect → status **ready**; session id visible

### P3-003 — Transcript UI

- [ ] Partials update one live line; finals append as stable segments (use live audio in P3-005)

### P3-004 — Rust audio capture

- [ ] Start capture; frame counter / debug indicates ~50 frames/s while speaking

### P3-005 — End-to-end streaming

- [ ] Connect → **Start transcription** → speak → partials and finals appear → **Stop**

### P3-006 — Settings

- [ ] Change backend URL; restart app; reconnect uses saved URL
- [ ] Connection status reflects disconnected / connecting / ready / error
- [ ] Input device list populated; alternate device works if available

### P3-007 — Heartbeat

- [ ] Connect without starting transcription; wait **60 s** — connection stays up
- [ ] Start/stop transcription; `audio.stop` sent; finals behave as expected

### P3-008 — Session resume

- [ ] Start transcription; stop backend briefly; restart within **30 s**; client resumes and transcription continues

### P3-009 — Tray and shortcuts

- [ ] Hide window; **⌘⇧T** (macOS) or **Ctrl+Shift+T** (Windows) toggles start/stop
- [ ] Tray → **Show Voragon** restores window; **Quit** exits cleanly
- [ ] (Windows) Repeat tray and shortcut smoke test

## Platform Notes

| Platform | Verified by | Date | Notes |
|----------|-------------|------|-------|
| macOS | | | |
| Windows | | | Optional smoke; document build if not run |

## Sign-Off

When all boxes above are checked:

1. Set **Status** in this file to `done` and record sign-off date.
2. Update [dev-steps-index.md](dev-steps-index.md) — Phase 3 exit complete; **Active Step** → first Phase 4 dev-step (`P4-001`).
3. Update [phases.md](phases.md) Phase 3 **Status** to complete with sign-off date.
4. In each [P3-001](dev-step-p3-001-tauri-scaffold.md)–[P3-009](dev-step-p3-009-tray-shortcuts.md) doc, mark **Manual Test Result** pass with date in **Completion**.
