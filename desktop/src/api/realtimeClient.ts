import { buildAudioFrame } from "./frames";
import {
  buildControlMessage,
  errorCode,
  parseEnvelope,
  type MessageEnvelope,
} from "./messages";

export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "ready"
  | "reconnecting"
  | "error";

export interface RealtimeClientCallbacks {
  onStateChange: (state: ConnectionState) => void;
  onMessage: (message: MessageEnvelope) => void;
  onSessionId: (sessionId: string) => void;
  onNotice: (text: string) => void;
}

const PING_INTERVAL_MS = 15_000;
const SESSION_RESUME_CODES = new Set(["SESSION_NOT_FOUND", "SESSION_EXPIRED"]);

export class RealtimeClient {
  private ws: WebSocket | null = null;
  private url: string;
  private language: string;
  private callbacks: RealtimeClientCallbacks;
  private sessionId: string | null = null;
  private lastSessionId: string | null = null;
  private reconnectWindowS = 30;
  private intentionalClose = false;
  private streaming = false;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private seqNum = 0;
  private resumeAttempted = false;

  constructor(url: string, language: string, callbacks: RealtimeClientCallbacks) {
    this.url = url;
    this.language = language;
    this.callbacks = callbacks;
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  isStreaming(): boolean {
    return this.streaming;
  }

  async connect(): Promise<void> {
    this.intentionalClose = false;
    this.resumeAttempted = false;
    await this.openSocket(false);
  }

  disconnect(): void {
    this.intentionalClose = true;
    this.stopPing();
    this.streaming = false;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.sessionId = null;
    this.lastSessionId = null;
    this.callbacks.onStateChange("disconnected");
  }

  async startAudio(): Promise<void> {
    if (!this.ws || !this.sessionId) {
      throw new Error("Not connected");
    }
    this.ws.send(
      buildControlMessage("audio.start", this.sessionId, { language: this.language }),
    );
    this.streaming = true;
    this.stopPing();
    this.seqNum = 0;
  }

  async stopAudio(): Promise<void> {
    if (!this.ws || !this.sessionId) {
      return;
    }
    this.streaming = false;
    this.ws.send(buildControlMessage("audio.stop", this.sessionId, {}));
    this.startPing();
  }

  sendPcmFrame(pcm: Uint8Array): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }
    this.ws.send(buildAudioFrame(pcm, this.seqNum));
    this.seqNum += 1;
  }

  private async openSocket(isReconnect: boolean): Promise<void> {
    this.resumeAttempted = false;
    this.callbacks.onStateChange(isReconnect ? "reconnecting" : "connecting");
    await new Promise<void>((resolve, reject) => {
      const ws = new WebSocket(this.url);
      ws.binaryType = "arraybuffer";
      this.ws = ws;

      ws.onopen = () => {
        resolve();
      };

      ws.onerror = () => {
        reject(new Error("WebSocket connection failed"));
      };

      ws.onclose = () => {
        this.stopPing();
        this.streaming = false;
        if (!this.intentionalClose && this.lastSessionId) {
          void this.tryReconnect();
        } else if (!this.intentionalClose) {
          this.callbacks.onStateChange("disconnected");
        }
      };

      ws.onmessage = (event) => {
        if (typeof event.data === "string") {
          this.handleJsonMessage(event.data);
        }
      };
    }).catch((err) => {
      this.callbacks.onStateChange("error");
      throw err;
    });

    this.startPing();
  }

  private handleJsonMessage(raw: string): void {
    let message: MessageEnvelope;
    try {
      message = parseEnvelope(raw);
    } catch {
      return;
    }

    this.callbacks.onMessage(message);

    switch (message.type) {
      case "session.started": {
        const reconnectWindow = message.payload.reconnect_window_s;
        if (typeof reconnectWindow === "number") {
          this.reconnectWindowS = reconnectWindow;
        }
        const newId = message.session_id;
        if (
          !this.resumeAttempted &&
          this.lastSessionId &&
          this.lastSessionId !== newId &&
          this.ws
        ) {
          this.resumeAttempted = true;
          this.ws.send(buildControlMessage("session.resume", this.lastSessionId, {}));
          return;
        }
        this.sessionId = newId;
        this.lastSessionId = newId;
        this.callbacks.onSessionId(newId);
        this.callbacks.onStateChange("ready");
        break;
      }
      case "error": {
        const code = errorCode(message);
        if (SESSION_RESUME_CODES.has(code)) {
          this.callbacks.onNotice(`Session resume failed (${code}); starting fresh.`);
          this.sessionId = message.session_id;
          this.lastSessionId = message.session_id;
          this.callbacks.onSessionId(message.session_id);
          this.callbacks.onStateChange("ready");
        }
        break;
      }
      case "session.ended": {
        this.streaming = false;
        this.sessionId = null;
        this.startPing();
        break;
      }
      case "pong":
        break;
      default:
        break;
    }
  }

  private async tryReconnect(): Promise<void> {
    const previous = this.lastSessionId;
    if (!previous) {
      this.callbacks.onStateChange("disconnected");
      return;
    }
    this.callbacks.onNotice("Reconnecting…");
    this.resumeAttempted = false;
    const deadline = Date.now() + this.reconnectWindowS * 1000;
    while (Date.now() < deadline && !this.intentionalClose) {
      try {
        await this.openSocket(true);
        return;
      } catch {
        await sleep(1000);
      }
    }
    this.callbacks.onStateChange("error");
    this.callbacks.onNotice("Reconnection failed.");
  }

  private startPing(): void {
    this.stopPing();
    if (!this.ws || this.streaming) {
      return;
    }
    this.pingTimer = setInterval(() => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN || this.streaming) {
        return;
      }
      if (!this.sessionId) {
        return;
      }
      this.ws.send(buildControlMessage("ping", this.sessionId, {}));
    }, PING_INTERVAL_MS);
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
