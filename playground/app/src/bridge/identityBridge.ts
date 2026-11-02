import type { ConsentRequest, ConsentResponse, IdentityFields } from '../identity/types';

/** The native bridge contract from TRACK-12: the host app provides the config and saves the consent choice. The real adapter implements it later. */
export interface IdentityBridge {
  getConfig(): Promise<IdentityFields>;
  updateConsent(request: ConsentRequest): Promise<ConsentResponse>;
}
