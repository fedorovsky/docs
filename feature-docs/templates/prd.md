---
type: prd
title: <Feature name>
feature: <feature-slug>
status: draft            # draft | review | approved | shipped | deprecated
owner: <name>
reviewers: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
spec: ./spec.md
links: []                # tickets, designs, research, related docs
---

# <Feature name> — PRD

## Summary

<2–3 sentences: what we're building, for whom, and the outcome we expect.>

## Problem

<Who has the problem, what it is, and how we know (data, feedback, incidents, support tickets). What happens if we do nothing?>

## Goals

- <Outcome we want — phrased as a result, not a solution.>

## Non-goals

- <Explicitly out of scope, so nobody assumes otherwise.>

## Users & scenarios

<Who uses this and the key flows. User stories or short step-by-step scenarios. For a flow with branches, add a Mermaid `flowchart` showing what the user sees and does.>

- As a <user>, I want <capability> so that <benefit>.

## Requirements

| ID | Requirement | Priority | Acceptance criteria |
|----|-------------|----------|---------------------|
| R1 | <What the system must do, from the user's point of view> | Must | <How a tester verifies it> |
| R2 | | Should | |

<Priorities: Must / Should / Could. IDs are permanent — never renumber; strike through dropped ones with a reason.>

## Success metrics

| Metric | Baseline | Target | How measured |
|--------|----------|--------|--------------|
| <metric> | <current value or "unknown — see OQ"> | <target> | <source / dashboard / event> |

## Risks & dependencies *(optional)*

- <Teams, systems, legal/compliance, external partners this depends on; what could go wrong.>

## Timeline *(optional)*

- <Milestones or deadlines, and what drives them.>

## Open questions

- [ ] <Question> — <who should answer>
