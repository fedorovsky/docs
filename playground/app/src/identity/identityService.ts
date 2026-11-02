import type { IdentityBridge } from '../bridge/identityBridge';
import type { IdentityObserver } from './identityObserver';
import type { ConsentRequest } from './types';

export interface IdentityService {
  /** Loads the config and pushes it into the observer. Rejects on failure; the observer is untouched. A start() while one is in flight shares that request. */
  start(): Promise<void>;
  /** Saves both choices in one call. On success merges statuses and IDs into the observer; on failure rejects and touches nothing. */
  saveConsent(request: ConsentRequest): Promise<void>;
}

export function createIdentityService(bridge: IdentityBridge, observer: IdentityObserver): IdentityService {
  let starting: Promise<void> | null = null;
  return {
    start() {
      if (starting === null) {
        starting = bridge
          .getConfig()
          .then((fields) => observer.set(fields))
          .finally(() => {
            starting = null;
          });
      }
      return starting;
    },
    async saveConsent(request) {
      const current = observer.get();
      if (current === null) throw new Error('Identity is not loaded yet');
      const response = await bridge.updateConsent(request);
      observer.set({
        ...current,
        marketingConsentStatus: request.marketing,
        analyticsConsentStatus: request.analytics,
        marketingTrackingId: response.marketingTrackingId,
        analyticsTrackingId: response.analyticsTrackingId,
      });
    },
  };
}
