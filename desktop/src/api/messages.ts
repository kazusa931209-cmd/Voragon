export interface MessageEnvelope {
  type: string;
  id: string;
  session_id: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export function utcTimestamp(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, ".000Z");
}

export function newMessageId(): string {
  return crypto.randomUUID();
}

export function buildControlMessage(
  type: string,
  sessionId: string,
  payload: Record<string, unknown> = {},
): string {
  return JSON.stringify({
    type,
    id: newMessageId(),
    session_id: sessionId,
    timestamp: utcTimestamp(),
    payload,
  });
}

export function parseEnvelope(raw: string): MessageEnvelope {
  const data = JSON.parse(raw) as MessageEnvelope;
  if (!data.type || !data.session_id) {
    throw new Error("Invalid message envelope");
  }
  return data;
}

export function transcriptText(message: MessageEnvelope): string {
  const text = message.payload.text;
  return typeof text === "string" ? text : "";
}

export function errorCode(message: MessageEnvelope): string {
  const code = message.payload.code;
  return typeof code === "string" ? code : "UNKNOWN";
}

export function isRecoverableError(message: MessageEnvelope): boolean {
  return message.payload.recoverable === true;
}
