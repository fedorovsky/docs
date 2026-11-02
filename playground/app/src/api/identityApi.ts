import type { ConsentRequest, ConsentResponse, IdentityFields } from '../identity/types';

/** The backend contract from TRACK-12. The real adapter implements it later. */
export interface IdentityApi {
  getConfig(): Promise<IdentityFields>;
  updateConsent(request: ConsentRequest): Promise<ConsentResponse>;
}
