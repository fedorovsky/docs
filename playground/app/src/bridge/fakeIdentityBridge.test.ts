import { ConsentStatus } from '../identity/types';
import { createFakeIdentityBridge, DEVICE_ID, STORAGE_KEY, type StorageLike } from './fakeIdentityBridge';

function memoryStorage(): StorageLike & { data: Map<string, string> } {
  const data = new Map<string, string>();
  return {
    data,
    getItem: (key) => data.get(key) ?? null,
    setItem: (key, value) => void data.set(key, value),
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

test('consentRequired = false: both Accepted, IDs issued once and kept', async () => {
  const storage = memoryStorage();
  const a = bridge({ consentRequired: false, storage });
  const first = await a.getConfig();
  expect(first).toMatchObject({ marketingConsentStatus: Accepted, analyticsConsentStatus: Accepted, consentRequired: false });
  expect(first.marketingTrackingId).toBeTruthy();
  expect(first.analyticsTrackingId).toBeTruthy();
  const second = await a.getConfig();
  expect(second.marketingTrackingId).toBe(first.marketingTrackingId);
  expect(second.analyticsTrackingId).toBe(first.analyticsTrackingId);
});

test('consentRequired = false ignores a stored Declined choice', async () => {
  const storage = memoryStorage();
  const trueMode = bridge({ storage });
  await trueMode.updateConsent({ marketing: Declined, analytics: Accepted });
  const falseMode = bridge({ consentRequired: false, storage });
  const config = await falseMode.getConfig();
  expect(config.marketingConsentStatus).toBe(Accepted);
  expect(config.marketingTrackingId).toBeTruthy();
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
  };
  const a = bridge({ storage: broken });
  const config = await a.getConfig();
  expect(config.marketingConsentStatus).toBe(NotDecided);
  const saved = await a.updateConsent({ marketing: Accepted, analytics: Declined });
  const after = await a.getConfig();
  expect(after.marketingTrackingId).toBe(saved.marketingTrackingId);
});
