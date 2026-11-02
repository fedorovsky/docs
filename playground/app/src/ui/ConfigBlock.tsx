import type { IdentityObserver } from '../identity/identityObserver';
import { IDENTITY_FIELD_KEYS } from '../identity/types';
import { useIdentity } from '../identity/useIdentity';

interface Props {
  observer: IdentityObserver;
}

/** Debug block: the seven identity fields the app currently holds. Removed later (PRD Q7). */
export function ConfigBlock({ observer }: Props) {
  const fields = useIdentity(observer);
  if (fields === null) return null;
  return (
    <section className="block monitoring" aria-label="Config">
      <h3>Config</h3>
      <pre>{JSON.stringify(Object.fromEntries(IDENTITY_FIELD_KEYS.map((key) => [key, fields[key]])), null, 2)}</pre>
    </section>
  );
}
