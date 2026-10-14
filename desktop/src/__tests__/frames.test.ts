import { describe, expect, it } from "vitest";
import { buildAudioFrame, BYTES_PER_FRAME } from "../api/frames";

describe("buildAudioFrame", () => {
  it("produces 17-byte header plus PCM", () => {
    const pcm = new Uint8Array(BYTES_PER_FRAME);
    pcm.fill(1);
    const buf = buildAudioFrame(pcm, 7, 123456789n);
    expect(buf.byteLength).toBe(17 + BYTES_PER_FRAME);
    const view = new DataView(buf);
    expect(view.getUint8(0)).toBe(1);
    expect(view.getUint32(1, true)).toBe(7);
    expect(view.getBigUint64(5, true)).toBe(123456789n);
    expect(view.getUint32(13, true)).toBe(BYTES_PER_FRAME);
  });

  it("rejects wrong payload size", () => {
    expect(() => buildAudioFrame(new Uint8Array(100), 0)).toThrow();
  });
});
