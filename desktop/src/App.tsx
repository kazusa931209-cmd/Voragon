import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { useCallback, useEffect, useRef, useState } from "react";
import { errorCode, isRecoverableError, type MessageEnvelope } from "./api/messages";
import { pcmFromEventPayload } from "./api/frames";
import { RealtimeClient, type ConnectionState } from "./api/realtimeClient";
import { ConnectionStatus } from "./components/ConnectionStatus";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { useTranscript } from "./hooks/useTranscript";
import { DEFAULT_BACKEND_URL, loadSettings, saveSettings, type AppSettings } from "./settings/store";
import "./App.css";

interface AudioDevice {
  index: number;
  name: string;
}

function App() {
  const [settings, setSettings] = useState<AppSettings>({
    backendUrl: DEFAULT_BACKEND_URL,
    inputDeviceIndex: null,
    language: "en",
  });
  const [devices, setDevices] = useState<AudioDevice[]>([]);
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [transcribing, setTranscribing] = useState(false);
  const [frameCount, setFrameCount] = useState(0);

  const clientRef = useRef<RealtimeClient | null>(null);
  const transcribingRef = useRef(false);
  const { partial, finals, handleMessage, reset } = useTranscript();

  useEffect(() => {
    void loadSettings().then(setSettings);
    void invoke<AudioDevice[]>("list_audio_input_devices")
      .then(setDevices)
      .catch(() => setDevices([]));
  }, []);

  const onServerMessage = useCallback(
    (message: MessageEnvelope) => {
      if (message.type === "transcript.partial" || message.type === "transcript.final") {
        handleMessage(message);
      }
      if (message.type === "error") {
        const code = errorCode(message);
        const text =
          typeof message.payload.message === "string"
            ? message.payload.message
            : code;
        setNotice(`${code}: ${text}`);
        if (!isRecoverableError(message)) {
          setTranscribing(false);
          transcribingRef.current = false;
        }
      }
      if (message.type === "buffer.overflow") {
        setNotice("Audio buffer overflow — slow down or check connection.");
      }
    },
    [handleMessage],
  );

  const ensureClient = useCallback(async () => {
    if (clientRef.current?.getSessionId()) {
      return clientRef.current;
    }
    clientRef.current?.disconnect();
    const client = new RealtimeClient(settings.backendUrl, settings.language, {
      onStateChange: setConnectionState,
      onSessionId: setSessionId,
      onMessage: onServerMessage,
      onNotice: (text) => setNotice(text),
    });
    clientRef.current = client;
    await client.connect();
    return client;
  }, [onServerMessage, settings.backendUrl, settings.language]);

  const connect = useCallback(async () => {
    setNotice(null);
    try {
      await ensureClient();
    } catch {
      setNotice("Could not connect to backend.");
    }
  }, [ensureClient]);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
    clientRef.current = null;
    setTranscribing(false);
    transcribingRef.current = false;
    void invoke("stop_audio_capture").catch(() => undefined);
  }, []);

  const stopTranscription = useCallback(async () => {
    setTranscribing(false);
    transcribingRef.current = false;
    await invoke("stop_audio_capture").catch(() => undefined);
    await clientRef.current?.stopAudio();
  }, []);

  const startTranscription = useCallback(async () => {
    setNotice(null);
    try {
      const client = await ensureClient();
      reset();
      await client.startAudio();
      await invoke("start_audio_capture", {
        device_index: settings.inputDeviceIndex,
      });
      setTranscribing(true);
      transcribingRef.current = true;
      setFrameCount(0);
    } catch {
      setNotice("Failed to start transcription.");
      setTranscribing(false);
      transcribingRef.current = false;
    }
  }, [ensureClient, reset, settings.inputDeviceIndex]);

  const toggleTranscription = useCallback(async () => {
    if (transcribingRef.current) {
      await stopTranscription();
    } else {
      await startTranscription();
    }
  }, [startTranscription, stopTranscription]);

  useEffect(() => {
    const unlistenFrame = listen<number[] | Uint8Array>("audio-frame", (event) => {
      if (!transcribingRef.current || !clientRef.current) {
        return;
      }
      try {
        const pcm = pcmFromEventPayload(event.payload);
        clientRef.current.sendPcmFrame(pcm);
        setFrameCount((n) => n + 1);
      } catch {
        /* ignore malformed frames */
      }
    });
    const unlistenShortcut = listen("transcription-toggle", () => {
      void toggleTranscription();
    });
    return () => {
      void unlistenFrame.then((fn) => fn());
      void unlistenShortcut.then((fn) => fn());
    };
  }, [toggleTranscription]);

  useEffect(() => {
    return () => {
      clientRef.current?.disconnect();
      void invoke("stop_audio_capture").catch(() => undefined);
    };
  }, []);

  const save = async () => {
    await saveSettings(settings);
    setNotice("Settings saved.");
  };

  return (
    <main className="app">
      <header>
        <h1>Voragon</h1>
        <ConnectionStatus state={connectionState} sessionId={sessionId} />
      </header>

      {notice ? <p className="notice">{notice}</p> : null}

      <section className="controls">
        <button type="button" onClick={() => void connect()} disabled={connectionState === "connecting"}>
          Connect
        </button>
        <button type="button" onClick={disconnect}>
          Disconnect
        </button>
        <button
          type="button"
          className="primary"
          onClick={() => void toggleTranscription()}
          disabled={connectionState !== "ready" && connectionState !== "reconnecting"}
        >
          {transcribing ? "Stop transcription" : "Start transcription"}
        </button>
        <span className="frame-debug" aria-label="Frames sent">
          {transcribing ? `${frameCount} frames` : ""}
        </span>
      </section>

      <TranscriptPanel partial={partial} finals={finals} />

      <section className="settings">
        <h2>Settings</h2>
        <label>
          Backend URL
          <input
            type="url"
            value={settings.backendUrl}
            onChange={(e) => setSettings((s) => ({ ...s, backendUrl: e.target.value }))}
          />
        </label>
        <label>
          Input device
          <select
            value={settings.inputDeviceIndex ?? ""}
            onChange={(e) =>
              setSettings((s) => ({
                ...s,
                inputDeviceIndex: e.target.value === "" ? null : Number(e.target.value),
              }))
            }
          >
            <option value="">System default</option>
            {devices.map((d) => (
              <option key={d.index} value={d.index}>
                {d.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Language
          <input
            type="text"
            value={settings.language}
            onChange={(e) => setSettings((s) => ({ ...s, language: e.target.value }))}
          />
        </label>
        <button type="button" onClick={() => void save()}>
          Save settings
        </button>
        <p className="hint">Global shortcut: ⌘⇧T (Ctrl+Shift+T on Windows) toggles transcription.</p>
      </section>
    </main>
  );
}

export default App;
