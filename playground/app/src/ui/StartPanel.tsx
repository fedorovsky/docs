interface Props {
  consentRequired: boolean;
  onConsentRequiredChange(value: boolean): void;
  firstStart: boolean;
  onFirstStartChange(value: boolean): void;
  onStart(): void;
  pending: boolean;
}

/** Debug panel: picks the fake config's consentRequired and starts the app. Removed later (PRD Q7). */
export function StartPanel({ consentRequired, onConsentRequiredChange, firstStart, onFirstStartChange, onStart, pending }: Props) {
  return (
    <section className="block" aria-label="Start">
      <div className="row">
        <h2>Start</h2>
        <label>
          <input type="checkbox" role="switch" checked={consentRequired} disabled={pending} onChange={(e) => onConsentRequiredChange(e.target.checked)} />
          consentRequired
        </label>
        <label>
          <input type="checkbox" role="switch" checked={firstStart} disabled={pending} onChange={(e) => onFirstStartChange(e.target.checked)} />
          first start
        </label>
        <span className="actions">
          <button type="button" disabled={pending} onClick={onStart}>
            Start
          </button>
        </span>
      </div>
    </section>
  );
}
