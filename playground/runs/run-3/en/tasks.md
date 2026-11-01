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
---

# Command palette (Cmd+K) — Tasks

Delivers the command palette from the [Spec](./spec.md), behind the build-time variable `VITE_FEATURE_COMMAND_PALETTE` until rollout.

## Tasks

- [ ] **T1. Set up the component test environment**
  - Covers: setup
  - Files: `package.json`, new `vitest.config.ts`
  - Change: add `jsdom` as a dev dependency and `vitest.config.ts` with `environment: "jsdom"` (Spec *Testing plan*)
  - Done when: `npx vitest run --passWithNoTests` exits 0 and `npm run build` still passes
  - Depends on: —
- [ ] **T2. Open and close the palette with Cmd/Ctrl+K behind the flag**
  - Covers: R1
  - Files: `src/hooks/useHotkey.ts`, new `src/hooks/useHotkey.test.ts`, `src/components/layout/Header.tsx`, new `src/components/command-palette/CommandPalette.tsx`, new `src/components/command-palette/CommandPalette.test.tsx`, `src/analytics/track.ts`
  - Change: add `allowInInputs` to `useHotkey`; `Header` registers Cmd/Ctrl+K only when `VITE_FEATURE_COMMAND_PALETTE` is on, owns `open`, renders `CommandPalette` (a `Dialog` with the input) and tracks `command_palette_opened`; add that event to `EventName` (Spec *Components & changes*, *API / interfaces*). Handle the hotkey edge cases: palette already open, another dialog open (Spec *Edge cases & error handling*)
  - Done when: unit tests show `allowInInputs` fires inside an `input` and `?` still doesn't; component tests show Cmd+K and Ctrl+K open the palette with focus in its input, also from a focused input, Esc closes it on the same URL, a second Cmd+K opens no second dialog, Cmd+K is ignored while `ShortcutsHelp` is open, and with the variable off Cmd+K does nothing
  - Depends on: T1
- [ ] **T3. Find and open admin sections**
  - Covers: R2, R3
  - Files: new `src/components/command-palette/useSectionCommands.ts`, new `src/components/command-palette/useSectionCommands.test.ts`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`, `src/analytics/track.ts`
  - Change: `useSectionCommands` with the `Sidebar` rule and substring match on `title`; render the Sections group with the combobox + listbox pattern, ↑/↓, Enter or click; on select `navigate(path)`, close and track `command_palette_item_selected`, added to `EventName`; ignore Enter while `e.isComposing` (Spec *Components & changes*, *Edge cases & error handling*)
  - Done when: unit tests show "ref" matches "Refunds" in any case, no "Refunds" without `refunds:manage`, nothing before `loaded`; component tests show arrows + Enter and click both open `/refunds`, and Enter during IME composition selects nothing
  - Depends on: T2
- [ ] **T4. Find and open orders and customers**
  - Covers: R4
  - Files: new `src/components/command-palette/useEntitySearch.ts`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: `useEntitySearch` over `searchEntities(q, 5, signal)` with 2+ characters, 150 ms debounce, abort of outdated requests and dropping hits without `orders:view` / `customers:view`; render the Orders and Customers groups, their error state and the no-matches empty state; on select navigate to `/orders/:orderId` or `/customers/:customerId` and also track `search_result_opened` with `source: "command_palette"` (Spec *Components & changes*, *API / interfaces*, *Edge cases & error handling*)
  - Done when: component tests with `searchEntities` mocked show an order hit opens `/orders/ORD-10482` without visiting `/search`; a customer found by number, name and email opens `/customers/CUS-2210`; a 1-character query makes no call; hits are dropped without `orders:view` / `customers:view`; a failed search keeps sections visible and shows the error state; no matches shows the empty state; a slower outdated response is not shown
  - Depends on: T3
- [ ] **T5. Record recently opened orders and customers**
  - Covers: R5
  - Files: `src/auth/usePermissions.ts`, new `src/components/command-palette/recentItems.ts`, new `src/components/command-palette/recentItems.test.ts`, `src/pages/OrderDetailsPage.tsx`, `src/pages/CustomerDetailsPage.tsx`
  - Change: `usePermissions()` also returns `userId`; `localStorage` helpers and `useRecordRecent` as in Spec *Data model*; call `useRecordRecent` on mount of both detail pages (Spec *Components & changes*)
  - Done when: unit tests cover newest-first order, deduplication by type + id, the cap of 5, separate keys per `userId`, reset on invalid JSON, and no error when `localStorage` throws
  - Depends on: T1
- [ ] **T6. Show recent items when the input is empty**
  - Covers: R5
  - Files: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Change: with an empty input render the Recent group from `recentItems` for the current `userId`, showing stored ids and hiding items the agent no longer has access to; selecting one navigates and tracks with `from_recent: true` (Spec *Components & changes*, *Edge cases & error handling*)
  - Done when: component test: after order A and then customer B are recorded, the empty palette lists B then A, and choosing one opens its page; an order item is hidden without `orders:view`
  - Depends on: T4, T5
- [ ] **T7. Apply the design's wording**
  - Covers: setup
  - Files: `src/components/layout/ShortcutsHelp.tsx`, `src/components/command-palette/CommandPalette.tsx`
  - Change: add the Cmd/Ctrl+K entry to `SHORTCUTS`; put the design's text into the palette's empty and error states (Spec *Components & changes*, *Edge cases & error handling*)
  - Done when: the shortcuts help (`?`) lists the Cmd/Ctrl+K entry; the empty and error states show the design's text; existing tests still pass
  - Depends on: T4
  - Blocked by: the design (PRD *Risks & dependencies*); no open question tracks it
- [ ] **T8. Enable on staging and run the manual checks**
  - Covers: R1
  - Files: staging build configuration for `VITE_FEATURE_COMMAND_PALETTE`
  - Change: build staging with the variable on; run the manual checks from Spec *Testing plan*
  - Done when: on macOS and Windows, in the browsers the support team uses, Cmd/Ctrl+K opens the palette and the browser's own Ctrl+K / Cmd+K doesn't fire
  - Depends on: T6, T7
- [ ] **T9. Enable in production**
  - Covers: setup
  - Files: production build configuration for `VITE_FEATURE_COMMAND_PALETTE`
  - Change: build and deploy production with the variable on for everyone; rollback is a rebuild with it off (Spec *Rollout & rollback*)
  - Done when: in production Cmd/Ctrl+K opens the palette and `command_palette_opened` and `command_palette_item_selected` events arrive in analytics
  - Depends on: T8
  - Blocked by: Spec Q3, PRD Q2
