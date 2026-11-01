---
name: feature-docs
description: Writes, updates and reviews feature documentation — a PRD (why and what), a technical Spec (how) and an implementation task list derived from the Spec — stored next to each other in the project, each kept as mirrored English and Russian versions; also implements a feature task by task from that list. Use this skill whenever the user wants to describe, plan, document or design a feature, asks for a PRD, product requirements, spec, tech spec, design doc, RFC-style write-up, requirements or an implementation plan for something they are about to build, wants to break a spec into tasks, wants to turn notes / a ticket / a conversation into feature docs, asks to implement a feature from its docs, or asks to review or update existing PRD/spec/tasks files — even if they don't say "PRD" or "spec" explicitly (e.g. "let's write down what this feature should do", "опиши фичу", "напиши ПРД", "сделай спеку", "разбей на задачи", "делай по задачам").
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

When implementation starts, a third document, `tasks.md`, turns the Spec into an ordered checklist of small tasks. It says nothing new about what or how: it's the order of work, and the place where progress is ticked off. You, an engineer or a coding agent can work through it task by task.

Every document exists in two languages, English and Russian, and the two versions are exact mirrors at all times: same structure, same facts, same IDs, same diagrams. Each language has its own folder inside the feature folder, with the same file names in both:

```
<feature-slug>/
  en/prd.md   en/spec.md   en/tasks.md
  ru/prd.md   ru/spec.md   ru/tasks.md
```

See *Bilingual mirror* below. This applies to every create, update and fix.

Bundled files (paths relative to this skill's directory):

- Templates: `assets/templates/en/prd.md`, `assets/templates/en/spec.md`, `assets/templates/en/tasks.md`, and their Russian twins under `assets/templates/ru/`.
- Worked example: `references/examples/orders-csv-export/en/prd.md`, `.../en/spec.md` and `.../en/tasks.md`, with Russian twins under `.../ru/`. Read it once if you're unsure about the expected depth and tone.
- Mirror checker: `scripts/check_mirror.py`. Run it, don't read it. It needs only Python 3, no packages.

## Workflow

### 1. Find where docs live in this project

Look before you create anything, so new docs match what the team already has. "The project" is the codebase the feature belongs to, the directory you're working in. In a monorepo, it's the package or app the feature lives in.

- Check that project's `CLAUDE.md` / `README` for a stated docs location.
- Search for existing feature docs (e.g. `**/prd.md`, `**/spec.md`, `docs/features/`). If they exist, follow their location, naming and any deviations from the templates — the project's convention wins over this skill's defaults.
- Otherwise use `docs/features/<feature-slug>/en/` and `.../ru/`, and tell the user where you put them.
- The bilingual mirror in `en/` + `ru/` folders is not a convention a project can opt out of. If a project's existing feature docs are in one language or flat in the feature folder, move them into `en/` (or `ru/`) and create the missing mirror when you touch them. Tell the user you did.

`<feature-slug>` is short kebab-case (`orders-csv-export`, `sso-login`).

### 2. Work out what is being asked

- **New PRD** — the usual starting point.
- **New Spec** — read the PRD first. If there is no PRD, ask whether to write a short one first; if the user declines (small or purely technical change), write the Spec and put the problem and requirements into its Context section so the Spec still stands on its own.
- **PRD and Spec together**: when the user asks for both, write the PRD first and then the Spec from it, in the same pass. Don't stop between them to ask for a PRD review unless the user wants that.
- **Tasks**: read the Spec and the PRD, then write `tasks.md` (see *Tasks* below). Tasks come from a Spec. If there is none, write the Spec first. If the Spec is still `draft`, tell the user the tasks may change with it.
- **Implement from tasks**: see *Working through tasks* below.
- **Update**: edit the existing files in place, both languages in the same pass. Bump `updated` in both and keep requirement IDs stable (see below). Run the mirror check *before* editing too. If the pair is already out of sync, someone edited one side by hand: see *Bilingual mirror* for how to resolve it.
- **Review**: read the doc(s) and report against the checklist at the end of this file, including mirror problems. Don't rewrite unless asked.

### 3. Gather what you need — don't invent it

A feature doc is only useful if it is true. Use what's already available first: the conversation, tickets or notes the user shared, the existing PRD, and — for a Spec — the actual codebase. A Spec should be grounded in real modules, files, tables and endpoints, so explore the relevant code before designing.

Then ask the user for what's still missing. Read the code before you ask, because many product questions only surface there, such as a permission the backend doesn't check or a search that can't do what the ticket assumes. Ask once, before drafting: a single batch, most important first, limited to questions whose answers would change the content. For PRDs the gaps are usually: who exactly has the problem, how we know it's a problem, what success looks like in numbers, and what is explicitly out of scope.

Unanswered questions don't block the draft. If the user doesn't know, tells you to go ahead, or isn't available to ask, write the docs anyway and record every unanswered question under **Open questions**, with who should answer it if known.

Never fill a gap with a plausible guess, especially metrics, baselines, dates and owners. A visible gap gets resolved; a fabricated number gets shipped. Record dates the way the source states them ("next quarter"). Convert a relative date to a calendar date only when the conversion is unambiguous.

### 4. Write from the template

- Fill every frontmatter field. Use today's date for `created`/`updated` and the default `status: draft`. When a value is unknown, typically `owner` or `reviewers`, write `TBD` (or `reviewers: []`) and add an open question for it. Never write a guessed name.
- Sections marked *(optional)* in the template: drop them when they genuinely don't apply. Required sections stay; if one is truly empty, say so in one line (e.g. "No new dependencies.") so reviewers know it was considered.
- Leave no template scaffolding in the finished doc. Placeholder text in angle brackets, guidance paragraphs, *(optional)* markers and frontmatter comments all go.
- Size the doc to the feature. A small feature's PRD can fit on one screen. Prefer tables and short bullets over prose; nobody reads walls of text in review.
- Write the English version first, then produce the Russian mirror from the `assets/templates/ru/` template. Don't write the two independently: two separate drafts drift apart in substance.
- Link the documents. In both languages PRD `spec:` is `./spec.md`, Spec `prd:` is `./prd.md`, and Tasks has both `prd: ./prd.md` and `spec: ./spec.md`, since the siblings sit in the same language folder. Each file's `mirror:` points to its other-language twin: `../ru/prd.md` from `en/`, `../en/prd.md` from `ru/`.

### 5. Self-check, then hand over

Run the mirror check on the feature folder and fix every reported mismatch. `<skill-dir>` is this skill's directory, and the command runs from the project root:

```bash
python3 <skill-dir>/scripts/check_mirror.py docs/features/<feature-slug>
```

If `python3` isn't available, tell the user and do the structural comparison by hand, using the list below.

The script catches structural drift: headings, table rows, list items, checkboxes, requirement IDs, code identifiers, links, Mermaid blocks and frontmatter. It can't judge meaning, so also re-read both versions side by side for content that differs. Then go through the checklist below, fix what you can, and finish with a short message: where the files are, what's still open (the Open questions), and the natural next step. That might be who needs to answer the open questions before review or, once a Spec exists without tasks, offering to break it into `tasks.md`.

## Conventions

### Requirement IDs

PRD requirements are numbered `R1`, `R2`, … and the Spec's *Requirements coverage* table maps every ID to the part of the design that satisfies it. This is what lets anyone see at a glance whether something was forgotten.

IDs are permanent: never renumber. A dropped requirement stays in the table marked ~~struck through~~ with a short reason; new ones get the next free number. Other docs, tickets and tests may already reference them.

Priority uses MoSCoW: **Must** / **Should** / **Could**. Each requirement gets at least one acceptance criterion phrased so a tester could check it.

In *Requirements coverage*, each row says how the design meets the requirement. If the design meets it only in part, or not at all, start the cell with **Partial:** or **Not covered:** and say what's missing. Every such gap also goes to Open questions.

### When the PRD is silent

Sometimes the Spec needs a product decision the PRD doesn't make: a limit, a default, or who can see what. In that case:

- Choose the most conservative option.
- In the Spec, state it as an assumption that points to the question.
- Put the question in the PRD's Open questions, not the Spec's: the PRD is where product decisions get made, and the answer may change a requirement.

The Spec's Open questions are for technical unknowns and for questions about the Spec or `tasks.md` themselves, such as who owns them. `tasks.md` has no Open questions section of its own.

### Open question IDs

Open questions are numbered per document (`Q1`, `Q2`, …) and written as `- [ ] **Q1.** <question> — <who answers>`. Elsewhere, refer to them by document and number: "PRD Q3", "Spec Q1". This form is an ID, so the Russian side writes it the same way ("см. PRD Q3", not "см. Q3 в PRD"). Like requirement IDs they're permanent. When a question is answered, tick it, add the answer after it, and update the places that depended on it.

### Tasks

`tasks.md` is a checklist of tasks `T1`, `T2`, … in the order they should be done. Each task is one checkbox with fields underneath; see the template:

- **Covers**: the requirement IDs the task delivers. For a task that delivers no requirement, use one label instead: `setup` (groundwork such as config, test setup, schema or flags), `verify` (checks on a real environment) or `rollout` (turning it on for users). Every requirement covered by the Spec appears in at least one task.
- **Files**: the real paths it touches, taken from the Spec and the code. For things outside the repo, such as deploy config or a flag service, name the place.
- **Change**: what to do, in one or two lines, pointing to the Spec section. The Spec holds the detail, so don't retell it. If the change needs more than two lines, or the file list is long, the task is too big: split it.
- **Done when**: a check anyone can run, such as tests that pass or behaviour to see. The tests are part of the task, not a separate task at the end. For `setup` tasks, a passing build or test run is enough.
- **Depends on**: the task IDs that must be done first.
- **Blocked by**: the open question that has to be answered first, e.g. "PRD Q5". Anything else a task waits for, such as mockups, another team or an access request, is also recorded as an open question in the PRD (product and design) or the Spec (technical), and the task points to it. A blocker that isn't tracked as a question gets forgotten.

  A question the Spec already answers with an assumption doesn't block: the work goes ahead on that assumption. Block a task only when there's no sensible assumption, or when a different answer would mean redoing the task.

When mockups or final UI text don't exist yet, don't block every UI task on them. Build with provisional text behind the feature flag, and add one late task that applies the final design and text, blocked by the design question.

Size and order tasks so each one is reviewable on its own, roughly one small PR. After each task the app should still build and work: put new behaviour behind the feature flag from the Spec's rollout section early, and leave the rollout steps for the end. Don't add work the Spec doesn't describe. If something is missing, fix the Spec first, then add the task.

Fixing the PRD or Spec while writing tasks is an *Update* of that document: both languages, `updated` bumped, mirror check. That covers a gap the tasks need filled and any break of this skill's conventions you notice on the way, such as unnumbered open questions. List every such change in your hand-over message, because the user didn't ask for it and needs to review it.

Task IDs are permanent, like requirement IDs. Add new tasks with the next free number at the right place in the list. A dropped task stays ~~struck through~~ with a reason.

### Working through tasks

When asked to implement from `tasks.md`:

1. Take the first unchecked task whose dependencies are done and which isn't blocked. Tell the user which one.
2. Implement it and run its *Done when* check.
3. Tick it in both language versions, bump `updated`, and run the mirror check.
4. If the implementation had to differ from the Spec, update the Spec in both languages in the same step. The docs describe what was built, not what was planned.
5. Stop after each task unless the user asked you to continue through several.

When every task is ticked, suggest moving all three documents to `status: shipped`.

### Status lifecycle

`draft` → `review` → `approved` → `shipped` → (`deprecated`)

Change `status` only when the user says so or the situation is unambiguous (e.g. they say it shipped). An `approved` doc that needs a meaningful change goes back to `review`; mention that to the user rather than silently editing an approved doc.

### Bilingual mirror (EN + RU)

English is the primary version (`en/`, `lang: en`). Russian is its mirror: the same file name in `ru/`, with `lang: ru`. "Mirror" means a reader of either version learns exactly the same things:

- **Same structure.** Same headings in the same order, same tables with the same rows in the same order, same list items, same checkbox states. Use the headings from the `assets/templates/ru/` templates exactly, so terminology is consistent across all features.
- **Same facts.** Every number, date, name, status, priority and decision appears in both. Never add a clarification, example or caveat to only one side; if it's worth saying, say it in both.
- **Not translated:**
  - IDs (`R1`, `T1`, `Q1`), priorities (`Must` / `Should` / `Could`) and task labels (`setup` / `verify` / `rollout`);
  - anything in backticks: code, paths, endpoints, events, flags, table and field names;
  - fenced code blocks other than Mermaid, which stay byte-identical, comments included;
  - frontmatter keys, and all frontmatter values except `title`;
  - people's names;
  - UI text such as screen names, button labels, messages and empty states. Quote it exactly as the product shows it, or will show it, in the product's language. It's product content, not doc prose.
- **Diagrams.** The same Mermaid diagram on both sides: identical node IDs, participants and arrows. Only the human-readable labels are translated, and identifiers inside labels stay as they are.
- **Links.** Identical links in the same places. Relative links to sibling docs (`./prd.md`) stay the same and resolve within each language folder.
- **Frontmatter.** Identical except `title`, `lang` and `mirror`. `status` and `updated` always change together on both sides.

Translate for meaning, not word by word. The Russian should read like it was written by a Russian-speaking engineer. Common technical terms that the team says in English anyway (feature flag, rollout, endpoint) may stay in English when the Russian equivalent would be unnatural.

**When the pair is already out of sync** (someone edited one file by hand): use `git diff` / `git log` on both files to see which side changed and what. Port that change to the other side. If both sides changed in conflicting ways, show the user the differences and ask which is right before syncing. Never "fix" drift by blindly regenerating one file from the other: you'd silently discard someone's edit.

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
- [ ] No implementation details (tech choices, schemas, endpoints). Naming an existing analytics event or dashboard as the measurement source is fine.
- [ ] Each success metric has a way to measure and a target. An unknown baseline or target is an open question, not a guess.
- [ ] Product questions the Spec depends on are in the PRD's Open questions.

**Spec**
- [ ] Every PRD requirement appears in *Requirements coverage*. Gaps are marked **Partial:** or **Not covered:**, never left silent.
- [ ] Every assumption made where the PRD is silent points to a PRD open question.
- [ ] *Current state* reflects the real code, with paths where useful.
- [ ] At least one alternative is considered for each non-obvious decision.
- [ ] Failure modes / edge cases are addressed.
- [ ] Testing plan and rollout (including rollback) are present.
- [ ] Doesn't redefine goals or requirements — conflicts are raised as open questions.

**Tasks**
- [ ] Every requirement the Spec covers appears in some task's *Covers*.
- [ ] Every task has real *Files*, a *Change* of at most two lines and a runnable *Done when*, and adds nothing the Spec doesn't describe.
- [ ] *Covers* holds requirement IDs or one of `setup` / `verify` / `rollout`.
- [ ] *Depends on* only points to earlier tasks, and every *Blocked by* names an open question.
- [ ] Any change made to the PRD or Spec along the way is listed in the hand-over message.

**All documents**
- [ ] Frontmatter complete, with `TBD` for unknowns; `prd`/`spec` links point at the siblings.
- [ ] Open questions are numbered `Q1…`, and references to them name the document ("PRD Q2").
- [ ] No template scaffolding left: placeholders, guidance text, *(optional)* markers, frontmatter comments.
- [ ] Any diagrams are Mermaid blocks with valid syntax and names that match the text.
- [ ] `check_mirror.py` passes for the feature folder, and a side-by-side read finds no difference in meaning between EN and RU.
- [ ] Open questions list everything unresolved, with an owner where known.
