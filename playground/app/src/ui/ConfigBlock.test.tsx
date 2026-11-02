import { act, render, screen } from '@testing-library/react';
import { createIdentityObserver } from '../identity/identityObserver';
import { ConsentStatus, type IdentityFields } from '../identity/types';
import { ConfigBlock } from './ConfigBlock';

const fields: IdentityFields = {
  marketingTrackingId: null,
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: ConsentStatus.NotDecided,
  analyticsConsentStatus: ConsentStatus.NotDecided,
};

test('shows all seven fields after start and the new values after a change', () => {
  const observer = createIdentityObserver();
  render(<ConfigBlock observer={observer} />);
  expect(screen.queryByRole('region', { name: 'Config' })).not.toBeInTheDocument();

  act(() => observer.set(fields));
  const block = screen.getByRole('region', { name: 'Config' });
  for (const key of Object.keys(fields)) expect(block).toHaveTextContent(`"${key}":`);
  expect(block).toHaveTextContent('"deviceId": "device-0001"');
  expect(block).toHaveTextContent('"marketingConsentStatus": 2');

  act(() => observer.set({ ...fields, marketingConsentStatus: ConsentStatus.Accepted, marketingTrackingId: 'm-1' }));
  expect(block).toHaveTextContent('"marketingTrackingId": "m-1"');
  expect(block).toHaveTextContent('"marketingConsentStatus": 1');
});
