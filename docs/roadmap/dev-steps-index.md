# Dev-Steps Index

Registry of all dev-steps. **One dev-step = one PR.** Do not start the next step until the current PR is merged.

**Workflow:** [Dev-Step Template](dev-step-template.md) · Cursor rule: `.cursor/rules/dev-workflow.mdc`

## Status Legend

| Status | Meaning |
|--------|---------|
| `planned` | Defined in markdown; not started |
| `in-progress` | Implementation underway; PR open or pending |
| `done` | PR merged; completion recorded |

## Active Step

| ID | Title | Status | Doc |
|----|-------|--------|-----|
| **P2-003** | Audio frame `seq_num` ordering | in-progress | [dev-step-p2-003-audio-seq-ordering.md](dev-step-p2-003-audio-seq-ordering.md) |

**Also in progress (merge before starting follow-on work):** [P2-002](dev-step-p2-002-session-ended.md) — `session.ended` lifecycle (implementation complete; PR pending).

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
| P2-002 | `session.ended` lifecycle | in-progress | — | [dev-step-p2-002-session-ended.md](dev-step-p2-002-session-ended.md) |
| P2-003 | Audio frame `seq_num` ordering | in-progress | — | [dev-step-p2-003-audio-seq-ordering.md](dev-step-p2-003-audio-seq-ordering.md) |
| P2-004 | `buffer.overflow` and `BUFFER_OVERFLOW` | planned | — | [dev-step-p2-004-buffer-overflow.md](dev-step-p2-004-buffer-overflow.md) |
| P2-005 | Session registry and reconnect window | planned | — | [dev-step-p2-005-session-registry-reconnect-window.md](dev-step-p2-005-session-registry-reconnect-window.md) |
| P2-006 | `session.resume` reconnection | planned | — | [dev-step-p2-006-session-resume.md](dev-step-p2-006-session-resume.md) |
| P2-007 | API error handling alignment | planned | — | [dev-step-p2-007-api-error-handling.md](dev-step-p2-007-api-error-handling.md) |
| P2-008 | Prometheus `/metrics` | planned | — | [dev-step-p2-008-prometheus-metrics.md](dev-step-p2-008-prometheus-metrics.md) |
| P2-009 | Structured JSON logging | planned | — | [dev-step-p2-009-structured-json-logging.md](dev-step-p2-009-structured-json-logging.md) |

**Phase 2 exit:** Reconnect within window; `/metrics` live; errors match API spec; tests pass. See [phases.md](phases.md).

**Suggested order:** P2-001 → P2-002 → P2-003 → P2-004 → P2-005 → P2-006 → P2-007 → P2-008 → P2-009 (P2-007 may be partially folded into earlier steps; finish alignment in P2-007).

---

## Phase 3+

Dev-steps for Phase 3 (desktop) and beyond will be added when Phase 2 is complete. See [phases.md](phases.md).
