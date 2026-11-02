import { ConsentStatus } from '../identity/types';
import { createFakeIdentityBridge, DEVICE_ID, STORAGE_KEY, type StorageLike } from './fakeIdentityBridge';

function memoryStorage(): StorageLike & { data: Map<string, string> } {
  const data = new Map<string, string>();
  return {
    data,
    getItem: (key) => data.get(key) ?? null,
    setItem: (key, value) => void data.set(key, value),
    removeItem: (key) => void data.delete(key),
  };
}

function bridge(overrides: Partial<Parameters<typeof createFakeIdentityBridge>[0]> = {}) {
  let n = 0;
  return createFakeIdentityBridge({
    consentRequired: true,
    delayMs: [0, 0],
    storage: memoryStorage(),
    newId: () => `id-${++n}`,
    ...overrides,
  });
}

const { Accepted, Declined, NotDecided } = ConsentStatus;

test('first start with consentRequired = true: both NotDecided, IDs null, constant deviceId', async () => {
  const config = await bridge().getConfig();
  expect(config).toMatchObject({
    marketingConsentStatus: NotDecided,
    analyticsConsentStatus: NotDecided,
    marketingTrackingId: null,
    analyticsTrackingId: null,
    deviceId: DEVICE_ID,
    consentRequired: true,
  });
});

test('temporaryId is new on every getConfig', async () => {
  const a = bridge();
  const first = await a.getConfig();
  const second = await a.getConfig();
  expect(first.temporaryId).not.toBe(second.temporaryId);
  expect(first.deviceId).toBe(second.deviceId);
});

test('consentRequired = false: both NotDecided, no tracking IDs, nothing stored', async () => {
  const storage = memoryStorage();
  const config = await bridge({ consentRequired: false, storage }).getConfig();
  expect(config).toMatchObject({
    marketingConsentStatus: NotDecided,
    analyticsConsentStatus: NotDecided,
    marketingTrackingId: null,
    analyticsTrackingId: null,
    deviceId: DEVICE_ID,
    consentRequired: false,
  });
  expect(storage.data.size).toBe(0);
});

test('consentRequired = false ignores a stored choice and keeps it for the next consentRequired = true start', async () => {
  const storage = memoryStorage();
  const { analyticsTrackingId } = await bridge({ storage }).updateConsent({ marketing: Declined, analytics: Accepted });
  const config = await bridge({ consentRequired: false, storage }).getConfig();
  expect(config).toMatchObject({ marketingConsentStatus: NotDecided, analyticsConsentStatus: NotDecided, marketingTrackingId: null, analyticsTrackingId: null });
  const again = await bridge({ storage }).getConfig();
  expect(again).toMatchObject({ marketingConsentStatus: Declined, analyticsConsentStatus: Accepted, analyticsTrackingId });
});

test('Accepted → Accepted keeps the ID', async () => {
  const a = bridge();
  const first = await a.updateConsent({ marketing: Accepted, analytics: Accepted });
  const second = await a.updateConsent({ marketing: Accepted, analytics: Accepted });
  expect(second).toEqual(first);
});

test('NotDecided → Accepted and Declined → Accepted issue a new ID; Declined → null', async () => {
  const a = bridge();
  const first = await a.updateConsent({ marketing: Accepted, analytics: Declined });
  expect(first.marketingTrackingId).toBeTruthy();
  expect(first.analyticsTrackingId).toBeNull();
  const revoked = await a.updateConsent({ marketing: Declined, analytics: Declined });
  expect(revoked).toEqual({ marketingTrackingId: null, analyticsTrackingId: null });
  const again = await a.updateConsent({ marketing: Accepted, analytics: Accepted });
  expect(again.marketingTrackingId).not.toBe(first.marketingTrackingId);
  expect(again.analyticsTrackingId).toBeTruthy();
});

test('fields are independent', async () => {
  const a = bridge();
  const first = await a.updateConsent({ marketing: Accepted, analytics: Accepted });
  const second = await a.updateConsent({ marketing: Accepted, analytics: Declined });
  expect(second.marketingTrackingId).toBe(first.marketingTrackingId);
  expect(second.analyticsTrackingId).toBeNull();
});

test('the choice survives a new bridge instance over the same storage', async () => {
  const storage = memoryStorage();
  const saved = await bridge({ storage }).updateConsent({ marketing: Accepted, analytics: Declined });
  const config = await bridge({ storage }).getConfig();
  expect(config).toMatchObject({
    marketingConsentStatus: Accepted,
    analyticsConsentStatus: Declined,
    marketingTrackingId: saved.marketingTrackingId,
    analyticsTrackingId: null,
  });
  expect(storage.data.has(STORAGE_KEY)).toBe(true);
});


test('unreadable storage behaves as nothing stored and keeps the choice in memory', async () => {
  const broken: StorageLike = {
    getItem: () => '{not json',
    setItem: () => {
      throw new Error('quota');
    },
    removeItem: () => {
      throw new Error('quota');
    },
  };
  const a = bridge({ storage: broken });
  const config = await a.getConfig();
  expect(config.marketingConsentStatus).toBe(NotDecided);
  const saved = await a.updateConsent({ marketing: Accepted, analytics: Declined });
  const after = await a.getConfig();
  expect(after.marketingTrackingId).toBe(saved.marketingTrackingId);
});

test('forgetChoice drops the stored choice, so the next start is a first start', async () => {
  const storage = memoryStorage();
  await bridge({ storage }).updateConsent({ marketing: Accepted, analytics: Accepted });
  expect(storage.data.has(STORAGE_KEY)).toBe(true);
  const config = await bridge({ storage, forgetChoice: true }).getConfig();
  expect(config).toMatchObject({
    marketingConsentStatus: NotDecided,
    analyticsConsentStatus: NotDecided,
    marketingTrackingId: null,
    analyticsTrackingId: null,
  });
  expect(storage.data.has(STORAGE_KEY)).toBe(false);
});
