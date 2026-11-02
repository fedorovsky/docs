import { useSyncExternalStore } from 'react';
import type { IdentityObserver } from './identityObserver';
import type { IdentityFields } from './types';

/** The observer is the store: both consent blocks and the monitoring read from it. */
export function useIdentity(observer: IdentityObserver): IdentityFields | null {
  return useSyncExternalStore(observer.subscribe, observer.get, observer.get);
}
