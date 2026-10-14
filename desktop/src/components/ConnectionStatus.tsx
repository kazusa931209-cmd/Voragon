import type { ConnectionState } from "../api/realtimeClient";

const LABELS: Record<ConnectionState, string> = {
  disconnected: "Disconnected",
  connecting: "Connecting…",
  ready: "Connected",
  reconnecting: "Reconnecting…",
  error: "Error",
};

interface Props {
  state: ConnectionState;
  sessionId: string | null;
}

export function ConnectionStatus({ state, sessionId }: Props) {
  return (
    <div className="connection-status" data-state={state}>
      <span className="status-dot" aria-hidden />
      <span>{LABELS[state]}</span>
      {sessionId ? (
        <span className="session-id" title="Session ID">
          {sessionId.slice(0, 8)}…
        </span>
      ) : null}
    </div>
  );
}
