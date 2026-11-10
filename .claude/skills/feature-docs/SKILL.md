---
name: feature-docs
description: Writes, updates and reviews feature docs as three mirrored English/Ukrainian documents per feature — PRD (why and what), technical Spec (how), task list (order of work) — and implements a feature task by task from that list. Use whenever the user wants to describe, plan, document or design a feature; asks for a PRD, requirements, spec, design doc, RFC or implementation plan; wants to turn a ticket, notes or a conversation into feature docs; wants to break a spec into tasks or implement from it; or asks to review, audit, check or update PRD/spec/tasks files or a folder of feature docs, or to do the next task from such a list — even without the words "PRD" or "spec" ("let's write down what this feature should do", "опиши фічу", "напиши ПРД", "зроби спеку", "розбий на задачі", "проведи аудит доків", "перевір доки", "наступна задача", or in Russian: "сделай спеку", "разбей на задачи"). Not for READMEs, API reference, changelogs, ADRs or code comments, nor for implementing anything that has no tasks.md.
---

# Feature docs

Three documents per feature, each in English and Ukrainian:

| Document | Answers | Author | Holds | Never holds |
|---|---|---|---|---|
| `prd.md` | Why and what | product / feature owner | problem, users, goals, requirements `R1…`, success metrics | implementation details |
| `spec.md` | How | engineer | current state, design, requirements coverage, decisions, testing, rollout | new goals or changed requirements |
| `tasks.md` | In what order | engineer | checklist `T1…` derived from the Spec, progress ticked off | anything the Spec doesn't describe |

Keep the boundaries: each document is reviewed by different people at different times. A Spec that needs a requirement changed updates the PRD or raises an open question there; it never changes the requirement itself.

Layout inside the feature folder, fixed regardless of project conventions (where that folder lives and what it is called follows the project, see *Locate the docs*):

```
<feature-slug>/            # kebab-case: orders-csv-export
  en/prd.md  en/spec.md  en/tasks.md
  uk/prd.md  uk/spec.md  uk/tasks.md
```

Bundled files, relative to this skill's directory:

- `assets/templates/{en,uk}/{prd,spec,tasks}.md`: the document structure.
- `references/examples/orders-csv-export/`: a worked example, read only when writing a new document: the `en/` set once for depth and tone, and `uk/prd.md` before the first mirror. Review, Update and Implement don't need it.
- `references/mirror.md`: the bilingual mirror rules. Read before writing or editing any `uk/` file.
- `references/diagrams.md`: when to draw, which Mermaid type, where. Read before adding or editing a diagram.
- `references/checklist.md`: the review checklist. Read at hand-over and in Review mode.
- `scripts/check_mirror.py`: checks each file on its own (frontmatter complete, valid and matching the folder, `links:` entries well-formed, headings the template's, IDs defined once, priorities and acceptance criteria present, answered questions carrying their answer, task fields complete and consistent with ticks and drops, no bare URL, Mermaid types known, no scaffolding), each EN/UK pair structurally (headings paired by template position, lists, tables, code blocks byte-identical, Mermaid by node IDs and arrows) and each feature across its documents (every requirement in the Spec's coverage table and, unless dropped or **Not covered:**, in some task's *Covers*; every "PRD Qn" / "Spec Qn" defined; no task blocked by an answered question). Run it (Python 3, no packages); don't read it.
- `scripts/test_check_mirror.py`: the script's own regression cases, for whoever changes the script; not part of checking a feature.

## Workflow

### 1. Locate the docs

The project is the codebase the feature belongs to; in a monorepo, the package or app. Check its `CLAUDE.md` and `README` for a docs location, then search for existing feature docs (`**/prd.md`, `**/spec.md`, `docs/features/`). An existing location and naming win over the default `docs/features/<feature-slug>/`. No docs folder yet means creating `docs/features/<feature-slug>/`. The `en/` + `uk/` mirror is not negotiable: docs found in one language, or flat in the feature folder, belong in `en/` (or `uk/`) with a mirror beside them. Moving someone's files is not a routine edit: say what would move where and ask before doing it, then `git mv` so history follows. Restructuring one is no more routine: a document found with other headings gets the template's (the check script accepts nothing else), but only after saying what would change and asking. A document that exists in Ukrainian only keeps its text as the original; the English side is written as its translation with the same `created` and `updated`, and from then on the usual rule applies (English is the main document).

### 2. Identify the mode

| Request | Do |
|---|---|
| Full set | The default, and what a request that names no document means ("describe the feature", "write the docs"): PRD, then Spec, then Tasks, each from the previous one, in one pass. No review stop between them unless asked. |
| New PRD | Only when the request asks for the PRD and nothing else: the Spec and the tasks are offered in the hand-over. |
| New Spec | Read the PRD first. Without one, offer a short PRD; if declined, write the Spec without the `prd:` key, with the problem and a requirements table (`R1…`, same columns as the PRD's) under *Context & current state*; *Requirements coverage* and the tasks refer to those rows. |
| Tasks | Read the Spec and the PRD, then write `tasks.md` (see *Tasks*). No Spec means write the Spec first. A `draft` Spec means the tasks may change with it: say so. |
| Implement | See *Working through tasks*. |
| Update | Run the mirror check first and resolve an out-of-sync pair before editing (see `references/mirror.md`). Edit both languages in one pass, bump `updated`, keep IDs stable. A Spec change pulls `tasks.md` along (see *Tasks*). |
| Review | Report against `references/checklist.md`, mirror problems included. Read the code and the git log too, not only the documents: the usual findings are a Spec that still describes the state before the feature, tasks that describe a Spec since changed, and requirements with no evidence in the code. Don't rewrite unless asked. |

### 3. Gather facts; invent nothing

Sources, in order: the conversation, tickets and notes, existing docs, the code. A ticket key, a Confluence page, a Figma file or a PR that a connector or CLI can open is read in the same pass, before any question about it; one that can't be opened is asked for as a paste, never guessed at. Read the relevant code before asking anything: a permission the backend doesn't check, or a search that can't do what the ticket assumes, is a product question that surfaces only there. A Spec is grounded in real modules, files, tables and endpoints.

Check the sources for contradictions: two statements that can't both hold, or a value stated differently in two places. Each one becomes a PRD open question that quotes both statements; the Spec picks one reading as an assumption citing that question (see *Spec*). Never resolve a contradiction silently.

Sort what is still unknown by the cost of guessing wrong:

- **Blocking**: a wrong guess means rewriting the document. Who has the problem and the evidence, where the scope ends, a contradiction between sources, whether the feature is wanted at all. Usually one to four per feature.
- **Fill-in**: metrics, baselines, dates, owners, limits, defaults. A wrong guess changes a value, not the document. Never ask these: record each under *Open questions* with who should answer it, and let the Spec make a conservative assumption where it needs a value (see *Spec*).

Ask the blocking questions once, before drafting, and wait for the answer: one AskUserQuestion batch, most important first. Each question is a choice: the answer you would assume comes first, marked recommended, with the reason in its description ("Support operators: the ticket refers to their queue"), then the other readings, so that a reply is one click. Without that tool, ask the same batch in the message. Either way the turn ends there; the draft starts after the answer. Skip the batch and draft on assumptions only when the user said to just write, has already said they don't know, asked not to be asked, or the session runs unattended: then each blocking question goes under *Open questions* too, with the assumption made.

Never substitute a plausible value for a missing metric, baseline, date or owner: a visible gap gets resolved, a fabricated number gets shipped. Keep dates as the source states them ("next quarter") unless the conversion is unambiguous.

### 4. Write

- Fill every frontmatter field: today's date for `created` and `updated`, `status: draft`. A mirror written later copies `created` and `updated` from the original; the pair shares its dates. An unknown `owner` or `reviewers` is `TBD` / `[]`, never a guessed name, with one PRD open question covering all documents whose owner is unknown.
- Drop *(optional)* sections that don't apply. A required section with nothing to say gets one line ("No new dependencies.") so reviewers know it was considered.
- Remove all scaffolding: angle-bracket placeholders, guidance text, *(optional)* markers, frontmatter comments.
- Size to the feature: a small feature's PRD fits one screen. Tables and short bullets over prose.
- English first, in English whatever language the sources are in; then the Ukrainian mirror from the Ukrainian template, by the rules in `references/mirror.md`. Never draft the two independently. A diagram follows `references/diagrams.md`.
- Links: `prd:` / `spec:` / `tasks:` point to the two siblings in the same language folder (`./prd.md`), so every document reaches the other two; `mirror:` points to the twin (`../uk/prd.md` from `en/`).
- Sources: every external source (Jira, Figma, Confluence, a PR, research) is an entry in `links:` of the form `"Role: name — URL"` (`"Jira: TRACK-12"` alone when the key resolves in the team's tracker), in English in both versions, in the document it informs: tickets, designs and research in the PRD, PRs and technical pages in the Spec, the ticket and PRs in Tasks. A fact cites its source in the sentence that uses it (*Problem*, the metrics table, *Context & current state*, *Alternatives & decisions*). No bare URL anywhere, and no separate list of sources in the body.

### 5. Check and hand over

From the project root:

```bash
python3 <skill-dir>/scripts/check_mirror.py <path to the feature folder>
```

Pass the feature folder, or a folder of features, not the whole docs tree: the script reports what it ignored and exits 2 when it checked nothing. Fix every mismatch. Without `python3`, say so and compare by hand against `references/mirror.md`. The script sees structure only, so also read both versions side by side for differences in meaning. Then go through `references/checklist.md`.

The hand-over message names the files, the assumptions the draft rests on (listed apart from the open questions, so a reviewer knows what to check first), the open questions, every change made to a document the user didn't ask to change, and the next step: answers needed before review, or breaking a Spec into tasks.

## Document rules

### IDs

`R1…` requirements, `Q1…` open questions (numbered per document), `T1…` tasks. A task or question is defined by its bold header with the period, `**T1.**` / `**Q1.**`; without the period the script doesn't see it. IDs are permanent: never renumber. A dropped item stays ~~struck through~~ with a reason (the text, never the ID cell, so the row is still found); a new one takes the next free number. Refer to questions by document and number, "PRD Q3" / "Spec Q1", identically in Ukrainian ("див. PRD Q3"). An answered question is ticked and keeps its line, with the answer after the owner: `— Jane Doe. Answered 2026-03-09: …` (Ukrainian: `Відповідь 2026-03-09: …`); dependent text is updated in the same edit: an `Assumption (PRD Qn): …` the answer confirms or replaces becomes a plain statement that keeps the `(PRD Qn)` reference, so a reader can still find why. A requirement, like every other statement, says only what is true now: what it said before, who changed it and when belong to the answered question (or the struck row's reason), so a clarification received in conversation is recorded as a question answered that day, not as history inside the requirement or the summary.

A new item goes where it belongs in the order (a task where it runs, a requirement next to its neighbours), not at the end, so IDs may run out of file order. After inserting one, search the file for its ID: an edit that lands twice is how a duplicate appears, and the check script fails on it.

### PRD

- Requirements table: ID, requirement, priority (MoSCoW: **Must** / **Should** / **Could**), at least one acceptance criterion a tester can check. **Must** is what the feature can't ship without; a debug aid, a convenience, or anything the PRD says will be removed later is **Should** or **Could**. A table that is all **Must** hasn't been prioritised. Criteria may name routes, permissions and analytics events; those are product facts, not implementation details. Stubs, mocks, test names and module names are implementation details: when a criterion can only be verified in automated tests, it says so and stops there.
- Each success metric names a measurement source (an existing analytics event or dashboard is fine) and a target; an unknown baseline or target points to a question ("unknown — see PRD Q2").
- Product decisions the Spec needs but the PRD doesn't make belong in the PRD's open questions.

### Spec

- *Context & current state* describes the real code, with paths.
- *Requirements coverage* lists every PRD requirement, dropped ones included (`Dropped in PRD`). A row the design meets only partly, or not at all, starts with **Partial:** or **Not covered:** (Ukrainian: **Частково:** / **Не покрито:**), says what's missing, and has a matching open question.
- Where the PRD is silent or contradicts itself (a limit, a default, who sees what): take the most conservative option that breaks no other requirement, write it in the section it affects as `Assumption (PRD Q4): …` (Ukrainian: `Припущення (PRD Q4): …`), and add that question to the PRD. If every option breaks some requirement, the requirement it breaks is marked **Partial:** in *Requirements coverage*, citing the same question. The Spec's own open questions are technical, plus questions about the Spec or `tasks.md` themselves; `tasks.md` has no open-questions section. A technical value the Spec needs but can't settle gets the same treatment with its own question, `Assumption (Spec Qn): …`, so the work isn't blocked on it.
- *Alternatives & decisions* records each non-obvious choice: options, choice, reason. A decision spanning several features may deserve an ADR; suggest it, don't create it.
- Edge cases, testing plan, and rollout with rollback are always present.
- The release is the rollout: order it so it is safe (migrations backward compatible and ahead of the code), and roll back by redeploying the previous version.

### Tasks

One checkbox per task, fields underneath, in execution order:

- **Covers**: exactly one line per task: requirement IDs, or one label, never both: `setup` (scaffolding, config, test infrastructure, schema), `verify` (checks on a real environment), `rollout`. Every requirement the Spec covers appears in at least one task. A dropped task stays ~~struck through~~ with the reason and keeps no fields.
- **Files**: real paths from the Spec and the code; for things outside the repo, the place.
- **Change**: at most two sentences, citing the Spec section. Longer, or more than about five files, means the task is too big: split it.
- **Done when**: a check anyone can run. Tests belong to the task, not to a final "write tests" task; for `setup`, a passing build or test run is enough.
- **Depends on**: earlier task IDs.
- **Blocked by**: the open question that must be answered first; omit the line when nothing blocks. Every blocker, including mockups, another team or an access request, is tracked as an open question (PRD for product and design, Spec for technical). An assumption the Spec already makes doesn't block; block only when no sensible assumption exists or a different answer would mean redoing the task.

Each task is reviewable alone, about one small PR, and leaves the app building and working, with nothing half-built reachable: build the internals first and add the entry point (route, button, menu item) in the last task the flow needs. Missing mockups or final UI text don't block UI tasks: build with provisional text and add one late task for the final design, blocked by the design question.

Tasks add nothing the Spec doesn't describe. A gap is fixed in the Spec first, then the task is added. A change asked for during implementation takes the same road as the feature itself: a requirement in the PRD (the next free R), its design in the Spec, then the task. Any fix to the PRD or Spec while writing tasks, including convention breaks noticed on the way, is an *Update* (both languages, `updated`, mirror check) and is listed in the hand-over message.

Tasks follow the Spec after they are done as well. A Spec change is followed by a pass over `tasks.md`: every task, ticked or not, whose *Files*, *Change* or *Done when* cite what changed is brought in line in the same update; a ticked task whose work a later task replaced stays ticked and names it ("replaced by T13"). A task list that describes a Spec that no longer exists is a review finding.

### Working through tasks

1. Take the first unchecked task whose dependencies are done and which isn't blocked. Name it.
2. Implement it and run its *Done when*.
3. Tick it in both languages, bump `updated`, run the mirror check.
4. If the implementation diverged from the Spec, update the Spec in the same step: the docs describe what was built.
5. Stop after each task unless asked to continue.

When all tasks are ticked, re-read the Spec against the code: *Context & current state*, the diagrams and the signatures in *API / interfaces* describe the code as it is now, not the state before the feature. Then propose `status: shipped` for all three documents.

### Status

`draft` → `review` → `approved` → `shipped` → `deprecated`. Change it only on the user's word or when unambiguous. A meaningful change to an `approved` document returns it to `review`; say so instead of editing silently.
