interface Props {
  consentRequired: boolean;
  onConsentRequiredChange(value: boolean): void;
  onStart(): void;
  pending: boolean;
}

/** Debug panel: picks the fake config's consentRequired and starts the app. Removed later (PRD Q7). */
export function StartPanel({ consentRequired, onConsentRequiredChange, onStart, pending }: Props) {
  return (
    <section className="block" aria-label="Start">
      <h2>Start</h2>
      <label>
        <input type="checkbox" role="switch" checked={consentRequired} disabled={pending} onChange={(e) => onConsentRequiredChange(e.target.checked)} />
        consentRequired
      </label>
      <div className="actions">
        <button type="button" disabled={pending} onClick={onStart}>
          Start
        </button>
      </div>
    </section>
  );
}
