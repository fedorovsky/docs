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

Delivers the client-only command palette from the [Spec](./spec.md), behind the build-time variable `VITE_FEATURE_COMMAND_PALETTE` until rollout.

## Tasks

- [ ] **T1. Set up Vitest with jsdom**
  - Covers: `setup`
  - Files: `package.json`, `vitest.config.ts`, `src/components/ui/Dialog.test.tsx`
  - Change: add `jsdom` as a dev dependency and `vitest.config.ts` with the `jsdom` environment (Spec *Testing plan*)
  - Done when: `npx vitest run` passes a smoke test that renders `Dialog` open and finds its title
  - Depends on: —
- [ ] **T2. Add the `allowInInputs` option to `useHotkey`**
  - Covers: R1
  - Files: `src/hooks/useHotkey.ts`, `src/hooks/useHotkey.test.ts`
  - Change: new option `allowInInputs` (default `false`) that skips the focused-input check (Spec *Components & changes*, *API / interfaces*)
  - Done when: tests pass: with `{ meta: true, allowInInputs: true }` the handler fires on Cmd+K and Ctrl+K, also from a focused `input`; `?` without the option is still ignored in an `input`
  - Depends on: T1
- [ ] **T3. Open and close the palette from the header, behind the flag**
  - Covers: R1
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/layout/Header.tsx`, `src/components/layout/Header.test.tsx`
  - Change: `CommandPalette` shell (`Dialog` + input, provisional texts); `Header` registers Cmd/Ctrl+K and owns `open` only when `VITE_FEATURE_COMMAND_PALETTE` is on (Spec *Components & changes*, *Rollout & rollback*)
  - Done when: tests pass: with the flag on, Cmd+K and Ctrl+K open the palette with focus in its input, also from the header search; Esc closes it; Cmd+K while open keeps one dialog; ignored while `ShortcutsHelp` is open; with the flag off nothing opens
  - Depends on: T2
- [ ] **T4. Add `useSectionCommands`**
  - Covers: R2, R3
  - Files: `src/components/command-palette/useSectionCommands.ts`, `src/components/command-palette/useSectionCommands.test.ts`
  - Change: filter `routes` by `inNav && has(permission)` and match `title` by case-insensitive substring; return nothing until `loaded` (Spec *Components & changes*)
  - Done when: tests pass: "ref" returns Refunds with `refunds:manage` and nothing without it; detail pages and `/search` never appear; empty result while `loaded` is `false`
  - Depends on: T1
- [ ] **T5. List sections in the palette and open the selected one**
  - Covers: R2, R3
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: Sections group from `useSectionCommands`; ↑/↓, Enter or click calls `navigate(path)` and closes; combobox + listbox ARIA; Enter ignored while `e.isComposing` (Spec *Components & changes*, *Edge cases*)
  - Done when: tests pass: typing "ref" then ↓ + Enter, or a click, opens `/refunds` and closes the palette; `aria-activedescendant` follows the active item; Enter during composition selects nothing
  - Depends on: T3, T4
- [ ] **T6. Add `useEntitySearch`**
  - Covers: R4
  - Files: `src/components/command-palette/useEntitySearch.ts`, `src/components/command-palette/useEntitySearch.test.ts`
  - Change: TanStack Query over `searchEntities(q, 5, signal)`, 150 ms debounce, enabled from 2 characters; drop hits without `orders:view` / `customers:view` (Spec *Components & changes*, assumption PRD Q4)
  - Done when: tests with `searchEntities` mocked pass: no call below 2 characters; one call after a 150 ms pause; the outdated request's `signal` is aborted; hits dropped without each permission
  - Depends on: T1
- [ ] **T7. Show orders and customers in the palette**
  - Covers: R4
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: Orders and Customers groups from `useEntitySearch`; selecting navigates to `/orders/:orderId` or `/customers/:customerId`; error and empty states with provisional texts (Spec *Edge cases*)
  - Done when: tests pass: an order number shows the order and Enter opens `/orders/<id>` without visiting `/search`; same for a customer found by number, name and email; a failed search still shows sections plus an error state; no matches shows the empty state
  - Depends on: T5, T6
- [ ] **T8. Store recently opened orders and customers**
  - Covers: R5
  - Files: `src/auth/usePermissions.ts`, `src/components/command-palette/recentItems.ts`, `src/components/command-palette/recentItems.test.ts`, `src/pages/OrderDetailsPage.tsx`, `src/pages/CustomerDetailsPage.tsx`
  - Change: `usePermissions()` also returns `userId`; `recentItems` helpers and `useRecordRecent` over `acme-admin:recent:<userId>`, called on mount by both detail pages (Spec *Data model*, assumptions PRD Q5, PRD Q6)
  - Done when: tests pass: newest first, deduplicated by type + id, at most 5, separate keys per user, invalid JSON resets the value; mounting a detail page records its id
  - Depends on: T1
- [ ] **T9. Show recent items when the input is empty**
  - Covers: R5
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: Recent group with the stored ids when the input is empty; hide items the agent no longer has permission for; selecting opens the page (Spec *Data model*, *Edge cases*)
  - Done when: tests pass: after opening order A then customer B the palette shows B, A; choosing one opens its page; an item without permission is hidden; a throwing `localStorage` leaves the rest of the palette working
  - Depends on: T7, T8
- [ ] **T10. Send the palette analytics events**
  - Covers: `setup`
  - Files: `src/analytics/track.ts`, `src/components/layout/Header.tsx`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: add `command_palette_opened` / `command_palette_item_selected` to `EventName` and send them; send `search_result_opened` with `source: "command_palette"` for orders and customers (Spec *API / interfaces*)
  - Done when: tests with `track` mocked pass: opening sends `{ trigger: "hotkey" }`; selecting an order sends `command_palette_item_selected` with `kind`, `from_recent`, `query_length`, `ms_since_open` and `search_result_opened` with `source: "command_palette"`
  - Depends on: T9
- [ ] **T11. Apply the design's texts and the shortcuts help entry**
  - Covers: R1, R2, R4, R5
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/layout/ShortcutsHelp.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: replace the provisional texts with the design's; add the Cmd/Ctrl+K entry to `SHORTCUTS` (Spec *Components & changes*)
  - Done when: the palette and the shortcuts help match the mockups; `npx vitest run` passes
  - Depends on: T10
  - Blocked by: PRD Q12
- [ ] **T12. Enable on staging and check on macOS and Windows**
  - Covers: `verify`
  - Files: staging build environment (deploy config): `VITE_FEATURE_COMMAND_PALETTE`
  - Change: build staging with the variable on and run the manual checks from Spec *Testing plan*
  - Done when: on macOS and Windows, in the browsers the support team uses, the PRD acceptance criteria for R1–R5 pass and the browser's own Cmd+K / Ctrl+K doesn't fire
  - Depends on: T11
- [ ] **T13. Roll out to production**
  - Covers: `rollout`
  - Files: production build environment (deploy config): `VITE_FEATURE_COMMAND_PALETTE`
  - Change: build and deploy production with the variable on for everyone; rollback is a rebuild with it off (Spec *Rollout & rollback*)
  - Done when: agents in production open the palette and `command_palette_opened` events arrive from production
  - Depends on: T12
  - Blocked by: Spec Q3, PRD Q2
