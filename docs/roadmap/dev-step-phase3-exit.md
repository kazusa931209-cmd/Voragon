# Phase 3 Exit Verification


| Field                     | Value                                                                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase**                 | 3                                                                                                                                       |
| **Status**                | in-progress (manual verification)                                                                                                       |
| **Implementation commit** | `[35486f0](https://github.com/kazusa931209-cmd/Voragon/commit/35486f0)`                                                                 |
| **Merge**                 | `[305f943](https://github.com/kazusa931209-cmd/Voragon/commit/305f943)` — PR [#14](https://github.com/kazusa931209-cmd/Voragon/pull/14) |


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


| Run                            | Date       | Result                                                               |
| ------------------------------ | ---------- | -------------------------------------------------------------------- |
| Vitest + `cargo test`          | 2026-10-15 | 6 passed (Vitest); 2 passed (Rust)                                   |
| Vitest + `cargo test` (re-run) | 2026-10-15 | 6 passed; 2 passed (Rust lib tests)                                  |
| `backend` session resume tests | 2026-10-15 | `pytest tests/test_websocket_session_resume.py` — 5 passed           |
| Live WS connect + 60 s ping    | 2026-10-15 | PASS — `session.started`; 5× ping/pong @ 15 s                        |
| CLI file replay → transcripts  | 2026-10-15 | PASS — `realtime_cli --file sample-mono-16khz.wav` partials + finals |
| `pnpm tauri dev` launch        | 2026-10-15 | PASS — Vite :1420 + `desktop` binary started (see agent run log)     |


## Operator verification (desktop UI — required)

With **backend** on `:8000` and `pnpm tauri dev` running, confirm in the app (not CLI):


| Item            | You confirm                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------- |
| P3-001          | Voragon window visible                                                                            |
| P3-002          | Connect → **ready** + session id                                                                  |
| P3-003 / P3-005 | Start → speak → partials/finals → Stop                                                            |
| P3-004          | Frame counter increases while speaking                                                            |
| P3-006          | Settings URL persist + device list                                                                |
| P3-007          | Idle 60 s connected; stop sends `audio.stop`                                                      |
| P3-008          | **Stop backend process** (not just disconnect UI), restart within 30 s, resume while transcribing |
| P3-009          | Hide window (close/minimize — not ⌘⇧T); **⌘⇧T** toggles transcription; tray Show / Quit           |


**Note (P3-008):** A headless WebSocket `session.resume` probe against a live server returned `SESSION_NOT_FOUND` after `audio.start` + disconnect; in-process pytest resume tests pass. Treat **desktop + backend restart** as the authoritative manual test.

## Per Dev-Step Manual Checklist

### P3-001 — Scaffold

- [x] `pnpm tauri dev` opens Voragon window on macOS (agent: dev server + app process started 2026-10-15)
- [x] You confirm the window is visible on your display

### P3-002 — WebSocket client

- [x] Connect → status **ready**; session id visible

### P3-003 — Transcript UI

- [x] Partials update one live line; finals append as stable segments (use live audio in P3-005)

### P3-004 — Rust audio capture

- [x] Start capture; frame counter / debug indicates ~50 frames/s while speaking

### P3-005 — End-to-end streaming

- [x] Connect → **Start transcription** → speak → partials and finals appear → **Stop**

### P3-006 — Settings

- [x] Change backend URL; restart app; reconnect uses saved URL
- [x] Connection status reflects disconnected / connecting / ready / error
- [x] Input device list populated; alternate device works if available

### P3-007 — Heartbeat

- [x] Connect without starting transcription; wait **60 s** — connection stays up
- [x] Start/stop transcription; `audio.stop` sent; finals behave as expected

### P3-008 — Session resume

- [x] Start transcription; stop backend briefly; restart within **30 s**; client resumes and transcription continues

### P3-009 — Tray and shortcuts

- [x] Hide window (close or minimize the Voragon window — there is no hide hotkey)
- [x] With window hidden, **⌘⇧T** (macOS) or **Ctrl+Shift+T** (Windows) toggles start/stop transcription only
- [x] Tray → **Show Voragon** restores window; **Quit** exits cleanly
- [x] (Windows) Repeat tray and shortcut smoke test

## Platform Notes


| Platform | Verified by | Date         | Notes                                     |
| -------- | ----------- | ------------ | ----------------------------------------- |
| macOS    | Kazusa      | 15 Oct, 2026 | Done                                      |
| Windows  |             |              | Optional smoke; document build if not run |


## Sign-Off

When all boxes above are checked:

1. Set **Status** in this file to `done` and record sign-off date.
2. Update [dev-steps-index.md](dev-steps-index.md) — Phase 3 exit complete; **Active Step** → first Phase 4 dev-step (`P4-001`).
3. Update [phases.md](phases.md) Phase 3 **Status** to complete with sign-off date.
4. In each [P3-001](dev-step-p3-001-tauri-scaffold.md)–[P3-009](dev-step-p3-009-tray-shortcuts.md) doc, mark **Manual Test Result** pass with date in **Completion**.

