# docs

Claude Code skills for documentation.

## feature-docs

Skill for writing feature documentation as a linked pair:

- **PRD** — why and what: problem, goals, numbered requirements (`R1…`), success metrics.
- **Spec** — how: design grounded in the real code, requirements coverage, decisions, testing, rollout.

By default docs go to `docs/features/<feature-slug>/{prd,spec}.md` in the target project; if the project already has its own convention, the skill follows it.

```
feature-docs/
  SKILL.md                        # workflow, conventions, review checklist
  templates/prd.md, spec.md       # document templates
  examples/orders-csv-export/     # worked example of both documents
```

### Install

For all projects (symlink, so edits in this repo apply immediately):

```bash
ln -s "$(pwd)/feature-docs" ~/.claude/skills/feature-docs
```

For a single project (the skill is versioned with that project):

```bash
cp -r feature-docs /path/to/project/.claude/skills/
```

### Use

Just describe what you need — the skill triggers on requests like "write a PRD for …", "сделай спеку по этой фиче", "review the spec in docs/features/sso-login". You can also call it explicitly with `/feature-docs`.
