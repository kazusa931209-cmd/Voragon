import { useCallback, useReducer } from "react";
import type { MessageEnvelope } from "../api/messages";
import { transcriptText } from "../api/messages";

export interface TranscriptState {
  partial: string;
  finals: string[];
}

type Action =
  | { type: "partial"; text: string }
  | { type: "final"; text: string }
  | { type: "reset" };

function reducer(state: TranscriptState, action: Action): TranscriptState {
  switch (action.type) {
    case "partial":
      return { ...state, partial: action.text };
    case "final":
      return {
        partial: "",
        finals: action.text ? [...state.finals, action.text] : state.finals,
      };
    case "reset":
      return { partial: "", finals: [] };
    default:
      return state;
  }
}

export function applyTranscriptMessage(state: TranscriptState, message: MessageEnvelope): TranscriptState {
  const text = transcriptText(message);
  if (message.type === "transcript.partial") {
    return reducer(state, { type: "partial", text });
  }
  if (message.type === "transcript.final") {
    return reducer(state, { type: "final", text });
  }
  return state;
}

export function useTranscript() {
  const [state, dispatch] = useReducer(reducer, { partial: "", finals: [] });

  const handleMessage = useCallback((message: MessageEnvelope) => {
    if (message.type === "transcript.partial") {
      dispatch({ type: "partial", text: transcriptText(message) });
    } else if (message.type === "transcript.final") {
      dispatch({ type: "final", text: transcriptText(message) });
    }
  }, []);

  const reset = useCallback(() => dispatch({ type: "reset" }), []);

  return { ...state, handleMessage, reset };
}
