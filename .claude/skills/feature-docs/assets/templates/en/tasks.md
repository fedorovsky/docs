---
type: tasks
title: <Feature name>
feature: <feature-slug>
lang: en
mirror: ../ru/tasks.md
status: draft            # draft | review | approved | shipped | deprecated
owner: <name>
reviewers: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
prd: ./prd.md
spec: ./spec.md
links: []                # "Role: name — URL", e.g. "Jira: TRACK-12 — https://…", "PR: consent banner — https://…"
---

# <Feature name> — Tasks

<One or two sentences: what these tasks deliver. The [Spec](./spec.md) is the source of truth for how; this list is the order of work.>

## Tasks

- [ ] **T1. <Short imperative title>**
  - Covers: <R1, R2 — or exactly one label in backticks: setup, verify or rollout>
  - Files: <paths in backticks: path/to/file.ts, path/to/file.test.ts>
  - Change: <at most two sentences, pointing to the Spec section; more means split the task>
  - Done when: <a check anyone can run: tests that pass, behaviour to see>
  - Depends on: <T-ids, or "—">
- [ ] **T2. <Short imperative title>**
  - Covers: <R2>
  - Files: <paths>
  - Change: <…>
  - Done when: <…>
  - Depends on: <T1>
  - Blocked by: <PRD Q1 — the open question that must be answered first; track any other blocker as an open question too; omit the line when nothing blocks>
