import type { IdentityFields } from '../identity/types';
import { createRecorder, pickCommonFields, type Recorder } from './recorder';

export type RequestHeaders = Record<string, string>;

/** Header names proposed in the Spec (Spec Q3); confirmed with the backend before the real integration. */
export const HEADER_NAMES = {
  marketingTrackingId: 'X-Marketing-Tracking-Id',
  analyticsTrackingId: 'X-Analytics-Tracking-Id',
  temporaryId: 'X-Temporary-Id',
  deviceId: 'X-Device-Id',
  marketingConsentStatus: 'X-Marketing-Consent-Status',
  analyticsConsentStatus: 'X-Analytics-Consent-Status',
  consentRequired: 'X-Consent-Required',
} as const;

export function projectRequestHeaders(fields: IdentityFields): RequestHeaders {
  const values: Partial<Record<keyof typeof HEADER_NAMES, string | number | boolean | null>> = {
    ...pickCommonFields(fields),
    consentRequired: fields.consentRequired,
  };
  const headers: RequestHeaders = {};
  for (const key of Object.keys(HEADER_NAMES) as (keyof typeof HEADER_NAMES)[]) {
    const value = values[key];
    if (value === null || value === undefined) continue; // a null header is dropped
    headers[HEADER_NAMES[key]] = String(value);
  }
  return headers;
}

export function createRequestHeadersSubscriber(): Recorder<RequestHeaders> {
  return createRecorder('Request headers', projectRequestHeaders);
}
