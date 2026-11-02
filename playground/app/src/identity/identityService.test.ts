import type { IdentityApi } from '../api/identityApi';
import { createIdentityObserver } from './identityObserver';
import { createIdentityService } from './identityService';
import { ConsentStatus, type IdentityFields } from './types';

const config: IdentityFields = {
  marketingTrackingId: null,
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: ConsentStatus.NotDecided,
  analyticsConsentStatus: ConsentStatus.NotDecided,
};

function setup(api: Partial<IdentityApi>) {
  const observer = createIdentityObserver();
  const subscriber = vi.fn();
  observer.subscribe(subscriber);
  const service = createIdentityService(
    { getConfig: vi.fn().mockResolvedValue(config), updateConsent: vi.fn(), ...api },
    observer,
  );
  return { observer, subscriber, service };
}

test('start() loads the config into the observer', async () => {
  const { observer, subscriber, service } = setup({});
  await service.start();
  expect(observer.get()).toEqual(config);
  expect(subscriber).toHaveBeenCalledTimes(1);
});

test('a failed start() rejects and leaves the observer empty', async () => {
  const { observer, subscriber, service } = setup({ getConfig: vi.fn().mockRejectedValue(new Error('down')) });
  await expect(service.start()).rejects.toThrow('down');
  expect(observer.get()).toBeNull();
  expect(subscriber).not.toHaveBeenCalled();
});

test('a successful save merges statuses from the request and IDs from the response', async () => {
  const updateConsent = vi.fn().mockResolvedValue({ marketingTrackingId: 'm-1', analyticsTrackingId: null });
  const { observer, subscriber, service } = setup({ updateConsent });
  await service.start();
  await service.saveConsent({ marketing: ConsentStatus.Accepted, analytics: ConsentStatus.Declined });
  expect(updateConsent).toHaveBeenCalledWith({ marketing: ConsentStatus.Accepted, analytics: ConsentStatus.Declined });
  expect(observer.get()).toEqual({
    ...config,
    marketingConsentStatus: ConsentStatus.Accepted,
    analyticsConsentStatus: ConsentStatus.Declined,
    marketingTrackingId: 'm-1',
    analyticsTrackingId: null,
  });
  expect(subscriber).toHaveBeenCalledTimes(2);
});

test('a failed save rejects and leaves the observer untouched', async () => {
  const { observer, subscriber, service } = setup({ updateConsent: vi.fn().mockRejectedValue(new Error('Fake backend error')) });
  await service.start();
  await expect(service.saveConsent({ marketing: ConsentStatus.Accepted, analytics: ConsentStatus.Accepted })).rejects.toThrow();
  expect(observer.get()).toEqual(config);
  expect(subscriber).toHaveBeenCalledTimes(1);
});

test('saving before start() rejects', async () => {
  const { service } = setup({});
  await expect(service.saveConsent({ marketing: ConsentStatus.Accepted, analytics: ConsentStatus.Accepted })).rejects.toThrow();
});
