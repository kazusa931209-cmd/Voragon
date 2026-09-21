# P1-005: ASR Adapter and Model Load


| Field      | Value                         |
| ---------- | ----------------------------- |
| **ID**     | P1-005                        |
| **Phase**  | 1                             |
| **Status** | done                          |
| **PR**     | [#6](https://github.com/kazusa931209-cmd/Voragon/pull/6) |
| **Branch** | `dev-step/p1-005-asr-adapter` |


## Spec References

- [Backend Architecture](../architecture/backend.md) — `asr/` module layout, `ASR_BACKEND`, `ASR_MODEL` config
- [Model Serving](../architecture/model-serving.md) — `ASREngine` interface, model loading/warmup, faster-whisper vs whisper.cpp
- [Transcription API](../api/transcription.md) — `TranscriptResult` fields (`text`, `language`, `confidence`)
- [Error Handling](../api/error-handling.md) — `ASR_INFERENCE_FAILED`, `ASR_MODEL_UNAVAILABLE`
- [Local Development](../operations/local-development.md) — model download, env vars

## Scope

One verifiable behavior: **the backend loads an ASR model at startup and can transcribe segment PCM via the `ASREngine` abstraction (`transcribe_partial` / `transcribe_final`).**

- Add `app/asr/base.py` — `ASREngine` protocol, `TranscriptResult`, `HealthStatus`, factory
- Add `app/asr/faster_whisper.py` — faster-whisper adapter (default backend)
- Add `app/asr/mock_asr.py` — deterministic mock for fast tests (`ASR_BACKEND=mock`)
- Load and warm up the ASR model at application startup (FastAPI lifespan)
- Expose `ASR_BACKEND` and `ASR_MODEL` via settings (defaults: `faster_whisper`, `large-v3-turbo`)
- Run inference in a thread/process executor to avoid blocking the event loop
- `health()` reports whether the model is loaded and ready
- Optional: include ASR readiness in `GET /health` response

## Out of Scope

- `transcript.partial` / `transcript.final` WebSocket emission (P1-006)
- Wiring ASR to VAD segment close in the WebSocket handler (P1-006)
- `whisper_cpp` adapter (defer unless trivial; document as follow-up)
- AI Gateway / production `gateway` adapter (Phase 7+)
- `audio.stop`, session lifecycle changes
- Prometheus metrics
- Desktop or test-client changes (P1-007)

## Acceptance Criteria

- [x] `app/asr/base.py` defines swappable `ASREngine` with `transcribe_partial`, `transcribe_final`, `health`, `warmup`
- [x] `faster_whisper` adapter loads Whisper Large-v3 Turbo (or configured model) at startup
- [x] `transcribe_partial` and `transcribe_final` accept 16 kHz mono s16le PCM and return `TranscriptResult`
- [x] Mock adapter available via `ASR_BACKEND=mock` for unit tests
- [x] Startup warmup completes before server accepts traffic (or health reports not-ready until loaded)
- [x] `GET /health` reflects ASR readiness (or dedicated check documented in completion)
- [x] Automated tests cover mock adapter and interface; faster-whisper integration test may be marked/skipped in CI
- [x] Existing P1-001–P1-004 tests still pass

## Manual Test

1. `cd backend && source .venv/bin/activate && pip install -e ".[dev]"`
2. Set `ASR_BACKEND=faster_whisper` (first run downloads model weights ~1.5 GB)
3. `python -m app.main` — verify startup logs show model load/warmup
4. `curl http://localhost:8000/health` — verify ASR readiness in response
5. Run a small Python script that calls the adapter directly on a short PCM fixture:
  ```bash
   python -c "
   import asyncio
   from app.asr.base import create_asr_engine
   from app.config import get_settings

   async def main():
       engine = create_asr_engine(get_settings())
       await engine.warmup()
       # Use a short s16le PCM fixture or generated silence; expect str result object
       result = await engine.transcribe_final(b'\\x00' * 32000, 'seg-test', 'en')
       print(result)
   asyncio.run(main())
   "
  ```
6. Confirm `TranscriptResult` returns without crashing (empty/silent audio may yield empty text)

## Automated Tests

```bash
cd backend && pytest -v
```

Expected:

- Unit tests: mock adapter `transcribe_partial` / `transcribe_final`, factory selection
- Optional integration test: faster-whisper on fixture (skip if model unavailable)
- Existing health, WebSocket, and VAD tests pass

## Spec Changes

Expected: none

If health endpoint shape changes, update `backend.md` and `local-development.md` in the same PR.

---

## Completion

### Summary

- Added `app/asr/base.py` — `ASREngine` protocol, `TranscriptResult`, `HealthStatus`, factory, and error types
- Added `app/asr/faster_whisper.py` — faster-whisper adapter with thread-pool inference and startup warmup
- Added `app/asr/mock_asr.py` — deterministic mock adapter for fast tests (`ASR_BACKEND=mock`)
- Wired ASR load/warmup into FastAPI lifespan; `/health` includes `asr.ready`, `asr.backend`, and `asr.model`
- Added `ASR_BACKEND` and `ASR_MODEL` settings; dependency: `faster-whisper`
- Added `tests/test_asr.py`; updated `conftest.py` to auto-mock ASR in tests

### Spec Changes

- `docs/architecture/backend.md` — noted P1-005 implemented ASR modules
- `docs/operations/local-development.md` — documented `/health` ASR readiness shape and `ASR_BACKEND=mock`

### Automated Tests Run

```bash
cd backend && pytest -v
# 33 passed, 1 skipped in 1.21s
```

### Manual Test Result

- [x] Pass — 2026-09-22, ASR warmup via lifespan; `/health` reports `asr.ready`; mock adapter transcribe script OK

### PR

- **URL:** https://github.com/kazusa931209-cmd/Voragon/pull/6
- **Merged:** 2026-09-21

