---
type: prd
title: User identity and tracking consent
feature: identity-tracking-consent
lang: en
mirror: ../uk/prd.md
status: draft
owner: TBD
reviewers: []
created: 2026-11-10
updated: 2026-11-10
spec: ./spec.md
tasks: ./tasks.md
links: ["Jira: TRACK-12"]
---

# User identity and tracking consent — PRD

## Summary

The app learns the user's identity from the host app at start, asks for consent to marketing and analytics tracking in two blocks on the page, and hands every change of identity to the systems that use it, without a reload. The host app's bridge is still in the works, so for now the app runs against fake bridge methods and stand-in consumers, with debug blocks that show what each of them holds.

## Problem

The app doesn't yet know the user's identity and can't ask whether marketing and analytics tracking is allowed (TRACK-12). The parts that need this (the headers of backend requests, the analytics collector and the game config) have no tracking IDs or consent statuses to work with. The ticket states the need but not what drives it or how large it is: it cites no legal requirement, data or incident (PRD Q1).

## Goals

- The app knows the user's identity from the start and keeps it current.
- The user decides on marketing and on analytics tracking separately, and can change either decision at any time.
- A tracking ID exists only for tracking the user has accepted.
- Every consumer of identity sees a change at once, without a reload.
- Developers and testers can run every case on the page while the bridge and the consumers are stand-ins.

## Non-goals

- The real native bridge: the app works against fake methods that follow the agreed contract (PRD Q2).
- Real consumers: nothing is sent to the backend, the analytics collector or the game config; the stand-ins only record what they receive (PRD Q2).
- Deciding where consent is required: `consentRequired` comes from the config only.
- Modal dialogs or a separate consent screen: both consent blocks sit on the one page.
- Simulating bridge failures: the fake methods never fail.
- Final design and copy: there are no mockups (PRD Q3).
- Removing the monitoring blocks: they are a debug aid and go later, as separate work.

## Users & scenarios

- As a user of the app where consent is required, I want to choose marketing and analytics tracking separately at the first start, or accept both at once, so that I'm tracked only the way I agreed to.
- As a user, I want to change or withdraw either consent later in the settings, so that the decision stays mine.
- As a developer or tester, I want to start the app with consent required or not, as a first start or with the saved choice, and see what the config and each consumer hold, so that I can check every case before the real bridge exists.

Which consent block the user sees:

| `consentRequired` | Consent statuses | Start block | Settings block |
|---|---|---|---|
| `true` | at least one `NotDecided` | shown | shown |
| `true` | none `NotDecided` | hidden | shown |
| `false` | both `NotDecided` | hidden | hidden |

## Requirements

| ID | Requirement | Priority | Acceptance criteria |
|----|-------------|----------|---------------------|
| R1 | At start the app gets the user's identity from the host app's config: `marketingTrackingId`, `analyticsTrackingId`, `deviceId`, `temporaryId`, `consentRequired`, `marketingConsentStatus`, `analyticsConsentStatus` | Must | After a start all seven fields are known; `temporaryId` differs between two starts, `deviceId` doesn't; each consent status is `0` (`Declined`), `1` (`Accepted`) or `2` (`NotDecided`) |
| R2 | A tracking ID exists only while its consent is `Accepted` | Must | At the first start with `consentRequired = true` both statuses are `NotDecided` and both tracking IDs are `null`; a tracking ID is not `null` only while its status is `Accepted`; with `consentRequired = false` both statuses are `NotDecided` and both tracking IDs are `null` on every start |
| R3 | Where consent is required and not yet decided, the user is asked at the start, in a block on the page, not a modal | Must | The start block is shown when `consentRequired = true` and at least one status is `NotDecided`, and hidden otherwise; it has a "Marketing" switch and an "Analytics" switch that show the current statuses (on for `Accepted`, off for `Declined` and `NotDecided`), and the buttons "Save" and "Accept all" |
| R4 | The user can change or withdraw consent in a settings block on the same page | Must | The settings block is shown whenever `consentRequired = true` and hidden when it is `false`; it has the same switches and buttons as the start block; turning a switch off and pressing "Save" withdraws that consent |
| R5 | A save sends both choices in one call, and the two consents don't affect each other | Must | "Save" sends marketing and analytics as the switches stand: on is `Accepted`, off is `Declined`, so a `NotDecided` left off becomes `Declined`; "Accept all" sends both as `Accepted`; changing one consent leaves the other's status and tracking ID as they were |
| R6 | The tracking ID follows the consent | Must | `Accepted` saved again as `Accepted` keeps the same ID; `Declined` or `NotDecided` changed to `Accepted` gets a new ID, and an earlier ID never comes back; declining or withdrawing gives `null` and the status `Declined` |
| R7 | The saved choice is remembered between starts | Must | After a reload, a start with "First start" off shows both statuses as they were saved; whether an accepted consent also keeps its tracking ID is PRD Q5 |
| R8 | A failed consent call changes nothing | Must | When the call fails as a whole, both statuses and both tracking IDs stay as they were. The fake methods never fail, so this can only be verified in automated tests |
| R9 | Every consumer gets the identity at start and after each change, without a reload | Must | After a start, and after every save that changes a field, each consumer holds the new values at once; a save that changes nothing notifies no consumer, so its update time stays the same |
| R10 | The headers of backend requests carry the identity | Must | The headers are those of the table below for the current `consentRequired`; a header whose value is `null` is left out, so accepting a consent adds its tracking ID header and withdrawing removes it |
| R11 | The analytics collector receives the identity | Must | It holds the fields of the table below for the current `consentRequired`; a `null` tracking ID is kept as `null` |
| R12 | The game config receives the identity | Must | It holds the fields of the table below for the current `consentRequired`; a `null` tracking ID is kept as `null` |
| R13 | A start panel at the top of the page starts the app on demand | Should | The panel has a `consentRequired` switch, a "First start" switch and a "Start" button; the config is loaded only when "Start" is pressed, with `consentRequired` as its switch stands; with "First start" on, the saved choice is forgotten and both statuses come back `NotDecided` |
| R14 | A config block shows the seven identity fields | Should | The block sits under the start panel and lists all seven fields with their current values; after a save it shows the new statuses and tracking IDs without a reload |
| R15 | A monitoring block per consumer shows what the consumer holds | Should | Three blocks next to the settings block, one each for the backend request headers, the analytics collector and the game config; each shows the consumer's current state and the time of its last update, and changes at once when the consumer is notified |

Which fields each consumer holds:

| Consumer | With `consentRequired = false` | With `consentRequired = true` | A `null` value |
|---|---|---|---|
| Backend request headers | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `deviceId`, `consentRequired` | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `deviceId`, `consentRequired`, `marketingConsentStatus`, `analyticsConsentStatus` | the header is left out |
| Analytics collector | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `deviceId` | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `marketingConsentStatus`, `analyticsConsentStatus` | kept as `null` |
| Game config | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `deviceId` | `marketingTrackingId`, `analyticsTrackingId`, `temporaryId`, `marketingConsentStatus`, `analyticsConsentStatus` | kept as `null` |

## Success metrics

The ticket names no metric. What to measure, the baseline, the target and the source are PRD Q6.

## Risks & dependencies

- The host app's native bridge: the contract is agreed, the methods are fake for now. A real method that behaves differently (timing, failures) changes what the app has to handle.
- The failure rule (R8) can't be tried by hand until the bridge can fail.
- What the bridge keeps between starts is only partly stated (PRD Q5).

## Open questions

- [ ] **Q1.** What drives the feature and what is the evidence: which legal or policy requirement, in which markets `consentRequired` is `true`, how the problem shows today? Assumed for this draft: the users are the app's end users, who must be asked before a tracking ID is issued for them. — product owner (author of TRACK-12)
- [ ] **Q2.** Where does TRACK-12 end: are the switch to the real bridge and to the real backend, analytics collector and game config separate work? Assumed: yes; the feature is complete with fake bridge methods and stand-in consumers, and isn't released to real users in that state. — product owner
- [ ] **Q3.** Which languages does the UI ship in, what is the final copy, and will the consent blocks get mockups? The ticket gives the labels in Russian and says there are no mockups. Assumed: provisional English labels ("Save", "Accept all", "Start", "First start") and a provisional layout. — product owner, designer
- [ ] **Q4.** What does the user see when a consent call fails: a message, a retry? The ticket says only that no field changes. — product owner, designer
- [ ] **Q5.** What do the bridge methods keep between starts: does an accepted consent have the same tracking ID after a restart, and does a start with `consentRequired = false` leave the saved choice in place? The ticket says only that the methods "remember the choice between reloads". — host app (bridge) team
- [ ] **Q6.** Which success metrics does the feature have, with what baseline and target, and where are they measured? — product owner
- [ ] **Q7.** Who owns the PRD, the Spec and the task list, and who reviews them? — product owner
