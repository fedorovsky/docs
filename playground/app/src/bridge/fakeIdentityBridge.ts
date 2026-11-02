import { ConsentStatus, type ConsentRequest, type ConsentResponse } from '../identity/types';
import type { IdentityBridge } from './identityBridge';

export const STORAGE_KEY = 'track12.identity';
export const DEVICE_ID = 'device-0001';

export interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export interface FakeIdentityBridgeOptions {
  consentRequired: boolean;
  /** Forget the stored choice on creation, so the next getConfig is a first start (PRD R12). */
  forgetChoice?: boolean;
  /** [min, max] in milliseconds. The fake never fails: error handling is exercised with stubs in tests. */
  delayMs?: [number, number];
  random?: () => number;
  storage?: StorageLike | null;
  newId?: () => string;
}

interface StoredChoice {
  marketingConsentStatus: ConsentStatus;
  analyticsConsentStatus: ConsentStatus;
  marketingTrackingId: string | null;
  analyticsTrackingId: string | null;
}

const EMPTY: StoredChoice = {
  marketingConsentStatus: ConsentStatus.NotDecided,
  analyticsConsentStatus: ConsentStatus.NotDecided,
  marketingTrackingId: null,
  analyticsTrackingId: null,
};

function isStatus(value: unknown): value is ConsentStatus {
  return value === ConsentStatus.Declined || value === ConsentStatus.Accepted || value === ConsentStatus.NotDecided;
}

function isChoice(value: unknown): value is StoredChoice {
  if (typeof value !== 'object' || value === null) return false;
  const v = value as Record<string, unknown>;
  const id = (x: unknown) => x === null || typeof x === 'string';
  return isStatus(v.marketingConsentStatus) && isStatus(v.analyticsConsentStatus) && id(v.marketingTrackingId) && id(v.analyticsTrackingId);
}

function defaultStorage(): StorageLike | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage;
  } catch {
    return null;
  }
}

export function createFakeIdentityBridge(options: FakeIdentityBridgeOptions): IdentityBridge {
  const {
    consentRequired,
    forgetChoice = false,
    delayMs = [300, 1000],
    random = Math.random,
    newId = () => crypto.randomUUID(),
  } = options;
  const storage = options.storage === undefined ? defaultStorage() : options.storage;

  // Falls back to memory when storage is unavailable or corrupt.
  let memory: StoredChoice = EMPTY;

  if (forgetChoice && storage) {
    try {
      storage.removeItem(STORAGE_KEY);
    } catch {
      // storage unavailable: memory is already empty
    }
  }

  function read(): StoredChoice {
    if (storage) {
      try {
        const raw = storage.getItem(STORAGE_KEY);
        if (raw !== null) {
          const parsed: unknown = JSON.parse(raw);
          if (isChoice(parsed)) return parsed;
        }
      } catch {
        // unreadable: treat as nothing stored
      }
    }
    return memory;
  }

  function write(choice: StoredChoice): void {
    memory = choice;
    if (storage) {
      try {
        storage.setItem(STORAGE_KEY, JSON.stringify(choice));
      } catch {
        // storage unavailable: keep the choice in memory for the session
      }
    }
  }

  async function simulateDelay(): Promise<void> {
    const [min, max] = delayMs;
    const wait = min + (max - min) * random();
    if (wait > 0) await new Promise((resolve) => setTimeout(resolve, wait));
  }

  return {
    async getConfig() {
      await simulateDelay();
      // Without consentRequired nothing is decided: both NotDecided, no tracking IDs, storage left alone (PRD R2).
      const choice = consentRequired ? read() : EMPTY;
      return {
        ...choice,
        deviceId: DEVICE_ID,
        temporaryId: newId(),
        consentRequired,
      };
    },

    async updateConsent(request: ConsentRequest): Promise<ConsentResponse> {
      await simulateDelay();
      const stored = read();
      const next = (requested: ConsentStatus, storedStatus: ConsentStatus, storedId: string | null): string | null => {
        if (requested !== ConsentStatus.Accepted) return null;
        return storedStatus === ConsentStatus.Accepted && storedId !== null ? storedId : newId();
      };
      const marketingTrackingId = next(request.marketing, stored.marketingConsentStatus, stored.marketingTrackingId);
      const analyticsTrackingId = next(request.analytics, stored.analyticsConsentStatus, stored.analyticsTrackingId);
      write({
        marketingConsentStatus: request.marketing === ConsentStatus.Accepted ? ConsentStatus.Accepted : ConsentStatus.Declined,
        analyticsConsentStatus: request.analytics === ConsentStatus.Accepted ? ConsentStatus.Accepted : ConsentStatus.Declined,
        marketingTrackingId,
        analyticsTrackingId,
      });
      return { marketingTrackingId, analyticsTrackingId };
    },
  };
}
