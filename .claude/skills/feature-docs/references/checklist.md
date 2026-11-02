# Checklist

What a reviewer checks. Go through it before handing over a new or updated document, and report against it in Review mode.

**PRD**
- [ ] Problem names a concrete audience and evidence.
- [ ] Non-goals are present and specific.
- [ ] Every requirement has an ID, priority and checkable acceptance criteria.
- [ ] No implementation details.
- [ ] Every metric has a source and a target, or a question for the unknown.
- [ ] Product questions the Spec depends on are here.
- [ ] Every contradiction in the sources is an open question quoting both statements.

**Spec**
- [ ] Every requirement is in *Requirements coverage*; gaps marked **Partial:** / **Not covered:**.
- [ ] Every assumption cites a PRD question and breaks no requirement, or the one it breaks is marked **Partial:**.
- [ ] *Context & current state* matches the code, with paths; once the tasks are done, so do the diagrams and the signatures.
- [ ] Each non-obvious decision lists an alternative.
- [ ] Edge cases, testing plan, rollout and rollback present.
- [ ] No goal or requirement redefined.

**Tasks**
- [ ] Every task has exactly one *Covers*: requirement IDs or one label (`setup` / `verify` / `rollout`), never both; every covered requirement appears in some *Covers*.
- [ ] Real *Files*, *Change* ≤ 2 sentences, runnable *Done when*; nothing beyond the Spec.
- [ ] The entry point comes in the last task its flow needs; nothing half-built is reachable.
- [ ] Every task ID is defined once and tasks are in execution order: *Depends on* points to a task above; every *Blocked by* names a question.
- [ ] No task describes something the Spec no longer says; a replaced task names its replacement.
- [ ] Changes to the PRD or Spec are listed in the hand-over.

**All**
- [ ] Frontmatter complete (`TBD` for unknowns); sibling and mirror links correct.
- [ ] Every external source is a `"Role: name — URL"` entry in `links:` of the document it informs, and each fact taken from it is cited where it is used; no bare URLs.
- [ ] Open questions numbered and referenced as "PRD Qn"; everything unresolved listed, with an owner where known.
- [ ] Blocking questions were asked before drafting, or the hand-over says why they were skipped and lists the assumptions made instead.
- [ ] No scaffolding left.
- [ ] Mermaid syntax valid; names match the text.
- [ ] `check_mirror.py` passes; a side-by-side read finds no difference in meaning.
