import { createIdentityObserver } from './identityObserver';
import { ConsentStatus, type IdentityFields } from './types';

const base: IdentityFields = {
  marketingTrackingId: null,
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: ConsentStatus.NotDecided,
  analyticsConsentStatus: ConsentStatus.NotDecided,
};

test('calls subscribers on the first set', () => {
  const observer = createIdentityObserver();
  const fn = vi.fn();
  observer.subscribe(fn);
  observer.set(base);
  expect(fn).toHaveBeenCalledTimes(1);
  expect(fn).toHaveBeenCalledWith(base);
  expect(observer.get()).toEqual(base);
});

test('calls subscribers when a field changed', () => {
  const observer = createIdentityObserver();
  const fn = vi.fn();
  observer.subscribe(fn);
  observer.set(base);
  observer.set({ ...base, marketingConsentStatus: ConsentStatus.Accepted, marketingTrackingId: 'm-1' });
  expect(fn).toHaveBeenCalledTimes(2);
  expect(fn.mock.calls[1][0].marketingTrackingId).toBe('m-1');
});

test('does not call subscribers on an identical set', () => {
  const observer = createIdentityObserver();
  const fn = vi.fn();
  observer.subscribe(fn);
  observer.set(base);
  observer.set({ ...base });
  expect(fn).toHaveBeenCalledTimes(1);
});

test('calls a late subscriber at once with the current fields', () => {
  const observer = createIdentityObserver();
  observer.set(base);
  const fn = vi.fn();
  observer.subscribe(fn);
  expect(fn).toHaveBeenCalledTimes(1);
  expect(fn).toHaveBeenCalledWith(base);
});

test('does not call a subscriber before the first set, and stops after unsubscribe', () => {
  const observer = createIdentityObserver();
  const fn = vi.fn();
  const unsubscribe = observer.subscribe(fn);
  expect(fn).not.toHaveBeenCalled();
  unsubscribe();
  observer.set(base);
  expect(fn).not.toHaveBeenCalled();
});
