interface Props {
  partial: string;
  finals: string[];
}

export function TranscriptPanel({ partial, finals }: Props) {
  return (
    <section className="transcript-panel" aria-live="polite" aria-relevant="additions text">
      <h2>Transcript</h2>
      <ul className="final-lines">
        {finals.map((line, index) => (
          <li key={`${index}-${line.slice(0, 24)}`}>{line}</li>
        ))}
      </ul>
      {partial ? <p className="partial-line">{partial}</p> : null}
      {!partial && finals.length === 0 ? (
        <p className="transcript-placeholder">Speak to see live transcription.</p>
      ) : null}
    </section>
  );
}
