import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App, LOAD_ERROR_TEXT } from './App';
import type { IdentityApi } from './api/identityApi';
import { createIdentityObserver } from './identity/identityObserver';
import { createIdentityService } from './identity/identityService';
import { ConsentStatus, type IdentityFields } from './identity/types';
import { createAnalyticsCollectorSubscriber } from './subscribers/analyticsCollector';
import { createGameConfigSubscriber } from './subscribers/gameConfig';
import { createRequestHeadersSubscriber } from './subscribers/requestHeaders';

const { Accepted, Declined, NotDecided } = ConsentStatus;

const undecided: IdentityFields = {
  marketingTrackingId: null,
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: NotDecided,
  analyticsConsentStatus: NotDecided,
};

function setup(api: Partial<IdentityApi>) {
  const observer = createIdentityObserver();
  const service = createIdentityService({ getConfig: vi.fn().mockResolvedValue(undecided), updateConsent: vi.fn(), ...api }, observer);
  const recorders = [createRequestHeadersSubscriber(), createAnalyticsCollectorSubscriber(), createGameConfigSubscriber()];
  for (const recorder of recorders) observer.subscribe(recorder.handle);
  render(<App observer={observer} service={service} recorders={recorders} />);
  return { observer, recorders };
}

test('consentRequired = true with NotDecided: both blocks and three monitoring blocks', async () => {
  setup({});
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
  expect(screen.getByRole('region', { name: 'Request headers' })).toHaveTextContent('"X-Consent-Required": "true"');
  expect(screen.getByRole('region', { name: 'Analytics collector' })).toHaveTextContent('"marketingTrackingId": null');
  expect(screen.getByRole('region', { name: 'Game config' })).not.toHaveTextContent('deviceId');
});

test('only the settings block once both consents are decided', async () => {
  setup({ getConfig: vi.fn().mockResolvedValue({ ...undecided, marketingConsentStatus: Accepted, analyticsConsentStatus: Declined, marketingTrackingId: 'm-1' }) });
  expect(await screen.findByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
});

test('consentRequired = false: no consent blocks, monitoring shows both IDs and deviceId', async () => {
  setup({
    getConfig: vi.fn().mockResolvedValue({
      ...undecided,
      consentRequired: false,
      marketingConsentStatus: Accepted,
      analyticsConsentStatus: Accepted,
      marketingTrackingId: 'm-1',
      analyticsTrackingId: 'a-1',
    }),
  });
  const headers = await screen.findByRole('region', { name: 'Request headers' });
  expect(headers).toHaveTextContent('"X-Device-Id": "device-0001"');
  expect(headers).toHaveTextContent('"X-Analytics-Tracking-Id": "a-1"');
  expect(headers).not.toHaveTextContent('Consent-Status');
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking settings' })).not.toBeInTheDocument();
});

test('a save in the initial block hides it and updates the monitoring', async () => {
  const user = userEvent.setup();
  setup({ updateConsent: vi.fn().mockResolvedValue({ marketingTrackingId: 'm-1', analyticsTrackingId: 'a-1' }) });
  await screen.findByRole('heading', { name: 'Tracking consent' });
  await user.click(screen.getAllByRole('button', { name: 'Accept all' })[0]);
  expect(await screen.findByText(/"X-Marketing-Tracking-Id": "m-1"/)).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
});

test('a failed start shows the error and Retry loads again', async () => {
  const user = userEvent.setup();
  const getConfig = vi.fn().mockRejectedValueOnce(new Error('Fake backend error')).mockResolvedValue(undecided);
  setup({ getConfig });
  expect(await screen.findByRole('alert')).toHaveTextContent(LOAD_ERROR_TEXT);
  expect(screen.queryByRole('region', { name: 'Request headers' })).not.toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Retry' }));
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
});
