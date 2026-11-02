export enum ConsentStatus {
  Declined = 0,
  Accepted = 1,
  NotDecided = 2,
}

export interface IdentityFields {
  marketingTrackingId: string | null;
  analyticsTrackingId: string | null;
  deviceId: string;
  temporaryId: string;
  consentRequired: boolean;
  marketingConsentStatus: ConsentStatus;
  analyticsConsentStatus: ConsentStatus;
}

export const IDENTITY_FIELD_KEYS: readonly (keyof IdentityFields)[] = [
  'marketingTrackingId',
  'analyticsTrackingId',
  'deviceId',
  'temporaryId',
  'consentRequired',
  'marketingConsentStatus',
  'analyticsConsentStatus',
];

/** Both fields are Accepted or Declined, as the toggles stand. */
export interface ConsentRequest {
  marketing: ConsentStatus;
  analytics: ConsentStatus;
}

export interface ConsentResponse {
  marketingTrackingId: string | null;
  analyticsTrackingId: string | null;
}
