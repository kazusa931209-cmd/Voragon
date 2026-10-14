# Dev-Steps Index

Registry of all dev-steps. **One dev-step = one commit** (a PR may include multiple dev-step commits). Do not start the next step until the current dev-step is **done**.

**Workflow:** [Dev-Step Template](dev-step-template.md) · Cursor rule: `.cursor/rules/dev-workflow.mdc`

## Status Legend

| Status | Meaning |
|--------|---------|
| `planned` | Defined in markdown; not started |
| `in-progress` | Implementation underway; PR open or pending |
| `done` | Dev-step commit landed; completion recorded (optional PR link) |

## Active Step

Phase 3 implementation **landed in workspace** (P3-001–P3-009); split into per-step commits when landing on `dev`. Next: Phase 4 dev-step definitions — see [phases.md](phases.md).

---

## Phase 1: Local Single-User ASR Prototype

| ID | Title | Status | PR | Doc |
|----|-------|--------|-----|-----|
| P1-001 | Backend scaffold and health endpoint | done | [#2](https://github.com/kazusa931209-cmd/Voragon/pull/2) | [dev-step-p1-001-backend-scaffold.md](dev-step-p1-001-backend-scaffold.md) |
| P1-002 | WebSocket connect and `session.started` | done | [#3](https://github.com/kazusa931209-cmd/Voragon/pull/3) | [dev-step-p1-002-websocket-session-started.md](dev-step-p1-002-websocket-session-started.md) |
| P1-003 | `audio.start` and binary `audio.chunk` reception | done | [#4](https://github.com/kazusa931209-cmd/Voragon/pull/4) | [dev-step-p1-003-audio-start-chunk.md](dev-step-p1-003-audio-start-chunk.md) |
| P1-004 | VAD integration (Silero) | done | [#5](https://github.com/kazusa931209-cmd/Voragon/pull/5) | [dev-step-p1-004-vad-integration.md](dev-step-p1-004-vad-integration.md) |
| P1-005 | ASR adapter and model load | done | [#6](https://github.com/kazusa931209-cmd/Voragon/pull/6) | [dev-step-p1-005-asr-adapter.md](dev-step-p1-005-asr-adapter.md) |
| P1-006 | `transcript.partial` and `transcript.final` | done | [#7](https://github.com/kazusa931209-cmd/Voragon/pull/7) | [dev-step-p1-006-transcript-partial-final.md](dev-step-p1-006-transcript-partial-final.md) |
| P1-007 | Minimal test client (mic → transcript) | done | [#8](https://github.com/kazusa931209-cmd/Voragon/pull/8) | [dev-step-p1-007-minimal-test-client.md](dev-step-p1-007-minimal-test-client.md) |

**Phase 1 exit:** Speak into microphone via test client; receive partial and final English transcripts.

---

## Phase 2: Realtime Production-Like Backend

| ID | Title | Status | PR | Doc |
|----|-------|--------|-----|-----|
| P2-001 | `ping` / `pong` heartbeat | done | [#9](https://github.com/kazusa931209-cmd/Voragon/pull/9) | [dev-step-p2-001-ping-pong-heartbeat.md](dev-step-p2-001-ping-pong-heartbeat.md) |
| P2-002 | `session.ended` lifecycle | done | [#10](https://github.com/kazusa931209-cmd/Voragon/pull/10) | [dev-step-p2-002-session-ended.md](dev-step-p2-002-session-ended.md) |
| P2-003 | Audio frame `seq_num` ordering | done | [#11](https://github.com/kazusa931209-cmd/Voragon/pull/11) | [dev-step-p2-003-audio-seq-ordering.md](dev-step-p2-003-audio-seq-ordering.md) |
| P2-004 | `buffer.overflow` and `BUFFER_OVERFLOW` | done | [#12](https://github.com/kazusa931209-cmd/Voragon/pull/12) | [dev-step-p2-004-buffer-overflow.md](dev-step-p2-004-buffer-overflow.md) |
| P2-005 | Session registry and reconnect window | done | [`dev` @ `6d92099`](https://github.com/kazusa931209-cmd/Voragon/commit/6d92099) | [dev-step-p2-005-session-registry-reconnect-window.md](dev-step-p2-005-session-registry-reconnect-window.md) |
| P2-006 | `session.resume` reconnection | done | [`dev` @ `bc0fcb1`](https://github.com/kazusa931209-cmd/Voragon/commit/bc0fcb1) | [dev-step-p2-006-session-resume.md](dev-step-p2-006-session-resume.md) |
| P2-007 | API error handling alignment | done | [`feat/steps-P2-007-008-009` @ `a976b18`](https://github.com/kazusa931209-cmd/Voragon/commit/a976b18) | [dev-step-p2-007-api-error-handling.md](dev-step-p2-007-api-error-handling.md) |
| P2-008 | Prometheus `/metrics` | done | [`feat/steps-P2-007-008-009` @ `94d0880`](https://github.com/kazusa931209-cmd/Voragon/commit/94d0880) | [dev-step-p2-008-prometheus-metrics.md](dev-step-p2-008-prometheus-metrics.md) |
| P2-009 | Structured JSON logging | done | [`feat/steps-P2-007-008-009` @ `29c905f`](https://github.com/kazusa931209-cmd/Voragon/commit/29c905f) | [dev-step-p2-009-structured-json-logging.md](dev-step-p2-009-structured-json-logging.md) |

**Phase 2 exit:** Reconnect within window; `/metrics` live; errors match API spec; tests pass. See [phases.md](phases.md).

---

## Phase 3: Tauri Desktop Application

| ID | Title | Status | PR | Doc |
|----|-------|--------|-----|-----|
| P3-001 | Tauri 2 + React + TypeScript scaffold | done | — | [dev-step-p3-001-tauri-scaffold.md](dev-step-p3-001-tauri-scaffold.md) |
| P3-002 | WebSocket client (connect + control messages) | done | — | [dev-step-p3-002-websocket-client.md](dev-step-p3-002-websocket-client.md) |
| P3-003 | Transcript UI and client state | done | — | [dev-step-p3-003-transcript-ui.md](dev-step-p3-003-transcript-ui.md) |
| P3-004 | Rust audio capture + IPC | done | — | [dev-step-p3-004-rust-audio-capture.md](dev-step-p3-004-rust-audio-capture.md) |
| P3-005 | End-to-end mic → backend → transcript UI | done | — | [dev-step-p3-005-e2e-streaming.md](dev-step-p3-005-e2e-streaming.md) |
| P3-006 | Settings and connection chrome | done | — | [dev-step-p3-006-settings.md](dev-step-p3-006-settings.md) |
| P3-007 | Client heartbeat and session lifecycle | done | — | [dev-step-p3-007-heartbeat.md](dev-step-p3-007-heartbeat.md) |
| P3-008 | `session.resume` reconnection | done | — | [dev-step-p3-008-session-resume.md](dev-step-p3-008-session-resume.md) |
| P3-009 | System tray + global shortcuts | done | — | [dev-step-p3-009-tray-shortcuts.md](dev-step-p3-009-tray-shortcuts.md) |

**Phase 3 exit:** Desktop captures audio and displays realtime transcripts; reconnection per API; tray and shortcuts. Manual macOS/Windows verification pending per-step commits. See [phases.md](phases.md).

**Suggested order:** P3-001 → P3-002 → P3-003 → P3-004 → P3-005 → P3-006 → P3-007 → P3-008 → P3-009.

---

## Phase 4+

Dev-steps for Phase 4 (Docker Compose) and beyond — see [phases.md](phases.md).
