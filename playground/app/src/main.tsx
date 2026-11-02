import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { createFakeIdentityApi } from './api/fakeIdentityApi';
import { createIdentityObserver } from './identity/identityObserver';
import { createIdentityService } from './identity/identityService';
import { createAnalyticsCollectorSubscriber } from './subscribers/analyticsCollector';
import { createGameConfigSubscriber } from './subscribers/gameConfig';
import { createRequestHeadersSubscriber } from './subscribers/requestHeaders';
import './index.css';

// Dev switch: the fake config's consentRequired comes from the URL, default true.
const consentRequired = new URLSearchParams(window.location.search).get('consentRequired') !== 'false';

const api = createFakeIdentityApi({ consentRequired });
const observer = createIdentityObserver();
const service = createIdentityService(api, observer);

const recorders = [createRequestHeadersSubscriber(), createAnalyticsCollectorSubscriber(), createGameConfigSubscriber()];
for (const recorder of recorders) observer.subscribe(recorder.handle);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App observer={observer} service={service} recorders={recorders} />
  </StrictMode>,
);
