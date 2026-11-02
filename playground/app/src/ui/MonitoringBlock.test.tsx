import { act, render, screen } from '@testing-library/react';
import { ConsentStatus, type IdentityFields } from '../identity/types';
import { createRecorder } from '../subscribers/recorder';
import { MonitoringBlock } from './MonitoringBlock';

const fields: IdentityFields = {
  marketingTrackingId: 'm-1',
  analyticsTrackingId: null,
  deviceId: 'device-0001',
  temporaryId: 'tmp-1',
  consentRequired: true,
  marketingConsentStatus: ConsentStatus.Accepted,
  analyticsConsentStatus: ConsentStatus.Declined,
};

test('re-renders with the new state and time after the recorder is called', () => {
  const times = [new Date('2026-11-02T10:00:00'), new Date('2026-11-02T10:00:05')];
  let i = 0;
  const recorder = createRecorder('Game config', (f) => ({ temporaryId: f.temporaryId, analyticsTrackingId: f.analyticsTrackingId }), () => times[i++]);
  render(<MonitoringBlock recorder={recorder} />);
  expect(screen.getByRole('region', { name: 'Game config' })).toHaveTextContent('No update yet');

  act(() => recorder.handle(fields));
  expect(screen.getByText(/"temporaryId": "tmp-1"/)).toBeInTheDocument();
  expect(screen.getByText(/"analyticsTrackingId": null/)).toBeInTheDocument();
  expect(screen.getByRole('time')).toHaveAttribute('dateTime', times[0].toISOString());

  act(() => recorder.handle({ ...fields, temporaryId: 'tmp-2' }));
  expect(screen.getByText(/"temporaryId": "tmp-2"/)).toBeInTheDocument();
  expect(screen.getByRole('time')).toHaveAttribute('dateTime', times[1].toISOString());
});
