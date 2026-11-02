import type { IdentityFields } from '../identity/types';

export interface RecorderSnapshot<T> {
  state: T;
  updatedAt: Date;
}

/** A fake subscriber: remembers the projection of the last fields it received, with the time. */
export interface Recorder<T> {
  readonly name: string;
  handle(fields: IdentityFields): void;
  getSnapshot(): RecorderSnapshot<T> | null;
  subscribe(listener: () => void): () => void;
}

export function createRecorder<T>(name: string, project: (fields: IdentityFields) => T, now: () => Date = () => new Date()): Recorder<T> {
  let snapshot: RecorderSnapshot<T> | null = null;
  const listeners = new Set<() => void>();
  return {
    name,
    handle(fields) {
      snapshot = { state: project(fields), updatedAt: now() };
      for (const listener of listeners) listener();
    },
    getSnapshot() {
      return snapshot;
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
  };
}

/** The fields every subscriber writes; deviceId only without consentRequired, the statuses only with it. */
export interface CommonFields {
  marketingTrackingId: string | null;
  analyticsTrackingId: string | null;
  temporaryId: string;
  deviceId?: string;
  marketingConsentStatus?: number;
  analyticsConsentStatus?: number;
}

export function pickCommonFields(fields: IdentityFields): CommonFields {
  const common: CommonFields = {
    marketingTrackingId: fields.marketingTrackingId,
    analyticsTrackingId: fields.analyticsTrackingId,
    temporaryId: fields.temporaryId,
  };
  if (fields.consentRequired) {
    common.marketingConsentStatus = fields.marketingConsentStatus;
    common.analyticsConsentStatus = fields.analyticsConsentStatus;
  } else {
    common.deviceId = fields.deviceId;
  }
  return common;
}
