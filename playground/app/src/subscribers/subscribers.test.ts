import { ConsentStatus, type IdentityFields } from '../identity/types';
import { createAnalyticsCollectorSubscriber } from './analyticsCollector';
import { createGameConfigSubscriber } from './gameConfig';
import { createRecorder } from './recorder';
import { createRequestHeadersSubscriber } from './requestHeaders';

const required: IdentityFields = {
  marketingTrackingId: 'm-1',
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: ConsentStatus.Accepted,
  analyticsConsentStatus: ConsentStatus.Declined,
};

const notRequired: IdentityFields = {
  ...required,
  consentRequired: false,
  analyticsTrackingId: 'a-1',
  analyticsConsentStatus: ConsentStatus.Accepted,
};

test('with consentRequired = true: IDs, temporaryId and both statuses, never deviceId', () => {
  for (const make of [createAnalyticsCollectorSubscriber, createGameConfigSubscriber]) {
    const sub = make();
    sub.handle(required);
    expect(sub.getSnapshot()?.state).toEqual({
      marketingTrackingId: 'm-1',
      analyticsTrackingId: null,
      temporaryId: 'tmp-1',
      marketingConsentStatus: ConsentStatus.Accepted,
      analyticsConsentStatus: ConsentStatus.Declined,
    });
  }
});

test('with consentRequired = false: IDs, temporaryId and deviceId, no statuses', () => {
  for (const make of [createAnalyticsCollectorSubscriber, createGameConfigSubscriber]) {
    const sub = make();
    sub.handle(notRequired);
    expect(sub.getSnapshot()?.state).toEqual({
      marketingTrackingId: 'm-1',
      analyticsTrackingId: 'a-1',
      temporaryId: 'tmp-1',
      deviceId: 'device-0001',
    });
  }
});

test('request headers: strings, consentRequired included, null header dropped, no deviceId when required', () => {
  const sub = createRequestHeadersSubscriber();
  sub.handle(required);
  expect(sub.getSnapshot()?.state).toEqual({
    'X-Marketing-Tracking-Id': 'm-1',
    'X-Temporary-Id': 'tmp-1',
    'X-Marketing-Consent-Status': '1',
    'X-Analytics-Consent-Status': '0',
    'X-Consent-Required': 'true',
  });
});

test('request headers with consentRequired = false carry deviceId and no statuses', () => {
  const sub = createRequestHeadersSubscriber();
  sub.handle(notRequired);
  expect(sub.getSnapshot()?.state).toEqual({
    'X-Marketing-Tracking-Id': 'm-1',
    'X-Analytics-Tracking-Id': 'a-1',
    'X-Temporary-Id': 'tmp-1',
    'X-Device-Id': 'device-0001',
    'X-Consent-Required': 'false',
  });
});

test('a recorder sets updatedAt on each call and notifies listeners', () => {
  const times = [new Date('2026-11-02T10:00:00Z'), new Date('2026-11-02T10:00:05Z')];
  let i = 0;
  const recorder = createRecorder('Test', (fields) => fields.temporaryId, () => times[i++]);
  const listener = vi.fn();
  recorder.subscribe(listener);
  expect(recorder.getSnapshot()).toBeNull();
  recorder.handle(required);
  expect(recorder.getSnapshot()).toEqual({ state: 'tmp-1', updatedAt: times[0] });
  recorder.handle({ ...required, temporaryId: 'tmp-2' });
  expect(recorder.getSnapshot()).toEqual({ state: 'tmp-2', updatedAt: times[1] });
  expect(listener).toHaveBeenCalledTimes(2);
});
