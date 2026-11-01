---
type: tasks
title: Orders CSV export
feature: orders-csv-export
lang: en
mirror: ../ru/tasks.md
status: draft
owner: Alex Kim
created: 2026-03-13
updated: 2026-03-13
prd: ./prd.md
spec: ./spec.md
links: [SHOP-412]
---

# Orders CSV export — Tasks

Delivers the async CSV export from the [Spec](./spec.md), behind the `orders_csv_export` flag until rollout.

## Tasks

- [ ] **T1. Add the `order_exports` table and the feature flag**
  - Covers: `setup`
  - Files: new migration for `order_exports`, flag config for `orders_csv_export`
  - Change: create the table as in Spec *Data model*; register the flag, off by default
  - Done when: migration applies and rolls back cleanly on a local DB; flag is readable in code and off
  - Depends on: —
- [ ] **T2. Implement the export worker**
  - Covers: R2, R3
  - Files: `workers/orders-export.ts`, `workers/orders-export.test.ts`
  - Change: job that builds the query with `OrdersFilter`, streams rows with a DB cursor in batches of 1k and uploads the CSV (Spec *Components & changes*)
  - Done when: unit tests for CSV formatting pass; integration test shows export rows equal `GET /api/orders` results for each filter combination
  - Depends on: T1
- [ ] **T3. Add the export API**
  - Covers: R1
  - Files: `api/orders/exports.ts`, `api/orders/exports.test.ts`
  - Change: `POST /api/orders/exports` and `GET /api/orders/exports/{id}` as in Spec *API / interfaces*, limit of 3 concurrent exports per merchant
  - Done when: tests cover `202 { exportId }`, status polling with a signed `url`, and `429` on the fourth concurrent export
  - Depends on: T2
- [ ] **T4. Add the export button to the Orders page**
  - Covers: R1
  - Files: `web/pages/orders/ExportButton.tsx`
  - Change: button that starts an export with the current filters, polls status and downloads the file; rendered only when `orders_csv_export` is on
  - Done when: with the flag on, a filtered export downloads a `.csv`; with zero matches the UI shows "No orders match your filters"; with the flag off the button is absent
  - Depends on: T3
- [ ] **T5. Email the link for long exports**
  - Covers: R4
  - Files: `workers/orders-export.ts`, `workers/orders-export.test.ts`
  - Change: reuse the existing email job to send the download link when a job runs longer than 10 s
  - Done when: test with a job over 10 s sends exactly one email with the link; a fast job sends none
  - Depends on: T2
- [ ] **T6. Add export events and the failure alert**
  - Covers: `setup`
  - Files: `workers/orders-export.ts`, alert config
  - Change: emit `orders_export_started` / `orders_export_finished` with `row_count` and `duration_ms`; alert when the failure rate is above 5% over 1 h (Spec *Observability*)
  - Done when: both events appear in the analytics debugger for a local export; the alert rule is in the alert config
  - Depends on: T3
- [ ] **T7. Run the load test on staging**
  - Covers: R3
  - Files: load-test script for the 100k-order fixture
  - Change: run a 100k-order export on staging with the flag on for a test merchant
  - Done when: the export completes in under 2 minutes
  - Depends on: T4, T6
- [ ] **T8. Roll out**
  - Covers: `rollout`
  - Files: flag config for `orders_csv_export`
  - Change: internal stores → 10% of merchants → 100% over two weeks (Spec *Rollout & rollback*)
  - Done when: flag is on for 100% with the failure alert quiet for a week
  - Depends on: T7
  - Blocked by: Spec Q1
