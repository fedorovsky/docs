import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App, LOAD_ERROR_TEXT } from './App';
import type { IdentityBridge } from './bridge/identityBridge';
import { createIdentityObserver } from './identity/identityObserver';
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

const accepted: IdentityFields = {
  ...undecided,
  consentRequired: false,
  marketingConsentStatus: Accepted,
  analyticsConsentStatus: Accepted,
  marketingTrackingId: 'm-1',
  analyticsTrackingId: 'a-1',
};

/** A fake-like bridge: the config follows the consentRequired the App asked for. */
function setup(bridge: Partial<IdentityBridge> = {}) {
  const observer = createIdentityObserver();
  const recorders = [createRequestHeadersSubscriber(), createAnalyticsCollectorSubscriber(), createGameConfigSubscriber()];
  for (const recorder of recorders) observer.subscribe(recorder.handle);
  const createBridge = vi.fn((consentRequired: boolean, _firstStart: boolean): IdentityBridge => ({
    getConfig: vi.fn().mockResolvedValue(consentRequired ? undecided : { ...accepted, temporaryId: 'tmp-2' }),
    updateConsent: vi.fn(),
    ...bridge,
  }));
  render(<App observer={observer} recorders={recorders} createBridge={createBridge} />);
  return { observer, recorders, createBridge, user: userEvent.setup() };
}

const startButton = () => screen.getByRole('button', { name: 'Start' });
const consentSwitch = () => screen.getByRole('switch', { name: 'consentRequired' });

test('before Start only the start panel is shown, with consentRequired on', () => {
  const { createBridge } = setup();
  expect(consentSwitch()).toBeChecked();
  expect(createBridge).not.toHaveBeenCalled();
  expect(screen.queryByRole('region', { name: 'Config' })).not.toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
  expect(screen.queryByRole('region', { name: 'Request headers' })).not.toBeInTheDocument();
});

test('Start with consentRequired = true and NotDecided: config, both blocks and three monitoring blocks', async () => {
  const { user, createBridge } = setup();
  await user.click(startButton());
  expect(createBridge).toHaveBeenCalledWith(true, false);
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
  const config = screen.getByRole('region', { name: 'Config' });
  expect(config).toHaveTextContent('"deviceId": "device-0001"');
  expect(config).toHaveTextContent('"consentRequired": true');
  expect(config.compareDocumentPosition(screen.getByRole('heading', { name: 'Tracking consent' })) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  const subscribers = screen.getByRole('region', { name: 'Subscribers' });
  expect(subscribers).toHaveTextContent("identity observer's subscribers");
  expect(subscribers).toContainElement(screen.getByRole('region', { name: 'Request headers' }));
  expect(subscribers).toContainElement(screen.getByRole('region', { name: 'Analytics collector' }));
  expect(subscribers).toContainElement(screen.getByRole('region', { name: 'Game config' }));
  expect(screen.getByRole('region', { name: 'Request headers' })).toHaveTextContent('"X-Consent-Required": "true"');
  expect(screen.getByRole('region', { name: 'Analytics collector' })).toHaveTextContent('"marketingTrackingId": null');
  expect(screen.getByRole('region', { name: 'Game config' })).not.toHaveTextContent('deviceId');
});

test('only the settings block once both consents are decided', async () => {
  const { user } = setup({ getConfig: vi.fn().mockResolvedValue({ ...undecided, marketingConsentStatus: Accepted, analyticsConsentStatus: Declined, marketingTrackingId: 'm-1' }) });
  await user.click(startButton());
  expect(await screen.findByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
});

test('Start with the switch off: no consent blocks, monitoring shows both IDs and deviceId', async () => {
  const { user, createBridge } = setup();
  await user.click(consentSwitch());
  await user.click(startButton());
  expect(createBridge).toHaveBeenCalledWith(false, false);
  const headers = await screen.findByRole('region', { name: 'Request headers' });
  expect(headers).toHaveTextContent('"X-Device-Id": "device-0001"');
  expect(headers).toHaveTextContent('"X-Analytics-Tracking-Id": "a-1"');
  expect(headers).not.toHaveTextContent('Consent-Status');
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking settings' })).not.toBeInTheDocument();
});

test('Start again in the other mode switches the page without a reload', async () => {
  const { user, createBridge } = setup();
  await user.click(consentSwitch());
  await user.click(startButton());
  await screen.findByRole('region', { name: 'Request headers' });
  expect(screen.queryByRole('heading', { name: 'Tracking settings' })).not.toBeInTheDocument();
  await user.click(consentSwitch());
  await user.click(startButton());
  expect(await screen.findByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
  expect(createBridge).toHaveBeenNthCalledWith(2, true, false);
  expect(screen.getByRole('region', { name: 'Config' })).toHaveTextContent('"consentRequired": true');
});

test('the Start button and the switch are disabled while a start is pending', async () => {
  let resolve!: (fields: IdentityFields) => void;
  const { user } = setup({ getConfig: vi.fn(() => new Promise<IdentityFields>((r) => (resolve = r))) });
  await user.click(startButton());
  expect(startButton()).toBeDisabled();
  expect(consentSwitch()).toBeDisabled();
  resolve(undecided);
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
  expect(startButton()).toBeEnabled();
});

test('a save in the initial block hides it and updates the monitoring', async () => {
  const { user } = setup({ updateConsent: vi.fn().mockResolvedValue({ marketingTrackingId: 'm-1', analyticsTrackingId: 'a-1' }) });
  await user.click(startButton());
  await screen.findByRole('heading', { name: 'Tracking consent' });
  await user.click(screen.getAllByRole('button', { name: 'Accept all' })[0]);
  expect(await screen.findByText(/"X-Marketing-Tracking-Id": "m-1"/)).toBeInTheDocument();
  expect(screen.queryByRole('heading', { name: 'Tracking consent' })).not.toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Tracking settings' })).toBeInTheDocument();
});

test('a failed start shows the error and Retry loads again', async () => {
  const getConfig = vi.fn().mockRejectedValueOnce(new Error('Fake bridge error')).mockResolvedValue(undecided);
  const { user } = setup({ getConfig });
  await user.click(startButton());
  expect(await screen.findByRole('alert')).toHaveTextContent(LOAD_ERROR_TEXT);
  expect(screen.queryByRole('region', { name: 'Request headers' })).not.toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Retry' }));
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

test('the first start switch is off by default and is passed to createBridge', async () => {
  const { user, createBridge } = setup();
  const firstStart = screen.getByRole('switch', { name: 'first start' });
  expect(firstStart).not.toBeChecked();
  await user.click(firstStart);
  await user.click(startButton());
  expect(createBridge).toHaveBeenCalledWith(true, true);
  expect(await screen.findByRole('heading', { name: 'Tracking consent' })).toBeInTheDocument();
});
