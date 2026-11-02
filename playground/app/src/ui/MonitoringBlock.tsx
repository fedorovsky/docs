import { useSyncExternalStore } from 'react';
import type { Recorder } from '../subscribers/recorder';

interface Props {
  recorder: Recorder<unknown>;
}

/** Debug block: the recorder's current state and the time of its last update. Removed later (PRD Q7). */
export function MonitoringBlock({ recorder }: Props) {
  const snapshot = useSyncExternalStore(recorder.subscribe, recorder.getSnapshot, recorder.getSnapshot);
  return (
    <section className="block monitoring" aria-label={recorder.name}>
      <div className="head">
        <h3>{recorder.name}</h3>
        {snapshot === null ? (
          <span className="muted">No update yet</span>
        ) : (
          <span className="muted">
            Updated at <time dateTime={snapshot.updatedAt.toISOString()}>{snapshot.updatedAt.toLocaleTimeString()}</time>
          </span>
        )}
      </div>
      {snapshot !== null && <pre>{JSON.stringify(snapshot.state, null, 2)}</pre>}
    </section>
  );
}
