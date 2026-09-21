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
| **P1-004** | VAD integration (Silero) | in-progress | [dev-step-p1-004-vad-integration.md](dev-step-p1-004-vad-integration.md) |

---

## Phase 1: Local Single-User ASR Prototype

| ID | Title | Status | PR | Doc |
|----|-------|--------|-----|-----|
| P1-001 | Backend scaffold and health endpoint | done | [#2](https://github.com/kazusa931209-cmd/Voragon/pull/2) | [dev-step-p1-001-backend-scaffold.md](dev-step-p1-001-backend-scaffold.md) |
| P1-002 | WebSocket connect and `session.started` | done | [#3](https://github.com/kazusa931209-cmd/Voragon/pull/3) | [dev-step-p1-002-websocket-session-started.md](dev-step-p1-002-websocket-session-started.md) |
| P1-003 | `audio.start` and binary `audio.chunk` reception | done | [#4](https://github.com/kazusa931209-cmd/Voragon/pull/4) | [dev-step-p1-003-audio-start-chunk.md](dev-step-p1-003-audio-start-chunk.md) |
| P1-004 | VAD integration (Silero) | in-progress | — | [dev-step-p1-004-vad-integration.md](dev-step-p1-004-vad-integration.md) |
| P1-005 | ASR adapter and model load | planned | — | _create doc before start_ |
| P1-006 | `transcript.partial` and `transcript.final` | planned | — | _create doc before start_ |
| P1-007 | Minimal test client (mic → transcript) | planned | — | _create doc before start_ |

**Phase 1 exit:** Speak into microphone via test client; receive partial and final English transcripts.

---

## Phase 2+

Dev-steps will be added to this index when Phase 1 is complete. See [phases.md](phases.md).
