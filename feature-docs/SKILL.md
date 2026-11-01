---
name: feature-docs
description: Write, update and review feature documentation as a linked pair of documents — a PRD (why and what) and a technical Spec (how) — stored next to each other in the project. Use this skill whenever the user wants to describe, plan, document or design a feature, asks for a PRD, product requirements, spec, tech spec, design doc, RFC-style write-up or requirements for something they are about to build, wants to turn notes / a ticket / a conversation into feature docs, or asks to review or update existing PRD/spec files — even if they don't say "PRD" or "spec" explicitly (e.g. "let's write down what this feature should do", "опиши фичу", "напиши ПРД", "сделай спеку", "техническое описание фичи").
---

# Feature docs: PRD + Spec

Every feature gets two documents that live side by side:

| | PRD | Spec |
|---|---|---|
| Answers | *Why* are we building this and *what* must it do? | *How* will we build it? |
| Typical author | product owner / feature owner | engineer |
| Contains | problem, users, goals, numbered requirements, success metrics | design, data/API changes, decisions, testing, rollout |
| Must not contain | implementation details | new goals or changed requirements |

The boundary matters because the two documents get reviewed by different people at different times. If a Spec quietly changes what the feature does, product reviewers never see it; if a PRD prescribes a database schema, engineers lose room to find a better design. When you notice a Spec wanting to change a requirement, update the PRD (or raise it as an open question) instead.

Templates are in `templates/prd.md` and `templates/spec.md` (relative to this skill). A short worked example is in `examples/orders-csv-export/` — read it once if you're unsure about the expected depth and tone.

## Workflow

### 1. Find where docs live in this project

Look before you create anything, so new docs match what the team already has:

- Check the project's `CLAUDE.md` / `README` for a stated docs location.
- Search for existing feature docs (e.g. `**/prd.md`, `**/spec.md`, `docs/features/`). If they exist, follow their location, naming and any deviations from the templates — the project's convention wins over this skill's defaults.
- Otherwise use `docs/features/<feature-slug>/prd.md` and `.../spec.md`, and tell the user where you put them.

`<feature-slug>` is short kebab-case (`orders-csv-export`, `sso-login`).

### 2. Work out what is being asked

- **New PRD** — the usual starting point.
- **New Spec** — read the PRD first. If there is no PRD, ask whether to write a short one first; if the user declines (small or purely technical change), write the Spec and put the problem and requirements into its Context section so the Spec still stands on its own.
- **Update** — edit the existing file in place, bump `updated`, and keep requirement IDs stable (see below).
- **Review** — read the doc(s) and report against the checklist at the end of this file; don't rewrite unless asked.

### 3. Gather what you need — don't invent it

A feature doc is only useful if it is true. Use what's already available first: the conversation, tickets or notes the user shared, the existing PRD, and — for a Spec — the actual codebase. A Spec should be grounded in real modules, files, tables and endpoints, so explore the relevant code before designing.

Then ask the user for what's still missing. Batch your questions (a handful at a time, most important first) instead of asking one by one. For PRDs the gaps are usually: who exactly has the problem, how we know it's a problem, what success looks like in numbers, and what is explicitly out of scope.

If the user doesn't know something, don't fill the gap with a plausible guess — especially metrics, baselines, dates and owners. Write it as an item under **Open questions** (with who should answer it, if known). A visible gap gets resolved; a fabricated number gets shipped.

### 4. Write from the template

- Fill the frontmatter completely. Use today's date for `created`/`updated`. Default `status: draft`.
- Sections marked *(optional)* in the template: drop them when they genuinely don't apply. Required sections stay; if one is truly empty, say so in one line (e.g. "No new dependencies.") so reviewers know it was considered.
- Size the doc to the feature. A small feature's PRD can fit on one screen. Prefer tables and short bullets over prose; nobody reads walls of text in review.
- Write in the language the user is talking to you in, unless the project's existing docs use another language — then match the project. Keep frontmatter keys, requirement IDs and section structure as in the templates so docs stay machine-checkable across languages.
- Link the pair: PRD `spec:` points to `./spec.md`, Spec `prd:` points to `./prd.md`.

### 5. Self-check, then hand over

Run through the checklist below, fix what you can, and finish with a short message: where the files are, what's still open (the Open questions), and the natural next step (e.g. "PRD ready for review → then the Spec").

## Conventions

### Requirement IDs

PRD requirements are numbered `R1`, `R2`, … and the Spec's *Requirements coverage* table maps every ID to the part of the design that satisfies it. This is what lets anyone see at a glance whether something was forgotten.

IDs are permanent: never renumber. A dropped requirement stays in the table marked ~~struck through~~ with a short reason; new ones get the next free number. Other docs, tickets and tests may already reference them.

Priority uses MoSCoW: **Must** / **Should** / **Could**. Each requirement gets at least one acceptance criterion phrased so a tester could check it.

### Status lifecycle

`draft` → `review` → `approved` → `shipped` → (`deprecated`)

Change `status` only when the user says so or the situation is unambiguous (e.g. they say it shipped). An `approved` doc that needs a meaningful change goes back to `review`; mention that to the user rather than silently editing an approved doc.

### Diagrams

Draw every diagram in Mermaid, in a fenced `` ```mermaid `` block inside the doc. No ASCII art, no image files, no links to external drawing tools. Mermaid renders in GitHub, GitLab, Bitbucket, Confluence and most IDEs, and it stays diffable and editable in review alongside the text, so it doesn't go stale the way an exported picture does.

Pick the type by what you're showing:

| Showing | Mermaid type | Typical place |
|---------|--------------|---------------|
| User flow / decision logic | `flowchart` | PRD *Users & scenarios* |
| Interaction between components over time | `sequenceDiagram` | Spec *Overview* |
| Component / service structure | `flowchart` (with `subgraph`) | Spec *Overview*, *Components & changes* |
| Tables and relations | `erDiagram` | Spec *Data model* |
| Lifecycle of an entity (statuses) | `stateDiagram-v2` | Spec *Data model*, *Edge cases* |

Add a diagram when it explains something prose can't do quickly, usually when three or more parties interact or an entity has non-trivial states. Keep each one small, about 15 nodes or messages at most, and split a bigger one by concern. Use the same names as the code and the text, so a reader can map boxes to modules. A PRD diagram shows what the user sees and does, never internal components.

### Decisions

Record significant design choices in the Spec's *Alternatives & decisions* section: the options considered, what was chosen and why. Six months later this is the part people actually look for. If a decision affects several features, suggest to the user that it may deserve its own ADR — but don't create one unprompted.

## Checklist

**PRD**
- [ ] Problem names a concrete user/audience and gives some evidence, not just an assertion.
- [ ] Non-goals exist and are specific.
- [ ] Every requirement has an ID, priority and checkable acceptance criteria.
- [ ] No implementation details (tech choices, schemas, endpoints).
- [ ] Success metrics have a target and a way to measure; unknown baselines are open questions, not guesses.

**Spec**
- [ ] Every PRD requirement appears in *Requirements coverage*; nothing is silently uncovered.
- [ ] *Current state* reflects the real code, with paths where useful.
- [ ] At least one alternative is considered for each non-obvious decision.
- [ ] Failure modes / edge cases are addressed.
- [ ] Testing plan and rollout (including rollback) are present.
- [ ] Doesn't redefine goals or requirements — conflicts are raised as open questions.

**Both**
- [ ] Frontmatter complete; `prd`/`spec` links point at each other.
- [ ] Any diagrams are Mermaid blocks with valid syntax and names that match the text.
- [ ] Open questions list everything unresolved, with an owner where known.
