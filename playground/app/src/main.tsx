import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { createFakeIdentityApi } from './api/fakeIdentityApi';
import { createIdentityObserver } from './identity/identityObserver';
import { createAnalyticsCollectorSubscriber } from './subscribers/analyticsCollector';
import { createGameConfigSubscriber } from './subscribers/gameConfig';
import { createRequestHeadersSubscriber } from './subscribers/requestHeaders';
import './index.css';

const observer = createIdentityObserver();
const recorders = [createRequestHeadersSubscriber(), createAnalyticsCollectorSubscriber(), createGameConfigSubscriber()];
for (const recorder of recorders) observer.subscribe(recorder.handle);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App observer={observer} recorders={recorders} createApi={(consentRequired) => createFakeIdentityApi({ consentRequired })} />
  </StrictMode>,
);
