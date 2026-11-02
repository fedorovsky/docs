---
type: prd
title: Orders CSV export
feature: orders-csv-export
lang: en
mirror: ../ru/prd.md
status: approved
owner: Jane Doe
reviewers: [Alex Kim, Sam Lee]
created: 2026-03-02
updated: 2026-03-12
spec: ./spec.md
links: ["Jira: SHOP-412"]
---

# Orders CSV export — PRD

## Summary

Merchants can download their orders as a CSV file from the Orders page, so they can reconcile sales in their own accounting tools without asking support for a data dump.

## Problem

Merchants reconcile orders in spreadsheets or accounting software. Today the only way to get the data out is to ask support, who run a manual query. Support handled 140 such requests last quarter (≈ 9% of all tickets), with a median turnaround of 2 days. Merchants told us in interviews this delay blocks their month-end close.

## Goals

- Merchants get their order data without contacting support.
- Reduce support tickets about data exports.

## Non-goals

- Scheduled / automatic exports.
- Formats other than CSV (Excel, JSON).
- Exporting products, customers or payouts — orders only.

## Users & scenarios

- As a merchant, I want to export the orders I'm currently looking at so that I can import them into my accounting tool.
- As a merchant with a large store, I want the export to work for a full year of orders without the page freezing.

## Requirements

| ID | Requirement | Priority | Acceptance criteria |
|----|-------------|----------|---------------------|
| R1 | Merchant can export orders from the Orders page as CSV | Must | "Export CSV" button on the Orders page produces a downloadable `.csv` |
| R2 | Export respects the filters currently applied (date range, status) | Must | Exported rows match exactly the rows the filtered list shows |
| R3 | Export works for up to 100k orders | Must | 100k-order export completes and the merchant gets the file without the page timing out |
| R4 | Merchant is notified when a large export is ready | Should | For exports that don't finish instantly, merchant receives an email with a download link |
| R5 | ~~Merchant can choose which columns to export~~ | — | Dropped 2026-03-09: no demand in interviews; revisit after launch |

## Success metrics

| Metric | Baseline | Target | How measured |
|--------|----------|--------|--------------|
| Support tickets tagged "data export" per quarter | 140 | < 30 | Helpdesk tag report |
| Merchants using export at least once per month | 0 | unknown — see Q1 | `orders_export_started` event |

## Open questions

- [ ] **Q1.** What adoption target is realistic for monthly export usage? — Jane Doe
- [ ] **Q2.** How many exports may a merchant run at the same time? — Jane Doe
- [ ] **Q3.** In a store with several staff accounts, who receives the "export ready" email: the owner only, or the person who started it? — Jane Doe
