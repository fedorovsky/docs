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

Delivers the identity flow of the [Spec](./spec.md): scaffold, fake API, observer, subscribers and UI components first; the page that shows them comes last, so nothing is reachable before it is tested.

## Tasks

- [x] **T1. Scaffold the app**
  - Covers: `setup`
  - Files: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`, `src/App.tsx`
  - Change: create the Vite + React + TypeScript app with Vitest and Testing Library in `playground/app/`, rendering an empty page (Spec *Context & current state*)
  - Done when: `npm run build` and `npm test` pass
  - Depends on: —
- [x] **T2. Add the identity types and observer**
  - Covers: R8
  - Files: `src/identity/types.ts`, `src/identity/identityObserver.ts`, `src/identity/identityObserver.test.ts`
  - Change: `ConsentStatus`, `IdentityFields`, `ConsentRequest`, `ConsentResponse` and `createIdentityObserver` as in Spec *Components & changes*
  - Done when: tests show subscribers called on the first `set`, on a changed field, not on an identical `set`, and a late subscriber called at once
  - Depends on: T1
- [x] **T3. Implement the fake identity bridge**
  - Covers: R1, R2, R6, R11
  - Files: `src/bridge/identityBridge.ts`, `src/bridge/fakeIdentityBridge.ts`, `src/bridge/fakeIdentityBridge.test.ts`
  - Change: `IdentityBridge` and `createFakeIdentityBridge` with delay, error rate, storage and the ID rules (Spec *API / interfaces*)
  - Done when: tests cover the first start in both `consentRequired` modes, the same ID on Accepted → Accepted, a new ID after Declined or NotDecided, `null` on Declined, a failing call storing nothing, and a fresh `temporaryId` per call
  - Depends on: T2
- [x] **T4. Implement the identity service**
  - Covers: R7, R8
  - Files: `src/identity/identityService.ts`, `src/identity/identityService.test.ts`
  - Change: `start()` and `saveConsent()` as in Spec *Components & changes*
  - Done when: tests show `start()` sets the observer, a successful save merges statuses and IDs into the observer, and a failed save rejects and leaves the observer untouched
  - Depends on: T3
- [x] **T5. Add the three recording subscribers**
  - Covers: R9
  - Files: `src/subscribers/recorder.ts`, `src/subscribers/requestHeaders.ts`, `src/subscribers/analyticsCollector.ts`, `src/subscribers/gameConfig.ts`, `src/subscribers/subscribers.test.ts`
  - Change: `createRecorder` and the three projections of Spec *Subscriber fields*
  - Done when: tests show the field sets for both `consentRequired` modes, no `deviceId` when `true`, `null` headers dropped, `null` kept by the other two, and `updatedAt` set on each call
  - Depends on: T2
- [x] **T6. Build the consent block**
  - Covers: R3, R4, R5, R7
  - Files: `src/ui/ConsentBlock.tsx`, `src/ui/ConsentBlock.test.tsx`
  - Change: the component with both variants, toggles, "Save", "Accept all", pending and error state (Spec *Visibility and UI behaviour*); not rendered by `App` yet
  - Done when: tests show an off toggle saves `Declined`, "Accept all" sends both `Accepted`, buttons disabled while pending, and the error text on failure with the toggles kept
  - Depends on: T4
- [x] **T7. Build the monitoring block**
  - Covers: R10
  - Files: `src/ui/MonitoringBlock.tsx`, `src/ui/MonitoringBlock.test.tsx`
  - Change: render a recorder's state as JSON with its update time through `useSyncExternalStore` (Spec *Components & changes*); not rendered by `App` yet
  - Done when: a test shows the block re-renders with the new state and time after the recorder is called
  - Depends on: T5
- [x] **T8. Wire the page**
  - Covers: R1, R2, R3, R4, R8, R10
  - Files: `src/main.tsx`, `src/App.tsx`, `src/App.test.tsx`
  - Change: create the fake bridge from the `?consentRequired` query, the observer, the service and the recorders; `App` shows loading, the error with "Retry", the two blocks by their visibility rules and the three monitoring blocks (Spec *Components & changes*). This is the feature's entry point, added last.
  - Done when: `App` tests show both blocks with `consentRequired = true` and NotDecided, only settings once both are decided, none with `false`; the page runs in the browser
  - Depends on: T6, T7
- [x] **T9. Walk through the acceptance criteria**
  - Covers: `verify`
  - Files: `playground/app/` in the browser with `?consentRequired=true` and `?consentRequired=false`
  - Change: run the PRD acceptance criteria of R1–R11 by hand, including a failed save, a revoke-and-accept cycle and a reload
  - Done when: every criterion passes and the monitoring times change only when a field changed
  - Depends on: T8
- [x] **T13. Replace the URL switch with a manual start panel**
  - Covers: R12
  - Files: `src/ui/StartPanel.tsx`, `src/App.tsx`, `src/App.test.tsx`, `src/main.tsx`
  - Change: the start panel with the `consentRequired` switch and "Start"; `App` creates the fake bridge and service per "Start" (Spec *Components & changes*)
  - Done when: `App` tests show only the panel before "Start", both modes, a restart in the other mode and a failed start with "Retry"; in the browser the mode switches without a reload
  - Depends on: T12
- [ ] **T10. Apply the final design and copy**
  - Covers: R3, R4, R10
  - Files: `src/ui/ConsentBlock.tsx`, `src/ui/MonitoringBlock.tsx`, `src/App.tsx`
  - Change: replace the provisional layout and English text with the final design (Spec *Visibility and UI behaviour*)
  - Done when: the blocks match the mockups and the agreed copy; the T6–T8 tests still pass
  - Depends on: T9
  - Blocked by: PRD Q4
- [ ] **T11. Release**
  - Covers: `rollout`
  - Files: deploy pipeline (Spec Q2)
  - Change: deploy the app build (Spec *Rollout & rollback*)
  - Done when: the deployed app passes the T9 walkthrough in both modes
  - Depends on: T10
  - Blocked by: Spec Q2
- [x] **T12. Add the config block**
  - Covers: R10
  - Files: `src/ui/ConfigBlock.tsx`, `src/ui/ConfigBlock.test.tsx`, `src/App.tsx`, `src/App.test.tsx`
  - Change: a block at the top of the page with the observer's current seven fields as JSON (Spec *Components & changes*)
  - Done when: tests show all seven fields after start and the new values after a save; the block is visible in the browser above the consent blocks
  - Depends on: T8
- [x] **T13. Replace the URL switch with a manual start panel**
  - Covers: R12
  - Files: `src/ui/StartPanel.tsx`, `src/App.tsx`, `src/App.test.tsx`, `src/main.tsx`
  - Change: the start panel with the `consentRequired` switch and "Start"; `App` creates the fake bridge and service per "Start" (Spec *Components & changes*)
  - Done when: `App` tests show only the panel before "Start", both modes, a restart in the other mode and a failed start with "Retry"; in the browser the mode switches without a reload
  - Depends on: T12
