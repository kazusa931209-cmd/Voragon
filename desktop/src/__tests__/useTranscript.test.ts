import { describe, expect, it } from "vitest";
import { applyTranscriptMessage } from "../hooks/useTranscript";
import type { MessageEnvelope } from "../api/messages";

function msg(type: string, text: string): MessageEnvelope {
  return {
    type,
    id: "1",
    session_id: "s",
    timestamp: "2026-01-01T00:00:00.000Z",
    payload: { text },
  };
}

describe("applyTranscriptMessage", () => {
  it("updates partial and final lines", () => {
    let state = { partial: "", finals: [] as string[] };
    state = applyTranscriptMessage(state, msg("transcript.partial", "hel"));
    expect(state.partial).toBe("hel");
    state = applyTranscriptMessage(state, msg("transcript.final", "hello"));
    expect(state.partial).toBe("");
    expect(state.finals).toEqual(["hello"]);
  });
});
