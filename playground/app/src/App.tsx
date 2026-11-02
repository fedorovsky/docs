import { useCallback, useEffect, useState } from 'react';
import type { IdentityObserver } from './identity/identityObserver';
import type { IdentityService } from './identity/identityService';
import { useIdentity } from './identity/useIdentity';
import type { Recorder } from './subscribers/recorder';
import { ConsentBlock } from './ui/ConsentBlock';
import { MonitoringBlock } from './ui/MonitoringBlock';

export const LOAD_ERROR_TEXT = 'Could not load the config.';

export interface AppProps {
  observer: IdentityObserver;
  service: IdentityService;
  recorders: Recorder<unknown>[];
}

type StartState = { kind: 'pending' } | { kind: 'failed' } | { kind: 'ready' };

export function App({ observer, service, recorders }: AppProps) {
  const fields = useIdentity(observer);
  const [start, setStart] = useState<StartState>({ kind: 'pending' });

  const load = useCallback(() => {
    setStart({ kind: 'pending' });
    service
      .start()
      .then(() => setStart({ kind: 'ready' }))
      .catch(() => setStart({ kind: 'failed' }));
  }, [service]);

  useEffect(() => {
    if (fields === null) load();
    else setStart({ kind: 'ready' });
  }, [fields === null, load]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <main>
      <h1>Identity and tracking consent</h1>
      {start.kind === 'pending' && fields === null && <p className="muted">Loading…</p>}
      {start.kind === 'failed' && (
        <section className="block" role="alert">
          <p className="error">{LOAD_ERROR_TEXT}</p>
          <button type="button" onClick={load}>
            Retry
          </button>
        </section>
      )}
      {fields !== null && (
        <>
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
