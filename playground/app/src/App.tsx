import { useState } from 'react';
import type { IdentityApi } from './api/identityApi';
import type { IdentityObserver } from './identity/identityObserver';
import { createIdentityService, type IdentityService } from './identity/identityService';
import { useIdentity } from './identity/useIdentity';
import type { Recorder } from './subscribers/recorder';
import { ConfigBlock } from './ui/ConfigBlock';
import { ConsentBlock } from './ui/ConsentBlock';
import { MonitoringBlock } from './ui/MonitoringBlock';
import { StartPanel } from './ui/StartPanel';

export const LOAD_ERROR_TEXT = 'Could not load the config.';

export interface AppProps {
  observer: IdentityObserver;
  recorders: Recorder<unknown>[];
  createApi(consentRequired: boolean): IdentityApi;
}

type StartState = 'idle' | 'pending' | 'failed' | 'ready';

export function App({ observer, recorders, createApi }: AppProps) {
  const fields = useIdentity(observer);
  const [consentRequired, setConsentRequired] = useState(true);
  const [service, setService] = useState<IdentityService | null>(null);
  const [start, setStart] = useState<StartState>('idle');

  function handleStart() {
    const next = createIdentityService(createApi(consentRequired), observer);
    setService(next);
    setStart('pending');
    next
      .start()
      .then(() => setStart('ready'))
      .catch(() => setStart('failed'));
  }

  return (
    <main>
      <h1>Identity and tracking consent</h1>
      <StartPanel consentRequired={consentRequired} onConsentRequiredChange={setConsentRequired} onStart={handleStart} pending={start === 'pending'} />
      {start === 'pending' && fields === null && <p className="muted">Loading…</p>}
      {start === 'failed' && (
        <section className="block" role="alert">
          <p className="error">{LOAD_ERROR_TEXT}</p>
          <button type="button" onClick={handleStart}>
            Retry
          </button>
        </section>
      )}
      {fields !== null && service !== null && (
        <>
          <ConfigBlock observer={observer} />
          <ConsentBlock variant="initial" observer={observer} service={service} />
          <ConsentBlock variant="settings" observer={observer} service={service} />
          <section className="monitoring-row" aria-label="Monitoring">
            {recorders.map((recorder) => (
              <MonitoringBlock key={recorder.name} recorder={recorder} />
            ))}
          </section>
        </>
      )}
    </main>
  );
}
