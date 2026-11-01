---
type: tasks
title: Command palette (Cmd+K)
feature: command-palette
lang: en
mirror: ../ru/tasks.md
status: draft
owner: TBD
created: 2026-11-01
updated: 2026-11-01
prd: ./prd.md
spec: ./spec.md
links: [ADMIN-231]
---

# Command palette (Cmd+K) — Tasks

Delivers the command palette from the [Spec](./spec.md), behind the `VITE_FF_COMMAND_PALETTE` flag until rollout. The Spec is `draft`, so these tasks may change with it.

## Tasks

- [ ] **T1. Add the feature flag**
  - Covers: `setup`
  - Files: `src/flags.ts`, environment config for `VITE_FF_COMMAND_PALETTE`
  - Change: `isEnabled("command_palette")` reading `import.meta.env.VITE_FF_COMMAND_PALETTE` (Spec *Components & changes*); off by default
  - Done when: `npm run build` passes and `isEnabled("command_palette")` is `false` without the variable
  - Depends on: —
- [ ] **T2. Let `useHotkey` fire inside text fields**
  - Covers: R1
  - Files: `src/hooks/useHotkey.ts`, `src/hooks/useHotkey.test.ts`
  - Change: add the `inInputs` option that skips the `input` / `textarea` / `contenteditable` guard (Spec *Components & changes*)
  - Done when: tests show the handler fires with an input focused when `inInputs: true` and not otherwise; `?` still ignored inside inputs
  - Depends on: —
- [ ] **T3. Add `matchSections`**
  - Covers: R2, R4
  - Files: `src/components/palette/matchSections.ts`, `src/components/palette/matchSections.test.ts`
  - Change: pure function over `routes` with `inNav && has(permission)` and a case-insensitive `title` match (Spec *Components & changes*)
  - Done when: tests: "ref" returns "Refunds"; a route without permission is excluded for any query; `inNav: false` routes excluded; empty query returns all permitted
  - Depends on: —
- [ ] **T4. Add `useRecentItems`**
  - Covers: R5
  - Files: `src/components/palette/useRecentItems.ts`, `src/components/palette/useRecentItems.test.ts`
  - Change: `localStorage` list per user id with upsert-to-front, label keep, cap of 10, permission filter, and `useRecordVisits()` (Spec *Components & changes*, *Data model*)
  - Done when: tests cover upsert order, kept label, cap, per-user key, corrupt JSON → empty list, filtering by `has()`
  - Depends on: —
- [ ] **T5. Build the palette with sections and keyboard navigation**
  - Covers: R1, R2, R4, R6
  - Files: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`, `src/components/layout/AppLayout.tsx`
  - Change: Radix dialog with input, "Sections" group from `matchSections`, Up / Down / Enter, hotkey `{ meta: true, inInputs: true }`; mounted in `AppLayout` when the flag is on (Spec *Components & changes*)
  - Done when: with the flag on, Cmd+K and Ctrl+K open it, also from the header search; "ref" then Enter opens `/refunds`; without `refunds:manage` "Refunds" is absent; with the flag off nothing renders; tests pass
  - Depends on: T1, T2, T3
- [ ] **T6. Add order and customer search to the palette**
  - Covers: R3, R4
  - Files: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`
  - Change: debounced `searchEntities(q, 10)` from 2 characters, "Orders" / "Customers" groups filtered by permission, "Searching…", "Search is unavailable" and "No results for “<query>”" states (Spec *Edge cases*)
  - Done when: tests with `searchEntities` mocked: hits grouped and Enter opens `/orders/<id>`; no request below 2 characters or without both view permissions; error state shown
  - Depends on: T5
- [ ] **T7. Show and record recent items**
  - Covers: R5
  - Files: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`, `src/pages/SearchPage.tsx`
  - Change: "Recent" group on an empty query; `record()` on palette selection and on `SearchPage` result click; `useRecordVisits()` in the palette (Spec *Components & changes*)
  - Done when: open two orders, press Cmd+K: both listed, latest first, selecting one opens it; tests pass
  - Depends on: T4, T6
- [ ] **T8. Add the palette analytics events**
  - Covers: `setup`
  - Files: `src/analytics/track.ts`, `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`
  - Change: add `command_palette_opened` and `command_palette_item_opened` with the properties from Spec *API / interfaces*
  - Done when: a test asserts both events with `kind`, `position`, `query_length`, `duration_ms`; both appear in the analytics debugger locally
  - Depends on: T7
- [ ] **T9. List the shortcut in the keyboard shortcuts help**
  - Covers: R7
  - Files: `src/components/layout/ShortcutsHelp.tsx`
  - Change: add the "Cmd+K / Ctrl+K" — "Open command palette" entry when the flag is on (Spec *Components & changes*)
  - Done when: with the flag on, "?" shows the entry; with the flag off it is absent
  - Depends on: T1
- [ ] **T10. Apply the final design and texts**
  - Covers: R2, R3, R5
  - Files: `src/components/palette/CommandPalette.tsx`, the app stylesheet for `palette-*` classes
  - Change: replace the provisional layout and texts with the mockups (Spec *Components & changes*, styles)
  - Done when: the palette matches the mockups on staging and all palette tests still pass
  - Depends on: T7, T9
  - Blocked by: PRD Q4
- [ ] **T11. Verify on staging**
  - Covers: `verify`
  - Files: staging environment config for `VITE_FF_COMMAND_PALETTE`
  - Change: run the manual checks from Spec *Testing plan* with two accounts of different permissions, on macOS and Windows
  - Done when: R1–R7 acceptance criteria pass on staging for both accounts
  - Depends on: T8, T9
- [ ] **T12. Roll out**
  - Covers: `rollout`
  - Files: production environment config for `VITE_FF_COMMAND_PALETTE`
  - Change: turn the flag on in production (Spec *Rollout & rollback*)
  - Done when: the flag is on in production for a week and `command_palette_item_opened` events are arriving
  - Depends on: T10, T11
