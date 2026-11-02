import { IDENTITY_FIELD_KEYS, type IdentityFields } from './types';

export type IdentitySubscriber = (fields: IdentityFields) => void;

export interface IdentityObserver {
  /** Stores the fields and calls every subscriber if this is the first set or any field changed. */
  set(fields: IdentityFields): void;
  get(): IdentityFields | null;
  /** A subscriber added after the first set is called at once with the current fields. */
  subscribe(fn: IdentitySubscriber): () => void;
}

function sameFields(a: IdentityFields, b: IdentityFields): boolean {
  return IDENTITY_FIELD_KEYS.every((key) => a[key] === b[key]);
}

export function createIdentityObserver(): IdentityObserver {
  let current: IdentityFields | null = null;
  const subscribers = new Set<IdentitySubscriber>();

  return {
    set(fields) {
      if (current !== null && sameFields(current, fields)) return;
      current = { ...fields };
      for (const fn of subscribers) fn(current);
    },
    get() {
      return current;
    },
    subscribe(fn) {
      subscribers.add(fn);
      if (current !== null) fn(current);
      return () => {
        subscribers.delete(fn);
      };
    },
  };
}
