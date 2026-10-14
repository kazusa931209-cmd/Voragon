export const FRAME_VERSION = 1;
export const BYTES_PER_FRAME = 640;

const HEADER_SIZE = 17;

export function buildAudioFrame(pcmData: Uint8Array, seqNum: number, timestampUs?: bigint): ArrayBuffer {
  if (pcmData.length !== BYTES_PER_FRAME) {
    throw new Error(`Expected ${BYTES_PER_FRAME} bytes of PCM, got ${pcmData.length}`);
  }
  const ts = timestampUs ?? BigInt(Date.now()) * 1000n;
  const buffer = new ArrayBuffer(HEADER_SIZE + pcmData.length);
  const view = new DataView(buffer);
  view.setUint8(0, FRAME_VERSION);
  view.setUint32(1, seqNum, true);
  view.setBigUint64(5, ts, true);
  view.setUint32(13, pcmData.length, true);
  new Uint8Array(buffer, HEADER_SIZE).set(pcmData);
  return buffer;
}

export function pcmFromEventPayload(payload: unknown): Uint8Array {
  if (payload instanceof Uint8Array) {
    return payload;
  }
  if (Array.isArray(payload)) {
    return Uint8Array.from(payload as number[]);
  }
  throw new Error("Unsupported audio frame payload");
}
