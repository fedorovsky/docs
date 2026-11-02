import { act, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createIdentityObserver } from '../identity/identityObserver';
import type { IdentityService } from '../identity/identityService';
import { ConsentStatus, type IdentityFields } from '../identity/types';
import { ConsentBlock, isConsentBlockVisible, SAVE_ERROR_TEXT } from './ConsentBlock';

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

function setup(fields: IdentityFields | null, variant: 'initial' | 'settings' = 'initial', saveConsent = vi.fn().mockResolvedValue(undefined)) {
  const observer = createIdentityObserver();
  if (fields) observer.set(fields);
  const service: IdentityService = { start: vi.fn(), saveConsent };
  render(<ConsentBlock variant={variant} observer={observer} service={service} />);
  return { observer, saveConsent };
}

test('visibility rules', () => {
  const decided = { ...undecided, marketingConsentStatus: Accepted, analyticsConsentStatus: Declined };
  expect(isConsentBlockVisible('initial', null)).toBe(false);
  expect(isConsentBlockVisible('initial', undecided)).toBe(true);
  expect(isConsentBlockVisible('initial', { ...undecided, marketingConsentStatus: Accepted })).toBe(true);
  expect(isConsentBlockVisible('initial', decided)).toBe(false);
  expect(isConsentBlockVisible('settings', decided)).toBe(true);
  expect(isConsentBlockVisible('settings', { ...decided, consentRequired: false })).toBe(false);
  expect(isConsentBlockVisible('initial', { ...undecided, consentRequired: false })).toBe(false);
});

test('renders nothing when not visible', () => {
  setup({ ...undecided, consentRequired: false });
  expect(screen.queryByRole('button', { name: 'Save' })).not.toBeInTheDocument();
});

test('NotDecided shows as off; an off toggle saves Declined, an on toggle Accepted', async () => {
  const user = userEvent.setup();
  const { saveConsent } = setup(undecided);
  const marketing = screen.getByRole('switch', { name: 'Marketing' });
  const analytics = screen.getByRole('switch', { name: 'Analytics' });
  expect(marketing).not.toBeChecked();
  expect(analytics).not.toBeChecked();
  await user.click(marketing);
  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(saveConsent).toHaveBeenCalledWith({ marketing: Accepted, analytics: Declined });
});

test('Accept all sends both Accepted regardless of the toggles and turns them on', async () => {
  const user = userEvent.setup();
  const { saveConsent } = setup({ ...undecided, marketingConsentStatus: Accepted, analyticsConsentStatus: Accepted }, 'settings');
  await user.click(screen.getByRole('switch', { name: 'Marketing' }));
  expect(screen.getByRole('switch', { name: 'Marketing' })).not.toBeChecked();
  await user.click(screen.getByRole('button', { name: 'Accept all' }));
  expect(saveConsent).toHaveBeenCalledWith({ marketing: Accepted, analytics: Accepted });
  expect(await screen.findByRole('switch', { name: 'Marketing' })).toBeChecked();
});

test('settings block shows current statuses and revokes with an off toggle', async () => {
  const user = userEvent.setup();
  const { saveConsent } = setup({ ...undecided, marketingConsentStatus: Accepted, analyticsConsentStatus: Accepted }, 'settings');
  const marketing = screen.getByRole('switch', { name: 'Marketing' });
  expect(marketing).toBeChecked();
  await user.click(marketing);
  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(saveConsent).toHaveBeenCalledWith({ marketing: Declined, analytics: Accepted });
});

test('buttons and toggles are disabled while a call is pending', async () => {
  const user = userEvent.setup();
  let resolve!: () => void;
  const saveConsent = vi.fn(() => new Promise<void>((r) => (resolve = r)));
  setup(undecided, 'initial', saveConsent);
  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Accept all' })).toBeDisabled();
  expect(screen.getByRole('switch', { name: 'Marketing' })).toBeDisabled();
  resolve();
  expect(await screen.findByRole('button', { name: 'Save' })).toBeEnabled();
});

test('a failed save shows the error and keeps the toggles as the user left them', async () => {
  const user = userEvent.setup();
  setup(undecided, 'initial', vi.fn().mockRejectedValue(new Error('Fake backend error')));
  await user.click(screen.getByRole('switch', { name: 'Analytics' }));
  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(await screen.findByRole('alert')).toHaveTextContent(SAVE_ERROR_TEXT);
  expect(screen.getByRole('switch', { name: 'Analytics' })).toBeChecked();
  expect(screen.getByRole('switch', { name: 'Marketing' })).not.toBeChecked();
  expect(screen.getByRole('button', { name: 'Save' })).toBeEnabled();
});

test('re-reads the toggles when the observer changes', () => {
  const { observer } = setup(undecided, 'settings');
  const block = screen.getByTestId('consent-settings');
  expect(within(block).getByRole('switch', { name: 'Marketing' })).not.toBeChecked();
  act(() => observer.set({ ...undecided, marketingConsentStatus: Accepted, marketingTrackingId: 'm-1' }));
  expect(within(block).getByRole('switch', { name: 'Marketing' })).toBeChecked();
});
