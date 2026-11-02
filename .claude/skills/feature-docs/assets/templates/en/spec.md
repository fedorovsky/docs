---
type: spec
title: <Feature name>
feature: <feature-slug>
lang: en
mirror: ../ru/spec.md
status: draft            # draft | review | approved | shipped | deprecated
owner: <name>
reviewers: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
prd: ./prd.md
tasks: ./tasks.md
links: []                # "Role: name — URL", e.g. "Jira: TRACK-12 — https://…", "Confluence: tracking policy — https://…", "PR: consent banner — https://…"
---

# <Feature name> — Spec

## Summary

<2–3 sentences: what we're building technically and the shape of the solution. Link the PRD for the why.>

## Context & current state

<How the relevant part of the system works today, grounded in the actual code (modules, files, tables, endpoints). What constraints does it impose?>

## Proposed design

### Overview

<The solution at a glance. When several components interact, add a Mermaid `sequenceDiagram` or `flowchart`.>

### Components & changes

<What is added or changed, per component/module. Reference real paths.>

### Data model *(optional)*

<New or changed tables, fields, schemas, migrations. Relations as a Mermaid `erDiagram`, status lifecycles as `stateDiagram-v2`.>

### API / interfaces *(optional)*

<New or changed endpoints, events, messages, public functions — with request/response shapes.>

## Requirements coverage

| PRD ID | How it's satisfied | Section |
|--------|--------------------|---------|
| R1 | <mechanism> | <link to section above> |
| R2 | <mechanism> | <link to section above> |

<Start the cell with **Partial:** or **Not covered:** when the design doesn't fully meet the requirement, and say what's missing.>

## Alternatives & decisions

| Decision | Options considered | Chosen | Why |
|----------|-------------------|--------|-----|
| <what had to be decided> | <A, B, …> | <A> | <trade-offs> |

## Edge cases & error handling

- <Failure mode or edge case> → <behavior>

## Non-functional *(optional)*

<Performance, scalability, security, privacy, accessibility — only what's relevant to this feature.>

## Testing plan

<Unit / integration / e2e / manual — what is tested at which level, and how PRD acceptance criteria are verified.>

## Rollout & rollback

<Release order (migrations before code), backward compatibility, and how to roll back safely.>

## Observability *(optional)*

<Logs, metrics, alerts, dashboards — including how PRD success metrics will be collected.>

## Open questions

- [ ] **Q1.** <Question> — <who should answer>
