import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RealtimeClient } from "../api/realtimeClient";

class MockWebSocket {
  static OPEN = 1;
  static CONNECTING = 0;
  readyState = MockWebSocket.CONNECTING;
  binaryType = "arraybuffer";
  onopen: (() => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  sent: (string | ArrayBuffer)[] = [];
  failOnOpen = false;

  constructor(_url: string) {
    queueMicrotask(() => {
      if (this.failOnOpen) {
        this.onerror?.();
        this.readyState = 3;
        this.onclose?.();
        return;
      }
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.();
    });
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

function sessionStarted(sessionId: string) {
  return {
    type: "session.started",
    id: "1",
    session_id: sessionId,
    timestamp: "2026-01-01T00:00:00.000Z",
    payload: { reconnect_window_s: 30 },
  };
}

function parseSentControl(ws: MockWebSocket, index: number) {
  const raw = ws.sent[index];
  expect(typeof raw).toBe("string");
  return JSON.parse(raw as string) as { type: string; session_id: string };
}

async function flushAsync(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
  await vi.runOnlyPendingTimersAsync();
}

describe("RealtimeClient", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
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
    ws.emitJson(sessionStarted("sess-1"));
    await connectPromise;
    expect(states).toContain("ready");
    expect(client.getSessionId()).toBe("sess-1");
    client.disconnect();
  });

  it("sends session.resume after interim session.started", async () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: () => undefined,
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: () => undefined,
    });
    const connectPromise = client.connect();
    let ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("original-session"));
    await connectPromise;
    expect(client.getSessionId()).toBe("original-session");

    ws.close();
    await flushAsync();

    ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("interim-session"));
    expect(parseSentControl(ws, 0).type).toBe("session.resume");
    expect(parseSentControl(ws, 0).session_id).toBe("original-session");

    ws.emitJson(sessionStarted("original-session"));
    expect(client.getSessionId()).toBe("original-session");
    client.disconnect();
  });

  it("re-sends audio.start after reconnect while streaming", async () => {
    const allSent: string[] = [];
    class TrackingWebSocket extends MockWebSocket {
      send(data: string | ArrayBuffer) {
        if (typeof data === "string") {
          allSent.push(data);
        }
        super.send(data);
      }
    }
    vi.stubGlobal("WebSocket", TrackingWebSocket as unknown as typeof WebSocket);
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: () => undefined,
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: () => undefined,
    });
    const connectPromise = client.connect();
    let ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("stream-session"));
    await connectPromise;
    await client.startAudio();

    ws.close();
    await flushAsync();

    ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("interim"));
    ws.emitJson(sessionStarted("stream-session"));
    await flushAsync();

    const audioStarts = allSent
      .map((s) => JSON.parse(s).type)
      .filter((t: string) => t === "audio.start");
    expect(audioStarts.length).toBe(2);
    expect(client.isStreaming()).toBe(true);
    client.disconnect();
  });

  it("does not ping before session.started", async () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: () => undefined,
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: () => undefined,
    });
    const connectPromise = client.connect();
    const ws = (client as unknown as { ws: MockWebSocket }).ws;
    await connectPromise;
    await vi.advanceTimersByTimeAsync(20_000);
    const pingsBefore = ws.sent.filter(
      (s) => typeof s === "string" && JSON.parse(s as string).type === "ping",
    );
    expect(pingsBefore.length).toBe(0);

    ws.emitJson(sessionStarted("sess-ping"));
    await vi.advanceTimersByTimeAsync(15_000);
    const pingsAfter = ws.sent.filter(
      (s) => typeof s === "string" && JSON.parse(s as string).type === "ping",
    );
    expect(pingsAfter.length).toBe(1);
    client.disconnect();
  });

  it("does not session.resume after audio.stop closes the socket", async () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    const notices: string[] = [];
    const states: string[] = [];
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: (s) => states.push(s),
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: (n) => notices.push(n),
    });
    const connectPromise = client.connect();
    const ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("stop-session"));
    await connectPromise;
    await client.startAudio();
    await client.stopAudio();
    expect(parseSentControl(ws, 1).type).toBe("audio.stop");

    ws.emitJson({
      type: "session.ended",
      id: "2",
      session_id: "stop-session",
      timestamp: "2026-01-01T00:00:00.000Z",
      payload: { reason: "client_stop" },
    });
    ws.close();
    await flushAsync();

    expect(notices.some((n) => n.includes("SESSION_NOT_FOUND"))).toBe(false);
    expect(states).toContain("disconnected");
    expect(client.getSessionId()).toBeNull();
    client.disconnect();
  });

  it("stays reconnecting on transient connect failure until window expires", async () => {
    let connectCount = 0;
    class FlakyWebSocket extends MockWebSocket {
      constructor(url: string) {
        super(url);
        connectCount += 1;
        this.failOnOpen = connectCount === 2;
      }
    }
    vi.stubGlobal("WebSocket", FlakyWebSocket as unknown as typeof WebSocket);

    const states: string[] = [];
    const client = new RealtimeClient("ws://test", "en", {
      onStateChange: (s) => states.push(s),
      onMessage: () => undefined,
      onSessionId: () => undefined,
      onNotice: () => undefined,
    });
    const connectPromise = client.connect();
    let ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("flaky-session"));
    await connectPromise;

    ws.close();
    await vi.advanceTimersByTimeAsync(1000);
    await flushAsync();
    ws = (client as unknown as { ws: MockWebSocket }).ws;
    ws.emitJson(sessionStarted("interim"));
    ws.emitJson(sessionStarted("flaky-session"));
    await flushAsync();

    expect(states.filter((s) => s === "error").length).toBe(0);
    expect(states).toContain("reconnecting");
    expect(client.getSessionId()).toBe("flaky-session");
    client.disconnect();
  });
});
