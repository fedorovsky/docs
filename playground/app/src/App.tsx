import { useState } from 'react';
import type { IdentityBridge } from './bridge/identityBridge';
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
  createBridge(consentRequired: boolean, firstStart: boolean): IdentityBridge;
}

type StartState = 'idle' | 'pending' | 'failed' | 'ready';

export function App({ observer, recorders, createBridge }: AppProps) {
  const fields = useIdentity(observer);
  const [consentRequired, setConsentRequired] = useState(true);
  const [firstStart, setFirstStart] = useState(false);
  const [service, setService] = useState<IdentityService | null>(null);
  const [start, setStart] = useState<StartState>('idle');

  function handleStart() {
    const next = createIdentityService(createBridge(consentRequired, firstStart), observer);
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
      <div className="layout">
        <div>
          <StartPanel
            consentRequired={consentRequired}
            onConsentRequiredChange={setConsentRequired}
            firstStart={firstStart}
            onFirstStartChange={setFirstStart}
            onStart={handleStart}
            pending={start === 'pending'}
          />
          {start === 'pending' && fields === null && <p className="muted">Loading…</p>}
          {start === 'failed' && (
            <section className="block" role="alert">
              <div className="row">
                <span className="error">{LOAD_ERROR_TEXT}</span>
                <span className="actions">
                  <button type="button" onClick={handleStart}>
                    Retry
                  </button>
                </span>
              </div>
            </section>
          )}
          {fields !== null && service !== null && (
            <>
              <ConfigBlock observer={observer} />
              <ConsentBlock variant="initial" observer={observer} service={service} />
              <ConsentBlock variant="settings" observer={observer} service={service} />
            </>
          )}
        </div>
        {fields !== null && service !== null && (
          <section className="monitoring-row" aria-label="Monitoring">
            {recorders.map((recorder) => (
              <MonitoringBlock key={recorder.name} recorder={recorder} />
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
