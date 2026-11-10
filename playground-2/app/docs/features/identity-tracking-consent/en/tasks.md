---
type: tasks
title: User identity and tracking consent
feature: identity-tracking-consent
lang: en
mirror: ../uk/tasks.md
status: draft
owner: TBD
reviewers: []
created: 2026-11-10
updated: 2026-11-10
prd: ./prd.md
spec: ./spec.md
links: ["Jira: TRACK-12"]
---

# User identity and tracking consent — Tasks

Delivers the identity flow, the two consent blocks and the debug monitoring from the [Spec](./spec.md), against the fake bridge. The page is assembled last, so nothing is reachable before its parts are built and tested.

## Tasks

- [ ] **T1. Scaffold the app**
  - Covers: `setup`
  - Files: `package.json`, `vite.config.ts`, `tsconfig.json`, `.gitignore`, `index.html`, `src/main.tsx`, `src/App.tsx`
  - Change: create the Vite + React + TypeScript app with an empty page and the scripts `dev` and `build` (Spec *Components & changes*)
  - Done when: `npm run build` passes and `npm run dev` serves an empty page
  - Depends on: —
- [ ] **T2. Add the test setup**
  - Covers: `setup`
  - Files: `package.json`, `vite.config.ts`, `tsconfig.json`, `src/test/setup.ts`, `src/App.test.tsx`
  - Change: add Vitest with jsdom and Testing Library and the `test` script, with one smoke test of the empty page (Spec *Testing plan*)
  - Done when: `npm test` passes
  - Depends on: T1
- [ ] **T3. Add the identity types and the fake config method**
  - Covers: R1, R2, R7
  - Files: `src/identity/types.ts`, `src/bridge/identityBridge.ts`, `src/bridge/fakeIdentityBridge.ts`, `src/bridge/fakeIdentityBridge.test.ts`
  - Change: define the types and the `IdentityBridge` interface, and implement `getConfig()` and `setScenario()` in the fake with its `localStorage` entry and delay (Spec *Data model*, *API / interfaces*)
  - Done when: tests show seven fields, a new `temporaryId` and the same `deviceId` on each call, `NotDecided` and `null` on a first start and whenever `consentRequired` is `false`, and a stored entry reported by a new instance
  - Depends on: T2
- [ ] **T4. Add the fake consent method**
  - Covers: R5, R6, R7
  - Files: `src/bridge/fakeIdentityBridge.ts`, `src/bridge/fakeIdentityBridge.test.ts`
  - Change: implement `setConsent(choice)` with the transitions of the lifecycle diagram, each field handled on its own (Spec *Data model*)
  - Done when: tests cover every transition of the diagram and show that changing one consent leaves the other's status and ID alone, and that a new instance reports the saved statuses and the same ID for an accepted consent
  - Depends on: T3
- [ ] **T5. Add the identity observer**
  - Covers: R9
  - Files: `src/identity/identityObserver.ts`, `src/identity/identityObserver.test.ts`
  - Change: `subscribe` and `publish`, calling the subscribers on the first publish and whenever one of the seven fields differs from the last identity delivered (Spec *Components & changes*)
  - Done when: tests show a call on the first publish, no call for an equal identity, a call for each single changed field, and no call after unsubscribing
  - Depends on: T3
- [ ] **T6. Add the identity service**
  - Covers: R1, R8, R9
  - Files: `src/identity/identityService.ts`, `src/identity/identityService.test.ts`
  - Change: `start()` and `saveConsent(choice)` over the bridge and the observer, with the `busy` flag (Spec *Overview*, *API / interfaces*). A rejected `setConsent` changes nothing and publishes nothing (Spec *Edge cases & error handling*)
  - Done when: tests show the identity published after `start()` and after a save, `busy` set while a call is in flight, and an unchanged identity with no publish when the bridge rejects
  - Depends on: T4, T5
- [ ] **T7. Add the three subscribers**
  - Covers: R10, R11, R12
  - Files: `src/subscribers/recorder.ts`, `src/subscribers/requestHeaders.ts`, `src/subscribers/analyticsCollector.ts`, `src/subscribers/gameConfig.ts`, `src/subscribers/subscribers.test.ts`
  - Change: the shared recorder and the three mappings from an `Identity` to what each consumer holds (Spec *Components & changes*, the header table in *API / interfaces*)
  - Done when: tests show each subscriber's fields for both values of `consentRequired`, a header left out while its value is `null`, `null` kept by the other two, and `updatedAt` set on every notification
  - Depends on: T5
- [ ] **T8. Build the consent block**
  - Covers: R5
  - Files: `src/ui/ConsentBlock.tsx`, `src/ui/ConsentBlock.test.tsx`
  - Change: the component with a title, two switches, "Save" and "Accept all", keeping its own switch state until saved (Spec *Components & changes*, *Alternatives & decisions*)
  - Done when: tests show the switches following the statuses passed in, "Save" calling back with on as `Accepted` and off as `Declined`, "Accept all" with both `Accepted`, and both buttons disabled while busy
  - Depends on: T3
- [ ] **T9. Build the start panel**
  - Covers: R13
  - Files: `src/monitoring/StartPanel.tsx`, `src/monitoring/StartPanel.test.tsx`
  - Change: the panel with the `consentRequired` and "First start" switches and the "Start" button, reporting the scenario when "Start" is pressed (Spec *Components & changes*)
  - Done when: tests show "Start" calling back with the two switch values, and the button disabled while busy
  - Depends on: T3
- [ ] **T10. Build the config and subscriber blocks**
  - Covers: R14, R15
  - Files: `src/monitoring/ConfigBlock.tsx`, `src/monitoring/ConfigBlock.test.tsx`, `src/monitoring/SubscriberBlock.tsx`, `src/monitoring/SubscriberBlock.test.tsx`
  - Change: `ConfigBlock` lists the seven fields of the current identity, and `SubscriberBlock` shows the `value` and `updatedAt` of a recorder; both show their empty state before the first start (Spec *Components & changes*, *Edge cases & error handling*)
  - Done when: tests show "Not started" and "No update yet" before a start, the seven fields after it, and a new value and time after a notification
  - Depends on: T7
- [ ] **T11. Assemble the page**
  - Covers: R3, R4
  - Files: `src/main.tsx`, `src/App.tsx`, `src/App.test.tsx`, `src/index.css`
  - Change: create the bridge, the observer, the service and the subscribers in `src/main.tsx` and mount the blocks in `src/App.tsx` in the layout of the Spec, each consent block shown by its rule (Spec *Components & changes*). This is the feature's entry point, added last (Spec *Rollout & rollback*)
  - Done when: tests show the three rows of the block table in the PRD, and a save in one consent block reflected in the other block, the config block and the three subscriber blocks
  - Depends on: T6, T8, T9, T10
- [ ] **T12. Check the feature in the browser**
  - Covers: `verify`
  - Files: none; a manual pass on `npm run dev`
  - Change: run the manual check of Spec *Testing plan* on a first start with `consentRequired` on, then on a start with it off
  - Done when: each consent can be given and withdrawn on its own, the config block and the three subscriber blocks change at once without a reload, and no consent block is shown with `consentRequired` off
  - Depends on: T11
- [ ] **T13. Apply the final design and copy**
  - Covers: R3, R4
  - Files: `src/ui/ConsentBlock.tsx`, `src/App.tsx`, `src/index.css`
  - Change: replace the provisional English labels and layout with the final copy and design (Spec *Components & changes*)
  - Done when: the consent blocks match the mockups and the final copy, and the component tests pass with the new labels
  - Depends on: T11
  - Blocked by: PRD Q3
