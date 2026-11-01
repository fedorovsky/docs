# docs

Claude Code skills for documentation.

## feature-docs

Skill for writing feature documentation as a linked pair:

- **PRD** — why and what: problem, goals, numbered requirements (`R1…`), success metrics.
- **Spec** — how: design grounded in the real code, requirements coverage, decisions, testing, rollout.

Every document is kept in English and Russian, in `en/` and `ru/` folders, and the two are exact mirrors through every create and edit.

By default docs go here in the target project (if the project already has its own location for feature docs, the skill uses it):

```
docs/features/<feature-slug>/
  en/prd.md  en/spec.md
  ru/prd.md  ru/spec.md
```

```
feature-docs/
  SKILL.md                        # workflow, conventions, review checklist
  templates/en/, templates/ru/    # prd/spec templates
  scripts/check_mirror.py         # structural EN/RU mirror check
  examples/orders-csv-export/     # worked example, en/ + ru/
```

Check mirrors yourself (e.g. after editing a doc by hand, or in CI):

```bash
python3 ~/.claude/skills/feature-docs/scripts/check_mirror.py docs/features
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
