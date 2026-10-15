# Voragon Desktop

Tauri 2 + React + TypeScript client for the Voragon realtime backend.

## Prerequisites

- [Tauri prerequisites](https://tauri.app/start/prerequisites/) (Rust, platform tooling)
- Node.js and pnpm

## Development

```bash
# Terminal 1 — backend (choose one)
cd ../docker && docker compose up --build   # recommended; see docker/README.md
# Or Kind: kubectl port-forward -n voragon svc/realtime-service 8000:8000 — see ../k8s/README.md
# Or: cd ../backend && source .venv/bin/activate && python -m app.main

# Terminal 2 — desktop
cd desktop
pnpm install
pnpm tauri dev
```

Connect in the app, then **Start transcription**. Global shortcut: **⌘⇧T** (macOS) / **Ctrl+Shift+T** (Windows).

Default backend URL: `ws://localhost:8000/v1/realtime`

## Manual verification

- Phase 3 (desktop): [dev-step-phase3-exit.md](../docs/roadmap/dev-step-phase3-exit.md)
- Phase 4 (Docker backend + desktop): [dev-step-phase4-exit.md](../docs/roadmap/dev-step-phase4-exit.md)
- Phase 5 (Kind backend + desktop): [dev-step-phase5-exit.md](../docs/roadmap/dev-step-phase5-exit.md)

## Tests

```bash
pnpm test
cd src-tauri && cargo test
```
