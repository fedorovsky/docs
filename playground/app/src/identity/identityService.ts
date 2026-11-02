import type { IdentityApi } from '../api/identityApi';
import type { IdentityObserver } from './identityObserver';
import type { ConsentRequest } from './types';

export interface IdentityService {
  /** Loads the config and pushes it into the observer. Rejects on failure; the observer is untouched. */
  start(): Promise<void>;
  /** Saves both choices in one call. On success merges statuses and IDs into the observer; on failure rejects and touches nothing. */
  saveConsent(request: ConsentRequest): Promise<void>;
}

export function createIdentityService(api: IdentityApi, observer: IdentityObserver): IdentityService {
  return {
    async start() {
      const fields = await api.getConfig();
      observer.set(fields);
    },
    async saveConsent(request) {
      const current = observer.get();
      if (current === null) throw new Error('Identity is not loaded yet');
      const response = await api.updateConsent(request);
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
