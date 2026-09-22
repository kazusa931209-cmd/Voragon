# Voragon

Local-first, realtime AI assistant platform.

**Status:** Phase 1 ASR prototype in progress.

## Documentation

Full technical documentation is in [`docs/`](docs/README.md):

- [Architecture Overview](docs/architecture/overview.md)
- [Development Phases](docs/roadmap/phases.md)
- [Dev-Steps Index](docs/roadmap/dev-steps-index.md)
- [Realtime WebSocket API](docs/api/realtime-websocket.md)

## Quick Start

Active dev-step: **[P1-007 Minimal test client](docs/roadmap/dev-step-p1-007-minimal-test-client.md)**.

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && python -m app.main

# Test client (another terminal)
cd tools/realtime-cli && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && python -m realtime_cli --duration 15
```

Speak into the microphone; partial and final transcripts print to stdout.

File replay:

```bash
python -m realtime_cli --file tools/realtime-cli/sample-mono-16khz.wav --tail 90
```
