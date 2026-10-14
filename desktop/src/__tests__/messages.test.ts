import { describe, expect, it } from "vitest";
import { buildControlMessage, parseEnvelope } from "../api/messages";

describe("messages", () => {
  it("parses session.started envelope", () => {
    const raw = buildControlMessage("session.started", "abc-123", { reconnect_window_s: 30 });
    const msg = parseEnvelope(raw);
    expect(msg.type).toBe("session.started");
    expect(msg.session_id).toBe("abc-123");
  });
});
