import { afterEach, describe, expect, it, vi } from "vitest";
import { RealtimeClient } from "../api/realtimeClient";

class MockWebSocket {
  static OPEN = 1;
  readyState = MockWebSocket.OPEN;
  binaryType = "arraybuffer";
  onopen: (() => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  sent: (string | ArrayBuffer)[] = [];

  constructor(_url: string) {
    queueMicrotask(() => this.onopen?.());
  }

  send(data: string | ArrayBuffer) {
    this.sent.push(data);
  }

  close() {
    this.readyState = 3;
    this.onclose?.();
  }

  emitJson(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

describe("RealtimeClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("transitions to ready on session.started", async () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    const states: string[] = [];
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: (s) => states.push(s),
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: () => undefined,
    });
    const connectPromise = client.connect();
    const ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson({
      type: "session.started",
      id: "1",
      session_id: "sess-1",
      timestamp: "2026-01-01T00:00:00.000Z",
      payload: { reconnect_window_s: 30 },
    });
    await connectPromise;
    expect(states).toContain("ready");
    expect(client.getSessionId()).toBe("sess-1");
    client.disconnect();
  });
});
