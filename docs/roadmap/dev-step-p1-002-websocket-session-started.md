# P1-002: WebSocket Connect and `session.started`

| Field | Value |
|-------|-------|
| **ID** | P1-002 |
| **Phase** | 1 |
| **Status** | in-progress |
| **PR** | — |
| **Branch** | `dev-step/p1-002-websocket-session-started` |

## Spec References

- [Realtime WebSocket API](../api/realtime-websocket.md) — endpoint, envelope, `session.started`, connection lifecycle
- [Error Handling](../api/error-handling.md) — `UNKNOWN_MESSAGE_TYPE` (for unsolicited client messages)
- [Backend Architecture](../architecture/backend.md) — `websocket/` module layout

## Scope

One verifiable behavior: **a client can open a WebSocket to `/v1/realtime` and immediately receive a `session.started` message.**

- Add WebSocket endpoint `GET /v1/realtime` (WebSocket upgrade)
- On connection accept:
  - Generate a `session_id` (UUID)
  - Send `session.started` as the first server message
- Implement JSON message envelope per API spec (`type`, `id`, `session_id`, `timestamp`, `payload`)
- Add `app/websocket/` modules: `handler.py`, `messages.py`, `session.py`
- `session.started` payload includes `protocol_version: 1` and `reconnect_window_s: 30`
- Keep connection open until the client disconnects
- If the client sends any message before P1-003, respond with recoverable `error` (`UNKNOWN_MESSAGE_TYPE`)

## Out of Scope

- `audio.start`, `audio.chunk`, `audio.stop`
- `session.resume`
- `ping` / `pong` heartbeat
- `session.ended` on disconnect (Phase 2 session lifecycle)
- VAD, ASR, transcripts
- Authentication / TLS
- Binary audio frame handling
- Session state retention after disconnect

## Acceptance Criteria

- [x] `WS ws://localhost:8000/v1/realtime` accepts a connection
- [x] First server message is `session.started` with valid JSON envelope
- [x] `session_id` in the message is a valid UUID
- [x] `payload.protocol_version` is `1`
- [x] `payload.reconnect_window_s` is `30`
- [x] `timestamp` is ISO 8601 UTC
- [x] Connection remains open until client closes
- [x] Unsolicited client JSON messages receive `error` with code `UNKNOWN_MESSAGE_TYPE`
- [x] Automated WebSocket tests cover connect + `session.started` shape
- [x] Existing `GET /health` tests still pass

## Manual Test

1. `cd backend && source .venv/bin/activate && python -m app.main`
2. Connect with a WebSocket client:
   ```bash
   # Option A: websocat (if installed)
   websocat ws://localhost:8000/v1/realtime

   # Option B: Python one-liner
   python -c "
   import asyncio, json, websockets
   async def main():
       async with websockets.connect('ws://localhost:8000/v1/realtime') as ws:
           msg = json.loads(await ws.recv())
           print(json.dumps(msg, indent=2))
   asyncio.run(main())
   "
   ```
3. Verify first message is `session.started` with expected fields
4. Close the connection

## Automated Tests

```bash
cd backend && pytest -v
```

Expected:
- New WebSocket test: connect to `/v1/realtime`, assert first message type and payload
- Existing health tests pass

## Spec Changes

Expected: none

---

## Completion

_Fill in after implementation, before PR._

### Summary

- Added `app/websocket/` with `handler.py`, `messages.py`, `session.py`
- WebSocket endpoint `GET /v1/realtime` sends `session.started` on connect
- JSON envelope helpers and `reconnect_window_s` config (default 30)
- Error responses for malformed JSON (`INVALID_MESSAGE`) and unknown types (`UNKNOWN_MESSAGE_TYPE`)
- Added `tests/test_websocket_session.py` (3 tests)

### Spec Changes

- `docs/architecture/backend.md` — noted P1-002 implemented websocket modules

### Automated Tests Run

```bash
cd backend && pytest -v
# 4 passed in 0.24s
```

### Manual Test Result

- [ ] Pass — _pending your verification_

### PR

- **URL:** —
- **Merged:** —
