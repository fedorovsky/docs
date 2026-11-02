---
type: tasks
title: User identity and tracking consent
feature: identity-tracking-consent
lang: en
mirror: ../ru/tasks.md
status: draft
owner: TBD
created: 2026-11-02
updated: 2026-11-02
prd: ./prd.md
spec: ./spec.md
links: [TRACK-12]
---

# User identity and tracking consent — Tasks

Delivers the identity observer, the fake backend, the three recording subscribers, the consent block and the monitoring blocks from the [Spec](./spec.md). The blocks are mounted on the page in T9, after the internals are tested.

## Tasks

- [ ] **T1. Scaffold the app**
  - Covers: `setup`
  - Files: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`, `src/App.tsx`
  - Change: create the React + Vite + TypeScript app with Vitest, React Testing Library and jsdom (Spec *Testing plan*); `App` renders an empty page.
  - Done when: `npm run build` and `npm test` pass
  - Depends on: —
- [ ] **T2. Add the identity types and the fake config method**
  - Covers: R1, R13
  - Files: `src/identity/types.ts`, `src/api/identityApi.ts`, `src/api/fake/latency.ts`, `src/api/fake/fakeIdentityApi.ts`, `src/api/fake/fakeIdentityApi.test.ts`
  - Change: add the types and `IdentityApi` from Spec *API / interfaces*, and `getConfig()` with the `localStorage` record, both `consentRequired` modes and `withLatency` (Spec *Data model*).
  - Done when: tests pass for a constant `deviceId`, a new `temporaryId` per call, tracking IDs only for `Accepted`, both `Accepted` with IDs when `consentRequired` is `false`, a rejection at error rate `1` and the configured delay
  - Depends on: T1
- [ ] **T3. Add the fake consent method**
  - Covers: R4, R6, R7, R13
  - Files: `src/api/fake/fakeIdentityApi.ts`, `src/api/fake/fakeIdentityApi.test.ts`
  - Change: add `updateConsent(request)` that saves each field present and returns both tracking IDs, as in Spec *Data model*.
  - Done when: tests pass for `Accepted` giving an ID, `Declined` giving `null`, a new ID after a re-grant, the same ID when accepted again, `NotDecided` rejected, a new instance on the same storage returning the saved choice, a failure leaving the record unchanged and invalid JSON in storage
  - Depends on: T2
- [ ] **T4. Add the identity observer**
  - Covers: R8
  - Files: `src/identity/identityObserver.ts`, `src/identity/identityObserver.test.ts`
  - Change: observer that calls every subscriber with all fields on the first `set` and on any field change, as in Spec *Components & changes*.
  - Done when: tests pass for the first call, all subscribers called on any change, no call without a change, a late subscriber getting the current fields and a throwing subscriber not stopping the others
  - Depends on: T2
- [ ] **T5. Add the three recording subscribers**
  - Covers: R9, R10, R11
  - Files: `src/identity/subscribers/recorder.ts`, `src/identity/subscribers/requestHeaders.ts`, `src/identity/subscribers/analyticsCollector.ts`, `src/identity/subscribers/gameConfig.ts`, `src/identity/subscribers/subscribers.test.ts`
  - Change: `createRecordingSubscriber(map)` and the three subscribers with the provisional header and field names from Spec *Components & changes*.
  - Done when: tests pass for a `null` field having no header, `null` kept in the analytics collector and the game config, and `updatedAt` set on every call
  - Depends on: T4
- [ ] **T6. Add the identity service**
  - Covers: R1, R4, R5, R6
  - Files: `src/identity/identityService.ts`, `src/identity/identityService.test.ts`
  - Change: `createIdentityService(api, observer)` with `start()`, `save()`, `acceptAll()` and the state from Spec *API / interfaces*, with the failure handling from Spec *Edge cases & error handling*.
  - Done when: tests with a stub `IdentityApi` pass for loading, a config error and retry, `save()`, `acceptAll()`, a save error that changes nothing and a second call ignored while saving
  - Depends on: T3, T4
- [ ] **T7. Build the consent block**
  - Covers: R3, R4, R5, R6
  - Files: `src/features/consent/useIdentityState.ts`, `src/features/consent/ConsentBlock.tsx`, `src/features/consent/ConsentBlock.test.tsx`
  - Change: hook over `identityService` and the block with two toggles, "Save" and "Accept all" and provisional text (Spec *Components & changes*); not mounted on the page yet.
  - Done when: component tests pass for toggles matching the statuses, `NotDecided` shown as off, "Save" and "Accept all" calling the service, controls disabled with "Saving…" and the save error message
  - Depends on: T6
- [ ] **T8. Build the monitoring blocks**
  - Covers: R12
  - Files: `src/features/monitoring/MonitoringPanel.tsx`, `src/features/monitoring/SubscriberMonitor.tsx`, `src/features/monitoring/MonitoringPanel.test.tsx`
  - Change: three blocks showing each recorder's values and "Last updated" or "Not updated yet" (Spec *Components & changes*); not mounted on the page yet.
  - Done when: component tests pass for "Not updated yet" before the first call and for new values and a new time after a call
  - Depends on: T5
- [ ] **T9. Wire identity into the app and mount the blocks**
  - Covers: R2, R7, R8, R12
  - Files: `src/identity/bootstrap.ts`, `src/pages/HomePage.tsx`, `src/App.tsx`, `src/main.tsx`, `src/App.test.tsx`
  - Change: `bootstrap.ts` subscribes the recorders before `start()`, `main.tsx` calls `start()` once, and `HomePage` shows loading, the config error with "Retry", the consent block and the monitoring blocks (Spec *Components & changes*); this is the feature's entry point, added last (Spec *Rollout & rollback*).
  - Done when: `src/App.test.tsx` passes with the fake at zero delay and zero error rate for R2–R12 in both `consentRequired` modes, and rendering again with the same storage shows the saved choice
  - Depends on: T7, T8
- [ ] **T10. Check the acceptance criteria by hand**
  - Covers: `verify`
  - Files: local dev server (`npm run dev`)
  - Change: go through every PRD acceptance criterion with the default fake and with `VITE_FAKE_CONSENT_REQUIRED=false` (Spec *Testing plan*).
  - Done when: every criterion holds, including a visible delay and at least one failed save that shows the error and changes nothing
  - Depends on: T9
- [ ] **T11. Release**
  - Covers: `rollout`
  - Files: the app's deploy target (Spec Q4)
  - Change: deploy the build as in Spec *Rollout & rollback*.
  - Done when: the deployed app shows the consent block, and giving and revoking each consent updates all three monitoring blocks without a reload
  - Depends on: T10
  - Blocked by: Spec Q4
- [ ] **T12. Apply the final design and UI text**
  - Covers: R2, R3, R12
  - Files: `src/features/consent/ConsentBlock.tsx`, `src/features/monitoring/MonitoringPanel.tsx`, `src/features/monitoring/SubscriberMonitor.tsx`, `src/pages/HomePage.tsx`
  - Change: replace the provisional layout and text with the mockups and final copy (Spec *Components & changes*).
  - Done when: the page matches the mockups and the updated component tests and `src/App.test.tsx` pass
  - Depends on: T9
  - Blocked by: PRD Q11
