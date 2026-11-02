import { useEffect, useState } from 'react';
import type { IdentityObserver } from '../identity/identityObserver';
import type { IdentityService } from '../identity/identityService';
import { ConsentStatus, type IdentityFields } from '../identity/types';
import { useIdentity } from '../identity/useIdentity';

export type ConsentBlockVariant = 'initial' | 'settings';

// Provisional English copy (PRD Q4).
const TITLES: Record<ConsentBlockVariant, string> = {
  initial: 'Tracking consent',
  settings: 'Tracking settings',
};
export const SAVE_ERROR_TEXT = 'Could not save your choice. Try again.';

export function isConsentBlockVisible(variant: ConsentBlockVariant, fields: IdentityFields | null): boolean {
  if (fields === null || !fields.consentRequired) return false;
  if (variant === 'settings') return true;
  return fields.marketingConsentStatus === ConsentStatus.NotDecided || fields.analyticsConsentStatus === ConsentStatus.NotDecided;
}

/** Assumption (PRD Q2): NotDecided shows as off. */
function toggleOn(status: ConsentStatus): boolean {
  return status === ConsentStatus.Accepted;
}

function toStatus(on: boolean): ConsentStatus {
  return on ? ConsentStatus.Accepted : ConsentStatus.Declined;
}

interface Props {
  variant: ConsentBlockVariant;
  observer: IdentityObserver;
  service: IdentityService;
}

export function ConsentBlock({ variant, observer, service }: Props) {
  const fields = useIdentity(observer);
  const marketingStatus = fields?.marketingConsentStatus ?? ConsentStatus.NotDecided;
  const analyticsStatus = fields?.analyticsConsentStatus ?? ConsentStatus.NotDecided;

  const [marketing, setMarketing] = useState(toggleOn(marketingStatus));
  const [analytics, setAnalytics] = useState(toggleOn(analyticsStatus));
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // A save in the other block changes the statuses; re-read them into the toggles.
  useEffect(() => setMarketing(toggleOn(marketingStatus)), [marketingStatus]);
  useEffect(() => setAnalytics(toggleOn(analyticsStatus)), [analyticsStatus]);

  if (!isConsentBlockVisible(variant, fields)) return null;

  async function save(request: { marketing: ConsentStatus; analytics: ConsentStatus }) {
    setPending(true);
    setError(null);
    try {
      await service.saveConsent(request);
      // Accept all, or a save after a failed one, may leave the toggles out of step with an unchanged status.
      setMarketing(toggleOn(request.marketing));
      setAnalytics(toggleOn(request.analytics));
    } catch {
      setError(SAVE_ERROR_TEXT);
    } finally {
      setPending(false);
    }
  }

  const id = `consent-${variant}`;
  return (
    <section className="block" aria-labelledby={`${id}-title`} data-testid={id}>
      <h2 id={`${id}-title`}>{TITLES[variant]}</h2>
      <label>
        <input type="checkbox" role="switch" checked={marketing} disabled={pending} onChange={(e) => setMarketing(e.target.checked)} />
        Marketing
      </label>
      <label>
        <input type="checkbox" role="switch" checked={analytics} disabled={pending} onChange={(e) => setAnalytics(e.target.checked)} />
        Analytics
      </label>
      <div className="actions">
        <button type="button" disabled={pending} onClick={() => save({ marketing: toStatus(marketing), analytics: toStatus(analytics) })}>
          Save
        </button>
        <button type="button" disabled={pending} onClick={() => save({ marketing: ConsentStatus.Accepted, analytics: ConsentStatus.Accepted })}>
          Accept all
        </button>
      </div>
      {error && <p role="alert" className="error">{error}</p>}
    </section>
  );
}
