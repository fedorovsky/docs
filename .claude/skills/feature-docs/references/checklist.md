# Checklist

What a reviewer checks. Go through it before handing over a new or updated document, and report against it in Review mode. `check_mirror.py` owns the structure (frontmatter, headings, IDs, task fields, links, scaffolding); everything here is a judgment call it can't make.

**PRD**
- [ ] Problem names a concrete audience and evidence.
- [ ] Non-goals are present and specific.
- [ ] Every acceptance criterion is something a tester can check; **Must** is only what can't ship without.
- [ ] No implementation details.
- [ ] Every metric has a source and a target, or a question for the unknown; no number the sources don't state.
- [ ] Product questions the Spec depends on are here.
- [ ] Every contradiction in the sources is an open question quoting both statements.
- [ ] Requirements state the current truth only; history sits in the answered questions.

**Spec**
- [ ] Each coverage row claims no more than the design does; **Partial:** / **Not covered:** where it falls short.
- [ ] Every assumption cites a PRD question and breaks no requirement, or the one it breaks is marked **Partial:**.
- [ ] *Context & current state* matches the code, with paths; once the tasks are done, so do the diagrams and the signatures.
- [ ] Each non-obvious decision lists an alternative.
- [ ] Edge cases, testing plan, rollout and rollback present.
- [ ] No goal or requirement redefined.

**Tasks**
- [ ] Real *Files*, *Change* ≤ 2 sentences, runnable *Done when*; nothing beyond the Spec.
- [ ] The entry point comes in the last task its flow needs; nothing half-built is reachable.
- [ ] No task describes something the Spec no longer says; a replaced task names its replacement.
- [ ] Changes to the PRD or Spec are listed in the hand-over.

**All**
- [ ] `check_mirror.py` passes; a side-by-side read finds no difference in meaning.
- [ ] Unknown owner or reviewers are `TBD` / `[]`, not a guessed name.
- [ ] Every external source sits in `links:` of the document it informs, and each fact taken from it is cited where it is used.
- [ ] Everything unresolved is an open question, with an owner where known.
- [ ] Blocking questions were asked before drafting, or the hand-over says why they were skipped and lists the assumptions made instead.
- [ ] Mermaid renders, and its names match the text.
